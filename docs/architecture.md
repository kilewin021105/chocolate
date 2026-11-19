# Architecture

```text
+------------------------------+
| USER                         |
| Cashier / Inventory / Admin  |
+--------------+---------------+
               |
               | HTTP / JSON
               v
+------------------------------+
| FRONTEND                     |
| HTML + CSS + JavaScript      |
+--------------+---------------+
               |
               | REST API
               v
+------------------------------+
| FLASK BACKEND                |
| app.py                       |
| routes/                      |
| services/                    |
+--------------+---------------+
               |
               | Supabase client
               v
+------------------------------+
| SUPABASE POSTGRESQL          |
| users                        |
| products                     |
| customers                    |
| suppliers                    |
| sales                        |
| sale_items                   |
+------------------------------+
```

## Core integrated business process

```text
Customer order
      ↓
Cashier POS
      ↓
POST /api/sales
      ↓
Flask validation/business logic
      ↓
Supabase transaction records
      ↓
Inventory stock deduction
      ↓
Receipt + reports updated
```
