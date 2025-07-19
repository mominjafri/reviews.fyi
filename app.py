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
            # Get form data - LinkedIn is optional (default empty string)
            data = {
                "first_name": request.form["first_name"],  # Required fields
                "last_name": request.form["last_name"],
                "email": request.form["email"],
                "company": request.form["company"],
                "linkedin": request.form.get("linkedin", ""),  # Optional
                "rating": request.form["overall_rating"],
                "fairness": request.form["fairness"],
                "communication": request.form["communication"],
                "technical": request.form["technical"],
                "review": request.form["review"]
            }

            # Debug print to verify data
            print("Form data received:", data)

            # Write to sheet
            success = add_review_to_sheet(
                data["first_name"],
                data["last_name"],
                data["email"],
                data["company"],
                data["linkedin"],  # Will be empty string if not provided
                data["rating"],
                data["fairness"],
                data["communication"],
                data["technical"],
                data["review"]
            )

            success = add_review_to_sheet(
                data["first_name"],
                data["last_name"],
                data["email"],
                data["company"],
                data["linkedin"],  # Will be empty string if not provided
                data["rating"],
                data["fairness"],
                data["communication"],
                data["technical"],
                data["review"]
            )

        
            if success:
                return redirect(url_for("thank_you"))
            else:
                return "Failed to save review - please try again later", 500
        
        return render_template("write.html")
            
    except Exception as e:
        print(f"Critical error: {str(e)}")
        return "Internal server error", 500

        except KeyError as e:
            print(f"Missing required field: {e}")
            return f"Missing required field: {e}", 400
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return f"Internal Server Error: {str(e)}", 500

    return render_template("write.html")

@app.route("/thank-you")
def thank_you():
    return render_template("submit.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)