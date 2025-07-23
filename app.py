from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # Initialize SQLAlchemy here (no app passed)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reviews.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db with app
db.init_app(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/write-existing')
def existing():
    return render_template("write-existing.html")

@app.route('/write', methods=['GET', 'POST'])
def write():
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
                linkedin=request.form.get('linkedin')
            )
            db.session.add(employee)
            db.session.commit()

        # Create review
        review = Review(
            employee_id=employee.id,
            overall_rating=request.form['overall_rating'],
            fairness_rating=request.form['fairness'],
            communication_rating=request.form['communication'],
            technical_rating=request.form['technical'],
            leadership_rating=request.form['leadership'],
            review_text=request.form['review']
        )
        db.session.add(review)
        db.session.commit()

        return redirect(url_for('employee', employee_id=employee.id))
    
    return render_template('write.html')

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
        company = request.form.get('company', '').strip()
        employee_name = request.form.get('employee', '').strip()
        location = request.form.get('location', '').strip()
        
        # Perform the search
        results = search_employees(company, employee_name, location)
        return render_template('search.html', results=results, 
                             company=company, employee=employee_name, location=location)
    
    # GET request - show empty form
    return render_template('search.html', results=None)

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


@app.route("/thank-you")
def thank_you():
    return render_template("submit.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)