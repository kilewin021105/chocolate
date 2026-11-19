from flask import Blueprint, request, jsonify

from backend.services.store import (
    list_items,
    get_item,
    insert_item,
    update_item,
    delete_item
)


products_bp = Blueprint("products", __name__)


# ============================================================
# GET ALL PRODUCTS
# ============================================================

@products_bp.get("")
def get_products():
    try:
        products = list_items("products")
        return jsonify(products), 200

    except Exception as e:
        print("GET PRODUCTS ERROR:", e)
        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# GET ONE PRODUCT
# ============================================================

@products_bp.get("/<int:item_id>")
def get_product(item_id):
    try:
        product = get_item(
            "products",
            item_id
        )

        if not product:
            return jsonify({
                "error": "Product not found."
            }), 404

        return jsonify(product), 200

    except Exception as e:
        print("GET PRODUCT ERROR:", e)
        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# ADD PRODUCT
# ============================================================

@products_bp.post("")
def add_product():
    data = request.get_json(silent=True) or {}

    required = [
        "product_code",
        "product_name",
        "category",
        "price",
        "stock_quantity",
        "reorder_level"
    ]

    missing = [
        field
        for field in required
        if data.get(field) in (None, "")
    ]

    if missing:
        return jsonify({
            "error": (
                "Missing fields: "
                + ", ".join(missing)
            )
        }), 400

    try:
        # ----------------------------------------------------
        # Convert numeric fields
        # ----------------------------------------------------

        data["price"] = float(data["price"])
        data["stock_quantity"] = int(data["stock_quantity"])
        data["reorder_level"] = int(data["reorder_level"])

        # ----------------------------------------------------
        # Validate numeric values
        # ----------------------------------------------------

        if data["price"] < 0:
            return jsonify({
                "error": "Price cannot be negative."
            }), 400

        if data["stock_quantity"] < 0:
            return jsonify({
                "error": "Stock quantity cannot be negative."
            }), 400

        if data["reorder_level"] < 0:
            return jsonify({
                "error": "Reorder level cannot be negative."
            }), 400

        # ----------------------------------------------------
        # Insert into Supabase
        # ----------------------------------------------------

        product = insert_item(
            "products",
            data
        )

        return jsonify(product), 201

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400

    except Exception as e:
        print("ADD PRODUCT ERROR:", e)
        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# UPDATE PRODUCT
# ============================================================

@products_bp.put("/<int:item_id>")
def edit_product(item_id):
    data = request.get_json(silent=True) or {}

    try:
        # ----------------------------------------------------
        # Convert numeric fields when supplied
        # ----------------------------------------------------

        if "price" in data:
            data["price"] = float(data["price"])

            if data["price"] < 0:
                return jsonify({
                    "error": "Price cannot be negative."
                }), 400

        if "stock_quantity" in data:
            data["stock_quantity"] = int(
                data["stock_quantity"]
            )

            if data["stock_quantity"] < 0:
                return jsonify({
                    "error": "Stock quantity cannot be negative."
                }), 400

        if "reorder_level" in data:
            data["reorder_level"] = int(
                data["reorder_level"]
            )

            if data["reorder_level"] < 0:
                return jsonify({
                    "error": "Reorder level cannot be negative."
                }), 400

        # ----------------------------------------------------
        # Update Supabase
        # ----------------------------------------------------

        product = update_item(
            "products",
            item_id,
            data
        )

        if not product:
            return jsonify({
                "error": "Product not found."
            }), 404

        return jsonify(product), 200

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400

    except Exception as e:
        print("UPDATE PRODUCT ERROR:", e)
        return jsonify({
            "error": str(e)
        }), 500


# ============================================================
# DELETE PRODUCT
# ============================================================

@products_bp.delete("/<int:item_id>")
def remove_product(item_id):
    try:
        deleted = delete_item(
            "products",
            item_id
        )

        if not deleted:
            return jsonify({
                "error": "Product not found."
            }), 404

        return jsonify({
            "success": True
        }), 200

    except Exception as e:
        print("DELETE PRODUCT ERROR:", e)
        return jsonify({
            "error": str(e)
        }), 500