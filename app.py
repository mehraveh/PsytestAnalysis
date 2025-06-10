from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# Load data from public Google Sheet
csv_url = "https://docs.google.com/spreadsheets/d/1bpZjmiBsEnriX6y34ryvtho3vhn7rQ9t13kWyQA0cVQ/gviz/tq?tqx=out:csv&gid=420825805"
df = pd.read_csv(csv_url).dropna(how='all')

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

# Evaluation function
def evaluate_student(name):
    row = df[df['نام و نام خانوادگی'] == name]
    if row.empty:
        return {"error": f"دانش‌آموزی با نام '{name}' یافت نشد."}

    gender = row['جنسیت'].values[0].strip()

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

# Web routes
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        name = request.form.get("student_name")
        result = evaluate_student(name)
    return render_template("index.html", result=result)