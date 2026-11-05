-- Практическая работа 3. Практика SQL
-- Тема: Производство кофе
-- СУБД: MySQL 8.0

SET NAMES utf8mb4;

CREATE DATABASE coffee CHARACTER SET utf8mb4;

USE coffee;

-- 1. Таблица delivery_to (Поставка кофе)
CREATE TABLE delivery_to (
    id INT AUTO_INCREMENT,
    name VARCHAR(45) NOT NULL,
    quantity_kg INT NOT NULL,
    time DATETIME NOT NULL,
    from_location VARCHAR(45) NOT NULL,
    PRIMARY KEY (id)
);

-- 2. Таблица product (Продукт)
CREATE TABLE product (
    id INT AUTO_INCREMENT,
    delivery_to_id INT NOT NULL,
    name VARCHAR(45) NOT NULL,
    info VARCHAR(45) NOT NULL,
    size INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (delivery_to_id) REFERENCES delivery_to (id)
);

-- 3. Таблица brak (Брак)
CREATE TABLE brak (
    id INT AUTO_INCREMENT,
    info VARCHAR(45),
    size INT,
    product_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (product_id) REFERENCES product (id)
);

-- 4. Таблица cooking (Готовка зерен)
CREATE TABLE cooking (
    idcooking INT AUTO_INCREMENT,
    product_id INT NOT NULL,
    quantity_kg INT,
    PRIMARY KEY (idcooking),
    FOREIGN KEY (product_id) REFERENCES product (id)
);

-- 5. Таблица Pasport (Паспорт партии)
CREATE TABLE Pasport (
    id INT AUTO_INCREMENT,
    info VARCHAR(45) NOT NULL,
    cooking_idcooking INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (cooking_idcooking) REFERENCES cooking (idcooking)
);

-- 6. Таблица package (Сортировка по пакетам)
CREATE TABLE package (
    id INT AUTO_INCREMENT,
    cooking_idcooking INT NOT NULL,
    quantity INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (cooking_idcooking) REFERENCES cooking (idcooking)
);

-- 7. Таблица ready_product (Готовый продукт)
CREATE TABLE ready_product (
    id INT AUTO_INCREMENT,
    ready_status VARCHAR(10) NOT NULL,
    quantity INT NOT NULL,
    package_id INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (package_id) REFERENCES package (id)
);

-- 8. Таблица order (Заказ). order - служебное слово, поэтому в кавычках
CREATE TABLE `order` (
    id INT AUTO_INCREMENT,
    time DATETIME NOT NULL,
    info VARCHAR(45) NOT NULL,
    PRIMARY KEY (id)
);

-- 9. Таблица delivery (Доставка в магазины)
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

-- 10. Таблица logi (Логи доставки)
CREATE TABLE logi (
    id INT AUTO_INCREMENT,
    delivery_id INT NOT NULL,
    time DATETIME,
    info VARCHAR(45),
    PRIMARY KEY (id),
    FOREIGN KEY (delivery_id) REFERENCES delivery (id)
);

-- Внесение данных
INSERT INTO delivery_to (name, quantity_kg, time, from_location) VALUES
    ('ООО Кофе Импорт', 500, '2026-10-05 08:30:00', 'Бразилия'),
    ('ООО Зерно Трейд', 300, '2026-10-05 10:15:00', 'Колумбия'),
    ('ООО Южный порт', 150, '2026-10-06 09:00:00', 'Эфиопия'),
    ('ООО Восток Импорт', 80, '2026-10-06 11:40:00', 'Вьетнам'),
    ('ООО Кофейный двор', 20, '2026-10-07 13:05:00', 'Индия');

INSERT INTO product (delivery_to_id, name, info, size) VALUES
    (1, 'Арабика Сантос', 'сухая обработка', 300),
    (1, 'Робуста Конилон', 'сухая обработка', 200),
    (2, 'Арабика Супремо', 'мытая обработка', 300),
    (3, 'Арабика Сидамо', 'мытая обработка', 150),
    (4, 'Робуста Вьетнам', 'сухая обработка', 80),
    (5, 'Робуста Черри', 'сухая обработка', 20);

INSERT INTO brak (info, size, product_id) VALUES
    ('порван мешок, зерно отсырело', 15, 1),
    ('плесень на зернах', 10, 3),
    ('много битых зерен', 6, 4),
    ('посторонний запах', 4, 5),
    (NULL, 2, 6);

