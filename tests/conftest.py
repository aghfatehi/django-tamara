import os
import sys

# Ensure the project root and src are on the Python path
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in [_root, os.path.join(_root, "src")]:
    if p not in sys.path:
        sys.path.insert(0, p)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")
