#!/bin/bash
# Скрипт для настройки Traefik

set -e

echo "Настройка Traefik для skyrodev.ru..."

# Проверка наличия docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "Ошибка: docker-compose не установлен"
    exit 1
fi

# Создание директории для Let's Encrypt
mkdir -p ./traefik/letsencrypt
chmod 600 ./traefik/letsencrypt

# Проверка DNS записей
echo "Проверка DNS записей..."
for domain in api.skyrodev.ru admin.skyrodev.ru grafana.skyrodev.ru; do
    ip=$(dig +short $domain | tail -n1)
    if [ "$ip" != "95.31.44.165" ]; then
        echo "Предупреждение: $domain не указывает на 95.31.44.165 (текущий IP: $ip)"
    else
        echo "✓ $domain -> $ip"
    fi
done

echo ""
echo "Запуск Traefik и сервисов..."
docker-compose up -d traefik

echo ""
echo "Ожидание получения SSL сертификатов (может занять несколько минут)..."
sleep 10

# Проверка статуса Traefik
if docker ps | grep -q forecast-traefik; then
    echo "✓ Traefik запущен"
    echo ""
    echo "Доступные сервисы:"
    echo "  - API Gateway: https://api.skyrodev.ru"
    echo "  - Admin UI: https://admin.skyrodev.ru"
    echo "  - Grafana: https://grafana.skyrodev.ru"
    echo "  - Traefik Dashboard: https://traefik.skyrodev.ru:8080"
else
    echo "Ошибка: Traefik не запустился"
    docker logs forecast-traefik
    exit 1
fi

echo ""
echo "Настройка завершена!"

