"""ByteCityBD App Session doctype controller."""

import frappe
from frappe.model.document import Document


class ByteCityBDAppSession(Document):
    """ByteCityBD App Session - tracks user sessions across devices."""

    def before_insert(self):
        """Generate session ID on insert."""
        if not self.session_id:
            self.session_id = frappe.generate_hash(length=32)
        self.login_timestamp = frappe.utils.now_datetime()