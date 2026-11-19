from flask import Blueprint, request, jsonify
from datetime import datetime

from backend.services.store import (
    create_sale,
    list_items
)


sales_bp = Blueprint(
    "sales",
    __name__
)


# =========================================================
# HELPER: CONVERT BIGINT ID
# =========================================================

def _bigint_or_none(value):
    """
    Convert a numeric value to an integer for BIGINT fields.

    Numeric values:
        1       -> 1
        "1"     -> 1

    UUID/non-numeric values:
        UUID    -> None
        "abc"   -> None
    """

    if value in (None, ""):
        return None

    try:
        return int(value)

    except (TypeError, ValueError):
        return None


# =========================================================
# GENERATE INVOICE NUMBER
# =========================================================

def _invoice():
    """
    Generate a unique invoice number.

    Example:
        DAL-123456
    """

    return (
        "DAL-"
        + datetime.now().strftime(
            "%Y%m%d-%H%M%S-%f"
        )[-6:]
    )


# =========================================================
# GET ALL SALES / CUSTOMER ORDERS
# =========================================================

@sales_bp.get("")
def get_sales():

    try:

        sales = list_items(
            "sales"
        )

        return jsonify(
            sales
        ), 200

    except Exception as e:

        print(
            "========================================"
        )
        print(
            "GET SALES ERROR:",
            repr(e)
        )
        print(
            "========================================"
        )

        return jsonify({

            "error":
                "Unable to load sales.",

            "details":
                str(e)

        }), 500


# =========================================================
# CREATE SALE / CUSTOMER ORDER
# =========================================================

