from extensions import db
from datetime import datetime

class Employee(db.Model):
    __tablename__ = 'employee'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    linkedin = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    reviews = db.relationship('Review', backref='employee', lazy=True)

class Review(db.Model):
    __tablename__ = 'review'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    years_experience = db.Column(db.String(50))
    overall_rating = db.Column(db.Integer, nullable=False)
    fairness_rating = db.Column(db.Integer)
    communication_rating = db.Column(db.Integer)
    technical_rating = db.Column(db.Integer)
    leadership_rating = db.Column(db.Integer)
    review_text = db.Column(db.Text, nullable=False)
    
    # Verification fields
    verification_email = db.Column(db.String(100))
    verification_linkedin = db.Column(db.String(200))
    verification_token = db.Column(db.String(100))  # For email verification if needed
    is_verified = db.Column(db.Boolean, default=False)
    
    # Status fields
    approved = db.Column(db.Boolean)  # None=pending, True=approved, False=rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)
    
    # Add constraint to require at least one verification method
    __table_args__ = (
        db.CheckConstraint(
            'verification_email IS NOT NULL OR verification_linkedin IS NOT NULL',
            name='at_least_one_verification_method'
        ),
    )