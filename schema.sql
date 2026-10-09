CREATE DATABASE IF NOT EXISTS restaurante_db;
USE restaurante_db;

-- Tabla de Ingredientes (Inventario)
CREATE TABLE IF NOT EXISTS ingredientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    cantidad_disponible DECIMAL(10,2) NOT NULL,
    unidad_medida VARCHAR(20) NOT NULL, -- ej. gramos, piezas, ml
    stock_minimo DECIMAL(10,2) DEFAULT 5.0
);

-- Tabla de Platillos del Menú
CREATE TABLE IF NOT EXISTS platillos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    precio DECIMAL(10,2) NOT NULL
);

-- Tabla de Recetas (Relación Platillo -> Ingredientes)
CREATE TABLE IF NOT EXISTS recetas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    platillo_id INT,
    ingrediente_id INT,
    cantidad_requerida DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (platillo_id) REFERENCES platillos(id),
    FOREIGN KEY (ingrediente_id) REFERENCES ingredientes(id)
);

-- Tabla de Pedidos/Comandas
CREATE TABLE IF NOT EXISTS pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mesero VARCHAR(50) DEFAULT 'Mesero 1',
    estado ENUM('Pendiente', 'En preparación', 'Listo', 'Entregado') DEFAULT 'Pendiente',
    notas TEXT, -- Para especificaciones como "Sin cebolla"
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Detalle del Pedido
CREATE TABLE IF NOT EXISTS detalle_pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT,
    platillo_id INT,
    cantidad INT DEFAULT 1,
    FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
    FOREIGN KEY (platillo_id) REFERENCES platillos(id)
);

-- Datos iniciales de prueba
INSERT INTO ingredientes (nombre, cantidad_disponible, unidad_medida) VALUES 
('Carne de res', 5000, 'gramos'),
('Pan de hamburguesa', 20, 'piezas'),
('Cebolla', 1000, 'gramos');

INSERT INTO platillos (nombre, precio) VALUES 
('Hamburguesa Clásica', 85.00);

-- Una hamburguesa requiere 200g de carne, 1 pan y 30g de cebolla
INSERT INTO recetas (platillo_id, ingrediente_id, cantidad_requerida) VALUES 
(1, 1, 200),
(1, 2, 1),
(1, 3, 30);