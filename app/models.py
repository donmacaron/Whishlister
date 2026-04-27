from datetime import date
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_superuser = db.Column(db.Boolean, default=False, nullable=False)

    bio = db.Column(db.Text, default="")
    profile_pic = db.Column(db.String(256), default="")
    birth_day = db.Column(db.Integer, nullable=True)
    birth_month = db.Column(db.Integer, nullable=True)
    birth_year = db.Column(db.Integer, nullable=True)

    wish_items = db.relationship(
        "WishItem", backref="owner", lazy=True, cascade="all, delete-orphan"
    )
    pw_requests = db.relationship(
        "PasswordChangeRequest",
        backref="requester",
        lazy=True,
        foreign_keys="PasswordChangeRequest.user_id",
        cascade="all, delete-orphan",
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def age(self):
        if self.birth_year is None or self.birth_month is None or self.birth_day is None:
            return None
        today = date.today()
        born = date(self.birth_year, self.birth_month, self.birth_day)
        return (
            today.year - born.year
            - ((today.month, today.day) < (born.month, born.day))
        )

    @property
    def birthday_display(self):
        if self.birth_month is None or self.birth_day is None:
            return None
        months = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
        ]
        if self.birth_year:
            return f"{months[self.birth_month - 1]} {self.birth_day}, {self.birth_year}"
        return f"{months[self.birth_month - 1]} {self.birth_day}"


class WishItem(db.Model):
    __tablename__ = "wish_items"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    link = db.Column(db.String(512), default="")
    description = db.Column(db.Text, default="")
    picture = db.Column(db.String(256), default="")
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class PasswordChangeRequest(db.Model):
    __tablename__ = "password_change_requests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    new_password_hash = db.Column(db.String(256), nullable=False)
    status = db.Column(db.String(20), default="pending")
    requested_at = db.Column(db.DateTime, server_default=db.func.now())
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolved_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
