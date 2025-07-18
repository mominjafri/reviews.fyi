from flask import Flask, render_template, request, redirect, url_for
from sheets_util import add_review_to_sheet

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/write", methods=["GET", "POST"])
def write():
    if request.method == "POST":
        rating = request.form.get("rating")
        review = request.form.get("review")
        if rating and review:
            add_review_to_sheet(rating, review)
            return redirect(url_for("thank_you"))
    return render_template("write.html")

@app.route("/thank-you")
def thank_you():
    return "Thanks for your review!"

if __name__ == "__main__":
    app.run(debug=True)
