from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app import db
from app.models import PasswordChangeRequest
from app.settings import settings_bp
from app.utils import save_profile_picture


@settings_bp.route("/", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_profile":
            current_user.bio = request.form.get("bio", "").strip()
            try:
                raw_day = request.form.get("birth_day", "").strip()
                raw_month = request.form.get("birth_month", "").strip()
                raw_year = request.form.get("birth_year", "").strip()
                day = int(raw_day) if raw_day else None
                month = int(raw_month) if raw_month else None
                year = int(raw_year) if raw_year else None
                if day and month and 1 <= month <= 12 and 1 <= day <= 31:
                    current_user.birth_day = day
                    current_user.birth_month = month
                    current_user.birth_year = year
                elif not day and not month:
                    current_user.birth_day = None
                    current_user.birth_month = None
                    current_user.birth_year = None
            except (ValueError, TypeError):
                flash("Invalid birthday values.", "danger")
            if "profile_pic" in request.files and request.files["profile_pic"].filename:
                pic_path = save_profile_picture(request.files["profile_pic"], current_user.username)
                if pic_path:
                    current_user.profile_pic = pic_path
                else:
                    flash("Invalid image. Allowed: png, jpg, jpeg, gif, webp", "warning")
            db.session.commit()
            flash("Profile updated!", "success")

        elif action == "request_password_change":
            new_pw = request.form.get("new_password", "")
            confirm_pw = request.form.get("confirm_password", "")
            if len(new_pw) < 8:
                flash("Password must be at least 8 characters.", "danger")
            elif new_pw != confirm_pw:
                flash("Passwords do not match.", "danger")
            else:
                PasswordChangeRequest.query.filter_by(
                    user_id=current_user.id, status="pending"
                ).update({"status": "cancelled"})
                req = PasswordChangeRequest(
                    user_id=current_user.id,
                    new_password_hash=generate_password_hash(new_pw),
                )
                db.session.add(req)
                db.session.commit()
                flash("Request submitted. A super user will review it.", "info")

        return redirect(url_for("settings.settings"))

    return render_template("settings/settings.html")
