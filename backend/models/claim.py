from database.database import db
from datetime import datetime

class Claim(db.Model):

    __tablename__ = "claims"

    claim_id = db.Column(db.Integer, primary_key=True)

    lost_id = db.Column(
        db.Integer,
        db.ForeignKey("lost_items.lost_id"),
        nullable=False
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="Pending"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )