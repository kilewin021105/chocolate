"""Flask application entrypoint for Dalareich Integrated POS & Inventory."""

from pathlib import Path
import time

from dotenv import load_dotenv

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from backend.config.supabase_client import get_client

from backend.routes.auth import auth_bp
from backend.routes.customers import customers_bp
from backend.routes.dashboard import dashboard_bp
from backend.routes.products import products_bp
from backend.routes.reports import reports_bp
from backend.routes.sales import sales_bp
from backend.routes.suppliers import suppliers_bp


# ---------------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# ---------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------
# CREATE FLASK APPLICATION
# ---------------------------------------------------------

app = Flask(
    __name__,
    static_folder="frontend",
    static_url_path=""
)


# ---------------------------------------------------------
# ENABLE CORS
# ---------------------------------------------------------

CORS(app)


# ---------------------------------------------------------
# API BLUEPRINTS
# ---------------------------------------------------------

app.register_blueprint(
    auth_bp,
    url_prefix="/api/auth"
)

app.register_blueprint(
    dashboard_bp,
    url_prefix="/api/dashboard"
)

app.register_blueprint(
    products_bp,
    url_prefix="/api/products"
)

app.register_blueprint(
    customers_bp,
    url_prefix="/api/customers"
)

app.register_blueprint(
    suppliers_bp,
    url_prefix="/api/suppliers"
)

app.register_blueprint(
    sales_bp,
    url_prefix="/api/sales"
)

app.register_blueprint(
    reports_bp,
    url_prefix="/api/reports"
)


# =========================================================
# ONLINE CUSTOMER ORDERS
# =========================================================

VALID_ORDER_STATUSES = {
    "Pending",
    "Processing",
    "Completed",
    "Cancelled"
}


# =========================================================
# CREATE ONLINE ORDER
# =========================================================

@app.route("/api/orders", methods=["POST"])
def create_order():
    """
    Create a new online customer order.

    Every newly created order starts as Pending.
    """

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "No order data received."
        }), 400

    # -----------------------------------------------------
    # GET ORDER DATA
    # -----------------------------------------------------

    order_id = data.get("id")

    user_id = data.get("user_id")

    customer = data.get("customer")

    phone = data.get("phone")

    address = data.get("address", "")

    payment = data.get("payment", "Cash")

    order_type = data.get(
        "order_type",
        "Delivery"
    )

    items = data.get(
        "items",
        []
    )

    subtotal = data.get(
        "subtotal",
        0
    )

    delivery = data.get(
        "delivery",
        0
    )

    total = data.get(
        "total",
        0
    )

    order_date = data.get(
        "date"
    )


    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not user_id:
        return jsonify({
            "success": False,
            "message": "User ID is required."
        }), 400

    if not customer:
        return jsonify({
            "success": False,
            "message": "Customer name is required."
        }), 400

    if not phone:
        return jsonify({
            "success": False,
            "message": "Customer phone number is required."
        }), 400

    if not items:
        return jsonify({
            "success": False,
            "message": "Order must contain at least one item."
        }), 400


    # -----------------------------------------------------
    # DELIVERY ADDRESS
    #
    # Delivery requires an address.
    # Pickup does not.
    # -----------------------------------------------------

    if (
        str(order_type).lower() == "delivery"
        and not address
    ):
        return jsonify({
            "success": False,
            "message": "Delivery address is required."
        }), 400


    # -----------------------------------------------------
    # SUPABASE CLIENT
    # -----------------------------------------------------

    client = get_client()

    if client is None:
        return jsonify({
            "success": False,
            "message": "Supabase database is not configured."
        }), 503


    # -----------------------------------------------------
    # GENERATE ORDER ID IF NOT PROVIDED
    # -----------------------------------------------------

    if not order_id:

        order_id = (
            "ORD-"
            + str(int(time.time() * 1000))
        )


    # -----------------------------------------------------
    # GENERATE DATE IF NOT PROVIDED
    # -----------------------------------------------------

    if not order_date:

        from datetime import datetime, timezone

        order_date = (
            datetime.now(timezone.utc)
            .isoformat()
        )


    # -----------------------------------------------------
    # CONVERT NUMBERS
    # -----------------------------------------------------

    try:
        subtotal = float(subtotal or 0)
        delivery = float(delivery or 0)
        total = float(total or 0)

    except (TypeError, ValueError):

        return jsonify({
            "success": False,
            "message": "Invalid order amount."
        }), 400


    # -----------------------------------------------------
    # CREATE DATABASE ORDER
    # -----------------------------------------------------

    order = {
        "id": str(order_id),

        "user_id": str(user_id),

        "date": order_date,

        "status": "Pending",

        "customer": str(customer).strip(),

        "phone": str(phone).strip(),

        "address": str(address).strip(),

        "payment": str(payment).strip(),

        "order_type": str(order_type).strip(),

        "items": items,

        "subtotal": subtotal,

        "delivery": delivery,

        "total": total
    }


    # -----------------------------------------------------
    # SAVE TO SUPABASE
    # -----------------------------------------------------

    try:

        response = (
            client
            .table("orders")
            .insert(order)
            .execute()
        )

        saved_order = order

        if response.data:
            saved_order = response.data[0]


        return jsonify({
            "success": True,
            "message": "Order placed successfully.",
            "order": saved_order
        }), 201


    except Exception as error:

        print(
            "CREATE ORDER ERROR:",
            repr(error)
        )

        return jsonify({
            "success": False,
            "message": "Failed to save order.",
            "error": str(error)
        }), 500


