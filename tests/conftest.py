import os
import sys

import django
from django.conf import settings

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_src = os.path.join(_root, "src")
_tests = os.path.join(_root, "tests")

for p in [_root, _src, _tests]:
    if p not in sys.path:
        sys.path.insert(0, p)

os.environ["DJANGO_SETTINGS_MODULE"] = "tests.settings"

if not settings.configured:
    from tests.settings import DATABASES, INSTALLED_APPS, ROOT_URLCONF, SECRET_KEY
    settings.configure(
        DATABASES=DATABASES,
        INSTALLED_APPS=INSTALLED_APPS,
        SECRET_KEY=SECRET_KEY,
        ROOT_URLCONF=ROOT_URLCONF,
        TAMARA_SANDBOX=True,
        TAMARA_API_TOKEN="test-token",
    )
    django.setup()
