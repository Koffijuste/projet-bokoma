from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask import request, Response
from werkzeug.exceptions import HTTPException
import os

# 🔑 Récupère les identifiants depuis les variables d'environnement
# - En local : définis dans .env
# - Sur Render : définis dans le dashboard "Environment"
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")  # "admin" par défaut
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")           # Obligatoire pour accéder à l'admin

class AuthException(HTTPException):
    def __init__(self, message):
        super().__init__(message, Response(
            "Authentification requise pour accéder à l'administration.",
            401,
            {'WWW-Authenticate': 'Basic realm="BOKOMA Admin"'}
        ))

class AdminAuthMixin:
    def is_accessible(self):
        # Si le mot de passe n'est pas défini, refuse l'accès (sécurité)
        if not ADMIN_PASSWORD:
            return False
        
        auth = request.authorization
        if auth and auth.username == ADMIN_USERNAME and auth.password == ADMIN_PASSWORD:
            return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        raise AuthException("Accès refusé")

class MyAdminIndexView(AdminAuthMixin, AdminIndexView):
    pass

class MyModelView(AdminAuthMixin, ModelView):
    pass