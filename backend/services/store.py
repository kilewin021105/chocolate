from werkzeug.security import check_password_hash


# ============================================================
# SUPABASE TABLE HELPER
# ============================================================

def _supabase_table(table):
    from backend.config.supabase_client import get_client

    client = get_client()

    if not client:
        raise RuntimeError(
            "Supabase client is not configured."
        )

    return client.table(table)


# ============================================================
# BIGINT ID HELPER
# ============================================================

def _bigint_or_none(value):
    """
    Convert a value to an integer for BIGINT database columns.

    Examples:

        1       -> 1
        "1"     -> 1

        UUID    -> None
        "abc"   -> None
        None    -> None
    """

    if value in (None, ""):
        return None

    try:
        return int(value)

    except (TypeError, ValueError):
        return None


# ============================================================
# GENERIC LIST
# ============================================================

def list_items(table):
    try:

        response = (
            _supabase_table(table)
            .select("*")
            .execute()
        )

        return response.data or []

    except Exception as e:

        raise RuntimeError(
            f"Failed to load {table}: {str(e)}"
        ) from e


# ============================================================
# GENERIC GET ONE
# ============================================================

def get_item(table, item_id):
    try:

        response = (
            _supabase_table(table)
            .select("*")
            .eq(
                "id",
                item_id
            )
            .limit(1)
            .execute()
        )

        rows = response.data or []

        return rows[0] if rows else None

    except Exception as e:

        raise RuntimeError(
            f"Failed to load {table} item: {str(e)}"
        ) from e


# ============================================================
# GENERIC INSERT
# ============================================================

def insert_item(table, payload):
    try:

        response = (
            _supabase_table(table)
            .insert(payload)
            .execute()
        )

        rows = response.data or []

        if not rows:

            raise RuntimeError(
                f"Supabase did not return the inserted "
                f"{table} record."
            )

        return rows[0]

    except Exception as e:

        raise RuntimeError(
            f"Failed to insert into {table}: {str(e)}"
        ) from e


# ============================================================
# GENERIC UPDATE
# ============================================================

def update_item(table, item_id, payload):
    try:

        response = (
            _supabase_table(table)
            .update(payload)
            .eq(
                "id",
                item_id
            )
            .execute()
        )

        rows = response.data or []

        return rows[0] if rows else None

    except Exception as e:

        raise RuntimeError(
            f"Failed to update {table}: {str(e)}"
        ) from e


# ============================================================
# GENERIC DELETE
# ============================================================

def delete_item(table, item_id):
    try:

        response = (
            _supabase_table(table)
            .delete()
            .eq(
                "id",
                item_id
            )
            .execute()
        )

        return bool(response.data)

    except Exception as e:

        raise RuntimeError(
            f"Failed to delete {table}: {str(e)}"
        ) from e


# ============================================================
# AUTHENTICATION
# ============================================================

def authenticate(username, password):

    try:

        response = (
            _supabase_table("users")
            .select("*")
            .eq(
                "username",
                username
            )
            .limit(1)
            .execute()
        )

        rows = response.data or []

        if not rows:
            return None

        user = rows[0]

        password_hash = user.get(
            "password_hash"
        )

        if not password_hash:
            return None

        if not check_password_hash(
            password_hash,
            password
        ):
            return None

        return {

            "id":
                user.get("id"),

            "full_name":
                user.get("full_name"),

            "username":
                user.get("username"),

            "role":
                user.get("role")
        }

    except Exception as e:

        print(
            "AUTHENTICATION ERROR:",
            e
        )

        return None


# ============================================================
# FIND USER BY USERNAME
# ============================================================

def _find_user_by_username(username):
    """
    Find the local users record using username.

    This is important because the online frontend may have
    a UUID user ID while sales.user_id is BIGINT.
    """

    username = (
        username or ""
    ).strip()

    if not username:
        return None

    try:

        users = _supabase_table(
            "users"
        )

        response = (
            users
            .select("*")
            .eq(
                "username",
                username
            )
            .limit(1)
            .execute()
        )

        rows = response.data or []

        if rows:

            return rows[0]

        return None

    except Exception as e:

        print(
            "USER LOOKUP ERROR:",
            e
        )

        raise RuntimeError(
            f"Unable to find user '{username}': {str(e)}"
        ) from e


