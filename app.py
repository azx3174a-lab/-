import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "admin_secret_key_123" # غير المفتاح السري هنا
ADMIN_PASS = "1234" # كلمة مرور لوحة التحكم

DB_NAME = "questions.db"

# --- إعداد قاعدة البيانات ---
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        # جدول الأسئلة
        conn.execute('''CREATE TABLE IF NOT EXISTS questions 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                         q_text TEXT, 
                         q_type TEXT, 
                         q_options TEXT)''')
        # جدول الإجابات المستلمة من الناس
        conn.execute('''CREATE TABLE IF NOT EXISTS answers 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                         ans_data TEXT, 
                         submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()

init_db()

# --- التصاميم (HTML) ---

# واجهة لوحة التحكم
ADMIN_HTML = """
<div dir="rtl" style="font-family:sans-serif; max-width:600_px; margin:auto; padding:20px;">
    <h2>لوحة تحكم الأسئلة ⚙️</h2>
    <form method="POST" action="/admin/add">
        <input name="q_text" placeholder="اكتب نص السؤال هنا" required style="width:100%; padding:10px; margin-bottom:10px;">
        <select name="q_type" style="width:100%; padding:10px; margin-bottom:10px;">
            <option value="text">إجابة نصية (قصيرة)</option>
            <option value="textarea">إجابة نصية (طويلة)</option>
            <option value="radio">اختيار واحد فقط</option>
            <option value="checkbox">خيارات متعددة</option>
        </select>
        <input name="q_options" placeholder="الخيارات (افصل بينها بفاصلة ,) اتركها فارغة للنص" style="width:100%; padding:10px; margin-bottom:10px;">
        <button style="width:100%; padding:10px; background:#2ecc71; color:white; border:none; cursor:pointer;">إضافة السؤال +</button>
    </form>
    <hr>
    <h3>الأسئلة الحالية:</h3>
    {% for q in questions %}
    <div style="background:#f9f9f9; padding:10px; margin-bottom:5px; border-right:4px solid #3498db;">
        <b>{{ q[1] }}</b> ({{ q[2] }}) 
        <a href="/admin/delete/{{ q[0] }}" style="color:red; float:left; text-decoration:none;">حذف</a>
    </div>
    {% endfor %}
    <br><a href="/">العودة للموقع الرئيسي</a> | <a href="/admin/responses">رؤية الإجابات المستلمة</a>
</div>
"""

# واجهة الموقع للناس
USER_HTML = """
<div dir="rtl" style="font-family:sans-serif; max-width:600_px; margin:auto; padding:20px;">
    <h2 style="text-align:center;">نموذج الأسئلة 📝</h2>
    <form method="POST" action="/submit">
        {% for q in questions %}
        <div style="margin-bottom:20px; padding:15px; border:1px solid #eee; border-radius:10px;">
            <label style="display:block; font-weight:bold; margin-bottom:10px;">{{ q[1] }}</label>
            
            {% if q[2] == 'text' %}
                <input type="text" name="q_{{ q[0] }}" style="width:100%; padding:8px;">
            {% elif q[2] == 'textarea' %}
                <textarea name="q_{{ q[0] }}" style="width:100%; padding:8px;" rows="3"></textarea>
            {% elif q[2] == 'radio' %}
                {% for opt in q[3].split(',') %}
                <label><input type="radio" name="q_{{ q[0] }}" value="{{ opt.strip() }}"> {{ opt.strip() }}</label><br>
                {% endfor %}
            {% elif q[2] == 'checkbox' %}
                {% for opt in q[3].split(',') %}
                <label><input type="checkbox" name="q_{{ q[0] }}" value="{{ opt.strip() }}"> {{ opt.strip() }}</label><br>
                {% endfor %}
            {% endif %}
        </div>
        {% endfor %}
        <button style="width:100%; padding:15px; background:#3498db; color:white; border:none; border-radius:10px; cursor:pointer;">إرسال الإجابات ✅</button>
    </form>
    <hr>
    <center><a href="/admin" style="color:#ccc; text-decoration:none; font-size:0.8em;">دخول الإدارة</a></center>
</div>
"""

# --- المسارات (Routes) ---

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
        return '<div dir="rtl" style="text-align:center; padding-top:100px;"><h2>دخول الإدارة</h2><form method="POST"><input type="password" name="pass" placeholder="كلمة المرور"><button>دخول</button></form></div>'
    
    with sqlite3.connect(DB_NAME) as conn:
        questions = conn.execute("SELECT * FROM questions").fetchall()
    return render_template_string(ADMIN_HTML, questions=questions)

@app.route('/admin/add', methods=['POST'])
def add_question():
    if session.get('logged_in'):
        q_text = request.form.get('q_text')
        q_type = request.form.get('q_type')
        q_options = request.form.get('q_options')
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
    return '<div dir="rtl" style="text-align:center; padding-top:100px;"><h2>شكراً لك! تم استلام إجاباتك بنجاح. 🎉</h2><a href="/">العودة</a></div>'

@app.route('/admin/responses')
def view_responses():
    if not session.get('logged_in'): return redirect(url_for('admin'))
    with sqlite3.connect(DB_NAME) as conn:
        responses = conn.execute("SELECT * FROM answers ORDER BY id DESC").fetchall()
    return f'<div dir="rtl" style="font-family:sans-serif; padding:20px;"><h2>الإجابات المستلمة 📋</h2><pre>{str(responses)}</pre><br><a href="/admin">العودة</a></div>'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
