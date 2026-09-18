from email.mime import image

from flask import Flask, render_template, request, redirect, session, flash
from config import Config
from database.database import db
from models.user import User
from models.lost_item import LostItem
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from models.found_item import FoundItem
from models.notification import Notification
from models.claim import Claim
from models.match import Match
from services.ai_match import get_image_embedding, cosine_similarity
import numpy as np

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

app.config.from_object(Config)
app.secret_key = "smart_lost_found_secret"

db.init_app(app)

with app.app_context():
    try:
        db.engine.connect()
        print("✅ Database Connected Successfully!")

        # Create database tables if they do not exist
        db.create_all()
        print("✅ Database Tables Ready!")

    except Exception as e:
        print("❌ Database Connection Failed!")
        print(e)

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
@app.route("/login.html", methods=["GET", "POST"])
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

        if role == "admin":
            return redirect("/admin/dashboard.html")

        return redirect("/student/dashboard.html")

    flash("Invalid Email or Password")
    return redirect("/")

@app.route("/student/dashboard")
@app.route("/student/dashboard.html")
def student_dashboard():

    if "user_id" not in session:
        return redirect("/")

    user_id = session["user_id"]

    total_lost = LostItem.query.filter_by(user_id=user_id).count()

    total_found = FoundItem.query.filter_by(user_id=user_id).count()

    total_matches = LostItem.query.filter(
    LostItem.user_id == user_id,
    LostItem.status.in_(["Matched", "Owner Notified"])
).count()

    total_collected = LostItem.query.filter_by(
        user_id=user_id,
        status="Returned"
    ).count()

    recent_reports = LostItem.query.filter_by(
        user_id=user_id
    ).order_by(
        LostItem.created_at.desc()
    ).limit(5).all()

    latest_item = LostItem.query.filter_by(
    user_id=user_id
).order_by(
    LostItem.created_at.desc()
).first()

    return render_template(
         "student/dashboard.html",
    total_lost=total_lost,
    total_found=total_found,
    total_matches=total_matches,
    total_collected=total_collected,
    recent_reports=recent_reports,
    latest_item=latest_item
    )


@app.route("/admin/dashboard")
@app.route("/admin/dashboard.html")
def admin_dashboard():

    if "user_id" not in session:
        return redirect("/")

    if session.get("role") != "admin":
        flash("Access Denied")
        return redirect("/student/dashboard.html")

    total_lost = LostItem.query.count()

    total_found = FoundItem.query.count()

    total_matches = LostItem.query.filter_by(status="Matched").count()

    total_students = User.query.filter_by(role="student").count()

    recent_reports = LostItem.query.order_by(
        LostItem.created_at.desc()
    ).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        total_lost=total_lost,
        total_found=total_found,
        total_matches=total_matches,
        total_students=total_students,
        recent_reports=recent_reports
    )

@app.route("/student/report_lost", methods=["GET", "POST"])
@app.route("/student/report_lost.html", methods=["GET", "POST"])
def report_lost():

    if "user_id" not in session:
        return redirect("/")

    from datetime import date
    if request.method == "GET":
        return render_template(
            "student/report_lost.html",
            today=date.today().strftime("%Y-%m-%d")
        )

    image = request.files.get("image")

    # Default values if no image is uploaded
    filename = None
    embedding_json = None

    if image and image.filename != "":

        filename = secure_filename(image.filename)

        upload_folder = os.path.join(
            app.static_folder,
            "assets",
            "uploads"
        )

        os.makedirs(upload_folder, exist_ok=True)

        image_path = os.path.join(
            upload_folder,
            filename
        )

        image.save(image_path)

        embedding = get_image_embedding(image_path)

        embedding_json = json.dumps(
            embedding.tolist()
        )

    lost = LostItem(

        user_id=session["user_id"],

        item_name=request.form["item_name"],

        category=request.form["category"],

        description=request.form["description"],

        location=request.form["location"],

        lost_date=datetime.strptime(
            request.form["lost_date"],
            "%Y-%m-%d"
        ).date(),

        image=filename,

        image_embedding=embedding_json

    )

    db.session.add(lost)
    db.session.commit()

    flash("Lost Item Report Submitted Successfully!")

    return redirect("/student/dashboard.html")

