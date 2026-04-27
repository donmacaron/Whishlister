from flask import render_template
from app.models import User
from app.main import main_bp
from app.utils import get_random_avatar


@main_bp.route("/")
def index():
    users = User.query.order_by(User.username).all()
    return render_template("main/index.html", users=users)


@main_bp.route("/profile/<username>")
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    avatar = user.profile_pic if user.profile_pic else get_random_avatar()
    return render_template("main/profile.html", user=user, avatar=avatar)
