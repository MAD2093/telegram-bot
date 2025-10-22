package services

import (
	"context"
	"fmt"
	"strings"
	"tg_bot/models"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

type DBService struct {
	db *gorm.DB
}

func NewDBService(ctx context.Context, databaseURL string) (*DBService, error) {
	db, err := gorm.Open(postgres.Open(databaseURL), &gorm.Config{})
	if err != nil {
		return nil, fmt.Errorf("ошибка подключения к БД: %w", err)
	}

	// Проверяем подключение
	sqlDB, err := db.DB()
	if err != nil {
		return nil, fmt.Errorf("ошибка получения sql.DB: %w", err)
	}
	if err := sqlDB.PingContext(ctx); err != nil {
		return nil, fmt.Errorf("БД не отвечает: %w", err)
	}

	return &DBService{db: db}, nil
}

// AutoMigrate выполняет автоматические миграции для всех таблиц бота
func (s *DBService) AutoMigrate(ctx context.Context) error {
	return s.db.WithContext(ctx).AutoMigrate(
		&models.User{},
		&models.DepositExchange{},
		&models.WithdrawExchange{},
		&models.BlacklistedCoin{},
		&models.BlacklistedNet{},
	)
}

// LoadUsers загружает всех активных пользователей и их фильтры через GORM
func (s *DBService) LoadUsers(ctx context.Context) (*models.UserStore, error) {
	var users []models.User

	// GORM автоматически загрузит связанные таблицы черных списков
	if err := s.db.WithContext(ctx).Preload("DepositExchanges").Preload("WithdrawExchanges").Preload("BlacklistedCoins").Preload("BlacklistedNets").Where("active = ?", true).Find(&users).Error; err != nil {
		return nil, fmt.Errorf("ошибка запроса пользователей: %w", err)
	}

	result := models.NewUserStore()
	for i := range users {
		user := &users[i]
		// Нормализуем названия к UPPERCASE
		s.normalizeUserBlacklists(user)
		result.Set(user.TgID, user)
	}

	return result, nil
}

// normalizeUserBlacklists нормализует названия в черных списках к UPPERCASE
func (s *DBService) normalizeUserBlacklists(user *models.User) {
	for i := range user.BlacklistedDepositExchanges {
		user.BlacklistedDepositExchanges[i].Name = strings.ToUpper(strings.TrimSpace(user.BlacklistedDepositExchanges[i].Name))
	}
	for i := range user.BlacklistedWithdrawExchanges {
		user.BlacklistedWithdrawExchanges[i].Name = strings.ToUpper(strings.TrimSpace(user.BlacklistedWithdrawExchanges[i].Name))
	}
	for i := range user.BlacklistedCoins {
		user.BlacklistedCoins[i].Name = strings.ToUpper(strings.TrimSpace(user.BlacklistedCoins[i].Name))
	}
	for i := range user.BlacklistedNets {
		user.BlacklistedNets[i].Name = strings.ToUpper(strings.TrimSpace(user.BlacklistedNets[i].Name))
	}
}

// ContainsExchange проверяет наличие биржи в черном списке депозитов
func (s *DBService) ContainsExchange(exchanges []models.DepositExchange, name string) bool {
	for _, ex := range exchanges {
		if ex.Name == name {
			return true
		}
	}
	return false
}

// ContainsWithdrawExchange проверяет наличие биржи в черном списке выводов
func (s *DBService) ContainsWithdrawExchange(exchanges []models.WithdrawExchange, name string) bool {
	for _, ex := range exchanges {
		if ex.Name == name {
			return true
		}
	}
	return false
}

// ContainsCoin проверяет наличие монеты в черном списке
func (s *DBService) ContainsCoin(coins []models.BlacklistedCoin, name string) bool {
	for _, coin := range coins {
		if coin.Name == name {
			return true
		}
	}
	return false
}

// ContainsNetwork проверяет наличие сети в черном списке
func (s *DBService) ContainsNetwork(networks []models.BlacklistedNet, name string) bool {
	for _, net := range networks {
		if net.Name == name {
			return true
		}
	}
	return false
}
