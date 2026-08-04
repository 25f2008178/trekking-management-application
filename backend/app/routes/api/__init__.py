from flask import Blueprint
from app.routes.api.admin import admin_bp
from app.routes.api.staff import staff_bp
from app.routes.api.user import user_bp

api = Blueprint("api", __name__)
api.register_blueprint(admin_bp, url_prefix="/admin")
api.register_blueprint(staff_bp, url_prefix="/staff")
api.register_blueprint(user_bp, url_prefix="/user")

