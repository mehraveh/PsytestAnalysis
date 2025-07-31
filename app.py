from flask import Flask, render_template, request
import random
import pandas as pd

app = Flask(__name__)

csv_url = "https://docs.google.com/spreadsheets/d/1bpZjmiBsEnriX6y34ryvtho3vhn7rQ9t13kWyQA0cVQ/gviz/tq?tqx=out:csv&gid=420825805"
df = pd.read_csv(csv_url).dropna(how='all')

# ----- Dummy score functions for each test -----
def calculate_ders_scores(national_id):
    return {"عامل ۱": random.randint(10, 25), "عامل ۲": random.randint(10, 25), "عامل ۳": random.randint(10, 25)}

def calculate_csbs_scores(national_id):
    return {"عامل ۱": random.randint(5, 15), "عامل ۲": random.randint(5, 15), "عامل ۳": random.randint(5, 15)}

def calculate_cbcl_scores(national_id):
    return {"عامل ۱": random.randint(20, 60), "عامل ۲": random.randint(20, 60), "عامل ۳": random.randint(20, 60)}

def calculate_scrs_scores(national_id):
    return {"عامل ۱": random.randint(5, 20), "عامل ۲": random.randint(5, 20), "عامل ۳": random.randint(5, 20)}

def calculate_anger_scores(national_id):

        # Score map
    score_map = {
        'هرگز یا به ندرت': 1,
        'یک‌ بار در ماه': 2,
        'یک بار در هفته': 3,
        'اغلب روزا': 4,
    }
    
    # Identify columns for each factor
    columns = df.columns
    factor_1_cols = columns[10:17]  # Q7-Q13
    factor_2_cols = columns[17:25]  # Q14-Q21
    factor_3_cols = columns[4:10]   # Q1-Q6
    row = df[df['کد ملی'] == national_id]
    print(len(row))
    gender = row['جنسیت'].values[0].strip()
    if row.empty:
        return {"error": f"دانش‌آموزی با کد ملی '{NCode}' یافت نشد."}
    def score_factor(cols):
        return sum(score_map.get(str(row[col].values[0]).strip(), 0) for col in cols)

    f1 = score_factor(factor_1_cols)
    f2 = score_factor(factor_2_cols)
    f3 = score_factor(factor_3_cols)

    result = {
        'نام': name,
        'جنسیت': gender,
        'عامل ۱': f1,
        'پرخاشگر عامل ۱': f1 > (8 if gender == 'دختر' else 10),
        'عامل ۲': f2,
        'پرخاشگر عامل ۲': f2 > (18 if gender == 'دختر' else 17),
        'عامل ۳': f3,
        'پرخاشگر عامل ۳': f3 > (15 if gender == 'دختر' else 16)
    }
    return result

# Mapping of test codes to function references
test_functions = {
    "DERS": calculate_ders_scores,
    "CSBS": calculate_csbs_scores,
    "CBCL": calculate_cbcl_scores,
    "SCRS": calculate_scrs_scores,
    "ANGER": calculate_anger_scores
}

# Display names (Persian)
test_names = {
    "DERS": "مقیاس دشواری‌های تنظیم هیجانی",
    "CSBS": "مقیاس رفتار اجتماعی کودک",
    "CBCL": "چک‌لیست رفتاری کودکان",
    "SCRS": "مقیاس ارزیابی خودکنترلی",
    "ANGER": "پرسش‌نامه پرخاشگری رابطه‌ای و آشکار"
}

# ----------------- Routes --------------------
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html", tests=test_names)

@app.route("/results", methods=["POST"])
def results():
    test_code = request.form.get("test_name")
    national_id = request.form.get("national_id")

    if test_code not in test_functions:
        return render_template("index.html", tests=test_names, result={"error": "آزمون نامعتبر است"})

    calculate_fn = test_functions[test_code]
    scores = calculate_fn(national_id)

    return render_template(
        "results.html",
        test_code=test_code,
        test_name=test_names[test_code],
        national_id=national_id,
        result=scores
    )

# ----------------- Run the App --------------------
if __name__ == "__main__":
    app.run(debug=True)
