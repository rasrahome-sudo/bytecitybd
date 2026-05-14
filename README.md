# ByteCityBD - ERPNext Custom App

## Overview

ByteCityBD is a custom Frappe/ERPNext app that provides a whitelisted API layer for a Flutter web/mobile application. It enables organization users to interact with ERPNext data (Customers, Items, Sales Orders) through a separate frontend app hosted on a different domain.

## Key Principles

- **Never modifies ERPNext core doctypes** — all custom data lives in companion doctypes with Link Fields
- **Code-based updates only** — deployed via `bench migrate`, no manual UI changes
- **API versioning** — `bytecitybd.api.v1.*` pattern for future compatibility
- **Standardized responses** — all API endpoints return `{success, data, message, error}` format

## Custom Doctypes

| Doctype | Purpose | Links To |
|---------|---------|----------|
| ByteCityBD User Profile | App user preferences & settings | User |
| ByteCityBD App Session | Track user sessions from app | User |
| ByteCityBD Notification | App-specific notifications | User, Sales Order |
| ByteCityBD Sales Link | Additional metadata for sales orders | Sales Order, Customer |

## API Endpoints (v1)

| Category | Endpoints | Path |
|----------|-----------|------|
| Auth | login, logout, validate_session, get_user_info | `bytecitybd.api.v1.auth.*` |
| Dashboard | get_stats, get_recent_activities, get_pending_count | `bytecitybd.api.v1.dashboard.*` |
| Customer | list, details, create, update, search | `bytecitybd.api.v1.customer.*` |
| Item | list, details, search, get_stock_balance | `bytecitybd.api.v1.item.*` |
| Sales Order | list, details, create, update_status | `bytecitybd.api.v1.sales_order.*` |
| Notification | list, mark_read, mark_all_read, get_unread_count, dismiss | `bytecitybd.api.v1.notification.*` |
| Profile | get_profile, update_profile, change_password | `bytecitybd.api.v1.profile.*` |

## Installation

```bash
# Get the app
bench get-app bytecitybd /path/to/bytecitybd

# Install on site
bench install-app bytecitybd

# Run migrations
bench migrate
```

## CORS Configuration

Add to your `site_config.json`:

```json
{
  "allow_cors": "https://app.bytecity.com"
}
```

## API Usage Examples

```bash
# Login
curl -X POST https://erp.bytecity.com/api/method/bytecitybd.api.v1.auth.login \
  -d "usr=admin@example.com" -d "pwd=password"

# List Customers
curl -X GET https://erp.bytecity.com/api/method/bytecitybd.api.v1.customer.list \
  -H "Authorization: Bearer <token>"

# Get Dashboard Stats
curl -X GET https://erp.bytecity.com/api/method/bytecitybd.api.v1.dashboard.get_stats \
  -H "Authorization: Bearer <token>"
```

## Development

```bash
# Development mode
bench --site dev.bytecity.com clear-cache

# Run tests
bench run-tests --app bytecitybd
```

## License

MIT License - See [license.txt](license.txt)