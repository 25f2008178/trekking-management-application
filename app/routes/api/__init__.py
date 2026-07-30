from flask import Blueprint
from app.routes.api.admin import admin_bp

api = Blueprint("api", __name__)
api.register_blueprint(admin_bp, url_prefix="/admin")
