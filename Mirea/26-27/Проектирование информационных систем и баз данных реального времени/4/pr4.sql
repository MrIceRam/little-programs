-- Практическая работа 4. Практика SQL 2
-- Тема: Производство кофе (база coffee из практической работы 3)
-- СУБД: MySQL 8.0
-- Запросы выполняются по порядку: сначала выборки, потом изменение структуры
-- и данных, в конце удаление. Перед запуском база coffee должна быть создана
-- скриптом pr3.sql.

SET NAMES utf8mb4;
USE coffee;

-- =====================================================================
-- 1. ВЫБОРКА ДАННЫХ (SELECT)
-- =====================================================================

-- 1.1 Все столбцы таблицы
SELECT * FROM product;

-- 1.2 Один столбец
SELECT name FROM product;

-- 1.3 Несколько столбцов через запятую
SELECT name, size FROM product;

-- =====================================================================
-- 2. СОРТИРОВКА (ORDER BY)
-- =====================================================================

-- 2.1 По алфавиту (по возрастанию)
SELECT * FROM product ORDER BY name;

-- 2.2 По убыванию (DESC)
SELECT * FROM product ORDER BY size DESC;

-- 2.3 По нескольким столбцам: сначала по способу обработки,
--     внутри одинаковых - по размеру партии по убыванию
SELECT * FROM product ORDER BY info, size DESC;

-- 2.4 Заказы от самых новых к самым старым
SELECT id, time, info FROM `order` ORDER BY time DESC;

-- =====================================================================
-- 3. УСЛОВИЯ ВЫБОРКИ (WHERE) - по одному запросу на каждый оператор
-- =====================================================================

-- = (равно): партии размером ровно 300 кг
SELECT * FROM product WHERE size = 300;

-- > (больше)
SELECT * FROM product WHERE size > 150;

-- < (меньше)
SELECT * FROM product WHERE size < 150;

-- >= (больше или равно)
SELECT * FROM product WHERE size >= 150;

-- <= (меньше или равно)
SELECT * FROM product WHERE size <= 150;

-- != (не равно)
SELECT * FROM product WHERE size != 300;

-- IS NOT NULL: записи о браке, где причина указана
SELECT * FROM brak WHERE info IS NOT NULL;

-- IS NULL: запись о браке без причины
SELECT * FROM brak WHERE info IS NULL;

-- IS NULL: события доставки, у которых не записано время
SELECT * FROM logi WHERE time IS NULL;

-- BETWEEN (между, границы входят)
SELECT * FROM product WHERE size BETWEEN 80 AND 200;

-- IN (значение входит в список): продукты из поставок 1 и 3
SELECT * FROM product WHERE delivery_to_id IN (1, 3);

-- NOT IN (значение не входит в список)
SELECT * FROM product WHERE delivery_to_id NOT IN (1, 3);

-- LIKE с %: названия, которые начинаются на «Арабика»
SELECT * FROM product WHERE name LIKE 'Арабика%';

-- NOT LIKE: все, кроме арабики
SELECT * FROM product WHERE name NOT LIKE 'Арабика%';

-- LIKE с % с двух сторон: адреса доставки в Москве
SELECT * FROM delivery WHERE location LIKE '%Москва%';

-- LIKE с _: ровно один любой символ (Индия)
SELECT * FROM delivery_to WHERE from_location LIKE '_ндия';

-- =====================================================================
-- 4. ИЗМЕНЕНИЕ СТРУКТУРЫ ТАБЛИЦЫ (ALTER TABLE)
-- =====================================================================

-- 4.1 Добавить столбец в конец таблицы: статус приемки поставки
ALTER TABLE delivery_to ADD COLUMN status VARCHAR(20);
SELECT * FROM delivery_to;

-- 4.2 Добавить два столбца в нужное место (AFTER):
--     цена за кг и категория поставки, сразу после quantity_kg
ALTER TABLE delivery_to
    ADD COLUMN price_kg INT AFTER quantity_kg,
    ADD COLUMN category VARCHAR(20) AFTER price_kg;
SELECT * FROM delivery_to;

-- =====================================================================
-- 5. ИЗМЕНЕНИЕ ДАННЫХ (UPDATE)
-- =====================================================================

-- 5.1 Изменение одной строки
UPDATE delivery_to SET status = 'проверена' WHERE id = 1;
SELECT * FROM delivery_to;

-- 5.2 Заполнение цены для каждой поставки
UPDATE delivery_to SET price_kg = 1200 WHERE id = 1;
UPDATE delivery_to SET price_kg = 1500 WHERE id = 2;
UPDATE delivery_to SET price_kg = 1800 WHERE id = 3;
UPDATE delivery_to SET price_kg = 900  WHERE id = 4;
UPDATE delivery_to SET price_kg = 1100 WHERE id = 5;
SELECT * FROM delivery_to;

-- 5.3 Изменение сразу нескольких строк по условию
UPDATE delivery_to SET category = 'крупная' WHERE quantity_kg > 100;
UPDATE delivery_to SET category = 'мелкая'  WHERE quantity_kg <= 100;
SELECT * FROM delivery_to;

-- 5.4 Изменение всех строк (без WHERE меняется вся таблица)
UPDATE delivery_to SET status = 'принята';
SELECT * FROM delivery_to;

-- =====================================================================
-- 6. ПЕРЕИМЕНОВАНИЕ И СМЕНА ТИПА СТОЛБЦА (CHANGE, MODIFY)
-- =====================================================================

-- 6.1 CHANGE: переименовать category в supply_type
--     (тип указывается, даже если он не меняется)
ALTER TABLE delivery_to CHANGE category supply_type VARCHAR(20);
SELECT * FROM delivery_to;

-- 6.2 MODIFY: поменять только тип, чтобы цена могла быть с копейками
ALTER TABLE delivery_to MODIFY price_kg DECIMAL(8,2);
UPDATE delivery_to SET price_kg = price_kg * 1.05 WHERE from_location = 'Эфиопия';
SELECT * FROM delivery_to;
DESCRIBE delivery_to;

-- =====================================================================
-- 7. УДАЛЕНИЕ ДАННЫХ (DELETE)
-- =====================================================================

-- 7.1 Удаление строк по условию: события по доставке 5
SELECT * FROM logi;
DELETE FROM logi WHERE delivery_id = 5;
SELECT * FROM logi;

-- 7.2 Попытка удалить поставку, на которую ссылается продукт.
--     Сервер выдаст ERROR 1451: внешний ключ не дает удалить строку.
--     (Если запускать скрипт целиком в консоли, используйте --force,
--     иначе выполнение остановится на этой ошибке.)
DELETE FROM delivery_to WHERE id = 5;

-- 7.3 Правильный порядок: сначала зависимые записи, потом сама поставка
--     brak -> product -> delivery_to
DELETE FROM brak WHERE product_id = 6;
DELETE FROM product WHERE id = 6;
DELETE FROM delivery_to WHERE id = 5;
SELECT * FROM delivery_to;
SELECT * FROM product;
SELECT * FROM brak;
