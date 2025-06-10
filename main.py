import pandas as pd

# Replace with your actual public CSV export URL
csv_url = "https://docs.google.com/spreadsheets/d/1bpZjmiBsEnriX6y34ryvtho3vhn7rQ9t13kWyQA0cVQ/gviz/tq?tqx=out:csv&gid=420825805"

# Load the Google Sheet as DataFrame directly
df = pd.read_csv(csv_url)

# (Optional) Drop fully empty rows
df = df.dropna(how='all')

# Preview the data
print(df.head())


# تعریف نگاشت متنی به عددی
score_map = {
    'هرگز یا به ندرت': 1,
    'یک‌ بار در ماه': 2,
    'یک بار در هفته': 3,
    'اغلب روزا': 4,
}


columns = df.columns
factor_1_cols = columns[10:17]  # سوالات 7 تا 13
factor_2_cols = columns[17:25]  # سوالات 14 تا 21
factor_3_cols = columns[4:10]   # سوالات 1 تا 6

# تابع ارزیابی یک نفر
def evaluate_student(name):
    row = df[df['نام و نام خانوادگی'] == name]
    if row.empty:
        return f"دانش‌آموزی با نام '{name}' یافت نشد."

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
print(evaluate_student("مهراوه احمدی"))