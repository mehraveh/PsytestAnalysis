from flask import Flask, render_template, request, redirect, url_for
import random

app = Flask(__name__)

# ----- Dummy score functions for each test (we'll update them later) -----

def calculate_ders_scores(national_id):
    return {"عامل ۱": random.randint(10, 25), "عامل ۲": random.randint(10, 25), "عامل ۳": random.randint(10, 25)}

def calculate_csbs_scores(national_id):
    return {"عامل ۱": random.randint(5, 15), "عامل ۲": random.randint(5, 15), "عامل ۳": random.randint(5, 15)}

def calculate_cbcl_scores(national_id):
    return {"عامل ۱": random.randint(20, 60), "عامل ۲": random.randint(20, 60), "عامل ۳": random.randint(20, 60)}

def calculate_scrs_scores(national_id):
    return {"عامل ۱": random.randint(5, 20), "عامل ۲": random.randint(5, 20), "عامل ۳": random.randint(5, 20)}

def calculate_anger_scores(national_id):
    return {"عامل ۱": random.randint(5, 15), "عامل ۲": random.randint(5, 15), "عامل ۳": random.randint(5, 15)}

# Mapping of test codes to function references
test_functions = {
    "DERS": calculate_ders_scores,
    "CSBS": calculate_csbs_scores,
    "CBCL": calculate_cbcl_scores,
    "SCRS": calculate_scrs_scores,
    "ANGER": calculate_anger_scores
}

test_names = {
    "DERS": "مقیاس دشواری‌های تنظیم هیجانی",
    "CSBS": "مقیاس رفتار اجتماعی کودک",
    "CBCL": "چک‌لیست رفتاری کودکان",
    "SCRS": "مقیاس ارزیابی خودکنترلی",
    "ANGER": "پرسش‌نامه پرخاشگری رابطه‌ای و آشکار"
}

# ----------------- Routes --------------------

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        test = request.form.get("test_name")
        national_id = request.form.get("national_id")
        if test not in test_functions:
            return render_template("index.html", tests=test_names, result={"error": "آزمون نامعتبر است"})

        return redirect(url_for("results", test_code=test, national_id=national_id))
    return render_template("index.html", tests=test_names)

@app.route("/results")
def results():
    test_code = request.args.get("test_code")
    national_id = request.args.get("national_id")
    calculate_fn = test_functions.get(test_code)

    if not calculate_fn:
        return "Invalid test code", 400

    scores = calculate_fn(national_id)

    return render_template("results.html", test_name=test_names[test_code], national_id=national_id, result=scores)

# ----------------- Run the App --------------------

if __name__ == "__main__":
    app.run(debug=True)
