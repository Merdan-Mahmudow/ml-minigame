-- Создание базы данных
CREATE DATABASE IF NOT EXISTS forecast_ts;

USE forecast_ts;

-- Таблица рыночных данных (временные ряды)
CREATE TABLE IF NOT EXISTS market_data (
    asset_id String,
    timestamp DateTime64(3),
    open Float64,
    high Float64,
    low Float64,
    close Float64,
    volume Float64,
    source String,
    raw_data String, -- JSON сырых данных
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (asset_id, timestamp)
TTL timestamp + INTERVAL 2 YEAR;

-- Таблица новостей
CREATE TABLE IF NOT EXISTS news_feed (
    id String,
    asset_id String,
    timestamp DateTime64(3),
    source String,
    title String,
    text String,
    url String,
    sentiment Float64, -- -1 до 1
    importance Float64, -- 0 до 1
    raw_data String, -- JSON сырых данных
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (asset_id, timestamp)
TTL timestamp + INTERVAL 1 YEAR;

-- Таблица фичей (для batch-режима)
CREATE TABLE IF NOT EXISTS features (
    asset_id String,
    timestamp DateTime64(3),
    feature_name String,
    feature_value Float64,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (asset_id, timestamp, feature_name)
TTL timestamp + INTERVAL 1 YEAR;

-- Индексы для производительности
ALTER TABLE market_data ADD INDEX idx_asset_time asset_id TYPE minmax GRANULARITY 3;
ALTER TABLE news_feed ADD INDEX idx_asset_time asset_id TYPE minmax GRANULARITY 3;

