import sqlite3
import ast
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "admin_secret_key_999"  # مفتاح سري لتأمين الجلسات
ADMIN_PASS = "1234"  # كلمة مرور لوحة التحكم الخاصة بك

DB_NAME = "questions_v2.db"

# --- 1. إعداد قاعدة البيانات ---
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        # جدول الأسئلة التي تنشئها أنت
        conn.execute('''CREATE TABLE IF NOT EXISTS questions 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                         q_text TEXT, 
                         q_type TEXT, 
                         q_options TEXT)''')
        # جدول الإجابات التي يرسلها الناس
        conn.execute('''CREATE TABLE IF NOT EXISTS answers 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                         ans_data TEXT, 
                         submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()

init_db()

# --- 2. التصاميم (HTML & CSS) ---

# واجهة المستخدم (الناس اللي تجاوب)
USER_HTML = """
<div dir="rtl" style="font-family:sans-serif; max-width:600px; margin:auto; padding:20px; background:#fff; border-radius:15px; box-shadow:0 4px 15px rgba(0,0,0,0.1);">
    <h2 style="text-align:center; color:#2c3e50;">نموذج الأسئلة 📝</h2>
    <form method="POST" action="/submit">
        {% for q in questions %}
        <div style="margin-bottom:20px; padding:15px; border:1px solid #f0f0f0; border-radius:10px; background:#fafafa;">
            <label style="display:block; font-weight:bold; margin-bottom:10px; color:#333;">{{ q[1] }}</label>
            
            {% if q[2] == 'text' %}
                <input type="text" name="q_{{ q[0] }}" style="width:100%; padding:10px; border:1px solid #ddd; border-radius:5px;">
            {% elif q[2] == 'textarea' %}
                <textarea name="q_{{ q[0] }}" style="width:100%; padding:10px; border:1px solid #ddd; border-radius:5px;" rows="3"></textarea>
            {% elif q[2] == 'radio' %}
                {% for opt in q[3].split(',') %}
                <label style="display:block; margin:5px 0;"><input type="radio" name="q_{{ q[0] }}" value="{{ opt.strip() }}" required> {{ opt.strip() }}</label>
                {% endfor %}
            {% elif q[2] == 'checkbox' %}
                {% for opt in q[3].split(',') %}
                <label style="display:block; margin:5px 0;"><input type="checkbox" name="q_{{ q[0] }}" value="{{ opt.strip() }}"> {{ opt.strip() }}</label>
                {% endfor %}
            {% endif %}
        </div>
        {% endfor %}
        <button style="width:100%; padding:15px; background:#3498db; color:white; border:none; border-radius:10px; cursor:pointer; font-size:1.1em; font-weight:bold;">إرسال الإجابات ✅</button>
    </form>
    <center><br><a href="/admin" style="color:#ddd; text-decoration:none; font-size:0.7em;">إدارة</a></center>
</div>
"""

# واجهة الإدارة (إضافة الأسئلة)
ADMIN_HTML = """
<div dir="rtl" style="font-family:sans-serif; max-width:600px; margin:auto; padding:20px;">
    <h2 style="color:#2c3e50;">لوحة التحكم ⚙️</h2>
    <div style="background:#e8f4fd; padding:15px; border-radius:10px; margin-bottom:20px;">
        <h4>إضافة سؤال جديد:</h4>
        <form method="POST" action="/admin/add">
            <input name="q_text" placeholder="اكتب السؤال هنا..." required style="width:100%; padding:10px; margin-bottom:10px; border-radius:5px; border:1px solid #ccc;">
            <select name="q_type" style="width:100%; padding:10px; margin-bottom:10px; border-radius:5px;">
                <option value="text">إجابة نصية قصيرة</option>
                <option value="textarea">إجابة نصية طويلة</option>
                <option value="radio">اختيار واحد (Radio)</option>
                <option value="checkbox">خيارات متعددة (Checkbox)</option>
            </select>
            <input name="q_options" placeholder="الخيارات (افصل بينها بفاصلة ,)" style="width:100%; padding:10px; margin-bottom:10px; border-radius:5px; border:1px solid #ccc;">
            <button style="width:100%; padding:10px; background:#27ae60; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">إضافة السؤال +</button>
        </form>
    </div>
    <h3>الأسئلة الحالية:</h3>
    {% for q in questions %}
    <div style="background:#fff; border:1px solid #ddd; padding:10px; margin-bottom:10px; border-radius:8px;">
        <b>{{ q[1] }}</b> <small style="color:#888;">({{ q[2] }})</small>
        <a href="/admin/delete/{{ q[0] }}" style="color:#e74c3c; float:left; text-decoration:none; font-weight:bold;">حذف 🗑️</a>
    </div>
    {% endfor %}
    <hr>
    <a href="/admin/responses" style="display:block; text-align:center; background:#34495e; color:white; padding:15px; border-radius:10px; text-decoration:none; font-weight:bold;">رؤية الإجابات المستلمة 📋</a>
</div>
"""

# --- 3. المسارات (Routes) ---

@app.route('/')
def index():
    with sqlite3.connect(DB_NAME) as conn:
        questions = conn.execute("SELECT * FROM questions").fetchall()
    return render_template_string(USER_HTML, questions=questions)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('pass') == ADMIN_PASS:
            session['logged_in'] = True
            return redirect(url_for('admin'))
    
    if not session.get('logged_in'):
        return '<div dir="rtl" style="text-align:center; padding-top:100px; font-family:sans-serif;"><h2>دخول الإدارة 🔐</h2><form method="POST"><input type="password" name="pass" placeholder="كلمة المرور" style="padding:10px; border-radius:5px;"><br><br><button style="padding:10px 20px; background:#3498db; color:white; border:none; border-radius:5px;">دخول</button></form></div>'
    
    with sqlite3.connect(DB_NAME) as conn:
        questions = conn.execute("SELECT * FROM questions").fetchall()
    return render_template_string(ADMIN_HTML, questions=questions)

@app.route('/admin/add', methods=['POST'])
def add_question():
    if session.get('logged_in'):
        q_text, q_type, q_options = request.form.get('q_text'), request.form.get('q_type'), request.form.get('q_options')
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("INSERT INTO questions (q_text, q_type, q_options) VALUES (?, ?, ?)", (q_text, q_type, q_options))
    return redirect(url_for('admin'))

@app.route('/admin/delete/<int:id>')
def delete_question(id):
    if session.get('logged_in'):
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("DELETE FROM questions WHERE id = ?", (id,))
    return redirect(url_for('admin'))

@app.route('/submit', methods=['POST'])
def submit_answers():
    ans_data = str(request.form.to_dict(flat=False))
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT INTO answers (ans_data) VALUES (?)", (ans_data,))
    return '<div dir="rtl" style="text-align:center; padding-top:100px; font-family:sans-serif;"><h2>تم استلام إجاباتك بنجاح! 🎉</h2><a href="/">العودة للموقع</a></div>'

@app.route('/admin/responses')
def view_responses():
    if not session.get('logged_in'): return redirect(url_for('admin'))
    
    with sqlite3.connect(DB_NAME) as conn:
        # جلب نصوص الأسئلة للربط
        questions = {f"q_{q[0]}": q[1] for q in conn.execute("SELECT id, q_text FROM questions").fetchall()}
        responses = conn.execute("SELECT id, ans_data, submitted_at FROM answers ORDER BY id DESC").fetchall()
    
    html = '<div dir="rtl" style="font-family:sans-serif; padding:20px; max-width:700px; margin:auto;">'
    html += '<h2>الإجابات المستلمة 📋</h2><a href="/admin">🔙 العودة للوحة التحكم</a><hr>'
    
    for res in responses:
        res_id, ans_str, date = res
        try:
            ans_dict = ast.literal_eval(ans_str)
            html += f'<div style="background:#fff; border:1px solid #ddd; padding:15px; margin-bottom:20px; border-radius:12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">'
            html += f'<small style="color:#999;">استجابة رقم #{res_id} - {date}</small><br><br>'
            
            for q_id, answers in ans_dict.items():
                q_text = questions.get(q_id, "سؤال محذوف")
                ans_text = ", ".join(answers)
                html += f'<div style="margin-bottom:8px; line-height:1.6;">'
                html += f'<b style="color:#2980b9;">السؤال:</b> {q_text}<br>'
                html += f'<b style="color:#27ae60;">الجواب:</b> {ans_text}</div>'
            html += '</div>'
        except: continue
    
    html += '</div>'
    return html

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
