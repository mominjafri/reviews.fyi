from flask import Flask, render_template, request, redirect, url_for, abort, session, flash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from extensions import db
from models import Employee, Review
from sqlalchemy import or_, func
import os
import secrets
from datetime import datetime

app = Flask(__name__)

database_url = os.getenv('DATABASE_URL')

if database_url:
    # Handle different database providers
    if 'render.com' in database_url:
        # Render PostgreSQL - add SSL requirement
        if 'sslmode=require' not in database_url:
            if '?' in database_url:
                database_url += '&sslmode=require'
            else:
                database_url += '?sslmode=require'
    elif 'heroku.com' in database_url:
        # Heroku PostgreSQL - already includes SSL
        pass
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Local development fallback
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))

db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['ADMIN_KEY'] = secrets.token_urlsafe(32)  # Random admin key

if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
    raise ValueError("Use PostgreSQL, not SQLite!")

# Initialize db with app
db.init_app(app)
migrate = Migrate(app, db)

# Print admin key for initial setup (remove in production)
print(f"Admin Key: {app.config['ADMIN_KEY']}")

@app.route("/")
def home():
    # Get real metrics from database
    total_bosses = db.session.query(func.count(Employee.id)).scalar() or 0
    total_reviews = db.session.query(func.count(Review.id)).filter(Review.approved.is_(True)).scalar() or 0
    total_companies = db.session.query(func.count(func.distinct(Employee.company))).scalar() or 0
    
    # Get recently reviewed bosses (last 3 approved reviews)
    recent_bosses = db.session.query(Employee, Review)\
        .join(Review, Employee.id == Review.employee_id)\
        .filter(Review.approved.is_(True))\
        .order_by(Review.created_at.desc())\
        .limit(3)\
        .all()
    
    return render_template("index.html",
                         total_bosses=total_bosses,
                         total_reviews=total_reviews,
                         total_companies=total_companies,
                         recent_bosses=recent_bosses)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/write-existing/<int:employee_id>')
