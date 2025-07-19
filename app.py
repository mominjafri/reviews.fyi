from flask import Flask, render_template, request, redirect, url_for
from sheets_util import add_review_to_sheet

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/write", methods=["GET", "POST"])
def write():
    if request.method == "POST":
        try:
            # Get form data
            data = {
                "first_name": request.form.get("first_name"),
                "last_name": request.form.get("last_name"),
                "email": request.form.get("email"),
                "company": request.form.get("company"),
                "linkedin": request.form.get("linkedin", ""),
                "rating": request.form.get("overall_rating"),
                "fairness": request.form.get("fairness"),
                "communication": request.form.get("communication"),
                "technical": request.form.get("technical"),
                "review": request.form.get("review")
            }

            # Validate required fields
            if not all(data.values()):
                return "Missing required fields", 400

            # Write to sheet
            success = add_review_to_sheet(*data.values())
            if not success:
                return "Failed to save review", 500
                
            return redirect(url_for("thank_you"))
            
        except Exception as e:
            print(f"Error: {str(e)}")
            return f"Internal Server Error: {str(e)}", 500

    return render_template("write.html")

@app.route("/thank-you")
def thank_you():
    return render_template("submit.html")  # Changed from text response to template

if __name__ == "__main__":
    app.run(debug=True)
