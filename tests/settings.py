
SECRET_KEY = "test-secret-key-for-tamara-package"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "tamara",
]
ROOT_URLCONF = "urls"
TAMARA_SANDBOX = True
TAMARA_API_TOKEN = "test-token"
