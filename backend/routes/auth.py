"""
=========================================================
DALAREICH INTEGRATED POS & INVENTORY MANAGEMENT SYSTEM
Authentication Routes
=========================================================
"""

from flask import Blueprint, request, jsonify
import os
import traceback

from dotenv import load_dotenv
from supabase import create_client, Client


# =========================================================
# LOAD .ENV
# =========================================================
#
# This is required so os.getenv() can read your .env file.
#
# Your .env should contain:
#
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key-here
#
# =========================================================

load_dotenv()


# =========================================================
# BLUEPRINT
# =========================================================

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


# =========================================================
# SUPABASE CONFIGURATION
# =========================================================

SUPABASE_URL = os.getenv(
    "SUPABASE_URL"
)

SUPABASE_SERVICE_ROLE_KEY = os.getenv(
    "SUPABASE_SERVICE_ROLE_KEY"
)


# =========================================================
# CONFIGURATION CHECK
# =========================================================

if not SUPABASE_URL:
    print(
        "ERROR: SUPABASE_URL is not configured."
    )
else:
    print(
        "Supabase URL loaded:",
        SUPABASE_URL
    )


if not SUPABASE_SERVICE_ROLE_KEY:
    print(
        "ERROR: SUPABASE_SERVICE_ROLE_KEY is not configured."
    )
else:
    print(
        "Supabase server key loaded."
    )


# =========================================================
# SUPABASE CLIENT
# =========================================================

supabase: Client | None = None


def get_supabase():
    """
    Create the Supabase client only when needed.

    The Supabase credentials still come directly from
    SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env.
    """

    global supabase

    # -----------------------------------------------------
    # Reuse existing client
    # -----------------------------------------------------

    if supabase is not None:
        return supabase

    # -----------------------------------------------------
    # Check URL
    # -----------------------------------------------------

    if not SUPABASE_URL:

        raise RuntimeError(
            "SUPABASE_URL is missing from .env"
        )

    # -----------------------------------------------------
    # Check service key
    # -----------------------------------------------------

    if not SUPABASE_SERVICE_ROLE_KEY:

        raise RuntimeError(
            "SUPABASE_SERVICE_ROLE_KEY is missing from .env"
        )

    # -----------------------------------------------------
    # Create client
    # -----------------------------------------------------

    try:

        supabase = create_client(
            SUPABASE_URL,
            SUPABASE_SERVICE_ROLE_KEY
        )

        return supabase

    except Exception as error:

        print(
            "Supabase client initialization error:",
            repr(error)
        )

        raise


# =========================================================
# ROLE HELPERS
# =========================================================

def normalize_role(role):
    """
    Normalize the account role.

    Only two roles are supported:

        Admin
        User

    Staff is NOT supported.
    """

    if role is None:
        return None

    role = str(
        role
    ).strip().lower()

    # -----------------------------------------------------
    # ADMIN
    # -----------------------------------------------------

    if role in (
        "admin",
        "administrator",
        "superadmin",
        "super_admin"
    ):

        return "Admin"

    # -----------------------------------------------------
    # USER
    # -----------------------------------------------------

    if role in (
        "user",
        "cashier"
    ):

        return "User"

    # -----------------------------------------------------
    # UNKNOWN
    # -----------------------------------------------------

    return None


# =========================================================
# USER METADATA
# =========================================================

def get_user_metadata(user):
    """
    Safely retrieve Supabase user metadata.
    """

    if user is None:
        return {}

    # -----------------------------------------------------
    # Standard Supabase Python client
    # -----------------------------------------------------

    metadata = getattr(
        user,
        "user_metadata",
        None
    )

    if isinstance(
        metadata,
        dict
    ):

        return metadata

    # -----------------------------------------------------
    # Some Supabase versions expose raw metadata
    # -----------------------------------------------------

    raw_metadata = getattr(
        user,
        "raw_user_meta_data",
        None
    )

    if isinstance(
        raw_metadata,
        dict
    ):

        return raw_metadata

    return {}


