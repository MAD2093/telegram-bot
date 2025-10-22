package main

import (
	"log"
	"tg_bot/bot"
	"tg_bot/config"
	"tg_bot/monitoring"
)

func main() {
	// Загружаем конфигурацию
	cfg, err := config.LoadConfig()
	if err != nil {
		log.Fatalf("Ошибка загрузки конфигурации: %v", err)
	}

	// Запускаем сервер метрик
	go monitoring.StartMetricsServer("9001")

	// Инициализируем бота
	bot, err := bot.NewBot(cfg)
	if err != nil {
		log.Fatalf("Ошибка инициализации бота: %v", err)
	}

	// Запускаем бота
	bot.Start()
}
