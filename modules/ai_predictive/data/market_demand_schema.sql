CREATE TABLE market_demand (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    category VARCHAR(64) NOT NULL,
    keyword VARCHAR(128) NOT NULL,
    volume INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);