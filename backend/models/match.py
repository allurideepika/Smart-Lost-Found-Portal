from database.database import db
from datetime import datetime


class Match(db.Model):

    __tablename__ = "matches"

    match_id = db.Column(db.Integer, primary_key=True)

    lost_id = db.Column(
        db.Integer,
        db.ForeignKey("lost_items.lost_id"),
        nullable=False
    )

    found_id = db.Column(
        db.Integer,
        db.ForeignKey("found_items.found_id"),
        nullable=False
    )

    confidence = db.Column(
        db.Float,
        default=100.0
    )

    status = db.Column(
        db.String(20),
        default="Pending"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    lost_item = db.relationship("LostItem", backref="matches")
    found_item = db.relationship("FoundItem", backref="matches")