@sales_bp.post("")
def add_sale():

    # =====================================================
    # READ JSON
    # =====================================================

    data = request.get_json(
        silent=True
    ) or {}

    print(
        "========================================"
    )
    print(
        "CREATE SALE REQUEST"
    )
    print(
        "========================================"
    )

    print(
        "Incoming data:",
        data
    )

    # =====================================================
    # ITEMS
    # =====================================================

    items = data.get(
        "items",
        []
    )

    if (
        not isinstance(items, list)
        or not items
    ):

        return jsonify({

            "error":
                "At least one sale item is required."

        }), 400

    try:

        clean_items = []

        # =================================================
        # CLEAN SALE ITEMS
        # =================================================

        for item in items:

            if not isinstance(
                item,
                dict
            ):

                return jsonify({

                    "error":
                        "Each sale item must be an object."

                }), 400

            # ---------------------------------------------
            # PRODUCT ID
            # ---------------------------------------------

            if "product_id" not in item:

                return jsonify({

                    "error":
                        "Missing required field: product_id"

                }), 400

            # ---------------------------------------------
            # QUANTITY
            # ---------------------------------------------

            if "quantity" not in item:

                return jsonify({

                    "error":
                        "Missing required field: quantity"

                }), 400

            # ---------------------------------------------
            # PRODUCT ID
            # ---------------------------------------------

            try:

                product_id = int(
                    item["product_id"]
                )

            except (
                TypeError,
                ValueError
            ):

                return jsonify({

                    "error":
                        "Invalid product ID."

                }), 400

            # ---------------------------------------------
            # QUANTITY
            # ---------------------------------------------

            try:

                quantity = int(
                    item["quantity"]
                )

            except (
                TypeError,
                ValueError
            ):

                return jsonify({

                    "error":
                        "Quantity must be a valid number."

                }), 400

            # ---------------------------------------------
            # VALIDATE PRODUCT ID
            # ---------------------------------------------

            if product_id <= 0:

                return jsonify({

                    "error":
                        "Invalid product ID."

                }), 400

            # ---------------------------------------------
            # VALIDATE QUANTITY
            # ---------------------------------------------

            if quantity <= 0:

                return jsonify({

                    "error":
                        "Quantity must be greater than zero."

                }), 400

            # ---------------------------------------------
            # DO NOT TRUST FRONTEND PRICE
            #
            # store.py loads the real price from Supabase.
            # ---------------------------------------------

            clean_items.append({

                "product_id":
                    product_id,

                "quantity":
                    quantity

            })

        # =====================================================
        # DELIVERY
        # =====================================================

        try:

            delivery = float(
                data.get(
                    "delivery_amount",
                    data.get(
                        "delivery",
                        0
                    )
                )
                or 0
            )

            delivery = round(
                delivery,
                2
            )

        except (
            TypeError,
            ValueError
        ):

            return jsonify({

                "error":
                    "Invalid delivery amount."

            }), 400

        if delivery < 0:

            return jsonify({

                "error":
                    "Delivery amount cannot be negative."

            }), 400

        # =====================================================
        # TAX
        # =====================================================

        try:

            tax_rate = float(
                data.get(
                    "tax_rate",
                    0
                )
                or 0
            )

        except (
            TypeError,
            ValueError
        ):

            return jsonify({

                "error":
                    "Invalid tax rate."

            }), 400

        if tax_rate < 0:

            return jsonify({

                "error":
                    "Tax rate cannot be negative."

            }), 400

        # =====================================================
        # DISCOUNT
        # =====================================================

        try:

            discount_amount = float(
                data.get(
                    "discount_amount",
                    0
                )
                or 0
            )

            discount_amount = round(
                discount_amount,
                2
            )

        except (
            TypeError,
            ValueError
        ):

            return jsonify({

                "error":
                    "Invalid discount amount."

            }), 400

        if discount_amount < 0:

            return jsonify({

                "error":
                    "Discount amount cannot be negative."

            }), 400

        # =====================================================
        # CUSTOMER INFORMATION
        # =====================================================

        customer_name = str(
            data.get(
                "customer_name",
                ""
            )
            or ""
        ).strip()

        customer_phone = str(
            data.get(
                "customer_phone",
                ""
            )
            or ""
        ).strip()

        customer_email = str(
            data.get(
                "customer_email",
                ""
            )
            or ""
        ).strip()

        delivery_address = str(
            data.get(
                "delivery_address",
                ""
            )
            or ""
        ).strip()

        # =====================================================
        # USERNAME
        # =====================================================
        #
        # This is important for online customers.
        #
        # The browser may have:
        #
        #     user.id = UUID
        #
        # while the local users table may use:
        #
        #     id = BIGINT
        #
        # We therefore pass username to store.py.
        #
        # store.py can use the username to find the
        # corresponding BIGINT users.id.
        # =====================================================

        username = str(
            data.get(
                "username",
                ""
            )
            or ""
        ).strip()

        # =====================================================
        # ORDER TYPE
        # =====================================================

        order_type = str(
            data.get(
                "order_type",
                "Delivery"
            )
            or "Delivery"
        ).strip()

        if not order_type:

            order_type = "Delivery"

        # =====================================================
        # ORDER STATUS
        # =====================================================

        order_status = str(
            data.get(
                "order_status",
                "Pending"
            )
            or "Pending"
        ).strip()

        if not order_status:

            order_status = "Pending"

        # =====================================================
        # SALE STATUS
        # =====================================================

        sale_status = str(
            data.get(
                "sale_status",
                order_status
            )
            or order_status
        ).strip()

        if not sale_status:

            sale_status = "Pending"

        # =====================================================
        # PAYMENT METHOD
        # =====================================================

        payment_method = str(
            data.get(
                "payment_method",
                "Cash"
            )
            or "Cash"
        ).strip()

        if not payment_method:

            payment_method = "Cash"

        # =====================================================
        # USER ID
        # =====================================================
        #
        # If this is numeric:
        #
        #     "5" -> 5
        #
        # If this is a UUID:
        #
        #     "8de5a2d3-..." -> None
        #
        # store.py will then use username to resolve the
        # BIGINT users.id.
        # =====================================================

        raw_user_id = data.get(
            "user_id"
        )

        user_id = _bigint_or_none(
            raw_user_id
        )

        # =====================================================
        # CUSTOMER ID
        # =====================================================
        #
        # Same idea as user_id.
        #
        # If customer_id is a valid BIGINT it is preserved.
        #
        # If it is missing/UUID, store.py can find/create
        # the customer using customer_name/phone/email.
        # =====================================================

        raw_customer_id = data.get(
            "customer_id"
        )

        customer_id = _bigint_or_none(
            raw_customer_id
        )

        # =====================================================
        # INVOICE NUMBER
        # =====================================================

        invoice_number = str(
            data.get(
                "invoice_number"
            )
            or _invoice()
        ).strip()

        if not invoice_number:

            invoice_number = _invoice()

        # =====================================================
        # DEBUG INFORMATION
        # =====================================================

        print(
            "SALE USER INFORMATION:"
        )

        print(
            "Raw user_id:",
            raw_user_id
        )

        print(
            "Converted user_id:",
            user_id
        )

        print(
            "Username:",
            username
        )

        print(
            "Customer ID:",
            customer_id
        )

        print(
            "Customer name:",
            customer_name
        )

        print(
            "Items:",
            clean_items
        )

        # =====================================================
        # CREATE SALE PAYLOAD
        # =====================================================

        payload = {

            # -----------------------------------------------
            # SALE
            # -----------------------------------------------

            "invoice_number":
                invoice_number,

            # -----------------------------------------------
            # USER
            # -----------------------------------------------

            "user_id":
                user_id,

            "username":
                username,

            # -----------------------------------------------
            # CUSTOMER
            # -----------------------------------------------

            "customer_id":
                customer_id,

            "customer_name":
                customer_name,

            "customer_phone":
                customer_phone,

            "customer_email":
                customer_email,

            # -----------------------------------------------
            # DELIVERY
            # -----------------------------------------------

            "delivery_address":
                delivery_address,

            "delivery_amount":
                delivery,

            # -----------------------------------------------
            # ORDER
            # -----------------------------------------------

            "order_type":
                order_type,

            "order_status":
                order_status,

            "sale_status":
                sale_status,

            # -----------------------------------------------
            # PAYMENT
            # -----------------------------------------------

            "payment_method":
                payment_method,

            # -----------------------------------------------
            # FINANCIAL
            # -----------------------------------------------

            "discount_amount":
                discount_amount,

            "tax_rate":
                tax_rate,

            # -----------------------------------------------
            # ITEMS
            # -----------------------------------------------

            "items":
                clean_items
        }

        # =====================================================
        # SAVE SALE TO SUPABASE
        # =====================================================

        print(
            "========================================"
        )

        print(
            "SENDING SALE TO STORE"
        )

        print(
            "========================================"
        )

        sale = create_sale(
            payload
        )

        # =====================================================
        # SUCCESS
        # =====================================================

        print(
            "========================================"
        )

        print(
            "SALE CREATED SUCCESSFULLY"
        )

        print(
            "Sale:",
            sale
        )

        print(
            "========================================"
        )

        return jsonify(
            sale
        ), 201

    # =====================================================
    # INVALID VALUE
    # =====================================================

    except ValueError as e:

        print(
            "========================================"
        )

        print(
            "SALE VALIDATION ERROR:",
            repr(e)
        )

        print(
            "========================================"
        )

        return jsonify({

            "error":
                str(e),

            "details":
                str(e)

        }), 400

    # =====================================================
    # DATABASE / RUNTIME ERROR
    # =====================================================

    except RuntimeError as e:

        print(
            "========================================"
        )

        print(
            "SALE DATABASE ERROR:",
            repr(e)
        )

        print(
            "========================================"
        )

        return jsonify({

            "error":
                "Unable to create sale.",

            "details":
                str(e)

        }), 500

    # =====================================================
    # UNEXPECTED ERROR
    # =====================================================

    except Exception as e:

        print(
            "========================================"
        )

        print(
            "UNEXPECTED SALE ERROR:",
            repr(e)
        )

        print(
            "========================================"
        )

        return jsonify({

            "error":
                "An unexpected error occurred while "
                "creating the sale.",

            "details":
                str(e)

        }), 500