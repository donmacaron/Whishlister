from datetime import datetime
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import User, PasswordChangeRequest
from app.admin import admin_bp
from app.utils import superuser_required


@admin_bp.route("/")
@login_required
@superuser_required
def panel():
    users = User.query.order_by(User.username).all()
    pending = PasswordChangeRequest.query.filter_by(status="pending").all()
    return render_template("admin/panel.html", users=users, pending=pending)


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@superuser_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_superuser:
        flash("Cannot delete a super user.", "danger")
        return redirect(url_for("admin.panel"))
    if user.id == current_user.id:
        flash("Cannot delete yourself.", "danger")
        return redirect(url_for("admin.panel"))
    db.session.delete(user)
    db.session.commit()
    flash(f"User '{user.username}' deleted.", "info")
    return redirect(url_for("admin.panel"))


@admin_bp.route("/requests/<int:req_id>/approve", methods=["POST"])
@login_required
@superuser_required
def approve_request(req_id):
    req = PasswordChangeRequest.query.get_or_404(req_id)
    req.requester.password_hash = req.new_password_hash
    req.status = "approved"
    req.resolved_at = datetime.utcnow()
    req.resolved_by = current_user.id
    db.session.commit()
    flash(f"Password for '{req.requester.username}' approved.", "success")
    return redirect(url_for("admin.panel"))


@admin_bp.route("/requests/<int:req_id>/reject", methods=["POST"])
@login_required
@superuser_required
def reject_request(req_id):
    req = PasswordChangeRequest.query.get_or_404(req_id)
    req.status = "rejected"
    req.resolved_at = datetime.utcnow()
    req.resolved_by = current_user.id
    db.session.commit()
    flash(f"Password request for '{req.requester.username}' rejected.", "info")
    return redirect(url_for("admin.panel"))