@app.route("/student/report_found", methods=["GET", "POST"])
@app.route("/student/report_found.html", methods=["GET", "POST"])
def report_found():

    if "user_id" not in session:
        return redirect("/")

    from datetime import datetime, date

    if request.method == "GET":
        return render_template(
            "student/report_found.html",
            today=date.today().strftime("%Y-%m-%d")
        )

    image = request.files.get("image")

    filename = None
    embedding_json = None

    if image and image.filename != "":

        filename = secure_filename(image.filename)

        upload_folder = os.path.join(
            app.static_folder,
            "assets",
            "uploads"
        )

        os.makedirs(upload_folder, exist_ok=True)

        image_path = os.path.join(upload_folder, filename)

        image.save(image_path)

        embedding = get_image_embedding(image_path)

        embedding_json = json.dumps(embedding.tolist())

    # Save the found item
    found = FoundItem(
        user_id=session["user_id"],
        item_name=request.form["item_name"],
        category=request.form["category"],
        description=request.form["description"],
        location=request.form["location"],
        found_date=datetime.strptime(
            request.form["found_date"],
            "%Y-%m-%d"
        ).date(),
        image=filename,
        image_embedding=embedding_json
    )

    db.session.add(found)
    db.session.commit()

    # ---------------- AI Matching ---------------- #

    if found.image_embedding:

        best_match = None
        best_score = 0

        found_embedding = np.array(json.loads(found.image_embedding))

        lost_items = LostItem.query.filter_by(status="Pending").all()

        for lost in lost_items:

            print("-------------------------------------")
            print("Checking Lost ID:", lost.lost_id)
            print("Item:", lost.item_name)

            if lost.image_embedding:
                # AI Image Matching
                lost_embedding = np.array(json.loads(lost.image_embedding))

                score = cosine_similarity(
                    found_embedding,
                    lost_embedding
                )
            else:
                # Text-Based Matching
                score = 0

                # Category Match (40%)
                if found.category.lower() == lost.category.lower():
                    score += 0.40

                # Item Name Match (20%)
                if found.item_name.lower() == lost.item_name.lower():
                    score += 0.20

                # Location Match (20%)
                if found.location.lower() == lost.location.lower():
                    score += 0.20

                # Description Match (20%)
                found_words = set(found.description.lower().split())
                lost_words = set(lost.description.lower().split())

                common_words = found_words.intersection(lost_words)

                score += min(len(common_words) * 0.05, 0.20)

            print("Similarity Score:", score)

            if score > best_score:
                best_score = score
                best_match = lost

        print("Best Score:", best_score)
        print("Best Match:", best_match.item_name if best_match else "None")
        confidence = round(best_score * 100, 2)

        if best_match:

            # Decide whether it is Matched or Pending
            if confidence >= 50:
                match_status = "Matched"
                best_match.status = "Matched"
                found.status = "Matched"
            else:
                match_status = "Pending"

            match = Match(
                lost_id=best_match.lost_id,
                found_id=found.found_id,
                confidence=confidence,
                status=match_status
            )

            db.session.add(match)

            db.session.add(Notification(
                user_id=best_match.user_id,
                message=f"AI found a possible match ({confidence}%) for '{best_match.item_name}'."
            ))

            db.session.add(Notification(
                user_id=found.user_id,
                message=f"Your found item matched a lost report ({confidence}%)."
            ))

            db.session.commit()
    # ------------------------------------------------ #

    flash("Found Item Submitted Successfully!")
    return redirect("/student/dashboard.html")

@app.route("/student/my_reports")
@app.route("/student/my_reports.html")
def my_reports():

    if "user_id" not in session:
        return redirect("/")

    lost_items = LostItem.query.filter_by(
        user_id=session["user_id"]
    ).all()

    found_items = FoundItem.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "student/my_reports.html",
        lost_items=lost_items,
        found_items=found_items
    )




@app.route("/student/profile")
@app.route("/student/profile.html")
def profile():

    if "user_id" not in session:
        return redirect("/")

    user = User.query.get(session["user_id"])

    return render_template(
        "student/profile.html",
        user=user
    )
@app.route("/student/view/lost/<int:lost_id>")
def view_lost_report(lost_id):

    if "user_id" not in session:
        return redirect("/")

    item = LostItem.query.get_or_404(lost_id)

    # Allow only the owner to view the report
    if item.user_id != session["user_id"]:
        flash("Access Denied")
        return redirect("/student/my_reports")

    return render_template(
        "student/view_report.html",
        item=item,
        report_type="Lost"
    )


