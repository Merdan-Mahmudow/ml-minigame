#!/bin/bash
# Скрипт для генерации пароля для Traefik Dashboard

echo "Введите имя пользователя (по умолчанию: admin):"
read username
username=${username:-admin}

echo "Введите пароль:"
read -s password

hash=$(htpasswd -nb $username $password | sed 's/\$/\$\$/g')

echo ""
echo "Добавьте следующую строку в docker-compose.yml в labels для traefik:"
echo ""
echo "      - \"traefik.http.middlewares.auth.basicauth.users=$hash\""
echo ""

