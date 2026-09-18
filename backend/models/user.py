from database.database import db

class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(50))
    year = db.Column(db.Integer)
    phone = db.Column(db.String(15))
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime)

    def __repr__(self):
        return f"<User {self.email}>"