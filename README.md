# Django Tamara Payment Gateway

[![PyPI Version](https://img.shields.io/pypi/v/aghfatehi-django-tamara.svg)](https://pypi.org/project/aghfatehi-django-tamara/)
[![Django](https://img.shields.io/badge/Django-4.2%20|%205.0%20|%205.1-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/github/license/aghfatehi/django-tamara)](LICENSE)

A professional Django package for integrating [Tamara](https://tamara.co) - the leading Buy Now Pay Later (BNPL) payment solution in the Middle East. Supports Saudi Arabia, UAE, Kuwait, Bahrain, Qatar, and Oman.

## Features

- ✅ Full Tamara Online Checkout flow
- ✅ Payment Types lookup
- ✅ Create Checkout Sessions
- ✅ Authorise / Capture / Cancel / Refund orders
- ✅ Webhook management (register, list, update, delete)
- ✅ Sandbox & Production environments
- ✅ Multi-currency support (SAR, AED, KWD, BHD, QAR, OMR)
- ✅ Multi-country support (SA, AE, KW, BH, QA, OM)
- ✅ In-store checkout support
- ✅ Requests HTTP client (no raw cURL)
- ✅ Configurable URL prefix & middleware
- ✅ Transaction logging model
- ✅ Django 4.2, 5.0 & 5.1 compatible
- ✅ Python 3.9+

## Requirements

| Django  | Python | Package Version |
|---------|--------|-----------------|
| 4.2.x   | 3.9+   | ^1.0            |
| 5.0.x   | 3.10+  | ^1.0            |
| 5.1.x   | 3.10+  | ^1.0            |

## Installation

```bash
pip install aghfatehi-django-tamara
```

## Configuration

### 1. Add to INSTALLED_APPS

```python
# settings.py
INSTALLED_APPS = [
    ...
    'tamara',
]
```

### 2. Environment / Settings Variables

```python
# settings.py

# ─── Tamara Payment Gateway Settings ──────────────────────────────

TAMARA_SANDBOX_MODE = True
# bool | Sandbox mode (testing) when True, Production mode when False

TAMARA_API_TOKEN = "your-api-token-here"
# string | Your Tamara API token from Tamara dashboard

TAMARA_COUNTRY_CODE = "SA"
# string (2 chars) | Country code
# SA = Saudi Arabia | AE = UAE | KW = Kuwait | BH = Bahrain | QA = Qatar | OM = Oman

TAMARA_CURRENCY = "SAR"
# string (3 chars) | Currency code
# SAR = Saudi Riyal | AED = UAE Dirham | KWD = Kuwaiti Dinar | BHD = Bahraini Dinar | QAR = Qatari Riyal | OMR = Omani Riyal

TAMARA_INSTALMENTS = 3
# int | Number of instalments (3, 4, or 6)

TAMARA_PAYMENT_TYPE = "PAY_BY_INSTALMENTS"
# string | Payment type - "PAY_BY_INSTALMENTS" or "PAY_NEXT_MONTH" or "SINGLE_PAYMENT"

TAMARA_LOCALE = "en_US"
# string | Locale - "en_US" or "ar_SA"

TAMARA_ROUTE_PREFIX = "tamara"
# string | URL prefix for all Tamara routes
```

### 3. Include URLs

```python
# urls.py
from django.urls import include, path

urlpatterns = [
    ...
    path('tamara/', include('tamara.urls')),
]
```

### 4. Run Migrations

```bash
python manage.py migrate tamara
```

## Usage

### Quick Start - Frontend Checkout

```python
from tamara.client import client

# Get available payment types
types = client.get_payment_types('SA', 'SAR', 500)

# Create a checkout session
response = client.create_checkout({
    'total_amount': {'amount': 500, 'currency': 'SAR'},
    'order_reference_id': 'ORD-' + str(int(__import__('time').time())),
    'order_number': 'INV-2024-001',
    'consumer': {
        'email': 'customer@example.com',
        'first_name': 'Ahmed',
        'last_name': 'Ali',
        'phone_number': '500000000',
    },
    'country_code': 'SA',
    'merchant_url': {
        'success': 'https://example.com/tamara/callback',
        'failure': 'https://example.com/tamara/failure',
        'cancel': 'https://example.com/tamara/cancel',
        'notification': 'https://example.com/tamara/webhook',
    },
})

# Redirect customer to Tamara checkout
if 'checkout_url' in response:
    # return redirect(response['checkout_url'])
    print(f"Redirect to: {response['checkout_url']}")
```

### Using Routes

The package registers these routes under the configured prefix (`/tamara` by default):

| Method | URI                      | Name                    | Description              |
|--------|--------------------------|-------------------------|--------------------------|
| GET    | `/tamara/payment/types`  | `tamara:payment_types`  | Get eligible payment types |
| POST   | `/tamara/pay`            | `tamara:pay`            | Initiate checkout         |
| ANY    | `/tamara/callback`       | `tamara:callback`       | Payment callback          |
| GET    | `/tamara/cancel`         | `tamara:cancel`         | Cancel handler            |
| GET    | `/tamara/failure`        | `tamara:failure`        | Failure handler           |
| POST   | `/tamara/webhook`        | `tamara:webhook`        | Webhook receiver          |
| POST   | `/tamara/authorise`      | `tamara:authorise`      | Authorise order           |

### API Methods

```python
from tamara.client import client

# Payment Types
types = client.get_payment_types('SA', 'SAR', 500, '500000000')

# Checkout
checkout = client.create_checkout(data)

# Order Management
order = client.get_order('order-id-here')
order = client.get_order_by_reference_id('ref-id-here')

# Authorise / Capture / Cancel / Refund
authorised = client.authorise_order('order-id')
captured = client.capture_order('order-id', {'amount': 500})
cancelled = client.cancel_order('order-id', {'reason': 'out_of_stock'})
refunded = client.refund_order('order-id', 500, 'SAR', 'Refund comment')

# Webhook Management
webhook = client.webhook_register(
    'https://example.com/webhook',
    ['order_approved', 'order_declined', 'order_authorised', 'order_captured', 'order_refunded'],
)
webhook_list = client.webhook_list()
webhook_detail = client.webhook_get('webhook-id')
client.webhook_delete('webhook-id')
client.webhook_update('webhook-id', 'https://example.com/webhook', ['order_approved'])
```

## Handling Webhooks

The webhook endpoint logs all incoming events. Extend the view or listen to the log to implement your business logic:

```python
# views.py (custom webhook handler)
import json
import logging
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class CustomWebhookView(View):
    def post(self, request):
        payload = json.loads(request.body)
        event = payload.get('event_type')
        order_id = payload.get('order_id')
        status = payload.get('status')

        if event == 'order_approved':
            # Mark order as approved
            pass
        elif event == 'order_captured':
            # Fulfill the order
            pass
        elif event == 'order_refunded':
            # Process refund
            pass

        return JsonResponse({'success': True})
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check src/ tests/
```

## Changelog

See [CHANGELOG](CHANGELOG.md) for recent changes.

## Security

If you discover security issues, please email fathi.a.n2002@gmail.com instead of using the issue tracker.

## License

This package is open-sourced software licensed under the [MIT license](LICENSE).

## Support

- **Issues**: [GitHub Issues](https://github.com/aghfatehi/django-tamara/issues)
- **Tamara Docs**: [https://docs.tamara.co](https://docs.tamara.co)
- **Author**: AL-AGHBARI Fatehi ([fathi.a.n2002@gmail.com](mailto:fathi.a.n2002@gmail.com))

## Countries & Currencies

| Country       | Code | Currency | Code |
|---------------|------|----------|------|
| Saudi Arabia  | SA   | Riyal    | SAR  |
| UAE           | AE   | Dirham   | AED  |
| Kuwait        | KW   | Dinar    | KWD  |
| Bahrain       | BH   | Dinar    | BHD  |
| Qatar         | QA   | Riyal    | QAR  |
| Oman          | OM   | Riyal    | OMR  |
"# django-tamara" 
