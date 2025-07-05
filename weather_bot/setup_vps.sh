#!/bin/bash

echo "🚀 Настройка VPS для Weather Bot CI/CD..."

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "📦 Устанавливаем Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker установлен. Перезайдите в систему!"
    exit 1
fi

# Проверяем наличие Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Устанавливаем Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Проверяем наличие Git
if ! command -v git &> /dev/null; then
    echo "📦 Устанавливаем Git..."
    sudo apt-get update
    sudo apt-get install -y git
fi

# Создаем директорию для проекта
PROJECT_DIR="/opt/weather_bot"
echo "📁 Создаем директорию проекта: $PROJECT_DIR"
sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR

# Клонируем репозиторий (если еще не клонирован)
if [ ! -d "$PROJECT_DIR/.git" ]; then
    echo "📥 Клонируем репозиторий..."
    git clone https://github.com/your-username/weather_bot.git $PROJECT_DIR
fi

cd $PROJECT_DIR

# Настраиваем .env файл
if [ ! -f .env ]; then
    echo "⚙️  Настраиваем переменные окружения..."
    cp env.example .env
    echo "📝 Отредактируйте .env файл:"
    echo "nano .env"
    echo ""
    echo "Не забудьте заполнить:"
    echo "- BOT_TOKEN"
    echo "- WEATHER_API_KEY"
    echo "- DB_PASSWORD"
fi

# Делаем deploy.sh исполняемым
chmod +x deploy.sh

# Обновляем путь в workflow файле
if [ -f ".github/workflows/deploy.yml" ]; then
    echo "🔧 Обновляем путь в workflow..."
    sed -i "s|/path/to/your/project|$PROJECT_DIR|g" .github/workflows/deploy.yml
fi

echo ""
echo "✅ Настройка VPS завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Отредактируйте .env файл: nano .env"
echo "2. Настройте GitHub Secrets (см. CI_CD_SETUP.md)"
echo "3. Сделайте первый push в main ветку"
echo ""
echo "🛠️  Полезные команды:"
echo "- Проверить статус: docker-compose ps"
echo "- Посмотреть логи: docker-compose logs -f bot"
echo "- Обновить вручную: ./deploy.sh" 