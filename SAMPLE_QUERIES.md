# Sample Queries for Testing

The `sample.db` database contains a simple business schema with employees, products, orders, and order items. Here are some useful queries to test the SQLite research tool:

## Basic Queries

### List all tables
```sql
SELECT name FROM sqlite_master WHERE type='table';
```

### Show all employees
```sql
SELECT * FROM employees;
```

### Show all products
```sql
SELECT * FROM products;
```

## Intermediate Queries

### Find employees by department
```sql
SELECT first_name, last_name, salary
FROM employees
WHERE department = 'Engineering'
ORDER BY salary DESC;
```

### Products under $100
```sql
SELECT name, category, price, stock_quantity
FROM products
WHERE price < 100
ORDER BY price;
```

### Calculate average salary by department
```sql
SELECT department,
       COUNT(*) as employee_count,
       AVG(salary) as avg_salary,
       MIN(salary) as min_salary,
       MAX(salary) as max_salary
FROM employees
WHERE is_active = 1
GROUP BY department
ORDER BY avg_salary DESC;
```

## Advanced Queries

### Orders with customer details
```sql
SELECT
    o.id as order_id,
    e.first_name || ' ' || e.last_name as customer_name,
    e.department,
    o.order_date,
    o.total_amount,
    o.status
FROM orders o
JOIN employees e ON o.employee_id = e.id
ORDER BY o.order_date DESC;
```

### Top selling products
```sql
SELECT
    p.name as product_name,
    p.category,
    SUM(oi.quantity) as total_sold,
    SUM(oi.quantity * oi.unit_price) as total_revenue
FROM products p
JOIN order_items oi ON p.id = oi.product_id
GROUP BY p.id, p.name, p.category
ORDER BY total_revenue DESC;
```

### Order details with items
```sql
SELECT
    o.id as order_id,
    e.first_name || ' ' || e.last_name as customer,
    o.order_date,
    o.status,
    p.name as product_name,
    oi.quantity,
    oi.unit_price,
    (oi.quantity * oi.unit_price) as line_total
FROM orders o
JOIN employees e ON o.employee_id = e.id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
ORDER BY o.order_date DESC, o.id, p.name;
```

### Sales performance by employee
```sql
SELECT
    e.first_name || ' ' || e.last_name as salesperson,
    COUNT(DISTINCT o.id) as total_orders,
    SUM(o.total_amount) as total_sales,
    AVG(o.total_amount) as avg_order_value
FROM employees e
JOIN orders o ON e.id = o.employee_id
WHERE e.department = 'Sales'
GROUP BY e.id, e.first_name, e.last_name
ORDER BY total_sales DESC;
```

### Products running low on stock
```sql
SELECT
    name,
    category,
    stock_quantity,
    price
FROM products
WHERE stock_quantity < 50
ORDER BY stock_quantity ASC;
```

## Schema Exploration

### View table structure (employees)
```sql
PRAGMA table_info(employees);
```

### View table structure (orders)
```sql
PRAGMA table_info(orders);
```

### Show all indexes
```sql
SELECT name, tbl_name, sql
FROM sqlite_master
WHERE type = 'index';
```

### Show all views
```sql
SELECT name, sql
FROM sqlite_master
WHERE type = 'view';
```

### Use the employee_orders view
```sql
SELECT * FROM employee_orders;
```

## Aggregation Examples

### Monthly order summary
```sql
SELECT
    strftime('%Y-%m', order_date) as month,
    COUNT(*) as order_count,
    SUM(total_amount) as monthly_revenue
FROM orders
GROUP BY strftime('%Y-%m', order_date)
ORDER BY month;
```

### Product category performance
```sql
SELECT
    p.category,
    COUNT(DISTINCT p.id) as product_count,
    COUNT(DISTINCT oi.order_id) as orders_with_category,
    SUM(oi.quantity) as units_sold,
    SUM(oi.quantity * oi.unit_price) as category_revenue
FROM products p
LEFT JOIN order_items oi ON p.id = oi.product_id
GROUP BY p.category
ORDER BY category_revenue DESC;
```

## Database Statistics

### Overall database stats
```sql
SELECT
    (SELECT COUNT(*) FROM employees) as total_employees,
    (SELECT COUNT(*) FROM products) as total_products,
    (SELECT COUNT(*) FROM orders) as total_orders,
    (SELECT SUM(total_amount) FROM orders) as total_revenue;
```

### Show foreign keys
```sql
PRAGMA foreign_key_list(orders);
```

```sql
PRAGMA foreign_key_list(order_items);
```

## Tips

- You can combine multiple conditions with AND/OR
- Use LIKE for pattern matching: `WHERE name LIKE '%Laptop%'`
- Use LIMIT to restrict results: `SELECT * FROM products LIMIT 5`
- Use OFFSET with LIMIT for pagination: `SELECT * FROM products LIMIT 5 OFFSET 5`
- Always use semicolons to end statements