# ============================================================
# RESOLVE USER ID
# ============================================================

def _resolve_user_id(payload):
    """
    Resolve the user ID that should be stored in sales.user_id.

    Priority:

    1. Numeric payload.user_id
    2. payload.username -> users.id
    3. None

    This prevents UUID values from being inserted into a
    BIGINT database column.
    """

    # --------------------------------------------------------
    # TRY DIRECT USER ID
    # --------------------------------------------------------

    user_id = _bigint_or_none(
        payload.get("user_id")
    )

    if user_id is not None:

        print(
            "USER ID RESOLVED DIRECTLY:",
            user_id
        )

        return user_id

    # --------------------------------------------------------
    # TRY USERNAME
    # --------------------------------------------------------

    username = (
        payload.get("username")
        or ""
    ).strip()

    if username:

        user = _find_user_by_username(
            username
        )

        if user:

            resolved_id = _bigint_or_none(
                user.get("id")
            )

            print(
                "USER ID RESOLVED BY USERNAME:",
                username,
                "->",
                resolved_id
            )

            return resolved_id

        print(
            "USER NOT FOUND BY USERNAME:",
            username
        )

    # --------------------------------------------------------
    # NO USER
    # --------------------------------------------------------

    print(
        "NO NUMERIC USER ID COULD BE RESOLVED."
    )

    return None


# ============================================================
# CUSTOMER HELPER
# ============================================================

def _find_or_create_customer(
    name,
    phone="",
    email=""
):
    """
    Find an existing customer by phone or name.

    If no matching customer exists,
    create a new Individual customer.
    """

    name = (
        name or ""
    ).strip()

    phone = (
        phone or ""
    ).strip()

    email = (
        email or ""
    ).strip()

    if not name:
        return None

    customers = _supabase_table(
        "customers"
    )

    # ========================================================
    # FIND BY PHONE
    # ========================================================

    if phone:

        try:

            response = (
                customers
                .select("*")
                .eq(
                    "phone",
                    phone
                )
                .limit(1)
                .execute()
            )

            rows = response.data or []

            if rows:
                return rows[0]

        except Exception as e:

            print(
                "CUSTOMER PHONE LOOKUP ERROR:",
                e
            )

    # ========================================================
    # FIND BY NAME
    # ========================================================

    try:

        response = (
            customers
            .select("*")
            .eq(
                "full_name",
                name
            )
            .limit(1)
            .execute()
        )

        rows = response.data or []

        if rows:
            return rows[0]

    except Exception as e:

        print(
            "CUSTOMER NAME LOOKUP ERROR:",
            e
        )

    # ========================================================
    # GET LAST CUSTOMER CODE
    # ========================================================

    try:

        response = (
            customers
            .select("customer_code")
            .order(
                "id",
                desc=True
            )
            .limit(1)
            .execute()
        )

        rows = response.data or []

    except Exception as e:

        raise RuntimeError(
            f"Unable to determine customer code: {str(e)}"
        ) from e

    next_number = 1

    if rows:

        last_code = rows[0].get(
            "customer_code",
            ""
        )

        try:

            number_part = (
                str(last_code)
                .replace(
                    "CUS-",
                    ""
                )
            )

            next_number = (
                int(number_part)
                + 1
            )

        except (
            ValueError,
            TypeError
        ):

            next_number = 1

    customer_code = (
        f"CUS-{next_number:03d}"
    )

    # ========================================================
    # CREATE CUSTOMER
    # ========================================================

    customer_payload = {

        "customer_code":
            customer_code,

        "full_name":
            name,

        "customer_type":
            "Individual",

        "phone":
            phone or None,

        "email":
            email or None
    }

    try:

        response = (
            customers
            .insert(customer_payload)
            .execute()
        )

    except Exception as e:

        print(
            "CUSTOMER INSERT ERROR:",
            e
        )

        raise RuntimeError(
            f"Customer could not be created: {str(e)}"
        ) from e

    rows = response.data or []

    if not rows:

        raise RuntimeError(
            "Customer could not be created."
        )

    return rows[0]


