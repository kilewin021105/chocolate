from flask import Blueprint, jsonify

from backend.config.supabase_client import get_client


dashboard_bp = Blueprint(
    "dashboard",
    __name__
)


# =========================================================
# SUPABASE CLIENT
# =========================================================

def get_supabase():
    client = get_client()

    if client is None:
        raise RuntimeError(
            "Supabase connection is not available."
        )

    return client


# =========================================================
# DASHBOARD
# =========================================================

@dashboard_bp.get("")
def get_dashboard():

    try:
        supabase = get_supabase()

        # -------------------------------------------------
        # PRODUCTS
        # -------------------------------------------------

        products_response = (
            supabase
            .table("products")
            .select(
                "id,product_code,product_name,"
                "stock_quantity,reorder_level"
            )
            .execute()
        )

        products = products_response.data or []

        total_products = len(products)

        # -------------------------------------------------
        # CUSTOMERS
        # -------------------------------------------------

        customers_response = (
            supabase
            .table("customers")
            .select("id")
            .execute()
        )

        customers = customers_response.data or []

        total_customers = len(customers)

        # -------------------------------------------------
        # SALES
        # -------------------------------------------------

        sales_response = (
            supabase
            .table("sales")
            .select("id,total_amount")
            .execute()
        )

        sales = sales_response.data or []

        total_sales = sum(
            float(sale.get("total_amount") or 0)
            for sale in sales
        )

        total_sales = round(
            total_sales,
            2
        )

        # -------------------------------------------------
        # LOW STOCK
        # -------------------------------------------------

        low_stock_items = []

        for product in products:

            stock = int(
                product.get("stock_quantity") or 0
            )

            reorder_level = int(
                product.get("reorder_level") or 0
            )

            if stock <= reorder_level:

                low_stock_items.append({
                    "id": product.get("id"),
                    "product_code": product.get(
                        "product_code",
                        ""
                    ),
                    "product_name": product.get(
                        "product_name",
                        ""
                    ),
                    "stock_quantity": stock,
                    "reorder_level": reorder_level
                })

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return jsonify({
            "total_products": total_products,
            "total_customers": total_customers,
            "total_sales": total_sales,
            "low_stock_count": len(
                low_stock_items
            ),
            "low_stock_items": low_stock_items
        }), 200

    except Exception as error:

        print(
            "DASHBOARD ERROR:",
            error
        )

        return jsonify({
            "error":
                "Unable to load dashboard data.",
            "details":
                str(error)
        }), 500