def write_existing(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    return render_template("write-existing.html", employee=employee)

@app.route('/write', methods=['GET', 'POST'])
def write():
    # Get search parameters if they exist (for pre-filling the form)
    first_name = request.args.get('first_name', '')
    last_name = request.args.get('last_name', '')
    company = request.args.get('company', '')
    location = request.args.get('location', '')
    linkedin = request.args.get('linkedin', '')

    if request.method == 'POST':
        # Create or find employee
        employee = Employee.query.filter_by(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            company=request.form['company']
        ).first()
        
        if not employee:
            employee = Employee(
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                company=request.form['company'],
                location=request.form.get('location'),
                linkedin=request.form.get('linkedin')
            )
            db.session.add(employee)
            db.session.commit()

        # Create review (marked as pending approval)
        review = Review(
            employee_id=employee.id,
            years_experience=request.form['years_experience'],
            overall_rating=request.form['overall_rating'],
            fairness_rating=request.form.get('fairness', 0),
            communication_rating=request.form.get('communication', 0),
            technical_rating=request.form.get('technical', 0),
            leadership_rating=request.form.get('leadership', 0),
            review_text=request.form['review'],
            approved=None
        )
        db.session.add(review)
        db.session.commit()

        return redirect(url_for('employee', employee_id=employee.id))
    
    return render_template('write.html',
                         first_name=first_name,
                         last_name=last_name,
                         company=company,
                         location=location,
                         linkedin=linkedin)

@app.route('/employee/<int:employee_id>')
def employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    reviews = Review.query\
        .filter_by(employee_id=employee_id)\
        .filter(Review.approved.is_(True))\
        .order_by(Review.created_at.desc())\
        .all()
    
    # Calculate average ratings only for approved reviews
    avg_ratings = {
        'overall': db.session.query(func.avg(Review.overall_rating))
            .filter_by(employee_id=employee_id)
            .filter(Review.approved.is_(True))
            .scalar() or 0,
        'fairness': db.session.query(func.avg(Review.fairness_rating))
            .filter_by(employee_id=employee_id)
            .filter(Review.approved.is_(True))
            .scalar() or 0,
        'communication': db.session.query(func.avg(Review.communication_rating))
            .filter_by(employee_id=employee_id)
            .filter(Review.approved.is_(True))
            .scalar() or 0,
        'technical': db.session.query(func.avg(Review.technical_rating))
            .filter_by(employee_id=employee_id)
            .filter(Review.approved.is_(True))
            .scalar() or 0,
        'leadership': db.session.query(func.avg(Review.leadership_rating))
            .filter_by(employee_id=employee_id)
            .filter(Review.approved.is_(True))
            .scalar() or 0
    }
    
    return render_template('employee.html', 
                         employee=employee, 
                         reviews=reviews,
                         avg_ratings=avg_ratings)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        company = request.form.get('company', '').strip()
        location = request.form.get('location', '').strip()
        
        employees = search_employees(
            company=company,
            name=f"{first_name} {last_name}",
            location=location
        )
        
        if employees:
            return render_template('search.html', 
                                employees=employees,
                                search_completed=True,
                                first_name=first_name,
                                last_name=last_name,
                                company=company,
                                location=location)
        else:
            return render_template('search.html',
                                no_results=True,
                                first_name=first_name,
                                last_name=last_name,
                                company=company,
                                location=location,
                                search_completed=True)
    
    return render_template('search.html', search_completed=False)

def search_employees(company=None, name=None, location=None):
    query = Employee.query
    
    if company:
        query = query.filter(Employee.company.ilike(f'%{company}%'))
    
    if name:
        name_parts = name.split()
        for part in name_parts:
            query = query.filter(
                or_(
                    Employee.first_name.ilike(f'%{part}%'),
                    Employee.last_name.ilike(f'%{part}%')
                )
            )
    
    if location:
        query = query.filter(Employee.location.ilike(f'%{location}%'))
    
    return query.order_by(Employee.last_name, Employee.first_name).limit(50).all()

@app.route('/submit_review', methods=['POST'])
def submit_review():
    try:
        # For new employee reviews
        if 'employee_id' not in request.form:
            # Create new employee record
            employee = Employee(
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                company=request.form['company'],
                location=request.form.get('location'),
                linkedin=request.form.get('linkedin')
            )
            db.session.add(employee)
            db.session.commit()
            employee_id = employee.id
        else:
            # Existing employee
            employee_id = request.form['employee_id']
        
        # Store in session for verification
        session['review_data'] = {
            'employee_id': employee_id,
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'company': request.form.get('company'),
            'years_experience': request.form.get('years_experience'),
            'overall_rating': request.form.get('overall_rating'),
            'fairness': request.form.get('fairness'),
            'communication': request.form.get('communication'),
            'technical': request.form.get('technical'),
            'leadership': request.form.get('leadership'),
            'review_text': request.form.get('review')
        }
        
        return redirect(url_for('verify'))
        
    except Exception as e:
        flash('Error processing your review', 'error')
        return redirect(request.referrer or url_for('write'))

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        try:
            # Get verification data
            email = request.form.get('email', '')
            linkedin = request.form.get('linkedin', '')
            
            # Get review data from session
            review_data = session.get('review_data')
            if not review_data:
                flash('Session expired or invalid. Please submit your review again.', 'error')
                return redirect(url_for('write'))
            
            # Create and save review with correct column names
            new_review = Review(
                employee_id=review_data['employee_id'],
                years_experience=review_data['years_experience'],
                overall_rating=review_data['overall_rating'],
                fairness_rating=review_data.get('fairness', 0),
                communication_rating=review_data.get('communication', 0),
                technical_rating=review_data.get('technical', 0),
                leadership_rating=review_data.get('leadership', 0),
                review_text=review_data['review_text'],
                verification_email=email,
                verification_linkedin=linkedin,
                approved=None  # Pending approval
            )
            
            db.session.add(new_review)
            db.session.commit()
            
            # Clear session and redirect to thank you page
            session.pop('review_data', None)
            flash('Your review has been submitted for approval!', 'success')
            return redirect(url_for('thank_you'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error in verify route: {str(e)}")
            flash('Error saving your review. Please try again.', 'error')
            return redirect(url_for('verify'))
    
    # GET request - show verification form
    if 'review_data' not in session:
        flash('No review data found. Please submit a review first.', 'error')
        return redirect(url_for('write'))
    
    return render_template('verify.html')

@app.route('/vote/<int:review_id>/<vote_type>', methods=['POST'])
def vote(review_id, vote_type):
    review = Review.query.get_or_404(review_id)
    if vote_type == 'up':
        review.upvotes += 1
    elif vote_type == 'down':
        review.downvotes += 1
    db.session.commit()
    return redirect(url_for('employee', employee_id=review.employee_id))

@app.route('/top-rated')
def top_rated():
    # Get top rated employees (minimum 5 approved reviews)
    top_leaders = db.session.query(
        Employee,
        func.avg(Review.overall_rating).label('avg_rating'),
        func.count(Review.id).label('review_count')
    ).join(Review, Employee.id == Review.employee_id)\
     .filter(Review.approved.is_(True))\
     .group_by(Employee.id)\
     .having(func.count(Review.id) >= 5)\
     .order_by(func.avg(Review.overall_rating).desc())\
     .limit(12)\
     .all()

    leaders_data = []
    for employee, avg_rating, review_count in top_leaders:
        leaders_data.append({
            'id': employee.id,
            'first_name': employee.first_name,
            'last_name': employee.last_name,
            'company': employee.company,
            'avg_rating': float(avg_rating) if avg_rating else 0.0,
            'review_count': review_count
        })

    top_rated_count = db.session.query(Employee)\
        .join(Review)\
        .filter(Review.approved.is_(True))\
        .group_by(Employee.id)\
        .having(func.count(Review.id) >= 5)\
        .count()
    
    avg_rating = db.session.query(func.avg(Review.overall_rating))\
        .filter(Review.approved.is_(True))\
        .scalar() or 0
    reviewer_count = db.session.query(func.count(func.distinct(Review.id)))\
        .filter(Review.approved.is_(True))\
        .scalar()
    company_count = db.session.query(func.count(func.distinct(Employee.company))).scalar()

    return render_template("top-rated.html",
                         top_leaders=leaders_data,
                         top_rated_count=top_rated_count,
                         avg_rating=round(float(avg_rating), 1),
                         reviewer_count=reviewer_count,
                         company_count=company_count)

@app.route('/companies')
def companies():
    companies = db.session.query(
        Employee.company,
        func.count(Review.id).label('review_count'),
        func.max(Employee.location).label('location')
    ).join(Review, Employee.id == Review.employee_id)\
     .filter(Review.approved.is_(True))\
     .group_by(Employee.company)\
     .order_by(func.count(Review.id).desc())\
     .all()

    total_companies = db.session.query(func.count(func.distinct(Employee.company))).scalar()
    total_leaders = db.session.query(func.count(func.distinct(Employee.id))).scalar()
    
    return render_template('companies.html', 
                         companies=companies,
                         total_companies=total_companies,
                         total_leaders=total_leaders)

# Admin routes
@app.route('/admin/reviews', methods=['GET', 'POST'])
def admin_review_auth():
    if request.method == 'POST':
        submitted_key = request.form.get('admin_key')
        if submitted_key == app.config['ADMIN_KEY']:
            session['admin_authenticated'] = True
            return redirect(url_for('admin_review_dashboard'))
        else:
            flash('Invalid admin key', 'error')
            return redirect(url_for('admin_review_auth'))
    
    return render_template('admin/auth.html')

@app.route('/admin/reviews/dashboard')
def admin_review_dashboard():
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_review_auth'))
    
    pending_reviews = db.session.query(Review, Employee)\
        .join(Employee, Review.employee_id == Employee.id)\
        .filter(Review.approved.is_(None))\
        .order_by(Review.created_at.desc())\
        .all()
    
    return render_template('admin/dashboard.html', pending_reviews=pending_reviews)

@app.route('/admin/reviews/action/<int:review_id>', methods=['POST'])
def admin_review_action(review_id):
    if not session.get('admin_authenticated'):
        abort(403)
    
    review = Review.query.get_or_404(review_id)
    action = request.form.get('action')
    
    if action == 'approve':
        review.approved = True
        db.session.commit()
        flash('Review approved and published', 'success')
    elif action == 'reject':
        review.approved = False
        db.session.commit()
        flash('Review rejected', 'info')
    
    return redirect(url_for('admin_review_dashboard'))

@app.route('/submit_verification', methods=['POST'])
def submit_verification():
    try:
        # Get verification data
        email = request.form.get('email', '')
        linkedin = request.form.get('linkedin', '')
        
        # Get review data from session
        review_data = session.get('review_data')
        if not review_data:
            flash('Your review session has expired', 'error')
            return redirect(url_for('write'))
        
        # Save to database (example - adjust to your model)
        new_review = Review(
            employee_id=review_data['employee_id'],
            first_name=review_data['first_name'],  # Only if you have these columns in Review model
            last_name=review_data['last_name'],    # Otherwise remove these
            company=review_data['company'],        # They might belong only in Employee
            years_experience=review_data['years_experience'],
            overall_rating=review_data['overall_rating'],
            fairness_rating=review_data.get('fairness', 0),
            communication_rating=review_data.get('communication', 0),
            technical_rating=review_data.get('technical', 0),
            leadership_rating=review_data.get('leadership', 0),
            review_text=review_data['review_text'],
            verification_email=email,
            verification_linkedin=linkedin,
            approved=None  # Changed from status='pending' to match your model's approved column
        )
        
        db.session.add(new_review)
        db.session.commit()
        
        # Clear session
        session.pop('review_data', None)
        
        # Redirect to thank you page
        return redirect(url_for('thank_you'))
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while submitting your review', 'error')
        return redirect(url_for('verify'))


@app.route("/thank-you")
def thank_you():
    employee_id = request.args.get('employee_id')
    return render_template("submit.html", employee_id=employee_id)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)