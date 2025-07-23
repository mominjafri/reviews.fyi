from flask import Flask, render_template, request, redirect, url_for
from sheets_util import add_review_to_sheet
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/write", methods=["GET", "POST"])
def write():
    if request.method == "POST":
        try:
            # Get all form data with proper field names
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            email = request.form["email"]
            company = request.form["company"]
            linkedin = request.form.get("linkedin", "")  # Optional
            
            # Rating fields - must match your HTML name attributes
            rating = request.form["overall_rating"]
            fairness = request.form["fairness"]
            communication = request.form["communication"]
            technical = request.form["technical"]
            leadership = request.form["leadership"]
            
            review = request.form["review"]
            
            # Print received data for debugging
            print("Received data:", {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "company": company,
                "linkedin": linkedin,
                "ratings": {
                    "overall": rating,
                    "fairness": fairness,
                    "communication": communication,
                    "technical": technical,
                    "leadershp": leadership
                },
                "review": review
            })
            
            # Save to sheet
            if add_review_to_sheet(
                first_name, last_name, email, company, linkedin,
                rating, fairness, communication, technical, leadership, review
            ):
                return redirect(url_for("thank_you"))
            else:
                return "Failed to save review", 500
                
        except KeyError as e:
            print(f"Missing field: {e}")
            return f"Missing required field: {e}", 400
        except Exception as e:
            print(f"Error: {str(e)}")
            return f"Server error: {str(e)}", 500
    
    # GET request - show the form
    return render_template("write.html")

@app.route("/search")
def search():
    return render_template("search.html")

@app.route("/thank-you")
def thank_you():
    return render_template("submit.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)