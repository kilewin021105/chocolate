from flask import Blueprint, request, jsonify

from backend.services.store import (
    list_items,
    insert_item,
    update_item,
    delete_item
)


suppliers_bp = Blueprint("suppliers", __name__)


# ============================================================
# GET ALL SUPPLIERS
# ============================================================

@suppliers_bp.get("")
def get_suppliers():
    try:
        suppliers = list_items("suppliers")
        return jsonify(suppliers), 200

    except Exception as e:
        print("GET SUPPLIERS ERROR:", e)
        return jsonify({"error": str(e)}), 500


# ============================================================
# ADD SUPPLIER
# ============================================================

@suppliers_bp.post("")
def add_supplier():
    data = request.get_json(silent=True) or {}

    required = [
        "supplier_code",
        "supplier_name"
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
        supplier = insert_item(
            "suppliers",
            data
        )

        return jsonify(supplier), 201

    except Exception as e:
        print("ADD SUPPLIER ERROR:", e)
        return jsonify({"error": str(e)}), 500


# ============================================================
# UPDATE SUPPLIER
# ============================================================

@suppliers_bp.put("/<int:item_id>")
def edit_supplier(item_id):
    data = request.get_json(silent=True) or {}

    try:
        supplier = update_item(
            "suppliers",
            item_id,
            data
        )

        if not supplier:
            return jsonify({
                "error": "Supplier not found."
            }), 404

        return jsonify(supplier), 200

    except Exception as e:
        print("UPDATE SUPPLIER ERROR:", e)
        return jsonify({"error": str(e)}), 500


# ============================================================
# DELETE SUPPLIER
# ============================================================

@suppliers_bp.delete("/<int:item_id>")
def remove_supplier(item_id):
    try:
        deleted = delete_item(
            "suppliers",
            item_id
        )

        if not deleted:
            return jsonify({
                "error": "Supplier not found."
            }), 404

        return jsonify({
            "success": True
        }), 200

    except Exception as e:
        print("DELETE SUPPLIER ERROR:", e)
        return jsonify({"error": str(e)}), 500