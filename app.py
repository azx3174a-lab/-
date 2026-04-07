from flask import Flask, render_template_string, request

app = Flask(__name__)

# --- واجهة تصميم الاختبار ---
# ملاحظة: جعلت التصميم أنيقاً وسهلاً للاستخدام من الجوال
html_ui = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منصة الاختبارات الذكية 📝</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f7f9; margin: 0; padding: 20px; color: #333; }
        .container { max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.05); }
        h2 { text-align: center; color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        .question-block { margin-bottom: 25px; padding: 15px; border: 1px solid #f0f0f0; border-radius: 10px; }
        label { display: block; font-weight: bold; margin-bottom: 10px; font-size: 1.1em; }
        input[type="text"], textarea { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; }
        .options { margin-top: 10px; }
        .option-item { margin-bottom: 8px; display: flex; align-items: center; }
        input[type="radio"], input[type="checkbox"] { margin-left: 10px; transform: scale(1.2); }
        .submit-btn { background: #3498db; color: white; border: none; padding: 15px; width: 100%; border-radius: 10px; font-weight: bold; cursor: pointer; font-size: 1.2em; transition: 0.3s; }
        .submit-btn:hover { background: #2980b9; }
        .result-card { background: #e8f6f3; padding: 20px; border-radius: 10px; border-right: 5px solid #27ae60; }
    </style>
</head>
<body>
    <div class="container">
        <h2>نموذج اختبار تجريبي 📝</h2>
        
        <form action="/submit" method="post">
            <div class="question-block">
                <label>1. ما هو اسمك الكريم؟ (إجابة قصيرة)</label>
                <input type="text" name="user_name" placeholder="اكتب اسمك هنا..." required>
            </div>

            <div class="question-block">
                <label>2. تحدث عن طموحك في تعلم البرمجة؟ (إجابة طويلة)</label>
                <textarea name="user_bio" rows="4" placeholder="اكتب بالتفصيل..."></textarea>
            </div>

            <div class="question-block">
                <label>3. ما هو فريقك المفضل في DLS؟ (اختيار واحد)</label>
                <div class="options">
                    <div class="option-item"><input type="radio" name="fav_team" value="الهلال" required> الهلال</div>
                    <div class="option-item"><input type="radio" name="fav_team" value="النصر"> النصر</div>
                    <div class="option-item"><input type="radio" name="fav_team" value="الاتحاد"> الاتحاد</div>
                </div>
            </div>

            <div class="question-block">
                <label>4. ما هي لغات البرمجة التي تود تعلمها؟ (اختيارات متعددة)</label>
                <div class="options">
                    <div class="option-item"><input type="checkbox" name="langs" value="Python"> Python</div>
                    <div class="option-item"><input type="checkbox" name="langs" value="HTML/CSS"> HTML/CSS</div>
                    <div class="option-item"><input type="checkbox" name="langs" value="JavaScript"> JavaScript</div>
                </div>
            </div>

            <button type="submit" class="submit-btn">إرسال الإجابات ✅</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_ui)

@app.route('/submit', methods=['POST'])
def submit():
    # استلام البيانات
    name = request.form.get('user_name')
    bio = request.form.get('user_bio')
    team = request.form.get('fav_team')
    langs = request.form.getlist('langs') # getlist تستخدم لجلب أكثر من قيمة من الـ Checkbox

    # واجهة عرض النتائج
    result_html = f"""
    <div dir="rtl" style="font-family:sans-serif; max-width:500px; margin:50px auto; padding:20px; border:1px solid #ccc; border-radius:15px;">
        <h2 style="color:#27ae60;">تم استلام إجاباتك بنجاح! 🎉</h2>
        <hr>
        <p><b>الاسم:</b> {name}</p>
        <p><b>الطموح:</b> {bio}</p>
        <p><b>الفريق المفضل:</b> {team}</p>
        <p><b>اللغات المختارة:</b> {', '.join(langs) if langs else 'لم يتم اختيار شيء'}</p>
        <br>
        <a href="/" style="text-decoration:none; color:#3498db;">العودة للاختبار</a>
    </div>
    """
    return result_html

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
