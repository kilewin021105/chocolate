from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from backend.config.supabase_client import get_client

load_dotenv()
client = get_client()
if not client:
    raise SystemExit("Supabase credentials are missing. Update .env first.")

users = [
    {"full_name":"System Administrator","username":"admin","password_hash":generate_password_hash("admin123"),"role":"Administrator"},
    {"full_name":"Dalareich Cashier","username":"cashier","password_hash":generate_password_hash("cashier123"),"role":"Staff"},
    {"full_name":"Inventory Manager","username":"inventory","password_hash":generate_password_hash("inventory123"),"role":"Manager"},
]
customers = [
    {"customer_code":"CUS-001","full_name":"Walk-in Customer","customer_type":"Individual","phone":"","email":""},
    {"customer_code":"CUS-002","full_name":"Bohol Pasalubong Center","customer_type":"Wholesale","phone":"09170000001","email":"orders@example.com"},
    {"customer_code":"CUS-003","full_name":"Island Resort Supply","customer_type":"Institutional","phone":"09170000002","email":"purchasing@example.com"},
]
suppliers = [
    {"supplier_code":"SUP-001","supplier_name":"Bohol Cacao Farmers Cooperative","contact_person":"Supplier Desk","phone":"09180000001","email":"supplier@example.com"},
    {"supplier_code":"SUP-002","supplier_name":"Island Packaging Solutions","contact_person":"Sales Team","phone":"09180000002","email":"packaging@example.com"},
    {"supplier_code":"SUP-003","supplier_name":"Bohol Food Ingredients Trading","contact_person":"Accounts Desk","phone":"09180000003","email":"ingredients@example.com"},
]
products = [
    {"product_code":"DAL-TBL-001","product_name":"Classic Cacao Tablea 200g","category":"Tablea","price":180,"stock_quantity":42,"reorder_level":10,"unit":"pack","batch_number":"TB-2026-01","expiration_date":"2027-01-15"},
    {"product_code":"DAL-TBL-002","product_name":"Premium Cacao Tablea 400g","category":"Tablea","price":340,"stock_quantity":8,"reorder_level":10,"unit":"pack","batch_number":"TB-2026-02","expiration_date":"2027-02-10"},
    {"product_code":"DAL-CHO-001","product_name":"Dark Chocolate 70% 100g","category":"Chocolate","price":220,"stock_quantity":25,"reorder_level":8,"unit":"bar","batch_number":"CH-2026-01","expiration_date":"2027-03-20"},
    {"product_code":"DAL-CHO-002","product_name":"Milk Chocolate 100g","category":"Chocolate","price":210,"stock_quantity":31,"reorder_level":8,"unit":"bar","batch_number":"CH-2026-02","expiration_date":"2027-04-05"},
    {"product_code":"DAL-CHO-003","product_name":"Cacao Nibs 150g","category":"Cacao","price":260,"stock_quantity":6,"reorder_level":10,"unit":"pack","batch_number":"NB-2026-01","expiration_date":"2027-02-28"},
    {"product_code":"DAL-RAW-001","product_name":"Fermented Cacao Beans 1kg","category":"Raw Material","price":450,"stock_quantity":75,"reorder_level":20,"unit":"kg","batch_number":"CB-2026-05","expiration_date":"2027-05-30"},
    {"product_code":"DAL-GFT-001","product_name":"Bohol Chocolate Gift Box","category":"Gift Set","price":650,"stock_quantity":14,"reorder_level":5,"unit":"box","batch_number":"GB-2026-01","expiration_date":"2027-03-15"},
    {"product_code":"DAL-TBL-003","product_name":"Cacao Tablea 100g","category":"Tablea","price":95,"stock_quantity":55,"reorder_level":15,"unit":"pack","batch_number":"TB-2026-03","expiration_date":"2027-06-01"},
    {"product_code":"DAL-CHO-004","product_name":"Coconut Chocolate Bar 80g","category":"Chocolate","price":195,"stock_quantity":19,"reorder_level":7,"unit":"bar","batch_number":"CH-2026-03","expiration_date":"2027-05-12"},
    {"product_code":"DAL-GFT-002","product_name":"Tourist Mini Chocolate Pack","category":"Gift Set","price":300,"stock_quantity":4,"reorder_level":10,"unit":"pack","batch_number":"MP-2026-01","expiration_date":"2027-01-30"},
]

def seed(table, rows, unique_field):
    for row in rows:
        existing = client.table(table).select("id").eq(unique_field, row[unique_field]).limit(1).execute().data
        if not existing:
            client.table(table).insert(row).execute()

seed("users", users, "username")
seed("customers", customers, "customer_code")
seed("suppliers", suppliers, "supplier_code")
seed("products", products, "product_code")
print("Supabase seed completed.")