# =========================================================
# GET ONLINE ORDERS
#
# CUSTOMER:
# /api/orders?user_id=123
#
# ADMIN:
# /api/orders
#
# STATUS FILTER:
# /api/orders?status=Pending
#
# CUSTOMER + STATUS:
# /api/orders?user_id=123&status=Pending
# =========================================================

@app.route("/api/orders", methods=["GET"])
def get_orders():

    client = get_client()

    if client is None:
        return jsonify({
            "success": False,
            "message": "Supabase database is not configured."
        }), 503


    try:

        user_id = request.args.get(
            "user_id"
        )

        status = request.args.get(
            "status"
        )


        # -------------------------------------------------
        # START QUERY
        # -------------------------------------------------

        query = (
            client
            .table("orders")
            .select("*")
        )


        # -------------------------------------------------
        # CUSTOMER FILTER
        # -------------------------------------------------

        if user_id:

            query = query.eq(
                "user_id",
                str(user_id)
            )


        # -------------------------------------------------
        # STATUS FILTER
        # -------------------------------------------------

        if (
            status
            and status.lower() != "all"
        ):

            normalized_status = (
                status.strip().capitalize()
            )

            if (
                normalized_status
                not in VALID_ORDER_STATUSES
            ):

                return jsonify({
                    "success": False,
                    "message": "Invalid order status."
                }), 400


            query = query.eq(
                "status",
                normalized_status
            )


        # -------------------------------------------------
        # GET ORDERS
        # -------------------------------------------------

        response = (
            query
            .order(
                "date",
                desc=True
            )
            .execute()
        )

        orders = response.data or []


        return jsonify({
            "success": True,
            "orders": orders
        }), 200


    except Exception as error:

        print(
            "GET ORDERS ERROR:",
            repr(error)
        )

        return jsonify({
            "success": False,
            "message": "Failed to load orders.",
            "error": str(error)
        }), 500


# =========================================================
# GET ONE ORDER
# =========================================================

