"""
ASGI config for hellodjango project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hellodjango.settings')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# Daphne automatically handles WSGI compatibility
# For future WebSocket/Django Channels support, wrap here:
# from channels.routing import ProtocolTypeRouter
# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#     "websocket": websocket_application,  # Add when needed
# })

application = django_asgi_app
