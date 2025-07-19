from flask import Flask, render_template, request, redirect, url_for
from sheets_util import add_review_to_sheet

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/write", methods=["GET", "POST"])
def write():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        company = request.form.get("company")
        linkedin = request.form.get("linkedin", "")
        rating = request.form.get("overall_rating")  # Changed from "rating"
        fairness = request.form.get("fairness")
        communication = request.form.get("communication")
        technical_competence = request.form.get("technical")  # Changed from "technical_competence"
        review = request.form.get("review")

        if all([first_name, last_name, email, company, rating, fairness, communication, technical_competence, review]):
            add_review_to_sheet(
                first_name, last_name, email, company, linkedin,
                rating, fairness, communication, technical_competence,
                review
            )
            return redirect(url_for("thank_you"))

    return render_template("write.html")


@app.route("/thank-you")
def thank_you():
    return render_template("submit.html")  # Changed from text response to template

if __name__ == "__main__":
    app.run(debug=True)
