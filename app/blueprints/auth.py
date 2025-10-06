"""Authentication blueprint."""

from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.forms import LoginForm
from app.models import User

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for("manuals.list_manuals"))

    form = LoginForm()

    if form.validate_on_submit():
        # Strip whitespace from email
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(form.password.data):
            # Update last login time
            user.last_login = datetime.utcnow()
            db.session.commit()

            # Log user in
            login_user(user)

            # Redirect to next page or home
            next_page = request.args.get("next")
            if next_page and next_page.startswith("/"):
                return redirect(next_page)
            return redirect(url_for("manuals.list_manuals"))

        flash("Invalid email or password.", "danger")

    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
