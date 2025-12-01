from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask import request, Response
from werkzeug.exceptions import HTTPException
import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

if not ADMIN_USERNAME or not ADMIN_PASSWORD:
    raise RuntimeError("❌ Variables ADMIN_USERNAME et ADMIN_PASSWORD requises dans .env")

class AuthException(HTTPException):
    def __init__(self, message):
        super().__init__(message, Response(
            "Authentification requise pour l'administration.",
            401,
            {'WWW-Authenticate': 'Basic realm="BOKOMA Admin"'}
        ))

class AdminAuthMixin:
    def is_accessible(self):
        auth = request.authorization
        if auth and auth.username == ADMIN_USERNAME and auth.password == ADMIN_PASSWORD:
            return True
        raise AuthException("Accès refusé")

    def inaccessible_callback(self, name, **kwargs):
        raise AuthException("Accès refusé")

class MyAdminIndexView(AdminAuthMixin, AdminIndexView):
    pass

class MyModelView(AdminAuthMixin, ModelView):
    pass