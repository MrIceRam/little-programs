-- 1-ый структурный объект: процедура
-- Сколько продуктов пришло в одной поставке
DELIMITER //

CREATE PROCEDURE count_delivery_products(
    IN p_delivery_to_id INT,
    OUT p_total INT
)
BEGIN
    SELECT COUNT(*) INTO p_total
    FROM product
    WHERE delivery_to_id = p_delivery_to_id;
END //

DELIMITER ;

CALL count_delivery_products(1, @total);
SELECT @total;

-- 2-ой структурный объект: функция
-- Категория партии по ее размеру (кг)
CREATE FUNCTION check_product_size(p_size INT)
RETURNS VARCHAR(20)
DETERMINISTIC
RETURN IF(p_size >= 200, 'Крупная', 'Обычная');

SELECT check_product_size(300);
SELECT check_product_size(150);
SELECT name, size, check_product_size(size) AS category FROM product;

-- 3-ий структурный объект: представление
-- Продукт и поставщик, от которого он пришел
CREATE VIEW v_product_suppliers AS
    SELECT p.name, p.size, d.name AS supplier_name, d.from_location
    FROM delivery_to AS d
    JOIN product AS p
        ON p.delivery_to_id = d.id;

SELECT * FROM v_product_suppliers;

-- 4-ый структурный объект: триггер
-- Новый готовый продукт всегда получает статус «не готов»
CREATE TRIGGER trg_ready_status
    BEFORE INSERT ON ready_product
    FOR EACH ROW
    SET NEW.ready_status = 'не готов';

INSERT INTO ready_product (ready_status, quantity, package_id) VALUES ('готов', 100, 5);
SELECT * FROM ready_product;

-- 5-ый структурный объект: представление со статистикой
-- Сколько продуктов и сколько кг пришло от каждого поставщика
CREATE VIEW v_supplier_statistics AS
    SELECT d.name AS supplier_name, COUNT(*) AS total_products, SUM(p.size) AS total_kg
    FROM delivery_to AS d
    JOIN product AS p
        ON p.delivery_to_id = d.id
    GROUP BY d.id, d.name;

SELECT * FROM v_supplier_statistics;
