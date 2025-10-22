package services

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"tg_bot/models"

	"github.com/redis/go-redis/v9"
)

type RedisService struct {
	client *redis.Client
}

func NewRedisService(addr, password string) (*RedisService, error) {
	client := redis.NewClient(&redis.Options{
		Addr:     addr,
		Password: password,
		DB:       0,
	})

	// Проверяем подключение
	if err := client.Ping(context.Background()).Err(); err != nil {
		return nil, err
	}

	return &RedisService{
		client: client,
	}, nil
}

func (s *RedisService) SubscribeToArbitrage(ctx context.Context, pairChan chan<- models.ArbPair) error {
	pubsub := s.client.Subscribe(ctx, "arbitrage:spot:update")
	defer pubsub.Close()

	ch := pubsub.Channel()

	for msg := range ch {
		fmt.Println("Получено новое сообщение")
		var redisMsg models.RedisMessage
		if err := json.Unmarshal([]byte(msg.Payload), &redisMsg); err != nil {
			log.Printf("Ошибка разбора JSON: %v", err)
			continue
		}

		if redisMsg.Type != "update_data" {
			log.Printf("Неизвестный тип сообщения: %s", redisMsg.Type)
			continue
		}

		fmt.Printf("Обработана пара: %+v\n", redisMsg.Update)
		pairChan <- redisMsg.Update
	}

	return nil
}
