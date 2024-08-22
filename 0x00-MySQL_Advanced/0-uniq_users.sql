-- Creating users with unique email and auto incremented id.

CREATE TABLE IF NOT EXISTS Users (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
);
