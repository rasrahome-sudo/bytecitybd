"""ByteCityBD Sales Link doctype controller."""

import frappe
from frappe.model.document import Document


class ByteCityBDSalesLink(Document):
    """ByteCityBD Sales Link - companion doctype linking to Sales Order."""

    def validate(self):
        """Validate that only one link exists per sales order."""
        if frappe.db.exists("ByteCityBD Sales Link", {"sales_order": self.sales_order, "name": ["!=", self.name]}):
            frappe.throw(f"Sales Link already exists for Sales Order {self.sales_order}")