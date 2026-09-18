from database.database import db
from datetime import datetime

class LostItem(db.Model):

    __tablename__ = "lost_items"

    lost_id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    user = db.relationship("User", backref="lost_items")

    item_name = db.Column(db.String(100), nullable=False)

    category = db.Column(db.String(50))

    description = db.Column(db.Text)

    location = db.Column(db.String(100))

    lost_date = db.Column(db.Date)

    image = db.Column(db.String(255))

    image_embedding = db.Column(db.Text)

    status = db.Column(
        db.String(20),
        default="Pending"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )