CREATE TABLE market_demand (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    category VARCHAR(64) NOT NULL,
    keyword VARCHAR(128) NOT NULL,
    volume INT NOT NULL,
    spend FLOAT,
    sales FLOAT,
    target_acos FLOAT,
    optimized_bid FLOAT,
    activity_score FLOAT,
    engagement FLOAT,
    score FLOAT,
    url VARCHAR(256),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
