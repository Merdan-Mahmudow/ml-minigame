-- Создание расширений
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Таблица активов
CREATE TABLE IF NOT EXISTS assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticker VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    asset_type VARCHAR(50) NOT NULL, -- crypto, stock, commodity, hotel, etc.
    source VARCHAR(100), -- источник котировок
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Таблица источников данных
CREATE TABLE IF NOT EXISTS data_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    source_type VARCHAR(50) NOT NULL, -- exchange, api, rss, etc.
    config JSONB, -- конфигурация подключения
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Таблица конфигураций активов
CREATE TABLE IF NOT EXISTS asset_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    forecast_horizons INTEGER[] DEFAULT ARRAY[1, 7, 30], -- дни
    update_frequency VARCHAR(50) DEFAULT 'hourly', -- hourly, daily, etc.
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(asset_id)
);

-- Таблица моделей
CREATE TABLE IF NOT EXISTS models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- lightgbm, catboost, neural_network, etc.
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Таблица версий моделей
CREATE TABLE IF NOT EXISTS model_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID NOT NULL REFERENCES models(id) ON DELETE CASCADE,
    version VARCHAR(50) NOT NULL,
    artifact_path VARCHAR(500), -- путь в S3
    training_config JSONB, -- конфигурация обучения
    status VARCHAR(50) DEFAULT 'archived', -- prod, canary, archived
    trained_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(model_id, version)
);

-- Таблица метрик моделей
CREATE TABLE IF NOT EXISTS model_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_version_id UUID NOT NULL REFERENCES model_versions(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC NOT NULL,
    dataset_type VARCHAR(50), -- train, val, test
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Таблица прогнозов
CREATE TABLE IF NOT EXISTS forecasts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
    model_version_id UUID NOT NULL REFERENCES model_versions(id),
    timestamp_forecasted TIMESTAMP WITH TIME ZONE NOT NULL,
    horizon INTEGER NOT NULL, -- дни
    point_forecast NUMERIC NOT NULL,
    low_bound NUMERIC,
    high_bound NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_asset_forecast (asset_id, timestamp_forecasted)
);

-- Таблица метрик прогнозов
CREATE TABLE IF NOT EXISTS forecast_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    forecast_id UUID NOT NULL REFERENCES forecasts(id) ON DELETE CASCADE,
    actual_value NUMERIC,
    error NUMERIC,
    absolute_error NUMERIC,
    percentage_error NUMERIC,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для производительности
CREATE INDEX IF NOT EXISTS idx_assets_ticker ON assets(ticker);
CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(asset_type);
CREATE INDEX IF NOT EXISTS idx_model_versions_status ON model_versions(status);
CREATE INDEX IF NOT EXISTS idx_forecasts_created ON forecasts(created_at);
CREATE INDEX IF NOT EXISTS idx_forecasts_asset_horizon ON forecasts(asset_id, horizon);