@app.route(
    "/api/orders/<order_id>",
    methods=["GET"]
)
def get_order(order_id):

    client = get_client()

    if client is None:
        return jsonify({
            "success": False,
            "message": "Supabase database is not configured."
        }), 503


    try:

        response = (
            client
            .table("orders")
            .select("*")
            .eq(
                "id",
                order_id
            )
            .limit(1)
            .execute()
        )

        orders = response.data or []


        if not orders:

            return jsonify({
                "success": False,
                "message": "Order not found."
            }), 404


        return jsonify({
            "success": True,
            "order": orders[0]
        }), 200


    except Exception as error:

        print(
            "GET ORDER ERROR:",
            repr(error)
        )

        return jsonify({
            "success": False,
            "message": "Failed to load order.",
            "error": str(error)
        }), 500


# =========================================================
# UPDATE ORDER STATUS
#
# Pending
#    ↓
# Processing
#    ↓
# Completed
#
# Pending
#    ↓
# Cancelled
# =========================================================

@app.route(
    "/api/orders/<order_id>/status",
    methods=["PATCH"]
)
def update_order_status(order_id):

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({
            "success": False,
            "message": "No status data received."
        }), 400


    new_status = str(
        data.get("status") or ""
    ).strip().capitalize()


    # -----------------------------------------------------
    # VALIDATE STATUS
    # -----------------------------------------------------

    if new_status not in VALID_ORDER_STATUSES:

        return jsonify({
            "success": False,
            "message": (
                "Invalid order status. "
                "Allowed statuses are: "
                "Pending, Processing, "
                "Completed, Cancelled."
            )
        }), 400


    client = get_client()

    if client is None:

        return jsonify({
            "success": False,
            "message": "Supabase database is not configured."
        }), 503


    try:

        # -------------------------------------------------
        # GET CURRENT ORDER
        # -------------------------------------------------

        order_response = (
            client
            .table("orders")
            .select("*")
            .eq(
                "id",
                order_id
            )
            .limit(1)
            .execute()
        )

        orders = (
            order_response.data or []
        )


        if not orders:

            return jsonify({
                "success": False,
                "message": "Order not found."
            }), 404


        order = orders[0]


        # -------------------------------------------------
        # CURRENT STATUS
        # -------------------------------------------------

        current_status = str(
            order.get(
                "status",
                "Pending"
            )
        ).strip().capitalize()


        # -------------------------------------------------
        # ALLOWED STATUS TRANSITIONS
        # -------------------------------------------------

        allowed_transitions = {

            "Pending": {
                "Processing",
                "Cancelled"
            },

            "Processing": {
                "Completed"
            },

            "Completed": set(),

            "Cancelled": set()
        }


        allowed_statuses = (
            allowed_transitions.get(
                current_status,
                set()
            )
        )


        # -------------------------------------------------
        # PREVENT INVALID TRANSITION
        # -------------------------------------------------

        if new_status not in allowed_statuses:

            return jsonify({
                "success": False,
                "message": (
                    "Cannot change order status "
                    f"from '{current_status}' "
                    f"to '{new_status}'."
                )
            }), 400


        # -------------------------------------------------
        # UPDATE DATABASE
        # -------------------------------------------------

        update_response = (
            client
            .table("orders")
            .update({
                "status": new_status
            })
            .eq(
                "id",
                order_id
            )
            .execute()
        )


        # -------------------------------------------------
        # GET UPDATED ORDER
        # -------------------------------------------------

        updated_order = None

        if update_response.data:

            updated_order = (
                update_response.data[0]
            )

        else:

            verify_response = (
                client
                .table("orders")
                .select("*")
                .eq(
                    "id",
                    order_id
                )
                .limit(1)
                .execute()
            )

            verified_orders = (
                verify_response.data or []
            )

            if verified_orders:

                updated_order = (
                    verified_orders[0]
                )


        if updated_order is None:

            return jsonify({
                "success": False,
                "message": "Order status was not updated."
            }), 500


        return jsonify({
            "success": True,
            "message": (
                "Order status changed from "
                f"{current_status} to "
                f"{new_status}."
            ),
            "order": updated_order
        }), 200


    except Exception as error:

        print(
            "UPDATE ORDER STATUS ERROR:",
            repr(error)
        )

        return jsonify({
            "success": False,
            "message": "Failed to update order status.",
            "error": str(error)
        }), 500


