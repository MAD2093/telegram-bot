package config

import (
	"fmt"
	"log"
	"os"
)

// URL шаблоны для бирж
const (
	MEXC_URL     = "https://www.mexc.com/ru-RU/exchange/%s_%s"
	GATE_URL     = "https://www.gate.io/trade/%s_%s"
	BYBIT_URL    = "https://www.bybit.com/trade/spot/%s%s"
	BINGX_URL    = "https://bingx.com/en-us/spot/%s%s"
	BITGET_URL   = "https://www.bitget.com/spot/%s%s"
	KUCOIN_URL   = "https://www.kucoin.com/trade/%s-%s"
	HTX_URL      = "https://www.htx.com/en-us/markets/%s%s"
	OKX_URL      = "https://www.okx.com/trade-spot/%s-%s"
	POLONIEX_URL = "https://www.poloniex.com/trade/%s_%s"
	BITMART_URL  = "https://www.bitmart.com/trade/en?symbol=%s_%s"
	BINANCE_URL  = "https://www.binance.com/en/trade/%s_%s"
)

type Config struct {
	TelegramToken string
	RedisAddr     string
	RedisPassword string
	Exchanges     []string
	ExchangeURLs  map[string]string
	DatabaseURL   string
}

func LoadConfig() (*Config, error) {
	token := os.Getenv("TELEGRAM_BOT_TOKEN")
	if token == "" {
		return nil, fmt.Errorf("TELEGRAM_BOT_TOKEN не установлен")
	}

	redisAddr := os.Getenv("REDIS_ADDR")
	if redisAddr == "" {
		redisAddr = "localhost:6379"
	}

	redisPassword := os.Getenv("REDIS_PASSWORD")
	if redisPassword == "" {
		redisPassword = "your_strong_password"
	}

	databaseURL := os.Getenv("DATABASE_URL")
	if databaseURL == "" {
		log.Panic("DATABASE_URL не установлен")
	}

	// Список поддерживаемых бирж
	exchanges := []string{
		"MEXC",
		"GATE",
		"BYBIT",
		"BINGX",
		"BITGET",
		"KUCOIN",
		"HTX",
		"OKX",
		"POLONIEX",
		"BITMART",
		"BINANCE",
	}

	// URL шаблоны для бирж
	exchangeURLs := map[string]string{
		"MEXC":     MEXC_URL,
		"GATE":     GATE_URL,
		"BYBIT":    BYBIT_URL,
		"BINGX":    BINGX_URL,
		"BITGET":   BITGET_URL,
		"KUCOIN":   KUCOIN_URL,
		"HTX":      HTX_URL,
		"OKX":      OKX_URL,
		"POLONIEX": POLONIEX_URL,
		"BITMART":  BITMART_URL,
		"BINANCE":  BINANCE_URL,
	}

	return &Config{
		TelegramToken: token,
		RedisAddr:     redisAddr,
		RedisPassword: redisPassword,
		Exchanges:     exchanges,
		ExchangeURLs:  exchangeURLs,
		DatabaseURL:   databaseURL,
	}, nil
}