# ============================================================
# CREATE SALE
# ============================================================

def create_sale(payload):
    """
    Create an online/POS sale.

    Flow:

        1. Validate cart
        2. Resolve user
        3. Find/create customer
        4. Load products
        5. Validate stock
        6. Calculate subtotal
        7. Calculate discount
        8. Calculate tax
        9. Calculate delivery
        10. Calculate total
        11. Create sales record
        12. Create sale_items records
        13. Decrease product stock
        14. Return completed sale

    IMPORTANT:

    sale_items columns used here are:

        sale_id
        product_id
        quantity
        unit_price
        discount_amount
        subtotal

    The column "price" is NEVER inserted into sale_items.
    """

    # ========================================================
    # COPY PAYLOAD
    # ========================================================

    payload = dict(
        payload or {}
    )

    # ========================================================
    # GET ITEMS
    # ========================================================

    items = (
        payload.get("items")
        or []
    )

    if not items:

        raise ValueError(
            "At least one sale item is required."
        )

    if not isinstance(
        items,
        list
    ):

        raise ValueError(
            "Sale items must be a list."
        )

    # ========================================================
    # TABLES
    # ========================================================

    t_sales = _supabase_table(
        "sales"
    )

    t_items = _supabase_table(
        "sale_items"
    )

    t_products = _supabase_table(
        "products"
    )

    # ========================================================
    # RESOLVE USER ID
    # ========================================================

    user_id = _resolve_user_id(
        payload
    )

    # ========================================================
    # CUSTOMER INFORMATION
    # ========================================================

    customer_name = (
        payload.get("customer_name")
        or ""
    ).strip()

    customer_phone = (
        payload.get("customer_phone")
        or ""
    ).strip()

    customer_email = (
        payload.get("customer_email")
        or ""
    ).strip()

    # ========================================================
    # CUSTOMER ID
    # ========================================================

    customer_id = _bigint_or_none(
        payload.get("customer_id")
    )

    # ========================================================
    # FIND / CREATE CUSTOMER
    # ========================================================

    if (
        customer_id is None
        and customer_name
    ):

        customer = _find_or_create_customer(

            customer_name,

            customer_phone,

            customer_email
        )

        if customer:

            customer_id = _bigint_or_none(
                customer.get("id")
            )

            print(
                "CUSTOMER RESOLVED:",
                customer_id
            )

    # ========================================================
    # VALIDATE PRODUCTS
    # ========================================================

    subtotal = 0.0

    validated_items = []

    for item in items:

        if not isinstance(
            item,
            dict
        ):

            raise ValueError(
                "Each sale item must be an object."
            )

        # ----------------------------------------------------
        # PRODUCT ID
        # ----------------------------------------------------

        try:

            product_id = int(
                item.get("product_id")
            )

        except (
            TypeError,
            ValueError
        ):

            raise ValueError(
                "Invalid product ID."
            )

        if product_id <= 0:

            raise ValueError(
                "Invalid product ID."
            )

        # ----------------------------------------------------
        # QUANTITY
        # ----------------------------------------------------

        try:

            quantity = int(
                item.get("quantity")
            )

        except (
            TypeError,
            ValueError
        ):

            raise ValueError(
                "Quantity must be a valid number."
            )

        if quantity <= 0:

            raise ValueError(
                "Quantity must be greater than zero."
            )

        # ----------------------------------------------------
        # GET PRODUCT
        # ----------------------------------------------------

        try:

            response = (
                t_products
                .select("*")
                .eq(
                    "id",
                    product_id
                )
                .limit(1)
                .execute()
            )

        except Exception as e:

            raise RuntimeError(
                f"Unable to load product "
                f"{product_id}: {str(e)}"
            ) from e

        rows = response.data or []

        if not rows:

            raise ValueError(
                f"Product not found: {product_id}"
            )

        product = rows[0]

        # ----------------------------------------------------
        # PRODUCT NAME
        # ----------------------------------------------------

        product_name = (
            product.get(
                "product_name"
            )
            or product.get(
                "name"
            )
            or "Product"
        )

        # ----------------------------------------------------
        # STOCK
        # ----------------------------------------------------

        try:

            stock = int(
                product.get(
                    "stock_quantity",
                    0
                )
                or 0
            )

        except (
            TypeError,
            ValueError
        ):

            stock = 0

        if stock < quantity:

            raise ValueError(
                f"Insufficient stock for "
                f"{product_name}. "
                f"Available: {stock}, "
                f"requested: {quantity}."
            )

        # ----------------------------------------------------
        # REAL PRODUCT PRICE
        # ----------------------------------------------------

        try:

            price = float(
                product.get(
                    "price",
                    0
                )
                or 0
            )

        except (
            TypeError,
            ValueError
        ):

            raise ValueError(
                f"Invalid price for "
                f"{product_name}."
            )

        if price < 0:

            raise ValueError(
                f"Invalid price for "
                f"{product_name}."
            )

        # ----------------------------------------------------
        # ITEM SUBTOTAL
        # ----------------------------------------------------

        item_subtotal = round(
            price * quantity,
            2
        )

        subtotal += item_subtotal

        # ----------------------------------------------------
        # VALIDATED ITEM
        # ----------------------------------------------------

        validated_items.append({

            "product_id":
                product["id"],

            "quantity":
                quantity,

            "unit_price":
                price,

            "discount_amount":
                0,

            "subtotal":
                item_subtotal,

            "product":
                product
        })

    # ========================================================
    # FINAL SUBTOTAL
    # ========================================================

    subtotal = round(
        subtotal,
        2
    )

    # ========================================================
    # DISCOUNT
    # ========================================================

    try:

        discount_amount = float(
            payload.get(
                "discount_amount",
                0
            )
            or 0
        )

    except (
        TypeError,
        ValueError
    ):

        raise ValueError(
            "Invalid discount amount."
        )

    discount_amount = round(
        discount_amount,
        2
    )

    if discount_amount < 0:

        raise ValueError(
            "Discount amount cannot be negative."
        )

    if discount_amount > subtotal:

        discount_amount = subtotal

    # ========================================================
    # TAX RATE
    # ========================================================

    try:

        tax_rate = float(
            payload.get(
                "tax_rate",
                0
            )
            or 0
        )

    except (
        TypeError,
        ValueError
    ):

        raise ValueError(
            "Invalid tax rate."
        )

    if tax_rate < 0:

        raise ValueError(
            "Tax rate cannot be negative."
        )

    # --------------------------------------------------------
    # Support both:
    #
    # 0.12 = 12%
    #
    # and:
    #
    # 12 = 12%
    # --------------------------------------------------------

    if tax_rate > 1:

        tax_rate = (
            tax_rate / 100
        )

    # ========================================================
    # TAXABLE AMOUNT
    # ========================================================

    taxable_amount = round(
        subtotal
        - discount_amount,
        2
    )

    # ========================================================
    # TAX
    # ========================================================

    tax_amount = round(
        taxable_amount
        * tax_rate,
        2
    )

    # ========================================================
    # DELIVERY
    # ========================================================

    try:

        delivery_amount = float(
            payload.get(
                "delivery_amount",
                payload.get(
                    "delivery",
                    0
                )
            )
            or 0
        )

    except (
        TypeError,
        ValueError
    ):

        raise ValueError(
            "Invalid delivery amount."
        )

    delivery_amount = round(
        delivery_amount,
        2
    )

    if delivery_amount < 0:

        raise ValueError(
            "Delivery amount cannot be negative."
        )

    # ========================================================
    # TOTAL
    # ========================================================

    total_amount = round(

        subtotal

        - discount_amount

        + tax_amount

        + delivery_amount,

        2
    )

    # ========================================================
    # INVOICE NUMBER
    # ========================================================

    invoice_number = str(
        payload.get(
            "invoice_number"
        )
        or ""
    ).strip()

    if not invoice_number:

        import uuid

        invoice_number = (
            "INV-"
            + uuid.uuid4().hex[:8].upper()
        )

    # ========================================================
    # SALE STATUS
    # ========================================================

    sale_status = str(
        payload.get(
            "sale_status"
        )
        or payload.get(
            "order_status"
        )
        or "Pending"
    ).strip()

    if not sale_status:

        sale_status = "Pending"

    # ========================================================
    # ORDER TYPE
    # ========================================================

    order_type = str(
        payload.get(
            "order_type"
        )
        or "Delivery"
    ).strip()

    if not order_type:

        order_type = "Delivery"

    # ========================================================
    # ORDER STATUS
    # ========================================================

    order_status = str(
        payload.get(
            "order_status"
        )
        or "Pending"
    ).strip()

    if not order_status:

        order_status = "Pending"

    # ========================================================
    # PAYMENT METHOD
    # ========================================================

    payment_method = str(
        payload.get(
            "payment_method"
        )
        or "Cash"
    ).strip()

    if not payment_method:

        payment_method = "Cash"

    # ========================================================
    # DELIVERY ADDRESS
    # ========================================================

    delivery_address = str(
        payload.get(
            "delivery_address"
        )
        or ""
    ).strip()

    # ========================================================
    # SALE ROW
    # ========================================================
    #
    # IMPORTANT:
    #
    # Only put columns here that belong to sales.
    #
    # Do NOT put:
    #     items
    #     price
    #     unit_price
    #
    # into this record.
    # ========================================================

    sale_row = {

        "invoice_number":
            invoice_number,

        "user_id":
            user_id,

        "customer_id":
            customer_id,

        "subtotal":
            subtotal,

        "discount_amount":
            discount_amount,

        "tax_amount":
            tax_amount,

        "total_amount":
            total_amount,

        "payment_method":
            payment_method,

        "sale_status":
            sale_status,

        "customer_name":
            customer_name or None,

        "customer_phone":
            customer_phone or None,

        "delivery_address":
            delivery_address or None,

        "order_type":
            order_type,

        "order_status":
            order_status,

        "delivery_amount":
            delivery_amount
    }

    # ========================================================
    # REMOVE NONE VALUES
    # ========================================================

    sale_row = {
        key: value
        for key, value in sale_row.items()
        if value is not None
    }

    # ========================================================
    # DEBUG
    # ========================================================

    print(
        "========================================"
    )

    print(
        "FINAL SALE ROW:"
    )

    print(
        sale_row
    )

    print(
        "========================================"
    )

    # ========================================================
    # INSERT SALE
    # ========================================================

    try:

        response = (
            t_sales
            .insert(sale_row)
            .execute()
        )

    except Exception as e:

        print(
            "========================================"
        )

        print(
            "SALE INSERT ERROR:",
            repr(e)
        )

        print(
            "========================================"
        )

        raise RuntimeError(
            f"Failed to create sale: {str(e)}"
        ) from e

    rows = response.data or []

    if not rows:

        raise RuntimeError(
            "Sale could not be created. "
            "Supabase returned no sale record."
        )

    sale = rows[0]

    # ========================================================
    # SALE ID
    # ========================================================

    sale_id = sale.get(
        "id"
    )

    if sale_id is None:

        raise RuntimeError(
            "Sale was created but no sale ID was returned."
        )

    print(
        "SALE CREATED:",
        sale_id
    )

    # ========================================================
    # BUILD SALE ITEMS
    # ========================================================

    sale_items = []

    for item in validated_items:

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # The sale_items table uses:
        #
        #     unit_price
        #
        # NOT:
        #
        #     price
        # ----------------------------------------------------

        sale_item = {

            "sale_id":
                sale_id,

            "product_id":
                item["product_id"],

            "quantity":
                item["quantity"],

            "unit_price":
                item["unit_price"],

            "discount_amount":
                item["discount_amount"],

            "subtotal":
                item["subtotal"]
        }

        sale_items.append(
            sale_item
        )

    # ========================================================
    # INSERT SALE ITEMS
    # ========================================================

    inserted_items = []

    try:

        print(
            "SALE ITEMS TO INSERT:",
            sale_items
        )

        item_response = (
            t_items
            .insert(sale_items)
            .execute()
        )

        inserted_items = (
            item_response.data
            or []
        )

        if not inserted_items:

            raise RuntimeError(
                "Supabase did not return the inserted "
                "sale items."
            )

        print(
            "SALE ITEMS CREATED:",
            inserted_items
        )

    except Exception as e:

        print(
            "========================================"
        )

        print(
            "SALE ITEMS INSERT ERROR:",
            repr(e)
        )

        print(
            "========================================"
        )

        # ----------------------------------------------------
        # DELETE INCOMPLETE SALE
        # ----------------------------------------------------

        try:

            (
                t_sales
                .delete()
                .eq(
                    "id",
                    sale_id
                )
                .execute()
            )

            print(
                "INCOMPLETE SALE DELETED:",
                sale_id
            )

        except Exception as cleanup_error:

            print(
                "SALE CLEANUP ERROR:",
                repr(cleanup_error)
            )

        raise RuntimeError(
            "Sale could not be completed because "
            "sale items could not be created: "
            f"{str(e)}"
        ) from e

    # ========================================================
    # UPDATE PRODUCT STOCK
    # ========================================================

    updated_products = []

    try:

        for item in validated_items:

            product = item["product"]

            quantity = item["quantity"]

            # ------------------------------------------------
            # CURRENT STOCK
            # ------------------------------------------------

            try:

                current_stock = int(
                    product.get(
                        "stock_quantity",
                        0
                    )
                    or 0
                )

            except (
                TypeError,
                ValueError
            ):

                current_stock = 0

            # ------------------------------------------------
            # NEW STOCK
            # ------------------------------------------------

            new_stock = (
                current_stock
                - quantity
            )

            if new_stock < 0:

                raise ValueError(
                    f"Insufficient stock for "
                    f"{product.get('product_name', 'product')}."
                )

            # ------------------------------------------------
            # SAVE FOR ROLLBACK
            # ------------------------------------------------

            updated_products.append({

                "id":
                    product["id"],

                "old_stock":
                    current_stock,

                "new_stock":
                    new_stock
            })

            # ------------------------------------------------
            # UPDATE DATABASE
            # ------------------------------------------------

            response = (
                t_products
                .update({

                    "stock_quantity":
                        new_stock

                })
                .eq(
                    "id",
                    product["id"]
                )
                .execute()
            )

            print(
                "STOCK UPDATED:",
                product["id"],
                current_stock,
                "->",
                new_stock
            )

    except Exception as e:

        print(
            "========================================"
        )

        print(
            "STOCK UPDATE ERROR:",
            repr(e)
        )

        print(
            "========================================"
        )

        # ====================================================
        # RESTORE STOCK
        # ====================================================

        for updated in updated_products:

            try:

                (
                    t_products
                    .update({

                        "stock_quantity":
                            updated["old_stock"]

                    })
                    .eq(
                        "id",
                        updated["id"]
                    )
                    .execute()
                )

                print(
                    "STOCK RESTORED:",
                    updated["id"],
                    updated["old_stock"]
                )

            except Exception as restore_error:

                print(
                    "STOCK RESTORE ERROR:",
                    updated["id"],
                    repr(restore_error)
                )

        # ====================================================
        # DELETE SALE
        # ====================================================

        try:

            (
                t_sales
                .delete()
                .eq(
                    "id",
                    sale_id
                )
                .execute()
            )

            print(
                "SALE DELETED AFTER STOCK FAILURE:",
                sale_id
            )

        except Exception as cleanup_error:

            print(
                "SALE CLEANUP ERROR:",
                repr(cleanup_error)
            )

        raise RuntimeError(
            "Sale could not be completed because "
            "product stock could not be updated: "
            f"{str(e)}"
        ) from e

    # ========================================================
    # ATTACH ITEMS TO RESPONSE
    # ========================================================

    sale["items"] = inserted_items

    # ========================================================
    # RETURN SALE
    # ========================================================

    print(
        "========================================"
    )

    print(
        "SALE COMPLETED SUCCESSFULLY:"
    )

    print(
        sale
    )

    print(
        "========================================"
    )

    return sale