"""ByteCityBD v1 Profile API endpoints.

Provides get_profile, update_profile, and change_password
for ByteCityBD User Profile via the mobile/web app.
"""

import frappe
from bytecitybd.bytecitybd.api.utils import success_response, error_response


@frappe.whitelist()
def get_profile():
    """Get the ByteCityBD user profile for the current user.

    Returns:
        dict: Success response with profile data including user info
    """
    try:
        user = frappe.session.user
        if user == "Guest":
            return error_response(message="Not logged in")

        # Get Frappe user info
        frappe_user = frappe.get_doc("User", user)

        data = {
            "user": user,
            "full_name": frappe_user.full_name,
            "email": frappe_user.email,
            "user_type": frappe_user.user_type,
            "image": frappe_user.user_image or None,
            "phone": frappe_user.phone or None,
            "mobile_no": frappe_user.mobile_no or None,
        }

        # Get ByteCityBD profile if exists
        profile_exists = frappe.db.exists(
            "ByteCityBD User Profile",
            {"user": user}
        )

        if profile_exists:
            profile = frappe.get_doc(
                "ByteCityBD User Profile",
                {"user": user}
            )
            data["role_in_app"] = profile.role_in_app
            data["default_customer"] = profile.default_customer or None
            data["default_warehouse"] = profile.default_warehouse or None
            data["app_theme"] = profile.app_theme or "Light"
            data["app_language"] = profile.app_language or "en"
            data["receive_notifications"] = profile.receive_notifications
            data["notification_sound"] = profile.notification_sound or "Default"

        return success_response(data=data, message="Profile retrieved")
    except Exception as e:
        return error_response(message="Failed to get profile", error=e)


@frappe.whitelist()
def update_profile(**kwargs):
    """Update the ByteCityBD user profile.

    Args:
        **kwargs: Fields to update (role_in_app, default_customer,
                  app_theme, app_language, receive_notifications, etc.)

    Returns:
        dict: Success response confirming update
    """
    try:
        user = frappe.session.user
        if user == "Guest":
            return error_response(message="Not logged in")

        # Check if profile exists, create if not
        profile_exists = frappe.db.exists(
            "ByteCityBD User Profile",
            {"user": user}
        )

        if profile_exists:
            profile = frappe.get_doc(
                "ByteCityBD User Profile",
                {"user": user}
            )
        else:
            profile = frappe.get_doc({
                "doctype": "ByteCityBD User Profile",
                "user": user,
            })

        # Update allowed fields
        allowed_fields = [
            "role_in_app", "default_customer", "default_warehouse",
            "app_theme", "app_language", "receive_notifications",
            "notification_sound"
        ]

        for field in allowed_fields:
            if field in kwargs:
                profile.set(field, kwargs[field])

        # Also update Frappe user fields if provided
        frappe_user = frappe.get_doc("User", user)
        user_fields = ["full_name", "phone", "mobile_no"]
        user_updated = False

        for field in user_fields:
            if field in kwargs:
                frappe_user.set(field, kwargs[field])
                user_updated = True

        if user_updated:
            frappe_user.save(ignore_permissions=True)

        if profile_exists:
            profile.save(ignore_permissions=True)
        else:
            profile.insert(ignore_permissions=True)

        frappe.db.commit()

        return success_response(message="Profile updated successfully")
    except Exception as e:
        return error_response(message="Failed to update profile", error=e)


@frappe.whitelist()
def change_password(old_password, new_password):
    """Change the current user's password.

    Args:
        old_password: Current password for verification
        new_password: New password to set

    Returns:
        dict: Success response confirming password change
    """
    try:
        user = frappe.session.user
        if user == "Guest":
            return error_response(message="Not logged in")

        # Verify old password
        from frappe.auth import validate_login
        try:
            validate_login(user, old_password)
        except frappe.AuthenticationError:
            return error_response(message="Current password is incorrect")

        # Update password
        frappe_user = frappe.get_doc("User", user)
        frappe_user.new_password = new_password
        frappe_user.save(ignore_permissions=True)
        frappe.db.commit()

        return success_response(message="Password changed successfully")
    except Exception as e:
        return error_response(message="Failed to change password", error=e)