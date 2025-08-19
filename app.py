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

def calculate_csbs_scores(national_id, timestamp):
    # Step 1: Read the Google Sheet
    sheet_id = "1rK_u0GUij4k7IGxJcUTAvJ_PhIzJsngZWBk59xbdakM"
    gid = "384146557"
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    df = pd.read_csv(csv_url, dtype=str, na_filter=False, keep_default_na=False)

    # Step 2: Define score map
    score_map = {
        'هرگز': 0,
        'بعضی اوقات': 1,
        'اغلب اوقات': 2
    }

    # Step 3: Define question numbers per subscale
    scales = {
        'رفتار اجتماعی عملی':      [1, 8, 11, 16],
        'رفتار اجتماعی ارتباطی':  [5, 14, 18, 22],
        'رفتار ضد اجتماعی آشکار': [4, 7, 12, 20],
        'رفتار ضد اجتماعی رابطه‌ای': [17, 19, 23, 24],
        'رفتار قربانی شدن':       [3, 6, 9, 13],
    }

    # Step 4: Convert question numbers to column indices (add 4 because index starts at 0 and first 5 columns are metadata)
    scales_index = {key: [q + 4 for q in val] for key, val in scales.items()}

    # Step 5: Map the string responses to numeric
    df_numeric = df.copy()
    for col in df.columns[5:]:
        df_numeric[col] = df[col].map(score_map)

    # Step 6: Build the result dictionary
    category_scores = {}
    for scale_name, indices in scales_index.items():
        # Sum the values row-wise for each participant in this subscale
        category_scores[scale_name] = df_numeric.iloc[:, indices].sum(axis=1).tolist()
    return category_scores


def calculate_cbcl_scores(national_id):
    return {"عامل ۱": random.randint(20, 60), "عامل ۲": random.randint(20, 60), "عامل ۳": random.randint(20, 60)}

def calculate_scrs_scores(national_id, timestamp):
    csv_url = 'https://docs.google.com/spreadsheets/d/17QsSqNPQ2a1ZFgYmwAH1UBS8btZe7RAHTxFcAZMHe6A/export?format=csv&gid=1991538008'
    df = pd.read_csv(csv_url, dtype=str, na_filter=False, keep_default_na=False)
    df = df[
    (df['کد ملی'].astype(str).str.strip().str.replace('.0', '', regex=False) == national_id) &
    (df['Timestamp'] == timestamp) 
    ]
    if not df[df['کد ملی'].astype(str).str.strip().str.replace('.0', '', regex=False) == national_id]['جنسیت'].values[0]:
        return {"error": f"دانش‌آموزی با کد ملی '{national_id}' یافت نشد."}
    ranges = [
    {'range': [33, 58], 'color': 'lightgreen', 'label': 'خیر'},
    {'range': [59, 142], 'color': 'yellow', 'label': 'سوسو'},
    {'range': [143, 231], 'color': 'red', 'label': 'بله'}
]

    result_label = None
    for r in ranges:
        low, high = r['range']
        if low <= int(df['Total Score']) <= high:
            result_label = r['label']
            break
    result = {

        'نام': df[df['کد ملی'].astype(str).str.strip().str.replace('.0', '', regex=False) == national_id]['نام و نام خانوادگی'].values[0],
        'نمره خودکنترلی': int(df['Total Score']),
        'وضعیت خودکنترلی' : result_label
    }
    graph = {
        'نمره خودکنترلی': int(df['Total Score'])
    }
    return [result, graph]

def calculate_anger_scores(national_id, timestamp):
    csv_url = (
            "https://docs.google.com/spreadsheets/d/1bpZjmiBsEnriX6y34ryvtho3vhn7rQ9t13kWyQA0cVQ/"
            "export?format=csv&gid=420825805&cachebust=" + str(int(time.time()))
        )

        # فقط این پارامترها کافی‌ان تا «nan» و تبدیل عددی رخ نده
    df = pd.read_csv(csv_url, dtype=str, na_filter=False, keep_default_na=False)
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
            'نمره پرخاش جسمانی': f1,
            'وضعیت پرخاش جسمانی': boolean_to_farsi(f1 > f1_threshold),
            'نمره پرخاش رابطه‌ای': f2,
            'وضعیت پرخاش رابطه‌ای': boolean_to_farsi(f2 > f2_threshold),
            'نمره واکنشی کلامی': f3,
            'وضعیت واکنشی کلامی': boolean_to_farsi(f3 > f3_threshold)
        }
        graph = {
            'نمره پرخاش جسمانی': f1,
            'نمره پرخاش رابطه‌ای': f2,
            'نمره واکنشی کلامی': f3,
        }
        return [result, graph]

    else:
        return {'error': 'this feature is not ready yet!'}


