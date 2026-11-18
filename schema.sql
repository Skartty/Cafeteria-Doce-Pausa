CREATE DATABASE IF NOT EXISTS doce_pausa
    CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE doce_pausa;

CREATE TABLE IF NOT EXISTS usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    login VARCHAR(50) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    perfil ENUM('admin', 'comum') NOT NULL DEFAULT 'comum',
    criado_em DATE NOT NULL DEFAULT (CURRENT_DATE)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS categoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(60) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS produto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    preco DECIMAL(8, 2) NOT NULL,
    categoria_id INT NOT NULL,
    criado_por INT NOT NULL,
    criado_em DATE NOT NULL DEFAULT (CURRENT_DATE),
    CONSTRAINT ck_produto_preco CHECK (preco >= 0),
    CONSTRAINT fk_produto_categoria FOREIGN KEY (categoria_id)
        REFERENCES categoria (id) ON DELETE RESTRICT,
    CONSTRAINT fk_produto_usuario FOREIGN KEY (criado_por)
        REFERENCES usuario (id) ON DELETE RESTRICT
) ENGINE=InnoDB;
