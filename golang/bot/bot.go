package bot

import (
	"context"
	"fmt"
	"log"
	"strconv"
	"strings"
	"sync"
	"tg_bot/config"
	"tg_bot/models"
	"tg_bot/services"

	"github.com/MAD2093/shared-go/pkg/models/spotarbitrage"
	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
)

type Bot struct {
	api          *tgbotapi.BotAPI
	config       *config.Config
	redisService *services.RedisService
	dbService    *services.DBService
	users        *models.UserStore
	wg           sync.WaitGroup
	ctx          context.Context
	cancel       context.CancelFunc
}

func NewBot(cfg *config.Config) (*Bot, error) {
	api, err := tgbotapi.NewBotAPI(cfg.TelegramToken)
	if err != nil {
		return nil, err
	}

	// Явно удаляем вебхук и не слушаем апдейты
	if _, err := api.Request(tgbotapi.DeleteWebhookConfig{DropPendingUpdates: true}); err != nil {
		log.Printf("Не удалось удалить webhook: %v", err)
	}

	ctx := context.Background()

	dbService, err := services.NewDBService(ctx, cfg.DatabaseURL)
	if err != nil {
		return nil, err
	}
	// Выполняем авто-миграции
	if err := dbService.AutoMigrate(ctx); err != nil {
		return nil, fmt.Errorf("ошибка авто-миграции: %w", err)
	}

	redisService, err := services.NewRedisService(cfg.RedisAddr, cfg.RedisPassword)
	if err != nil {
		return nil, err
	}

	users, err := dbService.LoadUsers(ctx)
	if err != nil {
		return nil, err
	}
	log.Printf("Загружено пользователей: %d", users.Len())

	bot := &Bot{
		api:          api,
		config:       cfg,
		redisService: redisService,
		dbService:    dbService,
		users:        users,
		ctx:          ctx,
	}

	return bot, nil
}

func (b *Bot) Start() {
	log.Printf("Бот %s запущен", b.api.Self.UserName)

	// Запускаем обработку пар из Redis
	b.wg.Add(1)
	go b.handleArbitragePairs()

	// Ждем завершения всех горутин
	b.wg.Wait()
}

func (b *Bot) handleArbitragePairs() {
	defer b.wg.Done()

	pairChan := make(chan models.ArbPair)
	go b.redisService.SubscribeToArbitrage(b.ctx, pairChan)

	for {
		select {
		case <-b.ctx.Done():
			return
		case pair := <-pairChan:
			b.processPair(pair)
		}
	}
}

func (b *Bot) processPair(pair models.ArbPair) {
	b.users.Range(func(userID int64, user *models.User) bool {
		if user.CheckFilter(&pair) {
			b.sendPair(user, pair)
		}
		return true
	})
}

// calculatePrice считает средневзвешенную цену для заданного объема.
func CalculatePrice(book *[]spotarbitrage.Order, coins float64) float64 {
	var sum float64
	var orderBookVol float64
	remainingVol := coins

	for _, order := range *book {
		orderBookVol += order.Amount

		if remainingVol <= order.Amount {
			sum += remainingVol * order.Price
			break
		}

		remainingVol -= order.Amount
		sum += order.Amount * order.Price
	}

	if orderBookVol < coins {
		return -1
	}

	return sum / coins
}

