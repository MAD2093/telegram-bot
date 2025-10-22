package monitoring

import (
	"fmt"
	"time"

	"tg_bot/models"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

var (
	// Метрики для пользователей
	TotalUsers = promauto.NewGauge(prometheus.GaugeOpts{
		Name: "bot_total_users",
		Help: "Общее количество пользователей бота",
	})

	// Метрики для пар
	ProcessedPairs = promauto.NewCounter(prometheus.CounterOpts{
		Name: "bot_processed_pairs_total",
		Help: "Общее количество обработанных пар",
	})

	FilteredPairs = promauto.NewCounterVec(prometheus.CounterOpts{
		Name: "bot_filtered_pairs_total",
		Help: "Количество отфильтрованных пар по причине",
	}, []string{"reason"})

	// Метрики для очередей
	QueueSize = promauto.NewGaugeVec(prometheus.GaugeOpts{
		Name: "bot_queue_size",
		Help: "Размер очередей для каждого пользователя",
	}, []string{"user_id", "queue_type"})

	// Метрики для времени обработки
	ProcessingTime = promauto.NewHistogram(prometheus.HistogramOpts{
		Name:    "bot_processing_time_seconds",
		Help:    "Время обработки пары в секундах",
		Buckets: prometheus.DefBuckets,
	})

	// Метрики для Redis
	RedisOperations = promauto.NewCounterVec(prometheus.CounterOpts{
		Name: "bot_redis_operations_total",
		Help: "Количество операций с Redis",
	}, []string{"operation"})

	RedisErrors = promauto.NewCounterVec(prometheus.CounterOpts{
		Name: "bot_redis_errors_total",
		Help: "Количество ошибок Redis",
	}, []string{"operation"})
)

// Обновление метрик
func UpdateUserMetrics(users map[int64]*models.User) {
	TotalUsers.Set(float64(len(users)))
}

func UpdateQueueMetrics(userID int64, newQueue, updateQueue []models.ArbPair) {
	QueueSize.WithLabelValues(fmt.Sprintf("%d", userID), "new").Set(float64(len(newQueue)))
	QueueSize.WithLabelValues(fmt.Sprintf("%d", userID), "update").Set(float64(len(updateQueue)))
}

func IncrementProcessedPairs() {
	ProcessedPairs.Inc()
}

func IncrementFilteredPairs(reason string) {
	FilteredPairs.WithLabelValues(reason).Inc()
}

func ObserveProcessingTime(duration time.Duration) {
	ProcessingTime.Observe(duration.Seconds())
}

func IncrementRedisOperation(operation string) {
	RedisOperations.WithLabelValues(operation).Inc()
}

func IncrementRedisError(operation string) {
	RedisErrors.WithLabelValues(operation).Inc()
}
