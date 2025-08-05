from flask import Flask, render_template, request, url_for, redirect
import random
import pandas as pd

app = Flask(__name__)


def convert_to_persian_digits(text):
    english_to_persian = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
    return str(text).translate(english_to_persian)

# ----- Dummy score functions for each test -----
def calculate_ders_scores(national_id):
    return {"عامل ۱": random.randint(10, 25), "عامل ۲": random.randint(10, 25), "عامل ۳": random.randint(10, 25)}

def calculate_csbs_scores(national_id):
    return {"عامل ۱": random.randint(5, 15), "عامل ۲": random.randint(5, 15), "عامل ۳": random.randint(5, 15)}

def calculate_cbcl_scores(national_id):
    return {"عامل ۱": random.randint(20, 60), "عامل ۲": random.randint(20, 60), "عامل ۳": random.randint(20, 60)}

def calculate_scrs_scores(national_id, timestamp):
    csv_url = 'https://docs.google.com/spreadsheets/d/17QsSqNPQ2a1ZFgYmwAH1UBS8btZe7RAHTxFcAZMHe6A/export?format=csv&gid=1991538008'
    df = pd.read_csv(csv_url)
    df = (df.head()) 
    df = df[
    (df['کد ملی'].astype(str).str.strip().str.replace('.0', '', regex=False) == national_id) &
    (df['Timestamp'] == timestamp) 
    ]
    if not df[df['کد ملی'].astype(str).str.strip().str.replace('.0', '', regex=False) == national_id]['جنسیت'].values[0]:
        return {"error": f"دانش‌آموزی با کد ملی '{national_id}' یافت نشد."}
    result = {

        'نام': df[df['کد ملی'].astype(str).str.strip().str.replace('.0', '', regex=False) == national_id]['نام و نام خانوادگی'].values[0],
        'نمره': int(df['Total Score'])
    }
    graph = {
        'نمره': int(df['Total Score'])
    }
    return [result, graph]

def calculate_anger_scores(national_id, timestamp):
    csv_url = "https://docs.google.com/spreadsheets/d/1bpZjmiBsEnriX6y34ryvtho3vhn7rQ9t13kWyQA0cVQ/gviz/tq?tqx=out:csv&gid=420825805"
    df = pd.read_csv(csv_url)
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
    df = (df.head()) 
    df = df[
    (df['کد ملی'].astype(str).str.strip().str.replace('.0', '', regex=False) == national_id) &
    (df['Timestamp'] == timestamp) 
    ]
    if not df[df['کد ملی'].astype(str).str.strip().str.replace('.0', '', regex=False) == national_id]['جنسیت'].values[0]:
        return {"error": f"دانش‌آموزی با کد ملی '{national_id}' یافت نشد."}
    if len(df) == 1:
        def score_factor(cols):
            return sum(score_map.get(str(df[col].values[0]).strip(), 0) for col in cols)

        f1 = score_factor(factor_1_cols)
        f2 = score_factor(factor_2_cols)
        f3 = score_factor(factor_3_cols)

        f1_threshold = 8 if df[df['کد ملی'].astype(str).str.strip().str.replace('.0', '', regex=False) == national_id]['جنسیت'].values[0] == 'دختر' else 10
        f2_threshold = 18 if df[df['کد ملی'].astype(str).str.strip().str.replace('.0', '', regex=False) == national_id]['جنسیت'].values[0] == 'دختر' else 17
        f3_threshold = 15 if df[df['کد ملی'].astype(str).str.strip().str.replace('.0', '', regex=False) == national_id]['جنسیت'].values[0] == 'دختر' else 16

        # تبدیل به بله/خیر
        def boolean_to_farsi(val):
            return 'بله' if val else 'خیر'

        result = {
            'نام': df[df['کد ملی'].astype(str).str.strip().str.replace('.0', '', regex=False) == national_id]['نام و نام خانوادگی'].values[0],
            'جنسیت': df[df['کد ملی'].astype(str).str.strip().str.replace('.0', '', regex=False) == national_id]['جنسیت'].values[0],
            'نمره پرخاشگر عامل اول': f1,
            'پرخاشگر عامل اول': boolean_to_farsi(f1 > f1_threshold),
            'نمره پرخاشگر عامل دوم': f2,
            'پرخاشگر عامل دوم': boolean_to_farsi(f2 > f2_threshold),
            'نمره پرخاشگر عامل سوم': f3,
            'پرخاشگر عامل سوم': boolean_to_farsi(f3 > f3_threshold)
        }
        graph = {
            'نمره پرخاشگر عامل اول': f1,
            'نمره پرخاشگر عامل دوم': f2,
            'نمره پرخاشگر عامل سوم': f3,
        }
        return [result, graph]

    else:
        return {'error': 'this feature is not ready yet!'}


import plotly.graph_objects as go

def create_scrs_gauge_chart(name, score, factor_index):

    title = 'نمره خودکنترلی'
    folder_path = f'static/{name}'
    os.makedirs(folder_path, exist_ok=True)  # ✅ Create if it doesn't exist
    filename = f'static/{name}/gauge_scrs.png'
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': title, 'font': {'size': 20, 'family': 'Vazirmatn'}},
        gauge={
            'axis': {'range': [33, 231]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [33, 58], 'color': 'lightgreen'},
                {'range': [59, 142], 'color': 'yellow'},
                {'range': [143, 231], 'color': 'red'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'value': score
            }
        }
    ))
    fig.write_image(filename)
    return f'{name}/gauge_scrs.png'