func (b *Bot) sendPair(user *models.User, pair models.ArbPair) {
	var userVolume float64
	// a   b    VolumeMin  VolumeMax
	// 400 600  500        1000       - return 600
	// 600 900  500        1000       - return 900
	// 900 1100 500        1000       - return 1000
	if pair.Data.Up.AskVolUsdt > user.VolumeMax {
		userVolume = user.VolumeMax
	} else {
		userVolume = pair.Data.Up.AskVolUsdt
	}

	// считаем данные с объёмом выведенным
	// из фильтра
	buyPrice := CalculatePrice(&pair.OrderBook.Asks, userVolume)
	sellPrice := CalculatePrice(&pair.OrderBook.Bids, userVolume-pair.WithdrawalFee)
	totalFee := pair.MakerFee*userVolume + pair.WithdrawalFee
	spread := ((sellPrice - buyPrice) / buyPrice) * 100
	profit := sellPrice*(userVolume-pair.WithdrawalFee) - buyPrice*userVolume

	var sb strings.Builder

	// Первая строка (основная инфа для шторки)
	sb.WriteString(pair.Symbol)
	sb.WriteString(" | ")
	sb.WriteString(pair.WithdrawalExchange)
	sb.WriteString(" → ")
	sb.WriteString(pair.DepositExchange)
	sb.WriteString(" | ")
	sb.WriteString(strconv.FormatFloat(spread, 'f', 2, 64))
	sb.WriteString("% ")
	sb.WriteString(strconv.FormatFloat(profit, 'f', 2, 64))
	sb.WriteString("$\n\n")

	sb.WriteString("🪙 Монета: *")
	sb.WriteString(pair.Symbol)
	sb.WriteString("*\n")
	sb.WriteString("🔗 Биржи: ")
	sb.WriteString(b.generateExchangeLinks(&pair))
	sb.WriteString("\n\n")

	// Блок 1 – первая биржа (Ask)
	sb.WriteString(pair.WithdrawalExchange)
	sb.WriteString(": ")
	sb.WriteString("\n    💰 Price: $*")
	sb.WriteString(strconv.FormatFloat(buyPrice, 'f', 2, 64))
	sb.WriteString("*\n    📊 Volume: *")
	sb.WriteString(strconv.FormatFloat(userVolume, 'f', 2, 64))
	sb.WriteString("* USDT → *")
	sb.WriteString(strconv.FormatFloat(userVolume/buyPrice, 'f', 2, 64)) // пересчет в coin
	sb.WriteString("* ")
	sb.WriteString(pair.Symbol)
	sb.WriteString("\n    🏦 Withdrawal: *")
	sb.WriteString(pair.WithdrawalNetwork)
	sb.WriteString("*\n\n")

	// Блок 2 – вторая биржа (Bid)
	sb.WriteString(pair.DepositExchange)
	sb.WriteString(": ")
	sb.WriteString("\n    💰 Price: $*")
	sb.WriteString(strconv.FormatFloat(sellPrice, 'f', 2, 64))
	sb.WriteString("*\n    📊 Volume: *")
	sb.WriteString(strconv.FormatFloat((userVolume-pair.WithdrawalFee)/sellPrice, 'f', 2, 64)) // пересчет в coin
	sb.WriteString("* ")
	sb.WriteString(pair.Symbol)
	sb.WriteString(" → *")
	sb.WriteString(strconv.FormatFloat(userVolume-pair.WithdrawalFee, 'f', 2, 64))
	sb.WriteString("* USDT")
	sb.WriteString("\n    🏦 Deposit: *")
	sb.WriteString(pair.WithdrawalNetwork)
	sb.WriteString("*\n\n")

	// Дополнительная инфа
	sb.WriteString("📈 Спред: *")
	sb.WriteString(strconv.FormatFloat(spread, 'f', 2, 64))
	sb.WriteString("%*\n")
	sb.WriteString("💵 Профит: *")
	sb.WriteString(strconv.FormatFloat(profit, 'f', 2, 64))
	sb.WriteString("$*\n")
	sb.WriteString("✂️ Комиссия: *")
	sb.WriteString(strconv.FormatFloat(totalFee, 'f', 2, 64))
	sb.WriteString("$*\n")
	sb.WriteString("⏳ Время вывода: ~*")
	sb.WriteString(pair.WithdrawalTime)
	sb.WriteString("*\n💰 Макс. объем: *")
	sb.WriteString(strconv.FormatFloat(pair.Data.Up.AskVolUsdt, 'f', 2, 64))
	sb.WriteString("$*\n\n")
	sb.WriteString("⏳ Время жизни: *")
	sb.WriteString(pair.TimeLife)
	sb.WriteString("*")

	msg := tgbotapi.NewMessage(user.TgID, sb.String())
	msg.ParseMode = "Markdown"
	msg.DisableWebPagePreview = true

	if _, err := b.api.Send(msg); err != nil {
		log.Printf("Ошибка отправки пары: %v", err)
	}
}

// generateExchangeLinks генерирует гиперссылки на биржи для пары
func (b *Bot) generateExchangeLinks(pair *models.ArbPair) string {
	var links []string
	base := pair.Symbol
	quote := "USDT"

	// Создаем ссылки для бирж из пары
	withdrawExchange := strings.ToUpper(pair.WithdrawalExchange)
	depositExchange := strings.ToUpper(pair.DepositExchange)

	// Добавляем ссылку на биржу вывода
	if urlTemplate, ok := b.config.ExchangeURLs[withdrawExchange]; ok {
		url := fmt.Sprintf(urlTemplate, base, quote)
		links = append(links, fmt.Sprintf("[%s](%s)", withdrawExchange, url))
	}

	// Добавляем ссылку на биржу депозита
	if urlTemplate, ok := b.config.ExchangeURLs[depositExchange]; ok {
		url := fmt.Sprintf(urlTemplate, base, quote)
		links = append(links, fmt.Sprintf("[%s](%s)", depositExchange, url))
	}

	return strings.Join(links, " → ")
}
