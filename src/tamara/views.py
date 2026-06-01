import json
import logging

from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from tamara.client import client
from tamara.conf import tamara_settings
from tamara.exceptions import TamaraException

logger = logging.getLogger(__name__)


class PaymentTypesView(View):
    def get(self, request):
        try:
            types = client.get_payment_types(
                country=request.GET.get("country", tamara_settings.COUNTRY_CODE),
                currency=request.GET.get("currency", tamara_settings.CURRENCY),
                order_value=float(request.GET.get("order_value", 1)),
                phone=request.GET.get("phone", ""),
            )
            return JsonResponse(types, safe=False)
        except TamaraException as e:
            logger.error(f"Tamara getPaymentTypes failed: {e}")
            return JsonResponse({"error": str(e)}, status=500)


class PayView(View):
    def post(self, request):
        logger.info("Initiating Tamara checkout...")

        amount = float(request.POST.get("amount", 0))
        currency = tamara_settings.CURRENCY
        country_code = tamara_settings.COUNTRY_CODE

        is_auth = request.user.is_authenticated
        first_name = request.POST.get("first_name", request.user.first_name if is_auth else "Customer")
        last_name = request.POST.get("last_name", request.user.last_name if is_auth else "Customer")
        email = request.POST.get("email", request.user.email if is_auth else "customer@example.com")
        phone = request.POST.get("phone", "")

        request_body = {
            "total_amount": {"amount": amount, "currency": currency},
            "shipping_amount": {"amount": 0, "currency": currency},
            "tax_amount": {"amount": 0, "currency": currency},
            "order_reference_id": f"tamara_{__import__('time').time()}",
            "order_number": f"ORD-{__import__('time').time()}",
            "items": [
                {
                    "name": request.POST.get("item_name", "Order Payment"),
                    "type": "Digital",
                    "reference_id": "1",
                    "sku": "PAYMENT-001",
                    "quantity": 1,
                    "unit_price": {"amount": amount, "currency": currency},
                    "total_amount": {"amount": amount, "currency": currency},
                },
            ],
            "consumer": {
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "phone_number": phone,
            },
            "country_code": country_code,
            "description": request.POST.get("description", "Payment for order"),
            "merchant_url": {
                "cancel": request.build_absolute_uri(reverse("tamara:cancel")),
                "failure": request.build_absolute_uri(reverse("tamara:failure")),
                "success": request.build_absolute_uri(reverse("tamara:callback")),
                "notification": request.build_absolute_uri(reverse("tamara:webhook")),
            },
            "payment_type": tamara_settings.PAYMENT_TYPE,
            "instalments": int(tamara_settings.INSTALMENTS),
            "billing_address": {
                "city": request.POST.get("city", "Riyadh"),
                "country_code": country_code,
                "first_name": first_name,
                "last_name": last_name,
                "line1": request.POST.get("address_line1", "Default Address"),
                "phone_number": phone,
            },
            "shipping_address": {
                "city": request.POST.get("city", "Riyadh"),
                "country_code": country_code,
                "first_name": first_name,
                "last_name": last_name,
                "line1": request.POST.get("address_line1", "Default Address"),
                "phone_number": phone,
            },
            "platform": "Django",
            "is_mobile": request.POST.get("is_mobile", "false").lower() == "true",
            "locale": tamara_settings.LOCALE,
        }

        try:
            response = client.create_checkout(request_body)
            logger.info(f"Tamara Checkout Response: {response}")

            if "errors" in response:
                error_message = response["errors"][0]["message"] if response["errors"] else "Payment failed"
                return JsonResponse({"error": error_message}, status=400)

            if "checkout_url" in response:
                request.session["tamara_order_id"] = response.get("order_id")
                request.session["tamara_checkout_id"] = response.get("checkout_id")
                return redirect(response["checkout_url"])

            return JsonResponse({"error": "No checkout URL returned"}, status=400)
        except TamaraException as e:
            logger.error(f"Tamara Checkout Error: {e}")
            return JsonResponse({"error": str(e)}, status=500)


class CallbackView(View):
    def get(self, request):
        logger.info(f"Tamara Callback: {request.GET}")

        order_id = request.GET.get("order_id") or request.session.get("tamara_order_id")
        if not order_id:
            if hasattr(request, "home"):
                return redirect("home")
            return JsonResponse({"error": "Payment verification failed"})

        try:
            response = client.get_order(order_id)
            logger.info(f"Tamara Order Status: {response}")

            status = response.get("status", "")
            success_statuses = {"approved", "authorised", "captured", "fully_captured"}

            if status in success_statuses:
                request.session["tamara_payment_success"] = True
                request.session["tamara_payment_response"] = json.dumps(response)
                return JsonResponse({"status": status, "order_id": order_id})

            return JsonResponse({"error": "Payment was not completed", "status": status})
        except TamaraException as e:
            logger.error(f"Tamara Callback Error: {e}")
            return JsonResponse({"error": str(e)}, status=500)


class CancelView(View):
    def get(self, request):
        logger.info("Tamara Payment Cancelled")
        return JsonResponse({"message": "Payment was cancelled"})


class FailureView(View):
    def get(self, request):
        logger.info("Tamara Payment Failed")
        return JsonResponse({"error": "Payment failed"})


@method_decorator(csrf_exempt, name="dispatch")
class WebhookView(View):
    def post(self, request):
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            payload = request.POST.dict()

        logger.info(f"Tamara Webhook Received: {payload}")

        event = payload.get("event_type", "")
        order_id = payload.get("order_id", "")
        status = payload.get("status", "")

        logger.info(f"Tamara Webhook - Event: {event}, Order: {order_id}, Status: {status}")
        return JsonResponse({"success": True})


class AuthoriseView(View):
    def post(self, request):
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            data = request.POST.dict()

        order_id = data.get("order_id")
        if not order_id:
            return JsonResponse({"error": "order_id is required"}, status=400)

        try:
            response = client.authorise_order(order_id)
            return JsonResponse(response)
        except TamaraException as e:
            logger.error(f"Tamara Authorise Error: {e}")
            return JsonResponse({"error": str(e)}, status=500)
