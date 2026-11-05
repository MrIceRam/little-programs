-- Practical work 3. SQL practice
-- Topic: coffee production
-- DBMS: MySQL 8.0

CREATE DATABASE coffee;

USE coffee;

-- 1. delivery_to (coffee supply)
CREATE TABLE delivery_to (
    id INT AUTO_INCREMENT,
    name VARCHAR(45) NOT NULL,
    quantity_kg INT NOT NULL,
    time DATETIME NOT NULL,
    from_location VARCHAR(45) NOT NULL,
    PRIMARY KEY (id)
);

-- 2. product
CREATE TABLE product (
    id INT AUTO_INCREMENT,
    delivery_to_id INT NOT NULL,
    name VARCHAR(45) NOT NULL,
    info VARCHAR(45) NOT NULL,
    size INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (delivery_to_id) REFERENCES delivery_to (id)
);

-- 3. brak (defects)
CREATE TABLE brak (
    id INT AUTO_INCREMENT,
    info VARCHAR(45),
    size INT,
    product_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (product_id) REFERENCES product (id)
);

-- 4. cooking (roasting)
CREATE TABLE cooking (
    idcooking INT AUTO_INCREMENT,
    product_id INT NOT NULL,
    quantity_kg INT,
    PRIMARY KEY (idcooking),
    FOREIGN KEY (product_id) REFERENCES product (id)
);

-- 5. Pasport (batch passport)
CREATE TABLE Pasport (
    id INT AUTO_INCREMENT,
    info VARCHAR(45) NOT NULL,
    cooking_idcooking INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (cooking_idcooking) REFERENCES cooking (idcooking)
);

-- 6. package
CREATE TABLE package (
    id INT AUTO_INCREMENT,
    cooking_idcooking INT NOT NULL,
    quantity INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (cooking_idcooking) REFERENCES cooking (idcooking)
);

-- 7. ready_product
CREATE TABLE ready_product (
    id INT AUTO_INCREMENT,
    ready_status VARCHAR(10) NOT NULL,
    quantity INT NOT NULL,
    package_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (package_id) REFERENCES package (id)
);

-- 8. order. It is a reserved word, so it goes in backticks
CREATE TABLE `order` (
    id INT AUTO_INCREMENT,
    time DATETIME NOT NULL,
    info VARCHAR(45) NOT NULL,
    PRIMARY KEY (id)
);

-- 9. delivery (to shops)
CREATE TABLE delivery (
    id INT AUTO_INCREMENT,
    order_id INT NOT NULL,
    time DATETIME NOT NULL,
    location VARCHAR(45) NOT NULL,
    ready_product_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (order_id) REFERENCES `order` (id),
    FOREIGN KEY (ready_product_id) REFERENCES ready_product (id)
);

-- 10. logi (delivery logs)
CREATE TABLE logi (
    id INT AUTO_INCREMENT,
    delivery_id INT NOT NULL,
    time DATETIME,
    info VARCHAR(45),
    PRIMARY KEY (id),
    FOREIGN KEY (delivery_id) REFERENCES delivery (id)
);

-- Data
INSERT INTO delivery_to (name, quantity_kg, time, from_location) VALUES
    ('Coffee Import LLC', 500, '2026-10-05 08:30:00', 'Brazil'),
    ('Grain Trade LLC', 300, '2026-10-05 10:15:00', 'Colombia'),
    ('South Port LLC', 150, '2026-10-06 09:00:00', 'Ethiopia'),
    ('East Import LLC', 80, '2026-10-06 11:40:00', 'Vietnam'),
    ('Coffee Yard LLC', 20, '2026-10-07 13:05:00', 'India');

INSERT INTO product (delivery_to_id, name, info, size) VALUES
    (1, 'Arabica Santos', 'dry process', 300),
    (1, 'Robusta Conilon', 'dry process', 200),
    (2, 'Arabica Supremo', 'washed process', 300),
    (3, 'Arabica Sidamo', 'washed process', 150),
    (4, 'Robusta Vietnam', 'dry process', 80),
    (5, 'Robusta Cherry', 'dry process', 20);

INSERT INTO brak (info, size, product_id) VALUES
    ('torn bag, damp beans', 15, 1),
    ('mold on beans', 10, 3),
    ('many broken beans', 6, 4),
    ('foreign smell', 4, 5),
    (NULL, 2, 6);

INSERT INTO cooking (product_id, quantity_kg) VALUES
    (1, 120),
    (3, 100),
    (4, 90),
    (1, 50),
    (2, 40);

INSERT INTO Pasport (info, cooking_idcooking) VALUES
    ('Arabica Santos, batch 1, GOST', 1),
    ('Arabica Supremo, batch 2, GOST', 2),
    ('Arabica Sidamo, batch 3, GOST', 3),
    ('Arabica Santos, batch 4, GOST', 4),
    ('Robusta Conilon, batch 5, GOST', 5);

INSERT INTO package (cooking_idcooking, quantity) VALUES
    (1, 400),
    (2, 330),
    (3, 300),
    (4, 165),
    (5, 130);

INSERT INTO ready_product (ready_status, quantity, package_id) VALUES
    ('ready', 400, 1),
    ('ready', 330, 2),
    ('ready', 300, 3),
    ('ready', 165, 4),
    ('not ready', 130, 5);

INSERT INTO `order` (time, info) VALUES
    ('2026-10-12 09:00:00', 'Home Foods store, 150 packs'),
    ('2026-10-12 11:30:00', 'North supermarket, 200 packs'),
    ('2026-10-13 10:00:00', 'Morning coffee shop, 80 packs'),
    ('2026-10-13 15:20:00', 'Birch store, 120 packs'),
    ('2026-10-14 08:45:00', 'North supermarket, 100 packs');

INSERT INTO delivery (order_id, time, location, ready_product_id) VALUES
    (1, '2026-10-13 07:30:00', 'Moscow, Lenina st, 10', 1),
    (2, '2026-10-13 08:10:00', 'Moscow, Mira st, 25', 2),
    (3, '2026-10-14 09:00:00', 'Khimki, Sadovaya st, 3', 3),
    (4, '2026-10-14 12:40:00', 'Lyubertsy, Parkovaya st, 7', 4),
    (5, '2026-10-15 07:15:00', 'Moscow, Mira st, 25', 1);

INSERT INTO logi (delivery_id, time, info) VALUES
    (1, '2026-10-13 07:35:00', 'truck left the warehouse'),
    (1, '2026-10-13 09:10:00', 'delivered, driver Ivanov'),
    (2, '2026-10-13 10:05:00', 'delivered, driver Petrov'),
    (3, '2026-10-14 10:20:00', 'delivered, driver Sidorov'),
    (4, NULL, 'truck on the way, time not recorded'),
    (5, '2026-10-15 07:20:00', 'truck left the warehouse');