INSERT INTO cooking (product_id, quantity_kg) VALUES
    (1, 120),
    (3, 100),
    (4, 90),
    (1, 50),
    (2, 40);

INSERT INTO Pasport (info, cooking_idcooking) VALUES
    ('Арабика Сантос, партия 1, по ГОСТ', 1),
    ('Арабика Супремо, партия 2, по ГОСТ', 2),
    ('Арабика Сидамо, партия 3, по ГОСТ', 3),
    ('Арабика Сантос, партия 4, по ГОСТ', 4),
    ('Робуста Конилон, партия 5, по ГОСТ', 5);

INSERT INTO package (cooking_idcooking, quantity) VALUES
    (1, 400),
    (2, 330),
    (3, 300),
    (4, 165),
    (5, 130);

INSERT INTO ready_product (ready_status, quantity, package_id) VALUES
    ('готов', 400, 1),
    ('готов', 330, 2),
    ('готов', 300, 3),
    ('готов', 165, 4),
    ('не готов', 130, 5);

INSERT INTO `order` (time, info) VALUES
    ('2026-10-12 09:00:00', 'Абрамова Виктория Владимировна, 150 пакетов'),
    ('2026-10-12 11:30:00', 'Астарханов Алим Гаджимурадович, 200 пакетов'),
    ('2026-10-13 10:00:00', 'Будаев Ярослав Андреевич, 80 пакетов'),
    ('2026-10-13 15:20:00', 'Бызин Григорий Максимович, 120 пакетов'),
    ('2026-10-14 08:45:00', 'Васильев Иван Ильич, 100 пакетов'),
    ('2026-10-14 12:10:00', 'Гейн Андрей Владимирович, 40 пакетов'),
    ('2026-10-15 09:30:00', 'Григорьев Антон Евгеньевич, 30 пакетов'),
    ('2026-10-15 14:00:00', 'Гусейнов Артём Яшарович, 25 пакетов'),
    ('2026-10-16 10:15:00', 'Дедков Никита Дмитриевич, 50 пакетов'),
    ('2026-10-16 16:40:00', 'Демидов Константин Андреевич, 20 пакетов'),
    ('2026-10-17 09:05:00', 'Жилина Карина Самуровна, 35 пакетов'),
    ('2026-10-17 13:25:00', 'Иванов Никита Александрович, 45 пакетов'),
    ('2026-10-19 08:50:00', 'Ивашова Мария Дмитриевна, 30 пакетов'),
    ('2026-10-19 11:20:00', 'Изотов Сергей Максимович, 25 пакетов'),
    ('2026-10-19 15:45:00', 'Иргит Александр Николаевич, 40 пакетов'),
    ('2026-10-20 09:40:00', 'Логачёв Егор Андреевич, 20 пакетов'),
    ('2026-10-20 12:55:00', 'Насуров Ильяс Арсенович, 30 пакетов'),
    ('2026-10-21 10:30:00', 'Новиков Константин Сергеевич, 50 пакетов'),
    ('2026-10-21 14:15:00', 'Оськин Владислав Андреевич, 25 пакетов'),
    ('2026-10-22 09:10:00', 'Рахмедов Дамир Рустемович, 35 пакетов'),
    ('2026-10-22 13:35:00', 'Романенко Алина Олеговна, 40 пакетов');

INSERT INTO delivery (order_id, time, location, ready_product_id) VALUES
    (1, '2026-10-13 07:30:00', 'Москва, ул. Ленина, 10', 1),
    (2, '2026-10-13 08:10:00', 'Москва, ул. Мира, 25', 2),
    (3, '2026-10-14 09:00:00', 'Химки, ул. Садовая, 3', 3),
    (4, '2026-10-14 12:40:00', 'Люберцы, ул. Парковая, 7', 4),
    (5, '2026-10-15 07:15:00', 'Москва, ул. Лесная, 14', 1);

INSERT INTO logi (delivery_id, time, info) VALUES
    (1, '2026-10-13 07:35:00', 'выезд: Шершнев Алексей Русланович'),
    (1, '2026-10-13 09:10:00', 'доставлено: Шершнев Алексей Русланович'),
    (2, '2026-10-13 10:05:00', 'доставлено: Шпакович Николай Янович'),
    (3, '2026-10-14 10:20:00', 'доставлено: Яременко Иван Анатольевич'),
    (4, NULL, 'в пути: Семагина Алина Александровна'),
    (5, '2026-10-15 07:20:00', 'выезд: Шершнев Алексей Русланович');
