from flask import Blueprint, jsonify, request

from datetime import datetime

from backend.services.store import list_items

from backend.config.supabase_client import get_client


reports_bp = Blueprint(
    "reports",
    __name__
)


# =========================================================
# SUMMARY REPORT
# =========================================================

@reports_bp.get("/summary")
def summary():

    try:

        products = list_items("products")

        sales = list_items("sales")


        return jsonify({

            "product_count":
                len(products),

            "inventory_units":
                sum(
                    int(
                        p.get(
                            "stock_quantity"
                        ) or 0
                    )

                    for p in products
                ),

            "sales_count":
                len(sales),

            "sales_total":
                round(
                    sum(
                        float(
                            s.get(
                                "total_amount"
                            ) or 0
                        )

                        for s in sales
                    ),
                    2
                ),

            "low_stock": [

                p

                for p in products

                if int(
                    p.get(
                        "stock_quantity"
                    ) or 0
                )
                <= int(
                    p.get(
                        "reorder_level"
                    ) or 0
                )

            ]

        }), 200


    except (RuntimeError, TypeError, ValueError) as e:

        print(
            "REPORT SUMMARY ERROR:",
            e
        )

        return jsonify({

            "error":
                str(e)

        }), 500


# =========================================================
# DAILY REPORT
# =========================================================

@reports_bp.get("/daily")
def daily():

    try:

        today = (
            datetime
            .now()
            .strftime("%Y-%m-%d")
        )

        sales = list_items("sales")


        rows = [

            s

            for s in sales

            if str(
                s.get(
                    "sale_date"
                ) or ""
            ).startswith(today)

        ]


        return jsonify({

            "date":
                today,

            "transaction_count":
                len(rows),

            "total_sales":
                round(
                    sum(
                        float(
                            s.get(
                                "total_amount"
                            ) or 0
                        )

                        for s in rows
                    ),
                    2
                ),

            "transactions":
                rows

        }), 200


    except (RuntimeError, TypeError, ValueError) as e:

        print(
            "DAILY REPORT ERROR:",
            e
        )

        return jsonify({

            "error":
                str(e)

        }), 500


# =========================================================
# INVENTORY REPORT
# =========================================================

@reports_bp.get("/inventory")
def inventory():

    try:

        products = list_items("products")

        return jsonify({

            "generated_at":
                datetime
                .now()
                .isoformat(
                    timespec="seconds"
                ),

            "items":
                products,

            "low_stock_items": [

                p

                for p in products

                if int(
                    p.get(
                        "stock_quantity"
                    ) or 0
                )
                <= int(
                    p.get(
                        "reorder_level"
                    ) or 0
                )

            ]

        }), 200


    except (RuntimeError, TypeError, ValueError) as e:

        print(
            "INVENTORY REPORT ERROR:",
            e
        )

        return jsonify({

            "error":
                str(e)

        }), 500


# =========================================================
# CUSTOMER REPORT / COMPLAINT
# =========================================================
#
# CUSTOMER:
# POST /api/reports/customer
#
# Saves a report submitted from UserDashboard.
#
# =========================================================

@reports_bp.post("/customer")
def create_customer_report():

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({

            "success":
                False,

            "message":
                "No report data received."

        }), 400


    # -----------------------------------------------------
    # GET REPORT DATA
    # -----------------------------------------------------

    user_id = data.get("user_id")
    customer = data.get("customer", "")
    email = data.get("email", "")
    subject = data.get("subject", "")
    report_type = data.get("type", "")
    order_id = data.get("order_id")
    message = data.get("message", "")


    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not subject:

        return jsonify({

            "success":
                False,

            "message":
                "Report subject is required."

        }), 400


    if not report_type:

        return jsonify({

            "success":
                False,

            "message":
                "Report type is required."

        }), 400


    if not message:

        return jsonify({

            "success":
                False,

            "message":
                "Report message is required."

        }), 400


    # -----------------------------------------------------
    # SUPABASE CLIENT
    # -----------------------------------------------------

    client = get_client()

    if client is None:

        return jsonify({

            "success":
                False,

            "message":
                "Supabase database is not configured."

        }), 503


    # -----------------------------------------------------
    # CREATE REPORT
    # -----------------------------------------------------

    report = {

        "user_id":
            str(user_id)
            if user_id
            else None,

        "customer":
            str(customer).strip(),

        "email":
            str(email).strip(),

        "subject":
            str(subject).strip(),

        "type":
            str(report_type).strip(),

        "order_id":
            str(order_id).strip()
            if order_id
            else None,

        "message":
            str(message).strip(),

        "status":
            "Pending"

    }


    # -----------------------------------------------------
    # SAVE REPORT TO SUPABASE
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
            saved_report = response.data[0]


        return jsonify({

            "success":
                True,

            "message":
                "Report submitted successfully.",

            "report":
                saved_report

        }), 201


    except (RuntimeError, TypeError, ValueError) as error:

        print(
            "CREATE CUSTOMER REPORT ERROR:",
            repr(error)
        )


        return jsonify({

            "success":
                False,

            "message":
                "Failed to save customer report.",

            "error":
                str(error)

        }), 500


# =========================================================
# GET CUSTOMER REPORTS
# =========================================================
#
# ADMIN:
# GET /api/reports/customer
#
# Loads all customer reports for the Admin Reports page.
#
# =========================================================

@reports_bp.get("/customer")
def get_customer_reports():

    client = get_client()

    if client is None:

        return jsonify({

            "success":
                False,

            "message":
                "Supabase database is not configured."

        }), 503


    try:

        response = (
            client
            .table("customer_reports")
            .select("*")
            .order("date", desc=True)
            .execute()
        )

        reports = response.data or []


        return jsonify({

            "success":
                True,

            "reports":
                reports

        }), 200


    except (RuntimeError, TypeError, ValueError) as error:

        print(
            "GET CUSTOMER REPORTS ERROR:",
            repr(error)
        )


        return jsonify({

            "success":
                False,

            "message":
                "Failed to load customer reports.",

            "error":
                str(error)

        }), 500