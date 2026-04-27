from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import WishItem
from app.wishes import wishes_bp
from app.utils import save_wish_picture


@wishes_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Item name is required.", "danger")
            return render_template("wishes/wish_form.html", item=None, action="Add")
        link = request.form.get("link", "").strip()
        description = request.form.get("description", "").strip()
        item = WishItem(user_id=current_user.id, name=name, link=link, description=description)
        db.session.add(item)
        db.session.flush()
        pic_path = None
        if "picture" in request.files and request.files["picture"].filename:
            pic_path = save_wish_picture(request.files["picture"], current_user.id, item.id)
        if pic_path:
            item.picture = pic_path
        db.session.commit()
        flash("Wish added!", "success")
        return redirect(url_for("main.profile", username=current_user.username))
    return render_template("wishes/wish_form.html", item=None, action="Add")


@wishes_bp.route("/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
def edit(item_id):
    item = WishItem.query.get_or_404(item_id)
    if item.user_id != current_user.id and not current_user.is_superuser:
        flash("Access denied.", "danger")
        return redirect(url_for("main.index"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Item name is required.", "danger")
            return render_template("wishes/wish_form.html", item=item, action="Edit")
        item.name = name
        item.link = request.form.get("link", "").strip()
        item.description = request.form.get("description", "").strip()
        if "picture" in request.files and request.files["picture"].filename:
            pic_path = save_wish_picture(request.files["picture"], item.user_id, item.id)
            if pic_path:
                item.picture = pic_path
        db.session.commit()
        flash("Wish updated!", "success")
        return redirect(url_for("main.profile", username=item.owner.username))
    return render_template("wishes/wish_form.html", item=item, action="Edit")


@wishes_bp.route("/<int:item_id>/delete", methods=["POST"])
@login_required
def delete(item_id):
    item = WishItem.query.get_or_404(item_id)
    if item.user_id != current_user.id and not current_user.is_superuser:
        flash("Access denied.", "danger")
        return redirect(url_for("main.index"))
    owner_username = item.owner.username
    db.session.delete(item)
    db.session.commit()
    flash("Wish deleted.", "info")
    return redirect(url_for("main.profile", username=owner_username))
