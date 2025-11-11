-- Create a sample database with multiple tables for testing

-- Employees table
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    department TEXT,
    salary REAL,
    hire_date TEXT,
    is_active INTEGER DEFAULT 1
);

-- Products table
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    price REAL NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    description TEXT
);

-- Orders table
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    order_date TEXT NOT NULL,
    total_amount REAL,
    status TEXT DEFAULT 'pending',
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);

-- Order items table
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Insert sample employees
INSERT INTO employees (first_name, last_name, email, department, salary, hire_date, is_active) VALUES
('Alice', 'Johnson', 'alice.johnson@example.com', 'Engineering', 95000.00, '2020-03-15', 1),
('Bob', 'Smith', 'bob.smith@example.com', 'Sales', 75000.00, '2019-07-22', 1),
('Carol', 'Williams', 'carol.williams@example.com', 'Marketing', 68000.00, '2021-01-10', 1),
('David', 'Brown', 'david.brown@example.com', 'Engineering', 102000.00, '2018-11-05', 1),
('Eve', 'Davis', 'eve.davis@example.com', 'HR', 72000.00, '2020-09-18', 1),
('Frank', 'Miller', 'frank.miller@example.com', 'Sales', 78000.00, '2021-06-30', 1),
('Grace', 'Wilson', 'grace.wilson@example.com', 'Engineering', 88000.00, '2022-02-14', 1),
('Henry', 'Moore', 'henry.moore@example.com', 'Marketing', 65000.00, '2019-04-25', 0),
('Iris', 'Taylor', 'iris.taylor@example.com', 'Engineering', 91000.00, '2021-08-12', 1),
('Jack', 'Anderson', 'jack.anderson@example.com', 'Sales', 71000.00, '2022-11-03', 1);

-- Insert sample products
INSERT INTO products (name, category, price, stock_quantity, description) VALUES
('Laptop Pro 15', 'Electronics', 1299.99, 45, 'High-performance laptop with 15-inch display'),
('Wireless Mouse', 'Electronics', 29.99, 150, 'Ergonomic wireless mouse with USB receiver'),
('Office Chair', 'Furniture', 249.99, 30, 'Comfortable ergonomic office chair'),
('Standing Desk', 'Furniture', 599.99, 12, 'Adjustable height standing desk'),
('USB-C Hub', 'Electronics', 49.99, 85, '7-in-1 USB-C hub with multiple ports'),
('Notebook Set', 'Stationery', 15.99, 200, 'Pack of 3 premium notebooks'),
('Mechanical Keyboard', 'Electronics', 149.99, 60, 'RGB mechanical keyboard with cherry switches'),
('Monitor 27"', 'Electronics', 349.99, 25, '27-inch 4K monitor'),
('Desk Lamp', 'Furniture', 39.99, 75, 'LED desk lamp with adjustable brightness'),
('Webcam HD', 'Electronics', 79.99, 40, '1080p HD webcam with built-in microphone');

-- Insert sample orders
INSERT INTO orders (employee_id, order_date, total_amount, status) VALUES
(2, '2024-01-15', 1329.98, 'completed'),
(6, '2024-01-18', 599.99, 'completed'),
(10, '2024-02-03', 2099.97, 'completed'),
(2, '2024-02-14', 249.99, 'completed'),
(6, '2024-02-20', 179.98, 'shipped'),
(10, '2024-03-05', 1299.99, 'shipped'),
(2, '2024-03-12', 429.98, 'processing'),
(6, '2024-03-15', 95.97, 'pending');

-- Insert sample order items
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
-- Order 1
(1, 1, 1, 1299.99),
(1, 2, 1, 29.99),
-- Order 2
(2, 4, 1, 599.99),
-- Order 3
(3, 1, 1, 1299.99),
(3, 7, 1, 149.99),
(3, 3, 1, 249.99),
(3, 8, 1, 349.99),
-- Order 4
(4, 3, 1, 249.99),
-- Order 5
(5, 5, 2, 49.99),
(5, 9, 2, 39.99),
-- Order 6
(6, 1, 1, 1299.99),
-- Order 7
(7, 8, 1, 349.99),
(7, 10, 1, 79.99),
-- Order 8
(8, 6, 6, 15.99);

-- Create a view for convenience
CREATE VIEW employee_orders AS
SELECT
    e.id as employee_id,
    e.first_name || ' ' || e.last_name as employee_name,
    e.department,
    o.id as order_id,
    o.order_date,
    o.total_amount,
    o.status
FROM employees e
LEFT JOIN orders o ON e.id = o.employee_id
WHERE e.department = 'Sales'
ORDER BY o.order_date DESC;

-- Create an index for better query performance
CREATE INDEX idx_orders_employee_id ON orders(employee_id);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
