-- 1. Таблица order (Заказ)
CREATE TABLE "order" (
    id INT PRIMARY KEY,
    time DATETIME not null, 
    info VARCHAR(45)
);

-- 2. Таблица delivery_to (Доставка)
CREATE TABLE delivery_to (
    id INT PRIMARY KEY,
    name VARCHAR(45),
    quantity_kg INT, 
    time DATETIME,
    from_location VARCHAR(45) 
);

-- 3. Таблица product (Продукт)
CREATE TABLE product (
    id INT PRIMARY KEY,
    delivery_to_id INT,
    name VARCHAR(45),
    info VARCHAR(45),
    size INT,
    FOREIGN KEY (delivery_to_id) REFERENCES delivery_to(id)
);

-- 4. Таблица cooking (Готовка)
CREATE TABLE cooking (
    idcooking INT PRIMARY KEY,
    product_id INT,
    quantity_kg INT,
    FOREIGN KEY (product_id) REFERENCES product(id)
);

-- 5. Таблица Pasport (Паспорт)
CREATE TABLE Pasport (
    id INT PRIMARY KEY,
    info VARCHAR(45),
    cooking_idcooking INT,
    FOREIGN KEY (cooking_idcooking) REFERENCES cooking(idcooking)
);

-- 6. Таблица package (Упаковка)
CREATE TABLE package (
    id INT PRIMARY KEY,
    cooking_idcooking INT,
    quantity INT,
    FOREIGN KEY (cooking_idcooking) REFERENCES cooking(idcooking)
);

-- 7. Таблица ready_product (Готовый продукт)
CREATE TABLE ready_product (
    id INT PRIMARY KEY,
    ready_status VARCHAR(10), 
    quantity INT,
    package_id INT,
    FOREIGN KEY (package_id) REFERENCES package(id)
);

-- 8. Таблица brak (Брак)
CREATE TABLE brak (
    id INT PRIMARY KEY,
    info VARCHAR(45),
    size INT,
    product_id INT,
    FOREIGN KEY (product_id) REFERENCES product(id)
);

-- 9. Таблица delivery (Доставка готовая)
CREATE TABLE delivery (
    id INT PRIMARY KEY,
    order_id INT,
    time DATETIME,
    location VARCHAR(45),
    ready_product_id INT,
    FOREIGN KEY (order_id) REFERENCES "order"(id),
    FOREIGN KEY (ready_product_id) REFERENCES ready_product(id)
);

-- 10. Таблица logi (Логистика)
CREATE TABLE logi (
    id INT PRIMARY KEY,
    delivery_id INT,
    time DATETIME,
    info VARCHAR(45),
    FOREIGN KEY (delivery_id) REFERENCES delivery(id)
);