# =========================================================
# USER EMAIL
# =========================================================

def get_user_email(user):
    """
    Safely retrieve the Supabase user's email.
    """

    if user is None:
        return ""

    # -----------------------------------------------------
    # Get email directly from Auth user
    # -----------------------------------------------------

    email = getattr(
        user,
        "email",
        None
    )

    if email:

        return str(
            email
        ).strip().lower()

    # -----------------------------------------------------
    # Fallback to metadata
    # -----------------------------------------------------

    metadata = get_user_metadata(
        user
    )

    email = metadata.get(
        "email",
        ""
    )

    return str(
        email
    ).strip().lower()


# =========================================================
# ACTUAL ROLE
# =========================================================

def get_actual_role(user):
    """
    Determine the user's actual role from Supabase
    user metadata.

    Supabase metadata is authoritative.

    Supported roles:

        Admin
        User

    If the metadata does not contain a recognized role,
    the account defaults to User.
    """

    metadata = get_user_metadata(
        user
    )

    metadata_role = normalize_role(
        metadata.get("role")
    )

    # -----------------------------------------------------
    # Valid role found
    # -----------------------------------------------------

    if metadata_role is not None:

        return metadata_role

    # -----------------------------------------------------
    # No valid role
    # -----------------------------------------------------

    return "User"


# =========================================================
# LOGIN
# =========================================================

