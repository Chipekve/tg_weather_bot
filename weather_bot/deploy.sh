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

# Получаем последние изменения из git
echo "📥 Получаем последние изменения..."
git pull origin main

# Останавливаем и удаляем старые контейнеры
echo "🛑 Останавливаем старые контейнеры..."
docker-compose down

# Удаляем старые образы (опционально)
echo "🧹 Очищаем старые образы..."
docker system prune -f

# Собираем и запускаем
echo "🔨 Собираем и запускаем контейнеры..."
docker-compose up -d --build

# Ждем немного для запуска
echo "⏳ Ждем запуска сервисов..."
sleep 10

# Проверяем статус
echo "📊 Проверяем статус контейнеров..."
docker-compose ps

# Проверяем логи на ошибки
echo "🔍 Проверяем логи на ошибки..."
if docker-compose logs bot | grep -i "error\|exception\|traceback" > /dev/null; then
    echo "⚠️  Обнаружены ошибки в логах бота!"
    docker-compose logs bot | tail -20
else
    echo "✅ Логи бота выглядят чисто"
fi

echo "✅ Развертывание завершено!"
echo "📝 Логи бота: docker-compose logs -f bot"
echo "📝 Логи БД: docker-compose logs -f postgres"
echo "🛑 Остановка: docker-compose down"
echo "🔄 Перезапуск: docker-compose restart" 