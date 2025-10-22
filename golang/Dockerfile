# Этап сборки
FROM golang:1.22-alpine AS builder

# Установка необходимых зависимостей для сборки
RUN apk add --no-cache git

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY go.mod go.sum ./
RUN go mod download

# Копирование исходного кода
COPY . .

# Сборка приложения
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

# Финальный этап
FROM alpine:latest

# Установка необходимых пакетов для работы
RUN apk --no-cache add ca-certificates tzdata curl

WORKDIR /root/

# Копирование бинарного файла из этапа сборки
COPY --from=builder /app/main .

# Открытие порта (замените на нужный вам порт)
EXPOSE 8081

# Добавляем healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8081/metrics || exit 1

# Запуск приложения
CMD ["./main"]
