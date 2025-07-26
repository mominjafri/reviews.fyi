from extensions import db
from datetime import datetime

class Employee(db.Model):
    __tablename__ = 'employee'  # Singular to match your DB
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    linkedin = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    reviews = db.relationship('Review', backref='employee', lazy=True)

class Review(db.Model):
    __tablename__ = 'review'  # Singular to match your DB
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)  # Note singular
    years_experience = db.Column(db.String(50))
    overall_rating = db.Column(db.Integer, nullable=False)
    fairness_rating = db.Column(db.Integer)
    communication_rating = db.Column(db.Integer)
    technical_rating = db.Column(db.Integer)
    leadership_rating = db.Column(db.Integer)
    review_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)
    