def create_anger_gauge_chart(name, score, factor_index):

    title = f'پرخاشگری - عامل {factor_index}'
    folder_path = f'static/{name}'
    os.makedirs(folder_path, exist_ok=True)  # ✅ Create if it doesn't exist
    filename = f'static/{name}/gauge_anger_{factor_index}.png'
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': title, 'font': {'size': 20, 'family': 'Vazirmatn'}},
        gauge={
            'axis': {'range': [0, 20]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 6], 'color': 'lightgreen'},
                {'range': [6, 13], 'color': 'yellow'},
                {'range': [13, 20], 'color': 'red'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'value': score
            }
        }
    ))
    fig.write_image(filename)
    return f'{name}/gauge_anger_{factor_index}.png'


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
@app.route("/results_page", methods=["GET"])
def results_page():
    print("Serving index page--------------------------")
    return render_template("index.html")

@app.route("/", methods=["GET"])
def home():
    print("Serving index page--------------------------")
    return render_template("first_page.html")

from docx import Document
from docx.shared import Inches
import os

import os
from docx import Document
from docx.shared import Inches

@app.route('/download_report/<national_id>')
def create_word_report(name, gender, national_id, f1, f2, f3, g1, g2, g3, image_folder="static"):
    doc = Document()
    doc.add_heading("نتایج آزمون", 0)

    doc.add_paragraph(f"نام: {name}")
    doc.add_paragraph(f"جنسیت: {gender}")
    doc.add_paragraph(f"کد ملی: {national_id}")
    doc.add_paragraph("")

    doc.add_paragraph(f"نمره پرخاشگر عامل 1: {f1}")
    doc.add_paragraph(f"پرخاشگر عامل 1: {g1}")
    doc.add_paragraph(f"نمره پرخاشگر عامل 2: {f2}")
    doc.add_paragraph(f"پرخاشگر عامل 2: {g2}")
    doc.add_paragraph(f"نمره پرخاشگر عامل 3: {f3}")
    doc.add_paragraph(f"پرخاشگر عامل 3: {g3}")
    doc.add_paragraph("")

    # ⬇️ Automatically insert all gauge images (GaugeAngle1, 2, 3) from folder
    for i in range(1, 4):
        image_name = f"gauge_anger_ {i}.png"
        image_path = os.path.join(image_folder, image_name)
        if os.path.exists(image_path):
            doc.add_paragraph(f"نمودار پرخاشگری عامل {i}:")
            doc.add_picture(image_path, width=Inches(4.5))
            doc.add_paragraph("")  # Add space after each chart

    # Save the report
    filepath = os.path.join(image_folder, f"report_{national_id}.docx")
    doc.save(filepath)
    return filepath


@app.route('/choose/<test_name>', methods=['POST'])
def choose(test_name):
    national_id = request.form.get('national_id')

    if test_name == 'ANGER':
       csv_url = "https://docs.google.com/spreadsheets/d/1bpZjmiBsEnriX6y34ryvtho3vhn7rQ9t13kWyQA0cVQ/gviz/tq?tqx=out:csv&gid=420825805"
       df = pd.read_csv(csv_url)
       df = (df.head()) 
       row = df[df['کد ملی'].astype(str).str.strip().str.replace('.0', '', regex=False) == national_id]
       row = row.to_dict(orient="records")
       return render_template(
        "view_attempts.html",
        test_code="ANGER",
        national_id=national_id,
        attempts=row,
        test_names=test_names
    )
    #render_template()
    elif test_name == 'SCRS':
       csv_url = 'https://docs.google.com/spreadsheets/d/17QsSqNPQ2a1ZFgYmwAH1UBS8btZe7RAHTxFcAZMHe6A/export?format=csv&gid=1991538008'
       df = pd.read_csv(csv_url)
       df = (df.head()) 
       row = df[df['کد ملی'].astype(str).str.strip().str.replace('.0', '', regex=False) == national_id]
       row = row.to_dict(orient="records")
       return render_template(
        "view_attempts.html",
        test_code="SCRS",
        national_id=national_id,
        attempts=row,
        test_names=test_names
    )
    elif test_name == 'CBCL':
        # Handle CBCL test
        return f"Processing CBCL test for {national_id}"
    elif test_name == 'CSBS':
        # Handle CSBS test
        return f"Processing CSBS test for {national_id}"
    elif test_name == 'DERS':
        # Handle DERS test
        return f"Processing DERS test for {national_id}"
    else:
        return "Invalid test name", 400


@app.route("/results", methods=["POST"])
def results():
    test_code = request.form.get("test_code")
    national_id = request.form.get("national_id")
    timestamp = request.form.get("timestamp")
    print(test_code, national_id)
    if test_code not in test_functions:
        return render_template("index.html", tests=test_names, result={"error": "آزمون نامعتبر است"})
    graph = None
    calculate_fn = test_functions[test_code]
    scores = calculate_fn(national_id, timestamp)
    if test_code == 'ANGER':
        scores, graph = scores
        chart_filenames = {}
        for i, factor in enumerate(["نمره پرخاشگر عامل اول", "نمره پرخاشگر عامل دوم", "نمره پرخاشگر عامل سوم"], start=1):
            chart_filename = create_anger_gauge_chart(scores['نام'], scores[factor], i)
            chart_filenames[factor] = chart_filename
    elif test_code == 'SCRS':
        scores, graph = scores
        chart_filenames = {}
        for i, factor in enumerate(["نمره"], start=1):
            print((scores[factor]))
            chart_filename = create_scrs_gauge_chart(scores['نام'], scores[factor], i)
            chart_filenames[factor] = chart_filename
    print(graph)
    return render_template(
        "results.html",
        name=scores['نام'],
        test_code=test_code,
        test_name=test_names[test_code],
        national_id=national_id,
        graph=graph,
        result=scores,
        charts=chart_filenames

    )

# ----------------- Run the App --------------------
if __name__ == "__main__":
    app.run(debug=True)
