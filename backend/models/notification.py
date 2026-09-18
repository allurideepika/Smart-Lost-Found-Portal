from database.database import db
from datetime import datetime

class Notification(db.Model):

    __tablename__ = "notifications"

    notification_id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    message = db.Column(db.Text, nullable=False)

    is_read = db.Column(db.Boolean, default=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )