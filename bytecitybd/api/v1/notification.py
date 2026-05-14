"""ByteCityBD v1 Notification API endpoints.

Provides list, mark_read, mark_all_read, unread_count, and dismiss
for ByteCityBD Notification doctype via the mobile/web app.
"""

import frappe
from frappe.utils import now_datetime
from bytecitybd.bytecitybd.api.utils import (
    success_response, error_response, list_response,
    get_pagination_params
)


@frappe.whitelist()
def list(limit=20, offset=0, notification_type=None, is_read=None):
    """List notifications for the current user.

    Args:
        limit: Number of records per page (max 100)
        offset: Starting record index
        notification_type: Filter by type (Info, Alert, Reminder, etc.)
        is_read: Filter by read status (0=unread, 1=read)

    Returns:
        dict: List response with pagination metadata
    """
    try:
        user = frappe.session.user
        if user == "Guest":
            return error_response(message="Not logged in")

        limit, offset = get_pagination_params(limit, offset)

        filters = {"to_user": user, "is_dismissed": 0}
        if notification_type:
            filters["notification_type"] = notification_type
        if is_read is not None:
            filters["is_read"] = int(is_read)

        total = frappe.db.count("ByteCityBD Notification", filters=filters)

        notifications = frappe.db.get_list(
            "ByteCityBD Notification",
            filters=filters,
            fields=["name", "subject", "notification_type",
                     "priority", "is_read", "creation",
                     "related_doctype", "related_docname"],
            limit_start=offset,
            limit_page_length=limit,
            order_by="creation desc"
        )

        return list_response(
            data=notifications,
            total=total,
            limit=limit,
            offset=offset,
            message="Notifications retrieved"
        )
    except Exception as e:
        return error_response(message="Failed to list notifications", error=e)


@frappe.whitelist()
def mark_read(name):
    """Mark a specific notification as read.

    Args:
        name: Notification ID

    Returns:
        dict: Success response confirming mark as read
    """
    try:
        user = frappe.session.user
        if user == "Guest":
            return error_response(message="Not logged in")

        if not frappe.db.exists("ByteCityBD Notification", name):
            return error_response(message=f"Notification {name} not found")

        notification = frappe.get_doc("ByteCityBD Notification", name)

        # Verify ownership
        if notification.to_user != user:
            return error_response(message="Not your notification")

        notification.is_read = 1
        notification.read_at = now_datetime()
        notification.save(ignore_permissions=True)
        frappe.db.commit()

        return success_response(message="Notification marked as read")
    except Exception as e:
        return error_response(message="Failed to mark notification as read", error=e)


@frappe.whitelist()
def mark_all_read():
    """Mark all unread notifications as read for the current user.

    Returns:
        dict: Success response with count of notifications marked
    """
    try:
        user = frappe.session.user
        if user == "Guest":
            return error_response(message="Not logged in")

        unread = frappe.db.get_list(
            "ByteCityBD Notification",
            filters={"to_user": user, "is_read": 0, "is_dismissed": 0},
            fields=["name"]
        )

        count = 0
        for n in unread:
            notification = frappe.get_doc("ByteCityBD Notification", n.name)
            notification.is_read = 1
            notification.read_at = now_datetime()
            notification.save(ignore_permissions=True)
            count += 1

        frappe.db.commit()

        return success_response(
            data={"count": count},
            message=f"{count} notifications marked as read"
        )
    except Exception as e:
        return error_response(message="Failed to mark all as read", error=e)


@frappe.whitelist()
def get_unread_count():
    """Get count of unread notifications for the current user.

    Returns:
        dict: Success response with unread count
    """
    try:
        user = frappe.session.user
        if user == "Guest":
            return error_response(message="Not logged in")

        count = frappe.db.count(
            "ByteCityBD Notification",
            filters={"to_user": user, "is_read": 0, "is_dismissed": 0}
        )

        return success_response(
            data={"unread_count": count},
            message="Unread count retrieved"
        )
    except Exception as e:
        return error_response(message="Failed to get unread count", error=e)


@frappe.whitelist()
def dismiss(name):
    """Dismiss (soft-delete) a notification.

    Args:
        name: Notification ID

    Returns:
        dict: Success response confirming dismissal
    """
    try:
        user = frappe.session.user
        if user == "Guest":
            return error_response(message="Not logged in")

        if not frappe.db.exists("ByteCityBD Notification", name):
            return error_response(message=f"Notification {name} not found")

        notification = frappe.get_doc("ByteCityBD Notification", name)

        # Verify ownership
        if notification.to_user != user:
            return error_response(message="Not your notification")

        notification.is_dismissed = 1
        notification.save(ignore_permissions=True)
        frappe.db.commit()

        return success_response(message="Notification dismissed")
    except Exception as e:
        return error_response(message="Failed to dismiss notification", error=e)