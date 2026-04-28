from flask import redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import WishItem, WishReservation
from app.reservations import reservations_bp


@reservations_bp.route("/<int:item_id>/reserve", methods=["POST"])
@login_required
def reserve(item_id):
    item = WishItem.query.get_or_404(item_id)

    if item.user_id == current_user.id:
        flash("You can't reserve your own wish.", "warning")
        return redirect(url_for("main.profile", username=item.owner.username))

    if item.reservation:
        flash("This wish is already reserved by someone.", "warning")
        return redirect(url_for("main.profile", username=item.owner.username))

    res = WishReservation(wish_id=item.id, reserved_by_id=current_user.id)
    db.session.add(res)
    db.session.commit()
    flash("Wish reserved! \U0001f440", "success")
    return redirect(url_for("main.profile", username=item.owner.username))


@reservations_bp.route("/<int:item_id>/cancel", methods=["POST"])
@login_required
def cancel(item_id):
    item = WishItem.query.get_or_404(item_id)
    res  = item.reservation

    if not res:
        flash("This wish is not reserved.", "warning")
        return redirect(url_for("main.profile", username=item.owner.username))

    if res.reserved_by_id != current_user.id and not current_user.is_superuser:
        flash("Access denied.", "danger")
        return redirect(url_for("main.profile", username=item.owner.username))

    db.session.delete(res)
    db.session.commit()
    flash("Reservation cancelled.", "info")

    # Redirect to the reserver's own profile if cancelling from My Reservations
    referrer_username = item.owner.username
    return redirect(url_for("main.profile", username=referrer_username))
