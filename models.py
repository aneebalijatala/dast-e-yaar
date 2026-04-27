from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# 👤 ADMIN / VERIFIER
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(200))
    role = db.Column(db.String(20))  # admin / verifier

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# 📄 CASE (FULL FORM VERSION)
class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # 🧍 Personal Info
    name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    dob = db.Column(db.String(20))
    cnic = db.Column(db.String(20))
    religion = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    gender = db.Column(db.String(10))

    # 👨‍👩‍👧 Family Info
    marital_status = db.Column(db.String(20))
    dependents = db.Column(db.String(50))
    family_members = db.Column(db.String(50))
    income = db.Column(db.String(50))
    expenses = db.Column(db.String(50))

    # 📄 Case Info
    case_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    amount = db.Column(db.String(50))
    previous_help = db.Column(db.String(10))

    # 🏦 Account Info
    account_type = db.Column(db.String(50))
    account_number = db.Column(db.String(50))
    account_holder = db.Column(db.String(100))
    relation = db.Column(db.String(50))

    # ⚙️ Admin Control
    status = db.Column(db.String(20), default="Pending")
    comments = db.Column(db.Text)


# 📁 DOCUMENTS
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))

    case_id = db.Column(db.Integer, db.ForeignKey('case.id'))