# Dalareich API Documentation

Base URL: `http://127.0.0.1:5000`

## Authentication

### POST `/api/auth/login`

Request:
```json
{"username":"admin","password":"admin123"}
```

Response:
```json
{"message":"Login successful.","user":{"id":1,"full_name":"System Administrator","username":"admin","role":"Administrator"}}
```

## Products CRUD

### GET `/api/products`
Returns all products.

### POST `/api/products`
Example:
```json
{
  "product_code":"DAL-NEW-001",
  "product_name":"Chocolate Sample",
  "category":"Chocolate",
  "price":150,
  "stock_quantity":20,
  "reorder_level":5,
  "unit":"pack"
}
```

### PUT `/api/products/1`
Updates a product.

### DELETE `/api/products/1`
Deletes a product.

## Sales

### POST `/api/sales`
Example:
```json
{
  "user_id":2,
  "customer_id":1,
  "payment_method":"Cash",
  "items":[
    {"product_id":1,"quantity":2,"price":180}
  ]
}
```

The backend calculates subtotal, 12% tax, total, saves the transaction, and deducts inventory.

## Reports

- GET `/api/reports/daily`
- GET `/api/reports/inventory`
- GET `/api/reports/summary`

## Health

- GET `/api/health`
