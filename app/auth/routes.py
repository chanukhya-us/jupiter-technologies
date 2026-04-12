from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash

from ..extensions import db
from ..models import User
from ..utils import add_activity

auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("reports.dashboard"))
    return render_template("auth/login.html")


@auth_bp.post("/login")
def login_post():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    user = User.query.filter_by(username=username, is_active=True).first()
    if user is None or not check_password_hash(user.password_hash, password):
        flash("Invalid credentials.", "danger")
        return redirect(url_for("auth.login"))

    login_user(user)
    add_activity("login", "user", user.id, f"User {user.username} logged in")
    db.session.commit()
    flash("Welcome back.", "success")
    return redirect(url_for("reports.dashboard"))


@auth_bp.post("/logout")
@login_required
def logout():
    user_id = current_user.id
    username = current_user.username
    logout_user()
    add_activity("logout", "user", user_id, f"User {username} logged out")
    db.session.commit()
    flash("Logged out.", "info")
    return redirect(url_for("auth.login"))