import plotly.graph_objects as go

import os
import plotly.graph_objects as go

def create_scrs_gauge_chart(national_id, score, factor_index):

    title = 'نمره خودکنترلی'
    folder_path = f'static/{national_id}'
    os.makedirs(folder_path, exist_ok=True)  # ✅ Create if it doesn't exist
    filename = f'static/{national_id}/gauge_scrs.png'
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
    return f'{national_id}/gauge_scrs.png'


def create_anger_gauge_chart(national_id, score, gender, factor_index, factor):

    title = factor
    folder_path = f'static/{national_id}'
    os.makedirs(folder_path, exist_ok=True)  # ✅ Create if it doesn't exist
    filename = f'static/{national_id}/gauge_anger_{factor_index}.png'

    if factor_index == 1:
        if gender == 'پسر':
            steps = [
                {'range': [0, 11], 'color': 'lightgreen'},
                {'range': [11, 22], 'color': 'red'}
            ]
        else:
            steps = [
                {'range': [0, 9], 'color': 'lightgreen'},
                {'range': [9, 22], 'color': 'red'}
            ]
        range = [0, 22]
    elif factor_index == 2:
        if gender == 'پسر':
            steps = [
                {'range': [0, 18], 'color': 'lightgreen'},
                {'range': [18, 25], 'color': 'red'}
            ]
        else:
            steps = [
                {'range': [0, 19], 'color': 'lightgreen'},
                {'range': [19, 25], 'color': 'red'}
            ]
        range = [0, 25]

    else:
        if gender == 'پسر':
            steps = [
                {'range': [0, 16], 'color': 'lightgreen'},
                {'range': [16, 19], 'color': 'red'}
            ]
        else:
            steps = [
                {'range': [0, 17], 'color': 'lightgreen'},
                {'range': [17, 19], 'color': 'red'}
            ]
        range = [0, 19]

    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': title, 'font': {'size': 20, 'family': 'Vazirmatn'}},
        gauge={
            'axis': {'range': range},
            'bar': {'color': "darkblue"},
            'steps': steps,
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'value': score
            }
        }
    ))
    fig.write_image(filename)
    return f'{national_id}/gauge_anger_{factor_index}.png'


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

import time
import re

def clean_digits(s: str) -> str:
    s = str(s or "")
    # حذف آپاستروف ابتدای مقدار (متن اجباری شیتس)
    if s.startswith("'"):
        s = s[1:]
    # حذف کاراکترهای جهت‌دهی و فاصله‌های نامرئی
    s = (s.replace("\u200e","")  # LRM
         .replace("\u200f","")   # RLM
         .replace("\u202a","").replace("\u202b","").replace("\u202c","")
         .replace("\u202d","").replace("\u202e","")
         .replace("\u00a0"," ")  # NBSP
         .strip())
    # فقط رقم‌ها را نگه دار (اگر می‌خواهی + هم بماند، الگو را عوض کن)
    return re.sub(r"\D", "", s)

@app.route('/choose/<test_name>', methods=['POST'])
def choose(test_name):
    national_id = request.form.get('national_id')

    if test_name == 'ANGER':
       csv_url = (
            "https://docs.google.com/spreadsheets/d/1bpZjmiBsEnriX6y34ryvtho3vhn7rQ9t13kWyQA0cVQ/"
            "export?format=csv&gid=420825805&cachebust=" + str(int(time.time()))
        )

        # فقط این پارامترها کافی‌ان تا «nan» و تبدیل عددی رخ نده
       df = pd.read_csv(csv_url, dtype=str, na_filter=False, keep_default_na=False, encoding="utf-8")
       row = df[df['کد ملی'].astype(str).str.strip().str.replace('.0', '', regex=False) == national_id]
       print('-----------------',df['شماره تلفن'])

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
       df = pd.read_csv(csv_url, dtype=str, na_filter=False, keep_default_na=False)
       row = df[df['کد ملی'].astype(str).str.strip().str.replace('.0', '', regex=False) == national_id]
       row = row.to_dict(orient="records")
       print(row)
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

