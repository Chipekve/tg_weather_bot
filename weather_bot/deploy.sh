#!/bin/bash

echo "🚀 Развертывание Weather Bot на VPS..."

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден!"
    echo "Скопируйте env.example в .env и заполните переменные:"
    echo "cp env.example .env"
    echo "nano .env"
    exit 1
fi

# Останавливаем и удаляем старые контейнеры
echo "🛑 Останавливаем старые контейнеры..."
docker-compose down

# Удаляем старые образы (опционально)
echo "🧹 Очищаем старые образы..."
docker system prune -f

# Собираем и запускаем
echo "🔨 Собираем и запускаем контейнеры..."
docker-compose up -d --build

# Проверяем статус
echo "📊 Проверяем статус контейнеров..."
docker-compose ps

echo "✅ Развертывание завершено!"
echo "📝 Логи бота: docker-compose logs -f bot"
echo "📝 Логи БД: docker-compose logs -f postgres"
echo "🛑 Остановка: docker-compose down" 