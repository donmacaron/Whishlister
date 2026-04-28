from flask import Blueprint

reservations_bp = Blueprint("reservations", __name__)

from app.reservations import routes  # noqa: F401, E402
