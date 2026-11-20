-- Подготовка к защите практики 4
-- Запросы того же типа, что пишут при преподавателе:
-- JOIN нескольких таблиц, агрегат, условие с функцией даты, подзапрос
-- База coffee, MySQL 8.0

SET NAMES utf8mb4;
USE coffee;

-- Посмотреть таблицы, с которыми работаем
SELECT * FROM `order`;
SELECT * FROM delivery;
SELECT * FROM ready_product;

-- Среднее время от заказа до доставки (в часах),
-- только по готовым продуктам
SELECT AVG(TIMESTAMPDIFF(HOUR, o.time, dl.time)) AS avg_hours
FROM `order` AS o
JOIN delivery AS dl
    ON dl.order_id = o.id
JOIN ready_product AS rp
    ON rp.id = dl.ready_product_id
WHERE rp.ready_status = 'готов';

-- Доставки, которые выехали раньше 9 утра
SELECT *
FROM delivery
WHERE HOUR(time) < 9;

-- Продукты из самой последней поставки и поставщик
SELECT p.name, p.size, d.name AS supplier_name, d.from_location
FROM product AS p
JOIN delivery_to AS d
    ON d.id = p.delivery_to_id
WHERE p.delivery_to_id = (
    SELECT id
    FROM delivery_to
    ORDER BY time DESC, id DESC
    LIMIT 1
);

-- Сколько кг обжарено по каждому продукту и сколько у него брака
SELECT p.name, SUM(c.quantity_kg) AS cooked_kg,
       (SELECT IFNULL(SUM(b.size), 0) FROM brak AS b WHERE b.product_id = p.id) AS brak_kg
FROM product AS p
JOIN cooking AS c
    ON c.product_id = p.id
GROUP BY p.id, p.name;
