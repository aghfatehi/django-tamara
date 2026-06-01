import json

import pytest
from django.test import Client
from django.urls import reverse


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def session(client):
    """Helper to set session values."""
    session = client.session
    session.save()
    return session


class TestTamaraViews:
    def test_cancel_view(self, client):
        url = reverse("tamara:cancel")
        response = client.get(url)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["message"] == "Payment was cancelled"

    def test_failure_view(self, client):
        url = reverse("tamara:failure")
        response = client.get(url)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["error"] == "Payment failed"

    def test_payment_types_view(self, client):
        url = reverse("tamara:payment_types")
        response = client.get(url)
        assert response.status_code == 500  # no API token set, will fail

    def test_authorise_view_missing_order_id(self, client):
        url = reverse("tamara:authorise")
        response = client.post(url, content_type="application/json")
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data["error"] == "order_id is required"