@auth_bp.route(
    "/login",
    methods=["POST"]
)
def login():

    print()
    print(
        "================================================="
    )
    print(
        "SUPABASE LOGIN ATTEMPT"
    )
    print(
        "================================================="
    )

    try:

        # =================================================
        # REQUEST BODY
        # =================================================

        data = request.get_json(
            silent=True
        ) or {}

        # -------------------------------------------------
        # Email
        # -------------------------------------------------

        email = str(
            data.get("email")
            or data.get("username")
            or ""
        ).strip().lower()

        # -------------------------------------------------
        # Password
        #
        # DO NOT trim passwords.
        # -------------------------------------------------

        password = (
            data.get("password")
            or ""
        )

        # -------------------------------------------------
        # Frontend may still send role.
        #
        # We accept it for compatibility, but it does NOT
        # determine the user's permissions.
        # -------------------------------------------------

        requested_role = str(
            data.get("role")
            or ""
        ).strip()

        print(
            "Email:",
            email
        )

        print(
            "Requested role:",
            requested_role
        )

        # =================================================
        # VALIDATION
        # =================================================

        if not email:

            return jsonify({
                "success": False,
                "error":
                    "Please enter your email."
            }), 400

        if not password:

            return jsonify({
                "success": False,
                "error":
                    "Please enter your password."
            }), 400

        # =================================================
        # SUPABASE
        # =================================================

        client = get_supabase()

        print(
            "Authenticating with Supabase..."
        )

        # =================================================
        # SUPABASE LOGIN
        # =================================================

        auth_response = (
            client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
        )

        # =================================================
        # CHECK RESPONSE
        # =================================================

        if auth_response is None:

            print(
                "Supabase returned None."
            )

            return jsonify({
                "success": False,
                "error":
                    "Invalid email or password."
            }), 401

        # =================================================
        # AUTH USER
        # =================================================

        user = getattr(
            auth_response,
            "user",
            None
        )

        session = getattr(
            auth_response,
            "session",
            None
        )

        # =================================================
        # USER CHECK
        # =================================================

        if user is None:

            print(
                "No user returned by Supabase."
            )

            return jsonify({
                "success": False,
                "error":
                    "Invalid email or password."
            }), 401

        # =================================================
        # USER INFORMATION
        # =================================================

        metadata = get_user_metadata(
            user
        )

        actual_email = get_user_email(
            user
        )

        actual_role = get_actual_role(
            user
        )

        user_id = getattr(
            user,
            "id",
            None
        )

        full_name = (
            metadata.get("full_name")
            or metadata.get("name")
            or ""
        )

        # =================================================
        # LOGGING
        # =================================================

        print(
            "Supabase user ID:",
            user_id
        )

        print(
            "Supabase email:",
            actual_email
        )

        print(
            "Supabase metadata:",
            metadata
        )

        print(
            "Actual role:",
            actual_role
        )

        # =================================================
        # IMPORTANT
        # =================================================
        #
        # DO NOT compare requested_role against actual_role.
        #
        # For example:
        #
        # Frontend:
        #     role = User
        #
        # Supabase:
        #     role = admin
        #
        # The old code returned 403.
        #
        # That check is intentionally removed.
        #
        # The frontend role selector does NOT grant
        # permissions.
        #
        # The Supabase metadata determines the final role.
        #
        # =================================================

        requested_role_normalized = normalize_role(
            requested_role
        )

        print(
            "Requested role normalized:",
            requested_role_normalized
        )

        print(
            "Using Supabase role:",
            actual_role
        )

        # =================================================
        # BUILD USER
        # =================================================

        current_user = {
            "id": user_id,
            "email": actual_email,
            "full_name": full_name,
            "role": actual_role
        }

        # =================================================
        # SUCCESS
        # =================================================

        print(
            "Login successful."
        )

        print(
            "Final role:",
            actual_role
        )

        print(
            "================================================="
        )

        # =================================================
        # RESPONSE
        # =================================================

        response_data = {
            "success": True,
            "message": "Login successful.",
            "user": current_user
        }

        # =================================================
        # SESSION
        # =================================================

        if session is not None:

            access_token = getattr(
                session,
                "access_token",
                None
            )

            refresh_token = getattr(
                session,
                "refresh_token",
                None
            )

            if access_token:

                response_data[
                    "access_token"
                ] = access_token

            if refresh_token:

                response_data[
                    "refresh_token"
                ] = refresh_token

        return jsonify(
            response_data
        ), 200

    # =====================================================
    # LOGIN ERROR
    # =====================================================

    except Exception as error:

        print()
        print(
            "================================================="
        )
        print(
            "LOGIN ERROR"
        )
        print(
            "================================================="
        )

        print(
            "Error:",
            repr(error)
        )

        traceback.print_exc()

        error_message = str(
            error
        )

        lowered = error_message.lower()

        # =================================================
        # INVALID LOGIN
        # =================================================

        if (
            "invalid login credentials"
            in lowered
        ):

            return jsonify({
                "success": False,
                "error":
                    "Invalid email or password."
            }), 401

        # =================================================
        # EMAIL NOT CONFIRMED
        # =================================================

        if (
            "email not confirmed"
            in lowered
        ):

            return jsonify({
                "success": False,
                "error":
                    "Please confirm your email before signing in."
            }), 403

        # =================================================
        # INVALID API KEY
        # =================================================

        if (
            "invalid api key"
            in lowered
            or
            "invalid api_key"
            in lowered
        ):

            return jsonify({
                "success": False,
                "error":
                    "Supabase authentication configuration error."
            }), 500

        # =================================================
        # USER NOT FOUND
        # =================================================

        if (
            "user not found"
            in lowered
        ):

            return jsonify({
                "success": False,
                "error":
                    "No account was found with this email."
            }), 401

        # =================================================
        # GENERIC ERROR
        # =================================================

        return jsonify({
            "success": False,
            "error":
                "Login failed. Please try again."
        }), 500


# =========================================================
# SIGN UP
# =========================================================