@app.route("/student/view/found/<int:found_id>")
def view_found_report(found_id):

    if "user_id" not in session:
        return redirect("/")

    item = FoundItem.query.get_or_404(found_id)

    # Allow only the owner to view the report
    if item.user_id != session["user_id"]:
        flash("Access Denied")
        return redirect("/student/my_reports")

    return render_template(
        "student/view_report.html",
        item=item,
        report_type="Found"
    )
@app.route("/student/delete/lost/<int:lost_id>")
def delete_lost_report(lost_id):

    if "user_id" not in session:
        return redirect("/")

    item = LostItem.query.get_or_404(lost_id)

    if item.user_id != session["user_id"]:
        flash("Access Denied")
        return redirect("/student/my_reports")

    # Delete uploaded image
    if item.image:

        image_path = os.path.join(
            app.static_folder,
            "assets",
            "uploads",
            item.image
        )

        if os.path.exists(image_path):
            os.remove(image_path)

    # Delete related match first
    Match.query.filter_by(lost_id=item.lost_id).delete()

    db.session.delete(item)
    db.session.commit()

    flash("Lost report deleted successfully!")

    return redirect("/student/my_reports")
@app.route("/student/delete/found/<int:found_id>")
def delete_found_report(found_id):

    if "user_id" not in session:
        return redirect("/")

    item = FoundItem.query.get_or_404(found_id)

    if item.user_id != session["user_id"]:
        flash("Access Denied")
        return redirect("/student/my_reports")

    if item.image:

        image_path = os.path.join(
            app.static_folder,
            "assets",
            "uploads",
            item.image
        )

        if os.path.exists(image_path):
            os.remove(image_path)

    # Delete related match first
    Match.query.filter_by(found_id=item.found_id).delete()

    db.session.delete(item)
    db.session.commit()

    flash("Found report deleted successfully!")

    return redirect("/student/my_reports")

@app.route("/student/notifications")
@app.route("/student/notifications.html")
def notifications():

    if "user_id" not in session:
        return redirect("/")

    notifications = Notification.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        Notification.notification_id.desc()
    ).all()

    return render_template(
        "student/notifications.html",
        notifications=notifications
    )
@app.route("/student/claim/<int:lost_id>")
def claim_item(lost_id):

    if "user_id" not in session:
        return redirect("/")

    item = LostItem.query.get_or_404(lost_id)

    if item.user_id != session["user_id"]:
        flash("You can only claim your own lost items.")
        return redirect("/student/matched_items")

    # Allow claim only if item is matched
    if item.status != "Matched":
        flash("This item is not available for claim.")
        return redirect("/student/my_reports")

    # Check if the user has already submitted a claim
    existing_claim = Claim.query.filter_by(
        lost_id=lost_id,
        student_id=session["user_id"]
    ).first()

    if existing_claim:
        flash("You have already submitted a claim for this item.")
        return redirect("/student/my_reports")

    # Create claim
    claim = Claim(
        lost_id=lost_id,
        student_id=session["user_id"]
    )

    db.session.add(claim)

    # Notify the student
    notification = Notification(
        user_id=session["user_id"],
        message=f"Your claim request for '{item.item_name}' has been submitted successfully."
    )

    db.session.add(notification)

    db.session.commit()

    flash("Claim submitted successfully!")

    return redirect("/student/my_reports")
@app.route("/student/matched_items")
@app.route("/student/matched_items.html")
def matched_items():

    if "user_id" not in session:
        return redirect("/")

    matches = (
        db.session.query(Match)
        .join(LostItem, Match.lost_id == LostItem.lost_id)
        .join(FoundItem, Match.found_id == FoundItem.found_id)
        .filter(LostItem.user_id == session["user_id"])
        .all()
    )

    return render_template(
        "student/matched_items.html",
        matches=matches
    )
@app.route("/admin/matches")
@app.route("/admin/matches.html")
def admin_matches():

    if "user_id" not in session:
        return redirect("/")

    if session.get("role") != "admin":
        flash("Access Denied")
        return redirect("/student/dashboard")

    matched_items = (
        db.session.query(Match, LostItem, FoundItem)
        .join(LostItem, Match.lost_id == LostItem.lost_id)
        .join(FoundItem, Match.found_id == FoundItem.found_id)
        .order_by(Match.created_at.desc())
        .all()
    )

    return render_template(
        "admin/matches.html",
        matched_items=matched_items
    )
