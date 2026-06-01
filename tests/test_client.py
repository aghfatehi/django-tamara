import pytest
import responses
from django.test import override_settings

from tamara.client import TamaraClient
from tamara.conf import tamara_settings


@pytest.fixture
def client():
    return TamaraClient()


class TestTamaraClient:
    def test_base_url_sandbox(self, client):
        tamara_settings.DEFAULTS["SANDBOX"] = True
        url = client.base_url()
        assert url == "https://api-sandbox.tamara.co"

    @override_settings(TAMARA_SANDBOX=False)
    def test_base_url_production(self, client):
        url = client.base_url()
        assert url == "https://api.tamara.co"

    @responses.activate
    def test_get_payment_types(self, client):
        responses.get(
            "https://api-sandbox.tamara.co/checkout/payment-types?country=SA&currency=SAR&order_value=1",
            json=[{"name": "PAY_BY_INSTALMENTS"}],
            status=200,
        )
        result = client.get_payment_types("SA", "SAR", 1)
        assert result == [{"name": "PAY_BY_INSTALMENTS"}]

    @responses.activate
    def test_create_checkout(self, client):
        responses.post(
            "https://api-sandbox.tamara.co/checkout",
            json={"checkout_url": "https://checkout.tamara.co/abc", "order_id": "ord-123"},
            status=200,
        )
        result = client.create_checkout({"total_amount": {"amount": 500, "currency": "SAR"}})
        assert result["checkout_url"] == "https://checkout.tamara.co/abc"
        assert result["order_id"] == "ord-123"

    @responses.activate
    def test_get_order(self, client):
        responses.get(
            "https://api-sandbox.tamara.co/orders/ord-123",
            json={"id": "ord-123", "status": "approved"},
            status=200,
        )
        result = client.get_order("ord-123")
        assert result["status"] == "approved"

    @responses.activate
    def test_authorise_order(self, client):
        responses.post(
            "https://api-sandbox.tamara.co/orders/ord-123/authorise",
            json={"id": "ord-123", "status": "authorised"},
            status=200,
        )
        result = client.authorise_order("ord-123")
        assert result["status"] == "authorised"

    @responses.activate
    def test_capture_order(self, client):
        responses.post(
            "https://api-sandbox.tamara.co/payments/capture",
            json={"id": "cap-123", "status": "captured"},
            status=200,
        )
        result = client.capture_order("ord-123", {"amount": 500})
        assert result["status"] == "captured"

    @responses.activate
    def test_cancel_order(self, client):
        responses.post(
            "https://api-sandbox.tamara.co/orders/ord-123/cancel",
            json={"id": "ord-123", "status": "cancelled"},
            status=200,
        )
        result = client.cancel_order("ord-123", {"reason": "out_of_stock"})
        assert result["status"] == "cancelled"

    @responses.activate
    def test_refund_order(self, client):
        responses.post(
            "https://api-sandbox.tamara.co/payments/simplified-refund/ord-123",
            json={"id": "ref-123", "status": "refunded"},
            status=200,
        )
        result = client.refund_order("ord-123", 500, "SAR", "Customer requested refund")
        assert result["status"] == "refunded"

    @responses.activate
    def test_webhook_register(self, client):
        responses.post(
            "https://api-sandbox.tamara.co/webhooks",
            json={"id": "wh-123", "url": "https://example.com/webhook"},
            status=200,
        )
        result = client.webhook_register("https://example.com/webhook", ["order_approved"])
        assert result["id"] == "wh-123"

    @responses.activate
    def test_webhook_list(self, client):
        responses.get(
            "https://api-sandbox.tamara.co/webhooks/list",
            json=[{"id": "wh-123"}],
            status=200,
        )
        result = client.webhook_list()
        assert result == [{"id": "wh-123"}]

    @responses.activate
    def test_get_order_by_reference_id(self, client):
        responses.get(
            "https://api-sandbox.tamara.co/merchants/orders/reference-id/ref-abc",
            json={"id": "ord-123", "reference_id": "ref-abc"},
            status=200,
        )
        result = client.get_order_by_reference_id("ref-abc")
        assert result["reference_id"] == "ref-abc"

    @responses.activate
    def test_webhook_delete(self, client):
        responses.delete(
            "https://api-sandbox.tamara.co/webhooks/wh-123",
            json={"success": True},
            status=200,
        )
        result = client.webhook_delete("wh-123")
        assert result["success"] is True

    @responses.activate
    def test_webhook_update(self, client):
        responses.put(
            "https://api-sandbox.tamara.co/webhooks/wh-123",
            json={"id": "wh-123", "url": "https://example.com/webhook-new"},
            status=200,
        )
        result = client.webhook_update("wh-123", "https://example.com/webhook-new", ["order_approved"])
        assert result["url"] == "https://example.com/webhook-new"
