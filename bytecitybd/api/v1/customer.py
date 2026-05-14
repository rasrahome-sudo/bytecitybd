"""ByteCityBD v1 Customer API endpoints.

Provides CRUD operations and search for Customer doctype
via the ByteCityBD mobile/web app.
"""

import frappe
from bytecitybd.bytecitybd.api.utils import (
    success_response, error_response, list_response,
    get_pagination_params, check_permission, sanitize_search_term
)


@frappe.whitelist()
def list(limit=20, offset=0, status=None, customer_group=None, territory=None):
    """List customers with pagination and optional filters.

    Args:
        limit: Number of records per page (max 100)
        offset: Starting record index
        status: Filter by customer status
        customer_group: Filter by customer group
        territory: Filter by territory

    Returns:
        dict: List response with pagination metadata
    """
    try:
        check_permission("Customer", "read")
        limit, offset = get_pagination_params(limit, offset)

        filters = {}
        if status:
            filters["status"] = status
        if customer_group:
            filters["customer_group"] = customer_group
        if territory:
            filters["territory"] = territory

        # Get total count
        total = frappe.db.count("Customer", filters=filters)

        # Get paginated data
        customers = frappe.db.get_list(
            "Customer",
            filters=filters,
            fields=["name", "customer_name", "customer_type",
                     "customer_group", "territory", "status",
                     "email_id", "mobile_no", "image"],
            limit_start=offset,
            limit_page_length=limit,
            order_by="customer_name asc"
        )

        return list_response(
            data=customers,
            total=total,
            limit=limit,
            offset=offset,
            message="Customers retrieved"
        )
    except frappe.PermissionError as e:
        return error_response(message="Permission denied", error=e)
    except Exception as e:
        return error_response(message="Failed to list customers", error=e)


@frappe.whitelist()
def details(name):
    """Get detailed info about a specific customer.

    Args:
        name: Customer ID/name

    Returns:
        dict: Success response with customer details
    """
    try:
        check_permission("Customer", "read")

        if not frappe.db.exists("Customer", name):
            return error_response(message=f"Customer {name} not found")

        customer = frappe.get_doc("Customer", name)

        data = {
            "name": customer.name,
            "customer_name": customer.customer_name,
            "customer_type": customer.customer_type,
            "customer_group": customer.customer_group,
            "territory": customer.territory,
            "status": customer.status,
            "email_id": customer.email_id,
            "mobile_no": customer.mobile_no,
            "image": customer.image or None,
            "tax_id": customer.tax_id or None,
            "default_price_list": customer.default_price_list or None,
            "default_currency": customer.default_currency or None,
            "primary_address": customer.primary_address or None,
            "primary_contact": customer.primary_contact or None,
        }

        # Get linked ByteCityBD Sales Links
        sales_links = frappe.db.get_list(
            "ByteCityBD Sales Link",
            filters={"customer": name},
            fields=["name", "priority_flag", "app_notes"]
        )
        data["sales_links"] = sales_links

        return success_response(data=data, message="Customer details retrieved")
    except frappe.PermissionError as e:
        return error_response(message="Permission denied", error=e)
    except Exception as e:
        return error_response(message="Failed to get customer details", error=e)


@frappe.whitelist()
def create(customer_name, customer_type="Company", customer_group=None, territory=None, email_id=None, mobile_no=None):
    """Create a new customer.

    Args:
        customer_name: Name of the customer (required)
        customer_type: Type - Company, Individual (default: Company)
        customer_group: Customer group
        territory: Territory
        email_id: Email address
        mobile_no: Mobile number

    Returns:
        dict: Success response with created customer name
    """
    try:
        check_permission("Customer", "create")

        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": customer_name,
            "customer_type": customer_type,
            "customer_group": customer_group or "All Customer Groups",
            "territory": territory or "All Territories",
            "email_id": email_id,
            "mobile_no": mobile_no,
        })
        customer.insert(ignore_permissions=True)
        frappe.db.commit()

        return success_response(
            data={"name": customer.name, "customer_name": customer.customer_name},
            message="Customer created successfully"
        )
    except frappe.PermissionError as e:
        return error_response(message="Permission denied", error=e)
    except Exception as e:
        return error_response(message="Failed to create customer", error=e)


@frappe.whitelist()
def update(name, **kwargs):
    """Update an existing customer.

    Args:
        name: Customer ID/name
        **kwargs: Fields to update (customer_name, email_id, mobile_no, etc.)

    Returns:
        dict: Success response with updated customer name
    """
    try:
        check_permission("Customer", "write")

        if not frappe.db.exists("Customer", name):
            return error_response(message=f"Customer {name} not found")

        customer = frappe.get_doc("Customer", name)

        # Update allowed fields
        allowed_fields = [
            "customer_name", "customer_type", "customer_group",
            "territory", "email_id", "mobile_no", "tax_id",
            "default_price_list", "default_currency"
        ]

        for field in allowed_fields:
            if field in kwargs:
                customer.set(field, kwargs[field])

        customer.save(ignore_permissions=True)
        frappe.db.commit()

        return success_response(
            data={"name": customer.name},
            message="Customer updated successfully"
        )
    except frappe.PermissionError as e:
        return error_response(message="Permission denied", error=e)
    except Exception as e:
        return error_response(message="Failed to update customer", error=e)


@frappe.whitelist()
def search(query, limit=20):
    """Search customers by name, email, or mobile number.

    Args:
        query: Search term
        limit: Maximum results to return

    Returns:
        dict: Success response with matching customers
    """
    try:
        check_permission("Customer", "read")
        query = sanitize_search_term(query)

        if not query:
            return error_response(message="Search query is required")

        # Search across multiple fields
        results = frappe.db.get_list(
            "Customer",
            filters=[
                ["customer_name", "like", f"%{query}%"],
                ["status", "!=", "Disabled"]
            ],
            fields=["name", "customer_name", "customer_type",
                     "customer_group", "territory", "status",
                     "email_id", "mobile_no"],
            limit_page_length=limit,
            order_by="customer_name asc"
        )

        # Also search by email and mobile
        email_results = frappe.db.get_list(
            "Customer",
            filters=[
                ["email_id", "like", f"%{query}%"],
                ["status", "!=", "Disabled"]
            ],
            fields=["name", "customer_name", "email_id", "mobile_no"],
            limit_page_length=limit
        )

        mobile_results = frappe.db.get_list(
            "Customer",
            filters=[
                ["mobile_no", "like", f"%{query}%"],
                ["status", "!=", "Disabled"]
            ],
            fields=["name", "customer_name", "email_id", "mobile_no"],
            limit_page_length=limit
        )

        # Merge and deduplicate
        all_results = results + email_results + mobile_results
        seen = set()
        unique_results = []
        for r in all_results:
            if r["name"] not in seen:
                seen.add(r["name"])
                unique_results.append(r)

        return success_response(
            data=unique_results[:limit],
            message=f"Found {len(unique_results)} customers"
        )
    except frappe.PermissionError as e:
        return error_response(message="Permission denied", error=e)
    except Exception as e:
        return error_response(message="Search failed", error=e)