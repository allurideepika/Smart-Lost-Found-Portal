from flask import Blueprint, render_template, request, redirect, session, flash
from models.user import User

auth = Blueprint("auth", __name__)

@auth.route("/", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("auth/login.html")

    email = request.form.get("email")
    password = request.form.get("password")
    role = request.form.get("role")

    user = User.query.filter_by(
        email=email,
        password=password,
        role=role
    ).first()

    if user:

        session["user_id"] = user.user_id
        session["name"] = user.name
        session["role"] = user.role

        if user.role == "admin":
            return redirect("/admin/dashboard.html")

        return redirect("/student/dashboard.html")

    flash("Invalid Email or Password")
    return redirect("/")