import json
import jdatetime
from datetime import datetime

# تبدیل اعداد انگلیسی به فارسی

PERSIAN_MONTHS = {
    1: "فروردین",
    2: "اردیبهشت",
    3: "خرداد",
    4: "تیر",
    5: "مرداد",
    6: "شهریور",
    7: "مهر",
    8: "آبان",
    9: "آذر",
    10: "دی",
    11: "بهمن",
    12: "اسفند"
}

# تبدیل اعداد انگلیسی به فارسی
def convert_to_persian_digits(text):
    english_to_persian = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
    return str(text).translate(english_to_persian)

# تابع نهایی برای تبدیل تاریخ-ساعت میلادی به تاریخ شمسی فارسی
def datetime_to_persian_date(datetime_str):
    # تبدیل رشته به datetime
    dt = datetime.strptime(datetime_str, "%d/%m/%Y %H:%M:%S")

    # تبدیل تاریخ میلادی به شمسی
    jalali_date = jdatetime.date.fromgregorian(date=dt.date())

    # گرفتن روز، ماه، سال شمسی
    day_persian = convert_to_persian_digits(jalali_date.day)
    month_persian = PERSIAN_MONTHS[jalali_date.month]
    year_persian = convert_to_persian_digits(jalali_date.year)

    return f"{day_persian} {month_persian} {year_persian}"

@app.route("/results", methods=["POST"])
def results():
    test_code = request.form.get("test_code")
    national_id = request.form.get("national_id")
    timestamp = request.form.get("timestamp")
    with open("test_descriptions.json", "r", encoding="utf-8") as f:
        DESCRIPTIONS = json.load(f)
    print(test_code, national_id)
    if test_code not in test_functions:
        return render_template("index.html", tests=test_names, result={"error": "آزمون نامعتبر است"})
    graph = None
    calculate_fn = test_functions[test_code]
    scores = calculate_fn(national_id, timestamp)
    date = datetime_to_persian_date(request.form.get('timestamp'))
    if test_code == 'ANGER':
        scores, graph = scores
        chart_filenames = {}
        gender = request.form.get("gender")
        phone = request.form.get("phone")
        DESCRIPTIONS = DESCRIPTIONS['tests']['ANGER']
        for i, factor in enumerate([ 'نمره پرخاش جسمانی',   'نمره پرخاش رابطه‌ای',  'نمره واکنشی کلامی'], start=1):
            chart_filename = create_anger_gauge_chart(national_id, scores[factor], gender,i, factor)
            chart_filenames[factor] = chart_filename
    elif test_code == 'SCRS':
        scores, graph = scores
        chart_filenames = {}
        DESCRIPTIONS = DESCRIPTIONS['tests']['SCRS']
        phone = request.form.get("phone")
        for i, factor in enumerate(["نمره خودکنترلی"], start=1):
            print((scores[factor]))
            chart_filename = create_scrs_gauge_chart(national_id, scores[factor], i)
            chart_filenames[factor] = chart_filename
    print(DESCRIPTIONS)
    return render_template(
        "results.html",
        name=scores['نام'],
        test_code=test_code,
        test_name=test_names[test_code],
        national_id=national_id,
        phone=phone,
        timestamp=date,
        graph=graph,
        result=scores,
        charts=chart_filenames,
        descriptions=DESCRIPTIONS

    )


from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.shape import WD_INLINE_SHAPE
from flask import request, render_template, send_file
from io import BytesIO
from docx import Document
from zipfile import ZipFile, BadZipFile

from htmldocx import HtmlToDocx


def tidy_text(text):
    """اصلاح فاصله‌ها و جلوگیری از چسبیدن کلمات فارسی"""
    text = text.replace(" :", " : ").replace("  ", " ")
    text = text.replace("نمره:", "نمره :")
    text = text.replace("وضعیت:", "وضعیت :")
    return text.strip()

def set_paragraph_rtl(paragraph):
    """تنظیم راست‌چین و راست به چپ برای پاراگراف"""
    p = paragraph._element
    pPr = p.get_or_add_pPr()

    # bidi راست به چپ
    bidi = OxmlElement('w:bidi')
    bidi.set(qn('w:val'), '1')
    pPr.append(bidi)

    # تراز به راست
    jc = OxmlElement('w:jc')
    jc.set(qn('w:val'), 'right')
    pPr.append(jc)

