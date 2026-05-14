"""ByteCityBD Notification doctype controller."""

import frappe
from frappe.model.document import Document


class ByteCityBDNotification(Document):
    """ByteCityBD Notification - app-specific notifications for users."""

    def on_update(self):
        """Set read_at timestamp when notification is marked as read."""
        if self.is_read and not self.read_at:
            self.read_at = frappe.utils.now_datetime()