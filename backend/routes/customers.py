from flask import Blueprint, request, jsonify

from backend.services.store import (
    list_items,
    insert_item,
    update_item,
    delete_item
)


customers_bp = Blueprint("customers", __name__)


# ============================================================
# GET ALL CUSTOMERS
# ============================================================

@customers_bp.get("")
def get_customers():
    try:
        customers = list_items("customers")
        return jsonify(customers), 200

    except Exception as e:
        print("GET CUSTOMERS ERROR:", e)
        return jsonify({"error": str(e)}), 500


# ============================================================
# ADD CUSTOMER
# ============================================================

@customers_bp.post("")
def add_customer():
    data = request.get_json(silent=True) or {}

    required = [
        "customer_code",
        "full_name",
        "customer_type"
    ]

    missing = [
        field
        for field in required
        if data.get(field) in (None, "")
    ]

    if missing:
        return jsonify({
            "error": (
                "Missing required fields: "
                + ", ".join(missing)
            )
        }), 400

    try:
        customer = insert_item(
            "customers",
            data
        )

        return jsonify(customer), 201

    except Exception as e:
        print("ADD CUSTOMER ERROR:", e)
        return jsonify({"error": str(e)}), 500


# ============================================================
# UPDATE CUSTOMER
# ============================================================

@customers_bp.put("/<int:item_id>")
def edit_customer(item_id):
    data = request.get_json(silent=True) or {}

    try:
        customer = update_item(
            "customers",
            item_id,
            data
        )

        if not customer:
            return jsonify({
                "error": "Customer not found."
            }), 404

        return jsonify(customer), 200

    except Exception as e:
        print("UPDATE CUSTOMER ERROR:", e)
        return jsonify({"error": str(e)}), 500


# ============================================================
# DELETE CUSTOMER
# ============================================================

@customers_bp.delete("/<int:item_id>")
def remove_customer(item_id):
    try:
        deleted = delete_item(
            "customers",
            item_id
        )

        if not deleted:
            return jsonify({
                "error": "Customer not found."
            }), 404

        return jsonify({
            "success": True
        }), 200

    except Exception as e:
        print("DELETE CUSTOMER ERROR:", e)
        return jsonify({"error": str(e)}), 500