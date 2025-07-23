# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    linkedin = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to reviews
    reviews = db.relationship('Review', backref='employee', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Employee {self.first_name} {self.last_name} ({self.company})>'

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    overall_rating = db.Column(db.Integer, nullable=False)
    fairness_rating = db.Column(db.Integer)
    communication_rating = db.Column(db.Integer)
    respect_rating = db.Column(db.Integer)
    review_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Review for Employee {self.employee_id}>'