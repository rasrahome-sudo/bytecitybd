app_name = "bytecitybd"
app_title = "ByteCityBD"
app_publisher = "ByteCity"
app_description = "Custom ERPNext app for ByteCityBD mobile/web integration"
app_email = "info@bytecity.com"
app_license = "MIT"
required_apps = ["frappe", "erpnext"]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/bytecitybd/css/bytecitybd.css"
# app_include_js = "/assets/bytecitybd/js/bytecitybd.js"

# Includes in <body>
# ------------------

# include js, css files in body of desk.html
# app_include_js = "/assets/bytecitybd/js/bytecitybd.js"

# Home page
# ------------------

# home_page = "bytecitybd_home"

# Generators
# ------------------

# automatically create page for each generator of type "new_page"
# page_generator = "bytecitybd.bytecitybd.doctype.bytecitybd_new_page.bytecitybd_new_page"

# Installation
# ------------------

# before_install = "bytecitybd.install.before_install"
# after_install = "bytecitybd.install.after_install"

# Uninstallation
# ------------------

# before_uninstall = "bytecitybd.uninstall.before_uninstall"
# after_uninstall = "bytecitybd.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.notifications for examples

# Permissions
# ------------------
# Permissions are defined in each doctype's JSON

# Website Parameters
# ------------------

# website_route_rules = [
#     {"from": "/bytecitybd", "to": "bytecitybd.bytecitybd.doctype.bytecitybd_new_page.bytecitybd_new_page"}
# ]

# Website Sidebar
# ------------------

# website_sidebar = "ByteCityBD Sidebar"

# Modules
# ------------------
modules = {
    "Bytecitybd": {
        "color": "#4CAF50",
        "icon": "octicon octicon-device-mobile",
        "type": "module"
    }
}