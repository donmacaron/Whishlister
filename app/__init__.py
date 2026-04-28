import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "warning"

DEFAULT_SUPERUSER_LOGIN    = os.environ.get("SUPERUSER_LOGIN",    "admin")
DEFAULT_SUPERUSER_PASSWORD = os.environ.get("SUPERUSER_PASSWORD", "FUCK1337")


def _seed_superuser():
    from app.models import User
    if User.query.filter_by(is_superuser=True).first():
        return
    existing = User.query.filter_by(username=DEFAULT_SUPERUSER_LOGIN).first()
    if existing:
        existing.is_superuser = True
        existing.set_password(DEFAULT_SUPERUSER_PASSWORD)
        db.session.commit()
        print(f"[Wishlister] Promoted '{DEFAULT_SUPERUSER_LOGIN}' to super user.")
        return
    user = User(username=DEFAULT_SUPERUSER_LOGIN, is_superuser=True)
    user.set_password(DEFAULT_SUPERUSER_PASSWORD)
    db.session.add(user)
    db.session.commit()
    print(f"[Wishlister] Default super user '{DEFAULT_SUPERUSER_LOGIN}' created.")


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "profiles"), exist_ok=True)
    os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], "wishes"),   exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from app.auth         import auth_bp
    from app.main         import main_bp
    from app.wishes       import wishes_bp
    from app.admin        import admin_bp
    from app.settings     import settings_bp
    from app.reservations import reservations_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(wishes_bp,       url_prefix="/wishes")
    app.register_blueprint(admin_bp,        url_prefix="/admin")
    app.register_blueprint(settings_bp,     url_prefix="/settings")
    app.register_blueprint(reservations_bp, url_prefix="/reserve")

    from app.cli import register_commands
    register_commands(app)

    with app.app_context():
        db.create_all()
        _seed_superuser()

    return app
