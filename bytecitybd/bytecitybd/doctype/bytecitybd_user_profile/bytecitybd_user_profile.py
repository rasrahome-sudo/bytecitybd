"""ByteCityBD User Profile doctype controller."""

import frappe
from frappe.model.document import Document


class ByteCityBDUserProfile(Document):
    """ByteCityBD User Profile - stores app-specific user settings."""

    def validate(self):
        """Validate that only one profile exists per user."""
        if frappe.db.exists("ByteCityBD User Profile", {"user": self.user, "name": ["!=", self.name]}):
            frappe.throw(f"Profile already exists for user {self.user}")