"""ByteCityBD v1 Sales Order API endpoints.

Provides list, details, create, and status update for Sales Order doctype
via the ByteCityBD mobile/web app.
"""

import frappe
from frappe.utils import getdate, today
from bytecitybd.bytecitybd.api.utils import (
    success_response, error_response, list_response,
    get_pagination_params, check_permission, sanitize_search_term
)


@frappe.whitelist()
def list(limit=20, offset=0, status=None, customer=None, from_date=None, to_date=None):
    """List sales orders with pagination and optional filters.

    Args:
        limit: Number of records per page (max 100)
        offset: Starting record index
        status: Filter by status (Draft, Submitted, etc.)
        customer: Filter by customer
        from_date: Filter by transaction date (from)
        to_date: Filter by transaction date (to)

    Returns:
        dict: List response with pagination metadata
    """
    try:
        check_permission("Sales Order", "read")
        limit, offset = get_pagination_params(limit, offset)

        filters = {}
        if status:
            filters["status"] = status
        if customer:
            filters["customer"] = customer
        if from_date:
            filters["transaction_date"] = [">=", getdate(from_date)]
        if to_date:
            filters["transaction_date"] = ["<=", getdate(to_date)]

        total = frappe.db.count("Sales Order", filters=filters)

        orders = frappe.db.get_list(
            "Sales Order",
            filters=filters,
            fields=["name", "customer", "customer_name",
                     "transaction_date", "status", "grand_total",
                     "currency", "order_type", "delivery_status"],
            limit_start=offset,
            limit_page_length=limit,
            order_by="transaction_date desc"
        )

        return list_response(
            data=orders,
            total=total,
            limit=limit,
            offset=offset,
            message="Sales orders retrieved"
        )
    except frappe.PermissionError as e:
        return error_response(message="Permission denied", error=e)
    except Exception as e:
        return error_response(message="Failed to list sales orders", error=e)


@frappe.whitelist()
def details(name):
    """Get detailed info about a specific sales order.

    Args:
        name: Sales Order ID

    Returns:
        dict: Success response with full order details including items
    """
    try:
        check_permission("Sales Order", "read")

        if not frappe.db.exists("Sales Order", name):
            return error_response(message=f"Sales Order {name} not found")

        order = frappe.get_doc("Sales Order", name)

        data = {
            "name": order.name,
            "customer": order.customer,
            "customer_name": order.customer_name,
            "transaction_date": str(order.transaction_date),
            "delivery_date": str(order.delivery_date) if order.delivery_date else None,
            "status": order.status,
            "order_type": order.order_type,
            "grand_total": order.grand_total,
            "net_total": order.net_total,
            "total_taxes_and_charges": order.total_taxes_and_charges,
            "currency": order.currency,
            "delivery_status": order.delivery_status,
            "billing_status": order.billing_status,
            "notes": order.notes or None,
            "items": []
        }

        for item in order.items:
            data["items"].append({
                "item_code": item.item_code,
                "item_name": item.item_name,
                "qty": item.qty,
                "rate": item.rate,
                "amount": item.amount,
                "delivered_qty": item.delivered_qty,
                "warehouse": item.warehouse or None,
                "description": item.description or None,
            })

        # Get linked ByteCityBD Sales Link
        sales_link_exists = frappe.db.exists(
            "ByteCityBD Sales Link",
            {"sales_order": name}
        )
        if sales_link_exists:
            link = frappe.get_doc(
                "ByteCityBD Sales Link",
                {"sales_order": name}
            )
            data["app_notes"] = link.app_notes
            data["priority_flag"] = link.priority_flag

        return success_response(data=data, message="Sales order details retrieved")
    except frappe.PermissionError as e:
        return error_response(message="Permission denied", error=e)
    except Exception as e:
        return error_response(message="Failed to get sales order details", error=e)


@frappe.whitelist()
def create(customer, items, delivery_date=None, order_type="Sales", notes=None, priority_flag=None, follow_up_date=None):
    """Create a new sales order.

    Args:
        customer: Customer ID (required)
        items: JSON string of items list (required)
            Each item: {"item_code": "...", "qty": 5, "rate": 100}
        delivery_date: Expected delivery date
        order_type: Order type (default: Sales)
        notes: Order notes
        priority_flag: Priority flag for ByteCityBD Sales Link
        follow_up_date: Follow-up date

    Returns:
        dict: Success response with created order name
    """
    try:
        check_permission("Sales Order", "create")

        import json
        if isinstance(items, str):
            items = json.loads(items)

        if not items:
            return error_response(message="Items are required")

        # Create Sales Order
        order = frappe.get_doc({
            "doctype": "Sales Order",
            "customer": customer,
            "delivery_date": delivery_date or today(),
            "order_type": order_type,
            "notes": notes,
        })

        for item_data in items:
            order.append("items", {
                "item_code": item_data.get("item_code"),
                "qty": item_data.get("qty", 1),
                "rate": item_data.get("rate", 0),
            })

        order.insert(ignore_permissions=True)

        # Optionally create ByteCityBD Sales Link
        if priority_flag or follow_up_date or notes:
            link = frappe.get_doc({
                "doctype": "ByteCityBD Sales Link",
                "sales_order": order.name,
                "customer": customer,
                "priority_flag": priority_flag or "Normal",
                "app_notes": notes or None,
                "follow_up_date": follow_up_date or None,
            })
            link.insert(ignore_permissions=True)

        frappe.db.commit()

        return success_response(
            data={"name": order.name, "status": order.status},
            message="Sales order created successfully"
        )
    except frappe.PermissionError as e:
        return error_response(message="Permission denied", error=e)
    except Exception as e:
        return error_response(message="Failed to create sales order", error=e)


@frappe.whitelist()
def update_status(name, action):
    """Update the status of a sales order (Submit, Cancel, Close, Amend).

    Args:
        name: Sales Order ID
        action: Action to perform (Submit, Cancel, Close, Amend)

    Returns:
        dict: Success response with updated status
    """
    try:
        if not frappe.db.exists("Sales Order", name):
            return error_response(message=f"Sales Order {name} not found")

        order = frappe.get_doc("Sales Order", name)

        valid_actions = ["Submit", "Cancel", "Close", "Amend"]
        if action not in valid_actions:
            return error_response(
                message=f"Invalid action. Valid actions: {valid_actions}"
            )

        if action == "Submit":
            check_permission("Sales Order", "submit")
            order.submit()
        elif action == "Cancel":
            check_permission("Sales Order", "cancel")
            order.cancel()
        elif action == "Close":
            check_permission("Sales Order", "write")
            order.close_order()
        elif action == "Amend":
            check_permission("Sales Order", "create")
            order = order.amend()

        frappe.db.commit()

        return success_response(
            data={"name": order.name, "status": order.status},
            message=f"Sales order {action} successful"
        )
    except frappe.PermissionError as e:
        return error_response(message="Permission denied", error=e)
    except Exception as e:
        return error_response(message=f"Failed to {action} sales order", error=e)