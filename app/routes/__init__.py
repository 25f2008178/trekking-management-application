from flask import Blueprint, render_template
from flask_security import auth_required

from app.routes.api import api

main = Blueprint("main", __name__)
main.register_blueprint(api, url_prefix="/api")

@main.route("/")
@main.route("/dashboard")
@auth_required()
def dashboard():
    return render_template("index.html")