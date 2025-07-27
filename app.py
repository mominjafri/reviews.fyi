from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from extensions import db
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
    raise ValueError("Use PostgreSQL, not SQLite!")

# Initialize db with app
db.init_app(app)

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@app.context_processor
def inject_dark_mode():
    dark_mode = session.get('dark_mode', False)
    return {'dark_mode': dark_mode}

# Dark mode toggle route
@app.route('/toggle-dark-mode')
def toggle_dark_mode():
    session['dark_mode'] = not session.get('dark_mode', False)
    return redirect(request.referrer or url_for('home'))

@app.route("/")
def home():
    return render_template("index.html")

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

        # Create review
        review = Review(
            employee_id=employee.id,
            years_experience=request.form['years_experience'],
            overall_rating=request.form['overall_rating'],
            fairness_rating=request.form.get('fairness', 0),  # Default to 0 if not provided
            communication_rating=request.form.get('communication', 0),
            technical_rating=request.form.get('technical', 0),
            leadership_rating=request.form.get('leadership', 0),
            review_text=request.form['review']
        )
        db.session.add(review)
        db.session.commit()

        return redirect(url_for('employee', employee_id=employee.id))
    
    # For GET requests, render the form with pre-filled values if available
    return render_template('write.html',
                         first_name=first_name,
                         last_name=last_name,
                         company=company,
                         location=location,
                         linkedin=linkedin)

@app.route('/employee/<int:employee_id>')
def employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    reviews = Review.query.filter_by(employee_id=employee_id).order_by(Review.created_at.desc()).all()
    
    # Calculate average ratings
    avg_ratings = {
        'overall': db.session.query(db.func.avg(Review.overall_rating)).filter_by(employee_id=employee_id).scalar() or 0,
        'fairness': db.session.query(db.func.avg(Review.fairness_rating)).filter_by(employee_id=employee_id).scalar() or 0,
        'communication': db.session.query(db.func.avg(Review.communication_rating)).filter_by(employee_id=employee_id).scalar() or 0,
        'technical': db.session.query(db.func.avg(Review.technical_rating)).filter_by(employee_id=employee_id).scalar() or 0,
        'leadership': db.session.query(db.func.avg(Review.leadership_rating)).filter_by(employee_id=employee_id).scalar() or 0
    }
    
    return render_template('employee.html', 
                         employee=employee, 
                         reviews=reviews,
                         avg_ratings=avg_ratings)
# Add these imports at the top
from models import db, Employee, Review
from sqlalchemy import or_

# Update the search route
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        company = request.form.get('company', '').strip()
        location = request.form.get('location', '').strip()
        
        # Search for employees with similar details
        employees = search_employees(
            company=company,
            name=f"{first_name} {last_name}",
            location=location
        )
        
        if employees:
            # Found matching employees - show results
            return render_template('search.html', 
                                employees=employees,
                                search_completed=True,
                                first_name=first_name,
                                last_name=last_name,
                                company=company,
                                location=location)
        else:
            # No matches found - show "not found" message with option to write review
            return render_template('search.html',
                                no_results=True,
                                first_name=first_name,
                                last_name=last_name,
                                company=company,
                                location=location,
                                search_completed=True)
    
    # For GET requests, show empty search form
    return render_template('search.html', search_completed=False)

# Add this helper function
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


@app.route('/submit-review', methods=['POST'])
def submit_review():
    # Get form data
    data = request.form
    
    # Create or find employee
    employee = Employee.query.filter_by(
        first_name=data['first_name'],
        last_name=data['last_name'],
        company=data['company']
    ).first()
    
    if not employee:
        employee = Employee(
            first_name=data['first_name'],
            last_name=data['last_name'],
            company=data['company'],
            location=data.get('location')
        )
        db.session.add(employee)
    
    # Create review
    review = Review(
        employee_id=employee.id,
        years_experience=data['years_experience'],
        overall_rating=data['overall_rating'],
        fairness_rating=data.get('fairness'),
        communication_rating=data.get('communication'),
        technical_rating=data.get('technical'),
        leadership_rating=data.get('leadership'),
        review_text=data['review']
    )
    db.session.add(review)
    db.session.commit()
    
    return redirect(url_for('employee', employee_id=employee.id))


@app.route('/vote/<int:review_id>/<vote_type>', methods=['POST'])
def vote(review_id, vote_type):
    review = Review.query.get_or_404(review_id)
    if vote_type == 'up':
        review.upvotes += 1
    elif vote_type == 'down':
        review.downvotes += 1
    db.session.commit()
    return redirect(url_for('employee', employee_id=review.employee_id))


@app.route("/thank-you")
def thank_you():
    return render_template("submit.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)