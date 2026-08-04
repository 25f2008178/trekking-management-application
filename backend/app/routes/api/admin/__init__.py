from flask import Blueprint
from flask_security import auth_required, roles_accepted

admin_bp = Blueprint("admin", __name__)

@admin_bp.before_request
@auth_required()
@roles_accepted("admin")
def check_admin_access():
    pass

from . import search, staff, treks, users