from functools import wraps
from flask import jsonify, request


# =========================================================
# ROLES
# =========================================================

ADMIN_ROLE = "admin"
USER_ROLE = "user"


# =========================================================
# ROLE NORMALIZATION
# =========================================================

def normalize_role(role):
    """
    Convert role values to a standard format.

    Examples:
        Admin -> admin
        ADMIN -> admin
        administrator -> admin
        User -> user
        USER -> user
    """

    if role is None:
        return None

    role = str(role).strip().lower()

    if role in ("admin", "administrator"):
        return ADMIN_ROLE

    if role == "user":
        return USER_ROLE

    return None


# =========================================================
# CURRENT USER
# =========================================================

def get_current_user():
    """
    Get the authenticated user attached to the
    current Flask request.

    auth.py should set:

        request.current_user = user
    """

    return getattr(request, "current_user", None)


# =========================================================
# CURRENT ROLE
# =========================================================

def get_current_role():
    """
    Get the role of the currently authenticated user.

    Supports:
        user["role"]

    and:

        user["raw_user_meta_data"]["role"]
    """

    user = get_current_user()

    if not user:
        return None

    # -----------------------------------------------------
    # Direct role
    # -----------------------------------------------------

    if isinstance(user, dict):

        role = user.get("role")

        if role:
            return normalize_role(role)

        # -------------------------------------------------
        # Supabase raw_user_meta_data
        # -------------------------------------------------

        metadata = user.get(
            "raw_user_meta_data",
            {}
        )

        if isinstance(metadata, dict):

            role = metadata.get("role")

            if role:
                return normalize_role(role)

    return None


# =========================================================
# AUTHENTICATION CHECK
# =========================================================

def is_authenticated():
    """
    Check whether a user is currently authenticated.
    """

    return get_current_user() is not None


# =========================================================
# ADMIN CHECK
# =========================================================

def is_admin():
    """
    Return True if the current user is an Admin.
    """

    return get_current_role() == ADMIN_ROLE


# =========================================================
# USER CHECK
# =========================================================

def is_user():
    """
    Return True if the current user is a normal User.
    """

    return get_current_role() == USER_ROLE


# =========================================================
# ROLE CHECK
# =========================================================

def has_role(required_role):
    """
    Check whether the current user has a specific role.
    """

    current_role = get_current_role()

    required_role = normalize_role(
        required_role
    )

    if current_role is None:
        return False

    return current_role == required_role


# =========================================================
# REQUIRE LOGIN
# =========================================================

def require_auth(f):
    """
    Protect a route so only authenticated users
    can access it.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):

        user = get_current_user()

        if not user:

            return jsonify({
                "success": False,
                "error": "Authentication required."
            }), 401

        return f(*args, **kwargs)

    return decorated_function


# =========================================================
# REQUIRE ADMIN
# =========================================================

def require_admin(f):
    """
    Protect a route so only Admin users can access it.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):

        user = get_current_user()

        # -------------------------------------------------
        # Not logged in
        # -------------------------------------------------

        if not user:

            return jsonify({
                "success": False,
                "error": "Authentication required."
            }), 401

        # -------------------------------------------------
        # Check role
        # -------------------------------------------------

        current_role = get_current_role()

        if current_role != ADMIN_ROLE:

            return jsonify({
                "success": False,
                "error": "Access denied.",
                "message": (
                    "Admin access required."
                ),
                "role": current_role
            }), 403

        return f(*args, **kwargs)

    return decorated_function


# =========================================================
# REQUIRE USER
# =========================================================

def require_user(f):
    """
    Protect a route so only normal User accounts
    can access it.

    Admin accounts are NOT treated as User accounts here.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):

        user = get_current_user()

        # -------------------------------------------------
        # Not logged in
        # -------------------------------------------------

        if not user:

            return jsonify({
                "success": False,
                "error": "Authentication required."
            }), 401

        # -------------------------------------------------
        # Check role
        # -------------------------------------------------

        current_role = get_current_role()

        if current_role != USER_ROLE:

            return jsonify({
                "success": False,
                "error": "Access denied.",
                "message": (
                    "User role required."
                ),
                "role": current_role
            }), 403

        return f(*args, **kwargs)

    return decorated_function


# =========================================================
# REQUIRE ADMIN OR USER
# =========================================================

def require_admin_or_user(f):
    """
    Allow both Admin and User accounts.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):

        user = get_current_user()

        # -------------------------------------------------
        # Not logged in
        # -------------------------------------------------

        if not user:

            return jsonify({
                "success": False,
                "error": "Authentication required."
            }), 401

        # -------------------------------------------------
        # Check role
        # -------------------------------------------------

        current_role = get_current_role()

        if current_role not in (
            ADMIN_ROLE,
            USER_ROLE
        ):

            return jsonify({
                "success": False,
                "error": "Access denied.",
                "message": (
                    "Your account does not have "
                    "a valid authorized role."
                ),
                "role": current_role
            }), 403

        return f(*args, **kwargs)

    return decorated_function


# =========================================================
# REQUIRE ROLES
# =========================================================

def require_roles(*allowed_roles):
    """
    Allow access to multiple specified roles.

    Example:

        @require_roles("admin", "user")
        def example():
            ...

    """

    normalized_roles = set()

    for role in allowed_roles:

        normalized_role = normalize_role(role)

        if normalized_role:

            normalized_roles.add(
                normalized_role
            )

    def decorator(f):

        @wraps(f)
        def decorated_function(*args, **kwargs):

            user = get_current_user()

            # ---------------------------------------------
            # Not logged in
            # ---------------------------------------------

            if not user:

                return jsonify({
                    "success": False,
                    "error": "Authentication required."
                }), 401

            # ---------------------------------------------
            # Current role
            # ---------------------------------------------

            current_role = get_current_role()

            # ---------------------------------------------
            # Invalid role
            # ---------------------------------------------

            if current_role not in normalized_roles:

                return jsonify({
                    "success": False,
                    "error": "Access denied.",
                    "message": (
                        "Your account does not have "
                        "a valid authorized role."
                    ),
                    "role": current_role
                }), 403

            return f(*args, **kwargs)

        return decorated_function

    return decorator


# =========================================================
# GET USER AUTHORIZATION INFORMATION
# =========================================================

def get_authorization_info():
    """
    Return clean authorization information for
    the currently authenticated user.
    """

    user = get_current_user()

    if not user:

        return {
            "authenticated": False,
            "role": None,
            "is_admin": False,
            "is_user": False
        }

    role = get_current_role()

    return {
        "authenticated": True,
        "role": role,
        "is_admin": role == ADMIN_ROLE,
        "is_user": role == USER_ROLE
    }


# =========================================================
# EXPORTS
# =========================================================

__all__ = [
    "ADMIN_ROLE",
    "USER_ROLE",

    "normalize_role",

    "get_current_user",
    "get_current_role",

    "is_authenticated",
    "is_admin",
    "is_user",
    "has_role",

    "require_auth",
    "require_admin",
    "require_user",
    "require_admin_or_user",
    "require_roles",

    "get_authorization_info",
]