@app.route("/admin/claims")
def admin_claims():

    claims = db.session.query(
        Claim,
        LostItem,
        User
    ).join(
        LostItem, Claim.lost_id == LostItem.lost_id
    ).join(
        User, Claim.student_id == User.user_id
    ).all()

    return render_template(
        "admin/claims.html",
        claims=claims
    )
@app.route("/admin/approve_claim/<int:claim_id>")
def approve_claim(claim_id):

    claim = Claim.query.get_or_404(claim_id)

    claim.status = "Approved"

    lost_item = LostItem.query.get(claim.lost_id)

    lost_item.status = "Returned"

    notification = Notification(
        user_id=claim.student_id,
        message=f"Your claim for '{lost_item.item_name}' has been approved. Please collect your item."
    )

    db.session.add(notification)

    db.session.commit()

    return redirect("/admin/claims")
@app.route("/admin/reject_claim/<int:claim_id>")
def reject_claim(claim_id):

    claim = Claim.query.get_or_404(claim_id)

    claim.status = "Rejected"

    notification = Notification(
        user_id=claim.student_id,
        message="Your claim request has been rejected."
    )

    db.session.add(notification)

    db.session.commit()

    return redirect("/admin/claims")


@app.route("/admin/delete_lost/<int:lost_id>")
def admin_delete_lost(lost_id):

    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/")

    item = LostItem.query.get_or_404(lost_id)

    if item.image:
        image_path = os.path.join(
            app.static_folder,
            "assets",
            "uploads",
            item.image
        )

        if os.path.exists(image_path):
            os.remove(image_path)

    # Delete related match first
    Match.query.filter_by(lost_id=item.lost_id).delete()

    db.session.delete(item)
    db.session.commit()

    flash("Lost report deleted successfully!")

    return redirect("/admin/manage_reports")
@app.route("/admin/delete_found/<int:found_id>")
def admin_delete_found(found_id):

    if "user_id" not in session or session.get("role") != "admin":
        return redirect("/")

    item = FoundItem.query.get_or_404(found_id)

    if item.image:
        image_path = os.path.join(
            app.static_folder,
            "assets",
            "uploads",
            item.image
        )

        if os.path.exists(image_path):
            os.remove(image_path)

    # Delete related match first
    Match.query.filter_by(found_id=item.found_id).delete()

    db.session.delete(item)
    db.session.commit()

    flash("Found report deleted successfully!")

    return redirect("/admin/manage_reports")
@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully!")

    return redirect("/")
@app.route("/admin/manage_reports")
def admin_manage_reports():

    if "user_id" not in session:
        return redirect("/")

    if session.get("role") != "admin":
        flash("Access Denied")
        return redirect("/student/dashboard")

    lost_reports = LostItem.query.order_by(
        LostItem.created_at.desc()
    ).all()

    found_reports = FoundItem.query.order_by(
        FoundItem.created_at.desc()
    ).all()

    return render_template(
        "admin/manage_reports.html",
        lost_reports=lost_reports,
        found_reports=found_reports
    )
@app.route("/admin/manage_users")
def admin_manage_users():

    if "user_id" not in session:
        return redirect("/")

    if session.get("role") != "admin":
        flash("Access Denied")
        return redirect("/student/dashboard")

    users = User.query.filter_by(role="student").all()

    return render_template(
        "admin/manage_users.html",
        users=users
    )
@app.route("/admin/notify_owner/<int:match_id>")
def notify_owner(match_id):

    if "user_id" not in session:
        return redirect("/")

    if session.get("role") != "admin":
        flash("Access Denied")
        return redirect("/student/dashboard")

    # Find the match
    match = Match.query.get_or_404(match_id)

    # Find the lost item
    lost_item = LostItem.query.get(match.lost_id)

    # Send notification to the owner
    notification = Notification(
        user_id=lost_item.user_id,
        message=(
            f"Your lost item '{lost_item.item_name}' may have been found.\n"
            f"AI Confidence: {match.confidence}%.\n"
            f"Please visit the Lost & Found Office to verify your item."
        )
    )

    db.session.add(notification)

    # Update match status
    match.status = "Owner Notified"

    db.session.commit()

    flash("Owner notified successfully!")

    return redirect("/admin/matches.html")

