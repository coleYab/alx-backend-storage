-- Creating users with unique email and auto incremented id.

CREATE TABLE IF NOT EXISTS users (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    country VARCHAR(3) NOT NULL DEFAULT 'US' CHECK (country='US' OR country='CO' OR country='TN')

);
