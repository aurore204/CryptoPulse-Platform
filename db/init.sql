CREATE TABLE IF NOT EXISTS crypto_prices (
    id                          SERIAL PRIMARY KEY,
    name                        TEXT NOT NULL,
    symbol                      TEXT NOT NULL,
    current_price               NUMERIC(20, 2),
    market_cap                  BIGINT,
    total_volume                BIGINT,
    high_24h                    NUMERIC(20, 2),
    low_24h                     NUMERIC(20, 2),
    price_change_percentage_24h NUMERIC(10, 2),
    last_updated                TIMESTAMPTZ,
    UNIQUE (symbol, last_updated)
);
