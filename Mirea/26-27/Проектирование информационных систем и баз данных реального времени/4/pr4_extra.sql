-- Дополнительно: темы из презентации «Презентация_SQL3»
-- JOIN, UNION, GROUP BY, подзапросы, VIEW, FUNCTION, PROCEDURE, TRIGGER
-- Тема: Производство кофе (база coffee), СУБД: MySQL 8.0
-- Работает и на исходной базе из pr3.sql, и после выполнения pr4.sql.

SET NAMES utf8mb4;
USE coffee;

-- =====================================================================
-- 1. JOIN
-- =====================================================================

-- 1.1 INNER JOIN: продукт и поставщик, от которого он пришел
SELECT p.id, p.name, d.name AS supplier, d.from_location
FROM product AS p
JOIN delivery_to AS d ON d.id = p.delivery_to_id;

-- 1.2 JOIN трех таблиц: доставка, заказ и готовый продукт
SELECT dl.id, o.info AS customer, dl.location, rp.ready_status
FROM delivery AS dl
JOIN `order` AS o ON o.id = dl.order_id
JOIN ready_product AS rp ON rp.id = dl.ready_product_id;

-- 1.3 LEFT JOIN: все заказы, у недоставленных столбцы доставки = NULL
SELECT o.id, o.info, dl.location
FROM `order` AS o
LEFT JOIN delivery AS dl ON dl.order_id = o.id;

-- 1.4 Антисоединение: заказы, которые еще не доставлены
SELECT o.id, o.info
FROM `order` AS o
WHERE NOT EXISTS (SELECT 1 FROM delivery AS dl WHERE dl.order_id = o.id);

-- =====================================================================
-- 2. UNION
-- =====================================================================

-- Продукты, которые обжаривали, и продукты с браком (одним списком)
SELECT product_id FROM cooking
UNION
SELECT product_id FROM brak;

-- =====================================================================
-- 3. GROUP BY и HAVING
-- =====================================================================

-- 3.1 Сколько раз и сколько кг обжарено по каждому продукту
SELECT p.name, COUNT(*) AS times, SUM(c.quantity_kg) AS total_kg
FROM cooking AS c
JOIN product AS p ON p.id = c.product_id
GROUP BY p.id, p.name
ORDER BY total_kg DESC;

-- 3.2 Только продукты, которых обжарено больше 100 кг
SELECT p.name, SUM(c.quantity_kg) AS total_kg
FROM cooking AS c
JOIN product AS p ON p.id = c.product_id
GROUP BY p.id, p.name
HAVING SUM(c.quantity_kg) > 100;

-- =====================================================================
-- 4. ПОДЗАПРОСЫ
-- =====================================================================

-- 4.1 Скалярный: партии больше среднего размера
SELECT name, size FROM product
WHERE size > (SELECT AVG(size) FROM product);

-- 4.2 IN: продукты, по которым был брак
SELECT id, name FROM product
WHERE id IN (SELECT product_id FROM brak);

-- 4.3 Подзапрос в FROM: сначала считаем, потом фильтруем
SELECT x.product_id, x.total_kg
FROM (SELECT product_id, SUM(quantity_kg) AS total_kg
      FROM cooking GROUP BY product_id) AS x
WHERE x.total_kg >= 90;

-- =====================================================================
-- 5. VIEW (представление)
-- =====================================================================

CREATE VIEW v_delivery_info AS
SELECT dl.id AS delivery_id, o.info AS customer, dl.time, dl.location
FROM delivery AS dl
JOIN `order` AS o ON o.id = dl.order_id;

SELECT * FROM v_delivery_info WHERE location LIKE 'Москва%';

-- =====================================================================
-- 6. FUNCTION: доля брака по продукту в процентах
-- =====================================================================

DELIMITER //
CREATE FUNCTION brak_percent(p_id INT) RETURNS DECIMAL(5,2)
READS SQL DATA
BEGIN
    DECLARE v_brak INT;
    DECLARE v_size INT;
    SELECT IFNULL(SUM(size), 0) INTO v_brak FROM brak WHERE product_id = p_id;
    SELECT size INTO v_size FROM product WHERE id = p_id;
    RETURN v_brak * 100 / v_size;
END//
DELIMITER ;

SELECT id, name, size, brak_percent(id) AS brak_pct FROM product;

-- =====================================================================
-- 7. PROCEDURE: число заказов за день
-- =====================================================================

DELIMITER //
CREATE PROCEDURE orders_by_day(IN p_day DATE, OUT p_total INT)
BEGIN
    SELECT COUNT(*) INTO p_total FROM `order` WHERE DATE(time) = p_day;
END//
DELIMITER ;

CALL orders_by_day('2026-10-19', @total);
SELECT @total;

-- =====================================================================
-- 8. TRIGGER: если время события не указано, ставится текущее
-- =====================================================================

CREATE TRIGGER logi_set_time
BEFORE INSERT ON logi
FOR EACH ROW
SET NEW.time = IFNULL(NEW.time, NOW());

INSERT INTO logi (delivery_id, info) VALUES (2, 'проверка триггера');
SELECT * FROM logi ORDER BY id DESC LIMIT 1;
