package models

import (
	"sync"

	sharedSpot "github.com/MAD2093/shared-go/pkg/models/spotarbitrage"
	sharedTelegramBot "github.com/MAD2093/shared-go/pkg/models/telegrambot"
)

// алиасы
type ArbPair = sharedSpot.ServerData
type RedisMessage = sharedSpot.RedisMessage
type User = sharedTelegramBot.User
type DepositExchange = sharedTelegramBot.DepositExchange
type WithdrawExchange = sharedTelegramBot.WithdrawExchange
type BlacklistedCoin = sharedTelegramBot.BlacklistedCoin
type BlacklistedNet = sharedTelegramBot.BlacklistedNet

type UserStore struct {
	mu    sync.RWMutex
	users map[int64]*User
}

func NewUserStore() *UserStore {
	return &UserStore{
		users: make(map[int64]*User),
	}
}

// Get возвращает фильтр пользователя (чтение, без блокировки для других читателей)
func (s *UserStore) Get(userID int64) (*User, bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	filter, ok := s.users[userID]
	return filter, ok
}

// Set обновляет фильтр (блокировка на запись)
func (s *UserStore) Set(userID int64, filter *User) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.users[userID] = filter
}

// Delete удаляет фильтр
func (s *UserStore) Delete(userID int64) {
	s.mu.Lock()
	defer s.mu.Unlock()
	delete(s.users, userID)
}

// Range применяет функцию ко всем фильтрам (блокировка на чтение)
func (s *UserStore) Range(f func(userID int64, filter *User) bool) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	for id, filter := range s.users {
		if !f(id, filter) {
			break
		}
	}
}

// Len возвращает количество элементов в хранилище (потокобезопасно)
func (s *UserStore) Len() int {
	s.mu.RLock()         // Блокируем на чтение
	defer s.mu.RUnlock() // Разблокируем при выходе
	return len(s.users)
}