def split_score_and_status(doc):
    """جدا کردن نمره و وضعیت در پاراگراف‌های جدا (نسخه بدون ارور)"""
    paragraphs_copy = list(doc.paragraphs)  # کپی امن از لیست پاراگراف‌ها
    for p in paragraphs_copy:
        text = p.text.strip()
        if "وضعیت" in text and "نمره" in text:
            # جدا کردن بخش نمره و وضعیت
            parts = text.split("وضعیت", 1)
            score_part = parts[0].strip()
            status_part = "وضعیت " + parts[1].strip()

            # پاراگراف اول (نمره)
            p.clear()
            p.add_run(score_part)
            set_paragraph_rtl(p)

            # پاراگراف دوم (وضعیت) → درست بعد از p اضافه می‌کنیم
            para = p.insert_paragraph_before(status_part)
            set_paragraph_rtl(para)

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

def fix_spacing_and_order(doc):
    for p in doc.paragraphs:
        p.paragraph_format.space_before = Pt(0)  # بدون فاصله قبل
        p.paragraph_format.space_after = Pt(0)   # بدون فاصله بعد
        text = p.text.strip()
        if "نمره" in text and "وضعیت" not in text:
            # شکستن متن به دو خط: عنوان و مقدار نمره
            parts = text.split("نمره")
            if len(parts) == 2:
                title = parts[0].strip()
                score = parts[1].strip(" :")
                
                # پاراگراف عنوان
                p.text = title + "    نمره: " + score
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                for run in p.runs:
                    run.font.size = Pt(12)
                    
        if "وضعیت" in text:
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

def style_document(doc):
    for paragraph in doc.paragraphs:
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
        # تنظیم فونت پیش‌فرض و اندازه
        for run in paragraph.runs:
            run.font.name = 'Vazirmatn'  # یا مثلاً 'Arial'
            run.font.size = Pt(12)
            # برای بولد کردن:
            run.bold = True
        
        # راست‌چین کردن همه پاراگراف‌ها
        paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT

@app.route('/results-docx', methods=['POST'])
def results_docx():
    data = request.get_json(force=True)
    with open("test_descriptions.json", "r", encoding="utf-8") as f:
        DESCRIPTIONS = json.load(f)
        DESCRIPTIONS = DESCRIPTIONS['tests'][data.get('test_code')]
    html = render_template(
        'results.html',
        name=data.get('name'),
        test_name=data.get('test_name'),
        national_id=data.get('national_id'),
        phone=data.get('phone'),
        result=data.get('result'),
        timestamp=data.get('timestamp'),
        graph=data.get('graph'),
        charts=data.get('charts'),
        descriptions=DESCRIPTIONS,
        for_docx=True
    )

    # ایجاد فایل Word
    doc = Document()
    converter = HtmlToDocx()

    # افزودن جهت RTL به HTML
    full_html = (
        '<!DOCTYPE html><html lang="fa" dir="rtl">'
        '<head><meta charset="utf-8"></head>'
        '<body>' + html + '</body></html>'
    )
    converter.add_html_to_document(full_html, doc)
    style_document(doc)
    fix_spacing_and_order(doc)
    # اصلاح متن و راست‌چین کردن
    for p in doc.paragraphs:
        fixed = tidy_text(p.text)
        if fixed != p.text:
            p.clear()
            p.add_run(fixed)
        set_paragraph_rtl(p)

    # جدا کردن نمره و وضعیت
    split_score_and_status(doc)

    # ذخیره در حافظه
    buf = BytesIO()
    doc.save(buf)

    # بررسی صحت فایل DOCX
    buf.seek(0)
    try:
        ZipFile(buf).testzip()
    except BadZipFile:
        raise RuntimeError("Generated DOCX is invalid ZIP.")
    buf.seek(0)

    TARGET_WIDTH = Inches(2.4)  # ~12.2 cm — pick what you like
    for ishape in doc.inline_shapes:
        if ishape.type == WD_INLINE_SHAPE.PICTURE:
            ishape.width = TARGET_WIDTH 
    filename = f"نتایج-آزمون-{data.get('test_name','')}-{data.get('national_id','')}.docx"

    folder_path =  'static/' + data.get('national_id')  # مسیر پوشه‌ای که می‌خوای پاک شه

    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        os.system(f'rm -rf "{folder_path}"') 
    return send_file(
        buf,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


# ----------------- Run the App --------------------
if __name__ == "__main__":
    app.run(debug=True)
