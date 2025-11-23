"""
ASGI config for real_estate_project project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_project.settings')

application = get_asgi_application()

