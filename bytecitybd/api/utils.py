"""ByteCityBD API utility functions.

Provides standardized response helpers, pagination, permission checks,
and search term sanitization for all v1 API endpoints.
"""

import frappe
import re


def success_response(data=None, message="OK"):
    """Return a standardized success response."""
    return {
        "success": 1,
        "data": data,
        "message": message
    }


def error_response(message="Error", error=None, data=None):
    """Return a standardized error response."""
    return {
        "success": 0,
        "data": data,
        "message": message,
        "error": str(error) if error else None
    }


def list_response(data, total, limit=20, offset=0, message="OK"):
    """Return a standardized list response with pagination metadata."""
    return {
        "success": 1,
        "data": data,
        "total": total,
        "limit": limit,
        "offset": offset,
        "message": message
    }


def get_pagination_params(limit=20, offset=0):
    """Validate and return pagination parameters"""
    try:
        limit = int(limit)
        offset = int(offset)
    except (TypeError, ValueError):
        limit = 20
        offset = 0

    # Clamp values
    limit = max(1, min(limit, 100))
    offset = max(0, offset)

    return limit, offset


def check_permission(doctype, permission_type="read"):
    """Check if current user has permission on the given doctype."""
    if not frappe.has_permission(doctype, permission_type):
        frappe.throw(
            f"You do not have {permission_type} permission on {doctype}",
            frappe.PermissionError
        )


def sanitize_search_term(term):
    """Sanitize search term to prevent injection attacks."""
    if not term:
        return ""
    # Remove special characters, keep alphanumeric and spaces
    term = re.sub(r'[^\w\s@.-]', '', str(term))
    # Limit length
    term = term[:100]
    return term.strip()