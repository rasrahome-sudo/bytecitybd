"""ByteCityBD v1 Item API endpoints.

Provides list, details, search, and stock balance for Item doctype
via the ByteCityBD mobile/web app.
"""

import frappe
from bytecitybd.bytecitybd.api.utils import (
    success_response, error_response, list_response,
    get_pagination_params, check_permission, sanitize_search_term
)


@frappe.whitelist()
def list(limit=20, offset=0, item_group=None, disabled=0):
    """List items with pagination and optional filters.

    Args:
        limit: Number of records per page (max 100)
        offset: Starting record index
        item_group: Filter by item group
        disabled: Filter by disabled status (0=active, 1=disabled)

    Returns:
        dict: List response with pagination metadata
    """
    try:
        check_permission("Item", "read")
        limit, offset = get_pagination_params(limit, offset)

        filters = {"disabled": int(disabled)}
        if item_group:
            filters["item_group"] = item_group

        total = frappe.db.count("Item", filters=filters)

        items = frappe.db.get_list(
            "Item",
            filters=filters,
            fields=["name", "item_name", "item_code", "item_group",
                     "standard_rate", "image", "disabled",
                     "has_variants", "variant_of"],
            limit_start=offset,
            limit_page_length=limit,
            order_by="item_name asc"
        )

        return list_response(
            data=items,
            total=total,
            limit=limit,
            offset=offset,
            message="Items retrieved"
        )
    except frappe.PermissionError as e:
        return error_response(message="Permission denied", error=e)
    except Exception as e:
        return error_response(message="Failed to list items", error=e)


@frappe.whitelist()
def details(name):
    """Get detailed info about a specific item.

    Args:
        name: Item code/name

    Returns:
        dict: Success response with item details including stock balance
    """
    try:
        check_permission("Item", "read")

        if not frappe.db.exists("Item", name):
            return error_response(message=f"Item {name} not found")

        item = frappe.get_doc("Item", name)

        data = {
            "name": item.name,
            "item_code": item.item_code,
            "item_name": item.item_name,
            "item_group": item.item_group,
            "description": item.description or None,
            "standard_rate": item.standard_rate or 0,
            "image": item.image or None,
            "disabled": item.disabled,
            "has_variants": item.has_variants,
            "variant_of": item.variant_of or None,
            "stock_uom": item.stock_uom,
            "brand": item.brand or None,
            "weight_uom": item.weight_uom or None,
            "net_weight": item.net_weight or 0,
        }

        # Get stock balance
        stock = _get_item_stock_balance(item.item_code)
        data["stock_balance"] = stock

        return success_response(data=data, message="Item details retrieved")
    except frappe.PermissionError as e:
        return error_response(message="Permission denied", error=e)
    except Exception as e:
        return error_response(message="Failed to get item details", error=e)


@frappe.whitelist()
def search(query, limit=20, item_group=None):
    """Search items by name, code, or description.

    Args:
        query: Search term
        limit: Maximum results to return
        item_group: Optional item group filter

    Returns:
        dict: Success response with matching items
    """
    try:
        check_permission("Item", "read")
        query = sanitize_search_term(query)

        if not query:
            return error_response(message="Search query is required")

        filters = [
            ["item_name", "like", f"%{query}%"],
            ["disabled", "=", 0]
        ]

        if item_group:
            filters.append(["item_group", "=", item_group])

        results = frappe.db.get_list(
            "Item",
            filters=filters,
            fields=["name", "item_code", "item_name", "item_group",
                     "standard_rate", "image"],
            limit_page_length=limit,
            order_by="item_name asc"
        )

        # Also search by item code
        code_filters = [
            ["item_code", "like", f"%{query}%"],
            ["disabled", "=", 0]
        ]
        if item_group:
            code_filters.append(["item_group", "=", item_group])

        code_results = frappe.db.get_list(
            "Item",
            filters=code_filters,
            fields=["name", "item_code", "item_name", "item_group",
                     "standard_rate", "image"],
            limit_page_length=limit
        )

        # Merge and deduplicate
        all_results = results + code_results
        seen = set()
        unique_results = []
        for r in all_results:
            if r["name"] not in seen:
                seen.add(r["name"])
                unique_results.append(r)

        return success_response(
            data=unique_results[:limit],
            message=f"Found {len(unique_results)} items"
        )
    except frappe.PermissionError as e:
        return error_response(message="Permission denied", error=e)
    except Exception as e:
        return error_response(message="Search failed", error=e)


@frappe.whitelist()
def get_stock_balance(name, warehouse=None):
    """Get stock balance for a specific item.

    Args:
        name: Item code
        warehouse: Optional warehouse filter

    Returns:
        dict: Success response with stock balance data
    """
    try:
        check_permission("Item", "read")

        if not frappe.db.exists("Item", name):
            return error_response(message=f"Item {name} not found")

        stock = _get_item_stock_balance(name, warehouse)

        return success_response(
            data=stock,
            message="Stock balance retrieved"
        )
    except frappe.PermissionError as e:
        return error_response(message="Permission denied", error=e)
    except Exception as e:
        return error_response(message="Failed to get stock balance", error=e)


def _get_item_stock_balance(item_code, warehouse=None):
    """Get stock balance for an item across warehouses.

    Args:
        item_code: Item code
        warehouse: Optional specific warehouse

    Returns:
        dict or list: Stock balance data
    """
    from erpnext.stock.utils import get_stock_balance

    if warehouse:
        qty = get_stock_balance(item_code, warehouse)
        return {
            "warehouse": warehouse,
            "actual_qty": qty or 0,
            "item_code": item_code
        }

    # Get balance across all warehouses
    bins = frappe.db.get_list(
        "Bin",
        filters={"item_code": item_code, "actual_qty": [">", 0]},
        fields=["warehouse", "actual_qty", "reserved_qty",
                 "projected_qty", "ordered_qty"]
    )

    total_qty = sum(b.get("actual_qty", 0) for b in bins)

    return {
        "item_code": item_code,
        "total_qty": total_qty,
        "warehouses": bins
    }