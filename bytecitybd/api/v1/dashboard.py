"""ByteCityBD v1 Dashboard API endpoints.

Provides dashboard statistics, recent activities, and pending counts
for the ByteCityBD mobile/web app.
"""

import frappe
from frappe.utils import flt, now_datetime
from bytecitybd.bytecitybd.api.utils import (
    success_response, error_response
)


@frappe.whitelist()
def get_stats():
    """Get dashboard statistics for the current user.

    Returns:
        dict: Success response with stats including:
            - total_customers, total_items, total_sales_orders
            - total_revenue, pending_orders, overdue_orders
            - monthly_revenue (last 6 months)
    """
    try:
        user = frappe.session.user
        if user == "Guest":
            return error_response(message="Not logged in")

        # Get customer stats
        total_customers = frappe.db.count("Customer", filters={"disabled": 0})

        # Get item stats
        total_items = frappe.db.count("Item", filters={"disabled": 0})

        # Get sales order stats
        total_sales_orders = frappe.db.count("Sales Order")
        pending_orders = frappe.db.count(
            "Sales Order",
            filters={"status": ["in", ["Draft", "To Deliver and Bill"]]}
        )
        overdue_orders = frappe.db.count(
            "Sales Order",
            filters={
                "status": ["in", ["To Deliver", "To Deliver and Bill"]],
                "delivery_date": ["<", now_datetime().date()]
            }
        )

        # Get revenue (submitted orders)
        submitted_orders = frappe.db.get_list(
            "Sales Order",
            filters={"status": ["in", ["To Deliver and Bill", "To Deliver", "To Bill", "Completed"]]},
            fields=["grand_total", "currency"]
        )
        total_revenue = flt(sum(flt(o.get("grand_total", 0)) for o in submitted_orders))

        # Monthly revenue (last 6 months)
        monthly_revenue = []
        for i in range(6):
            month_start = frappe.utils.add_months(now_datetime().date(), -(i + 1))
            month_end = frappe.utils.add_days(frappe.utils.add_months(month_start, 1), -1)
            month_total = frappe.db.get_list(
                "Sales Order",
                filters={
                    "status": ["in", ["To Deliver and Bill", "To Deliver", "To Bill", "Completed"]],
                    "transaction_date": ["between", [month_start, month_end]]
                },
                fields=["grand_total"]
            )
            month_sum = flt(sum(flt(o.get("grand_total", 0)) for o in month_total))
            monthly_revenue.append({
                "month": frappe.utils.formatdate(month_start, "MMM YYYY"),
                "revenue": month_sum
            })

        data = {
            "total_customers": total_customers,
            "total_items": total_items,
            "total_sales_orders": total_sales_orders,
            "pending_orders": pending_orders,
            "overdue_orders": overdue_orders,
            "total_revenue": total_revenue,
            "monthly_revenue": monthly_revenue,
        }

        return success_response(data=data, message="Dashboard stats retrieved")
    except Exception as e:
        return error_response(message="Failed to get dashboard stats", error=e)


@frappe.whitelist()
def get_recent_activities(limit=10):
    """Get recent activities for the current user.

    Args:
        limit: Number of activities to return (max 50)

    Returns:
        dict: Success response with recent activities list
    """
    try:
        user = frappe.session.user
        if user == "Guest":
            return error_response(message="Not logged in")

        limit = min(int(limit or 10), 50)

        # Get recent sales orders
        recent_orders = frappe.db.get_list(
            "Sales Order",
            fields=["name", "customer", "customer_name",
                     "transaction_date", "status", "grand_total",
                     "currency", "creation"],
            limit_page_length=limit,
            order_by="creation desc"
        )

        # Get recent customers
        recent_customers = frappe.db.get_list(
            "Customer",
            filters={"disabled": 0},
            fields=["name", "customer_name", "creation"],
            limit_page_length=limit,
            order_by="creation desc"
        )

        activities = []

        for order in recent_orders:
            activities.append({
                "type": "Sales Order",
                "name": order.name,
                "title": f"Order {order.name} - {order.customer_name}",
                "status": order.status,
                "amount": order.grand_total,
                "date": str(order.creation),
            })

        for customer in recent_customers:
            activities.append({
                "type": "Customer",
                "name": customer.name,
                "title": f"New Customer - {customer.customer_name}",
                "date": str(customer.creation),
            })

        # Sort by date descending
        activities.sort(key=lambda x: x.get("date", ""), reverse=True)
        activities = activities[:limit]

        return success_response(data=activities, message="Recent activities retrieved")
    except Exception as e:
        return error_response(message="Failed to get recent activities", error=e)


@frappe.whitelist()
def get_pending_count():
    """Get count of pending items requiring action.

    Returns:
        dict: Success response with pending counts
    """
    try:
        user = frappe.session.user
        if user == "Guest":
            return error_response(message="Not logged in")

        pending_orders = frappe.db.count(
            "Sales Order",
            filters={"status": ["in", ["Draft", "To Deliver and Bill"]]}
        )

        overdue_orders = frappe.db.count(
            "Sales Order",
            filters={
                "status": ["in", ["To Deliver", "To Deliver and Bill"]],
                "delivery_date": ["<", now_datetime().date()]
            }
        )

        unread_notifications = frappe.db.count(
            "ByteCityBD Notification",
            filters={"is_read": 0, "to_user": user, "is_dismissed": 0}
        )

        data = {
            "pending_orders": pending_orders,
            "overdue_orders": overdue_orders,
            "unread_notifications": unread_notifications,
            "total_pending": pending_orders + overdue_orders + unread_notifications,
        }

        return success_response(data=data, message="Pending count retrieved")
    except Exception as e:
        return error_response(message="Failed to get pending count", error=e)