@app.route("/admin/return_item/<int:match_id>")
def return_item(match_id):

    if "user_id" not in session:
        return redirect("/")

    if session.get("role") != "admin":
        flash("Access Denied")
        return redirect("/student/dashboard")

    # Find the match
    match = Match.query.get_or_404(match_id)

    # Find lost item
    lost_item = LostItem.query.get(match.lost_id)

    # Find found item
    found_item = FoundItem.query.get(match.found_id)

    # Update statuses
    match.status = "Returned"

    if lost_item:
        lost_item.status = "Returned"

    if found_item:
        found_item.status = "Returned"

    # Create notification for the owner
    notification = Notification(
        user_id=lost_item.user_id,
        message=f"Your lost item '{lost_item.item_name}' has been returned successfully."
    )

    db.session.add(notification)

    db.session.commit()

    flash("Item returned successfully!")

    return redirect("/admin/matches")
@app.route("/admin/settings")
def admin_settings():

    if "user_id" not in session:
        return redirect("/")

    if session.get("role") != "admin":
        flash("Access Denied")
        return redirect("/student/dashboard")

    return render_template("admin/settings.html")
@app.route("/admin/delete_user/<int:user_id>")
def delete_user(user_id):

    if "user_id" not in session:
        return redirect("/")

    if session.get("role") != "admin":
        flash("Access Denied")
        return redirect("/student/dashboard")

    user = User.query.get_or_404(user_id)

    # Don't allow deleting admins
    if user.role == "admin":
        flash("Admin cannot be deleted!")
        return redirect("/admin/manage_users")

    db.session.delete(user)
    db.session.commit()

    flash("Student deleted successfully!")

    return redirect("/admin/manage_users")
@app.route("/admin/edit_user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):

    if "user_id" not in session:
        return redirect("/")

    if session.get("role") != "admin":
        flash("Access Denied")
        return redirect("/student/dashboard")

    user = User.query.get_or_404(user_id)

    if request.method == "POST":

        user.roll_no = request.form["roll_no"]
        user.name = request.form["name"]
        user.email = request.form["email"]
        user.department = request.form["department"]
        user.year = int(request.form["year"])
        user.phone = request.form["phone"]

        db.session.commit()

        flash("Student updated successfully!")

        return redirect("/admin/manage_users")

    return render_template(
        "admin/edit_user.html",
        user=user
    )
@app.route("/admin/add_user", methods=["GET", "POST"])
def add_user():

    if "user_id" not in session:
        return redirect("/")

    if session.get("role") != "admin":
        flash("Access Denied")
        return redirect("/student/dashboard")

    if request.method == "POST":
        existing_roll = User.query.filter_by(
            roll_no=request.form["roll_no"]
        ).first()

        if existing_roll:
            flash("Roll Number already exists!")
            return redirect("/admin/add_user")

        existing_email = User.query.filter_by(
            email=request.form["email"]
        ).first()

        if existing_email:
            flash("Email already exists!")
            return redirect("/admin/add_user")

        student = User(
            roll_no=request.form["roll_no"],
            name=request.form["name"],
            email=request.form["email"],
            password=request.form["password"],
            department=request.form["department"],
            year=int(request.form["year"]),
            phone=request.form["phone"],
            role="student",
            created_at=datetime.now()
        )

        db.session.add(student)
        db.session.commit()

        flash("Student added successfully!")

        return redirect("/admin/manage_users")

    return render_template("admin/add_user.html")
@app.route("/student/lost_items")
def student_lost_items():

    if "user_id" not in session:
        return redirect("/")

    lost_items = LostItem.query.order_by(
        LostItem.created_at.desc()
    ).all()

    return render_template(
        "student/lost_items.html",
        lost_items=lost_items
    )
@app.route("/student/found_items")
def student_found_items():

    if "user_id" not in session:
        return redirect("/")

    found_items = FoundItem.query.order_by(
        FoundItem.created_at.desc()
    ).all()

    return render_template(
        "student/found_items.html",
        found_items=found_items
    )
if __name__ == "__main__":
    app.run(debug=True)