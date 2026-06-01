import logging

import requests

from tamara.conf import tamara_settings
from tamara.exceptions import TamaraException

logger = logging.getLogger(__name__)


class TamaraClient:
    def __init__(self):
        self._http = None

    @property
    def http(self):
        if self._http is None:
            self._http = requests.Session()
            self._http.headers.update({
                "Authorization": f"Bearer {tamara_settings.API_TOKEN}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            })
        return self._http

    def base_url(self):
        return tamara_settings.base_url

    def get_payment_types(self, country="SA", currency="SAR", order_value=1, phone=""):
        params = {
            "country": country,
            "currency": currency,
            "order_value": order_value,
        }
        if phone:
            params["phone"] = phone
        return self._get("/checkout/payment-types", params=params)

    def create_checkout(self, data):
        return self._post("/checkout", json=data)

    def get_order(self, order_id):
        return self._get(f"/orders/{order_id}")

    def get_order_by_reference_id(self, reference_id):
        return self._get(f"/merchants/orders/reference-id/{reference_id}")

    def authorise_order(self, order_id):
        return self._post(f"/orders/{order_id}/authorise")

    def capture_order(self, order_id, data=None):
        payload = {"order_id": order_id}
        if data:
            payload.update(data)
        return self._post("/payments/capture", json=payload)

    def cancel_order(self, order_id, data=None):
        return self._post(f"/orders/{order_id}/cancel", json=data or {})

    def refund_order(self, order_id, amount, currency="SAR", comment=""):
        return self._post(f"/payments/simplified-refund/{order_id}", json={
            "total_amount": {"amount": amount, "currency": currency},
            "comment": comment,
        })

    def webhook_register(self, url, events, headers=None):
        return self._post("/webhooks", json={
            "url": url,
            "events": events,
            "headers": headers or [],
        })

    def webhook_list(self):
        return self._get("/webhooks/list")

    def webhook_get(self, webhook_id):
        return self._get(f"/webhooks/{webhook_id}")

    def webhook_delete(self, webhook_id):
        return self._delete(f"/webhooks/{webhook_id}")

    def webhook_update(self, webhook_id, url, events, headers=None):
        return self._put(f"/webhooks/{webhook_id}", json={
            "url": url,
            "events": events,
            "headers": headers or [],
        })

    def _request(self, method, path, **kwargs):
        url = f"{self.base_url()}{path}"
        timeout = kwargs.pop("timeout", 30)
        try:
            response = self.http.request(method, url, timeout=timeout, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.RequestException as e:
            logger.error(f"Tamara API {method.upper()} Error: {e} | Path: {path}", extra={"kwargs": kwargs})
            raise TamaraException(str(e)) from e

    def _get(self, path, **kwargs):
        return self._request("GET", path, **kwargs)

    def _post(self, path, **kwargs):
        return self._request("POST", path, **kwargs)

    def _put(self, path, **kwargs):
        return self._request("PUT", path, **kwargs)

    def _delete(self, path, **kwargs):
        return self._request("DELETE", path, **kwargs)


client = TamaraClient()