@auth_bp.route(
    "/signup",
    methods=["POST"]
)
def signup():

    try:

        # =================================================
        # REQUEST BODY
        # =================================================

        data = request.get_json(
            silent=True
        ) or {}

        full_name = str(
            data.get("full_name")
            or ""
        ).strip()

        email = str(
            data.get("email")
            or ""
        ).strip().lower()

        # Passwords are NOT trimmed.
        password = (
            data.get("password")
            or ""
        )

        confirm_password = (
            data.get("confirm_password")
            or ""
        )

        # =================================================
        # VALIDATION
        # =================================================

        if not full_name:

            return jsonify({
                "success": False,
                "error":
                    "Please enter your full name."
            }), 400

        if not email:

            return jsonify({
                "success": False,
                "error":
                    "Please enter your email address."
            }), 400

        if not password:

            return jsonify({
                "success": False,
                "error":
                    "Please enter a password."
            }), 400

        if len(password) < 6:

            return jsonify({
                "success": False,
                "error":
                    "Password must be at least 6 characters."
            }), 400

        if password != confirm_password:

            return jsonify({
                "success": False,
                "error":
                    "Passwords do not match."
            }), 400

        # =================================================
        # SUPABASE
        # =================================================

        client = get_supabase()

        print()
        print(
            "================================================="
        )
        print(
            "SUPABASE SIGNUP ATTEMPT"
        )
        print(
            "================================================="
        )

        print(
            "Email:",
            email
        )

        # =================================================
        # NEW ACCOUNTS ARE ALWAYS USER
        # =================================================
        #
        # A normal signup must never be able to create
        # an Admin account.
        #
        # =================================================

        signup_response = (
            client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": full_name,
                        "role": "user"
                    }
                }
            })
        )

        # =================================================
        # CHECK RESPONSE
        # =================================================

        if signup_response is None:

            return jsonify({
                "success": False,
                "error":
                    "Supabase did not return a signup response."
            }), 500

        # =================================================
        # USER
        # =================================================

        user = getattr(
            signup_response,
            "user",
            None
        )

        if user is None:

            return jsonify({
                "success": False,
                "error":
                    "Unable to create account."
            }), 400

        # =================================================
        # SUCCESS LOG
        # =================================================

        print(
            "Signup successful:",
            getattr(
                user,
                "email",
                email
            )
        )

        print(
            "New account role: User"
        )

        print(
            "================================================="
        )

        # =================================================
        # RESPONSE
        # =================================================

        return jsonify({
            "success": True,
            "message":
                "Account created successfully. "
                "Please confirm your email before signing in."
        }), 201

    # =====================================================
    # SIGNUP ERROR
    # =====================================================

    except Exception as error:

        print()
        print(
            "================================================="
        )
        print(
            "SIGNUP ERROR"
        )
        print(
            "================================================="
        )

        print(
            "Error:",
            repr(error)
        )

        traceback.print_exc()

        error_message = str(
            error
        )

        lowered = error_message.lower()

        # =================================================
        # EXISTING ACCOUNT
        # =================================================

        if (
            "already registered"
            in lowered
            or
            "already exists"
            in lowered
        ):

            return jsonify({
                "success": False,
                "error":
                    "An account with this email already exists."
            }), 409

        # =================================================
        # INVALID API KEY
        # =================================================

        if (
            "invalid api key"
            in lowered
            or
            "invalid api_key"
            in lowered
        ):

            return jsonify({
                "success": False,
                "error":
                    "Supabase authentication configuration error."
            }), 500

        # =================================================
        # GENERIC ERROR
        # =================================================

        return jsonify({
            "success": False,
            "error":
                "Unable to create account."
        }), 400


# =========================================================
# LOGOUT
# =========================================================

@auth_bp.route(
    "/logout",
    methods=["POST"]
)
def logout():

    try:

        client = get_supabase()

        try:

            client.auth.sign_out()

        except Exception as signout_error:

            print(
                "Supabase sign-out warning:",
                repr(signout_error)
            )

        return jsonify({
            "success": True,
            "message":
                "Logged out successfully."
        }), 200

    except Exception as error:

        print(
            "Logout error:",
            repr(error)
        )

        # Logout should not break the frontend.
        return jsonify({
            "success": True,
            "message":
                "Logged out."
        }), 200