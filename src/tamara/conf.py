from django.conf import settings
from django.dispatch import receiver
from django.test.signals import setting_changed

PREFIX = "TAMARA"


class TamaraSettings:
    DEFAULTS = {
        "SANDBOX": True,
        "API_TOKEN": "",
        "COUNTRY_CODE": "SA",
        "CURRENCY": "SAR",
        "INSTALMENTS": 3,
        "PAYMENT_TYPE": "PAY_BY_INSTALMENTS",
        "LOCALE": "en_US",
        "ROUTE_PREFIX": "tamara",
        "ROUTE_MIDDLEWARE": [
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
        ],
        "SUCCESS_URL": "/tamara/callback",
        "FAILURE_URL": "/tamara/failure",
        "CANCEL_URL": "/tamara/cancel",
        "NOTIFICATION_URL": "/tamara/webhook",
        "API_URLS": {
            "SANDBOX": "https://api-sandbox.tamara.co",
            "PRODUCTION": "https://api.tamara.co",
        },
        "TRANSACTION_MODEL": "tamara.TamaraTransaction",
    }

    def __getattr__(self, attr):
        if attr in self.DEFAULTS:
            django_value = getattr(settings, f"{PREFIX}_{attr}", None)
            if django_value is not None:
                return django_value
            return self.DEFAULTS[attr]
        raise AttributeError(f"Invalid Tamara setting: {attr}")

    @property
    def base_url(self):
        urls = self.API_URLS
        if isinstance(urls, str):
            return urls
        key = "SANDBOX" if self.SANDBOX else "PRODUCTION"
        if isinstance(urls, dict) and key in urls:
            return urls[key]
        return "https://api-sandbox.tamara.co"

    @property
    def api_urls(self):
        urls = self.API_URLS
        if isinstance(urls, dict):
            return urls
        return {"SANDBOX": "https://api-sandbox.tamara.co", "PRODUCTION": "https://api.tamara.co"}


tamara_settings = TamaraSettings()


@receiver(setting_changed)
def reload_tamara_settings(**kwargs):
    if kwargs["setting"].startswith(PREFIX):
        tamara_settings.__dict__.pop("_cached_attr", None)