# =========================================================
# CUSTOMER REPORTS / COMPLAINTS
# =========================================================

@app.route(
    "/api/reports/customer",
    methods=["POST"]
)
def submit_customer_report():

    client = get_client()

    if client is None:

        return jsonify({
            "success": False,
            "message": "Database is not configured."
        }), 503


    data = request.get_json(
        silent=True
    ) or {}


    subject = str(
        data.get(
            "subject",
            ""
        )
    ).strip()


    report_type = str(
        data.get(
            "type",
            ""
        )
    ).strip()


    message = str(
        data.get(
            "message",
            ""
        )
    ).strip()


    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not subject:

        return jsonify({
            "success": False,
            "message": "Subject is required."
        }), 400


    if not report_type:

        return jsonify({
            "success": False,
            "message": "Report type is required."
        }), 400


    if not message:

        return jsonify({
            "success": False,
            "message": "Report message is required."
        }), 400


    # -----------------------------------------------------
    # CREATE CUSTOMER REPORT
    # -----------------------------------------------------

    report = {

        "user_id": data.get(
            "user_id"
        ),

        "customer": data.get(
            "customer",
            ""
        ),

        "email": data.get(
            "email",
            ""
        ),

        "subject": subject,

        "type": report_type,

        "order_id": data.get(
            "order_id"
        ),

        "message": message,

        "status": "Pending"
    }


    # -----------------------------------------------------
    # SAVE CUSTOMER REPORT
    # -----------------------------------------------------

    try:

        response = (
            client
            .table("customer_reports")
            .insert(report)
            .execute()
        )


        saved_report = report


        if response.data:

            saved_report = (
                response.data[0]
            )


        return jsonify({

            "success": True,

            "message":
                "Report submitted successfully.",

            "report":
                saved_report

        }), 201


    except Exception as error:

        print(
            "CUSTOMER REPORT ERROR:",
            repr(error)
        )


        return jsonify({

            "success": False,

            "message":
                "Failed to save customer report.",

            "error":
                str(error)

        }), 500


# =========================================================
# GET CUSTOMER REPORTS
# =========================================================

@app.route(
    "/api/reports/customer",
    methods=["GET"]
)
def get_customer_reports():

    client = get_client()


    if client is None:

        return jsonify({

            "success": False,

            "message":
                "Database is not configured."

        }), 503


    try:

        response = (
            client
            .table("customer_reports")
            .select("*")
            .order(
                "date",
                desc=True
            )
            .execute()
        )


        reports = (
            response.data or []
        )


        return jsonify({

            "success": True,

            "reports":
                reports

        }), 200


    except Exception as error:

        print(
            "GET CUSTOMER REPORTS ERROR:",
            repr(error)
        )


        return jsonify({

            "success": False,

            "message":
                "Failed to load customer reports.",

            "error":
                str(error)

        }), 500


# =========================================================
# FRONTEND
# =========================================================

@app.get("/")
def index():

    """
    Serve the main frontend page.
    """

    return send_from_directory(
        "frontend",
        "index.html"
    )


@app.get("/<path:path>")
def static_files(path):

    """
    Serve frontend files and fall back to index.html.
    """

    file_path = (
        Path("frontend")
        / path
    )


    if file_path.is_file():

        return send_from_directory(
            "frontend",
            path
        )


    return send_from_directory(
        "frontend",
        "index.html"
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/api/health")
def health():

    """
    Check whether Supabase is configured.
    """

    client = get_client()


    if client is None:

        return jsonify({
            "status": "error",
            "database": "not_configured",
            "application":
                "Dalareich Integrated POS & Inventory Management System"
        }), 503


    return jsonify({
        "status": "ok",
        "database": "supabase",
        "application":
            "Dalareich Integrated POS & Inventory Management System"
    }), 200


# =========================================================
# APPLICATION ENTRYPOINT
# =========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )