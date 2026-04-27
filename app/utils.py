import os
import random
from functools import wraps
from flask import abort, current_app
from flask_login import current_user
from werkzeug.utils import secure_filename


def superuser_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_superuser:
            abort(403)
        return f(*args, **kwargs)
    return decorated


def allowed_file(filename):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[-1].lower()
    return ext in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]


def save_profile_picture(file, username):
    if not file or not file.filename:
        return None
    if not allowed_file(file.filename):
        return None
    ext = file.filename.rsplit(".", 1)[-1].lower()
    filename = secure_filename(f"{username}.{ext}")
    folder = os.path.join(current_app.config["UPLOAD_FOLDER"], "profiles")
    os.makedirs(folder, exist_ok=True)
    file.save(os.path.join(folder, filename))
    return f"uploads/profiles/{filename}"


def save_wish_picture(file, user_id, item_id):
    if not file or not file.filename:
        return None
    if not allowed_file(file.filename):
        return None
    ext = file.filename.rsplit(".", 1)[-1].lower()
    filename = secure_filename(f"{user_id}_{item_id}.{ext}")
    folder = os.path.join(current_app.config["UPLOAD_FOLDER"], "wishes")
    os.makedirs(folder, exist_ok=True)
    file.save(os.path.join(folder, filename))
    return f"uploads/wishes/{filename}"


def get_random_avatar():
    folder = current_app.config.get("RANDOM_PROFILES_FOLDER", "")
    if folder and os.path.isdir(folder):
        exts = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
        avatars = [
            f for f in os.listdir(folder)
            if not f.startswith(".") and os.path.splitext(f)[1].lower() in exts
        ]
        if avatars:
            return f"random_picture_profiles/{random.choice(avatars)}"
    return "placeholder/wish_placeholder.png"
