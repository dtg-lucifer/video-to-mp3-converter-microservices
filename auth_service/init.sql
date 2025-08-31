CREATE USER 'piush'@'localhost' IDENTIFIED BY 'AuthPass123!';

CREATE DATABASE auth_db;

GRANT ALL PRIVILEGES ON auth_db.* TO 'piush'@'localhost';

USE auth_db;

CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);


INSERT INTO users (email, password) VALUES ('piush@gmail.com', 'password');
