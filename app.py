from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# نگاشت اسم تست به لینک Google Sheets
TEST_SHEETS = {
    "پرخاشگری": "https://docs.google.com/spreadsheets/d/1bpZjmiBsEnriX6y34ryvtho3vhn7rQ9t13kWyQA0cVQ/gviz/tq?tqx=out:csv&gid=420825805",
}

score_map = {
    'هرگز یا به ندرت': 1,
    'یک‌ بار در ماه': 2,
    'یک بار در هفته': 3,
    'اغلب روزا': 4,
}

def evaluate_student(name, df):
    row = df[df['نام و نام خانوادگی'] == name]
    if row.empty:
        return {"error": f"دانش‌آموزی با نام '{name}' یافت نشد."}

    gender = row['جنسیت'].values[0].strip()

    columns = df.columns
    factor_1_cols = columns[10:17]
    factor_2_cols = columns[17:25]
    factor_3_cols = columns[4:10]

    def score_factor(cols):
        return sum(score_map.get(str(row[col].values[0]).strip(), 0) for col in cols)

    f1 = score_factor(factor_1_cols)
    f2 = score_factor(factor_2_cols)
    f3 = score_factor(factor_3_cols)

    return {
        'نام': name,
        'جنسیت': gender,
        'عامل ۱': f1,
        'پرخاشگر عامل ۱': f1 > (8 if gender == 'دختر' else 10),
        'عامل ۲': f2,
        'پرخاشگر عامل ۲': f2 > (18 if gender == 'دختر' else 17),
        'عامل ۳': f3,
        'پرخاشگر عامل ۳': f3 > (15 if gender == 'دختر' else 16)
    }

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    selected_test = None

    if request.method == "POST":
        selected_test = request.form.get("test_name")
        student_name = request.form.get("student_name")

        url = TEST_SHEETS.get(selected_test)
        if url:
            df = pd.read_csv(url).dropna(how='all')
            result = evaluate_student(student_name, df)

    return render_template("index.html", tests=TEST_SHEETS.keys(), result=result)
