CREATE DATABASE IF NOT EXISTS python_data_analysis
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE python_data_analysis;

CREATE TABLE IF NOT EXISTS stock_quotes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    latest_price DECIMAL(12, 3) NULL,
    change_percent DECIMAL(10, 3) NULL,
    change_amount DECIMAL(10, 3) NULL,
    volume BIGINT NULL,
    turnover BIGINT NULL,
    amplitude DECIMAL(10, 3) NULL,
    high DECIMAL(12, 3) NULL,
    low DECIMAL(12, 3) NULL,
    open_price DECIMAL(12, 3) NULL,
    previous_close DECIMAL(12, 3) NULL,
    market VARCHAR(50) NULL,
    crawl_time DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_code_crawl_time (code, crawl_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

