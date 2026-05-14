"""ByteCityBD v1 Auth API endpoints.

Provides login, logout, session validation, and user info retrieval
for the ByteCityBD mobile/web app.
"""

import frappe
from frappe.auth import validate_login
from bytecitybd.bytecitybd.api.utils import success_response, error_response


@frappe.whitelist()
def login(usr, pwd):
    """Authenticate user and return session token.

    Args:
        usr: Username or email
        pwd: Password

    Returns:
        dict: Success response with user info and sid, or error response
    """
    try:
        # Use Frappe's built-in login
        validate_login(usr, pwd)

        # Get user details after successful login
        user = frappe.get_doc("User", frappe.session.user)

        return success_response(
            data={
                "user": frappe.session.user,
                "sid": frappe.session.sid,
                "full_name": user.full_name,
                "email": user.email,
                "user_type": user.user_type,
                "roles": [r.role for r in user.roles],
                "image": user.user_image or None
            },
            message="Login successful"
        )
    except frappe.AuthenticationError as e:
        return error_response(message="Invalid credentials", error=e)
    except Exception as e:
        return error_response(message="Login failed", error=e)


@frappe.whitelist()
def logout():
    """Logout current user and clear session.

    Returns:
        dict: Success response confirming logout
    """
    try:
        frappe.local.login_manager.logout()
        frappe.db.commit()
        return success_response(message="Logout successful")
    except Exception as e:
        return error_response(message="Logout failed", error=e)


@frappe.whitelist()
def validate_session():
    """Validate current session and return user info if valid.

    Returns:
        dict: Success response with user info if session valid, error if not
    """
    try:
        if frappe.session.user == "Guest":
            return error_response(message="No active session")

        user = frappe.get_doc("User", frappe.session.user)

        return success_response(
            data={
                "user": frappe.session.user,
                "full_name": user.full_name,
                "email": user.email,
                "user_type": user.user_type,
                "roles": [r.role for r in user.roles],
                "image": user.user_image or None
            },
            message="Session valid"
        )
    except Exception as e:
        return error_response(message="Session validation failed", error=e)


@frappe.whitelist()
def get_user_info():
    """Get detailed info about the currently logged-in user.

    Returns:
        dict: Success response with user details including profile info
    """
    try:
        if frappe.session.user == "Guest":
            return error_response(message="Not logged in")

        user = frappe.get_doc("User", frappe.session.user)

        # Check if ByteCityBD profile exists
        profile_exists = frappe.db.exists(
            "ByteCityBD User Profile",
            {"user": frappe.session.user}
        )

        data = {
            "user": frappe.session.user,
            "full_name": user.full_name,
            "email": user.email,
            "user_type": user.user_type,
            "roles": [r.role for r in user.roles],
            "image": user.user_image or None,
            "has_profile": 1 if profile_exists else 0
        }

        if profile_exists:
            profile = frappe.get_doc(
                "ByteCityBD User Profile",
                {"user": frappe.session.user}
            )
            data["role_in_app"] = profile.role_in_app
            data["default_customer"] = profile.default_customer

        return success_response(data=data, message="User info retrieved")
    except Exception as e:
        return error_response(message="Failed to get user info", error=e)