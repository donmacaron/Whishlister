from flask import Blueprint

wishes_bp = Blueprint("wishes", __name__)

from app.wishes import routes  # noqa: F401, E402
