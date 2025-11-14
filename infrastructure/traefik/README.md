# Traefik Configuration

Traefik настроен как reverse proxy с автоматическим получением SSL/TLS сертификатов через Let's Encrypt.

## Конфигурация

- **Email для Let's Encrypt**: softprank@gmail.com
- **Домен**: *.skyrodev.ru
- **IP сервера**: 95.31.44.165

## Поддомены

- `api.skyrodev.ru` - API Gateway
- `admin.skyrodev.ru` - Frontend (Next.js)
- `grafana.skyrodev.ru` - Grafana Dashboard
- `prometheus.skyrodev.ru` - Prometheus
- `minio.skyrodev.ru` - MinIO Console
- `traefik.skyrodev.ru` - Traefik Dashboard (с базовой аутентификацией)

## SSL/TLS

Все поддомены автоматически получают SSL сертификаты через Let's Encrypt с использованием TLS Challenge.

## HTTP -> HTTPS редирект

Все HTTP запросы автоматически перенаправляются на HTTPS.

## Traefik Dashboard

Доступен по адресу: https://traefik.skyrodev.ru:8080

**Важно**: Измените пароль для базовой аутентификации в docker-compose.yml!

## Генерация пароля для базовой аутентификации

```bash
htpasswd -nb admin your_password
```

Замените `$$apr1$$8k8k8k8k$$8k8k8k8k8k8k8k8k` на сгенерированный хеш.

