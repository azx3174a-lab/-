from flask import Flask, render_template_string, request, session, redirect, url_for
from flask_mail import Mail, Message
import random
import re

app = Flask(__name__)
app.secret_key = 'secure_key_99'

# --- إعدادات الإيميل (تأكد من بياناتك هنا) ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'azx3174a@gmail.com' 
app.config['MAIL_PASSWORD'] = 'iymffmyvwijjmdqt'    
mail = Mail(app)

users_db = {} 

def is_strong_pass(password):
    if len(password) < 6: return False
    has_upper = re.search(r'[A-Z]', password)
    has_symbol = re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
    return has_upper and has_symbol

common_style = '''
<style>
    body { font-family: sans-serif; background: #f0f2f5; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; direction: rtl; }
    .card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align: center; width: 85%; max-width: 350px; }
    input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; text-align: center; font-size: 16px; }
    button { width: 100%; padding: 12px; background: #222; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; margin-top: 10px; }
    .error { color: red; font-size: 12px; margin: 5px 0; }
    a { display: block; margin-top: 15px; font-size: 13px; color: #007bff; text-decoration: none; }
</style>
'''

login_html = common_style + '''
<div class="card">
    <h3>تسجيل الدخول</h3>
    <form method="POST">
        <input type="email" name="email" placeholder="الإيميل" required>
        <input type="password" name="password" placeholder="كلمة المرور" required>
        {% if error %}<p class="error">{{error}}</p>{% endif %}
        <button type="submit">دخول</button>
    </form>
    <a href="/register">ليس لديك حساب؟ اصنع واحد</a>
</div>
'''

register_html = common_style + '''
<div class="card">
    <h3>إنشاء حساب جديد</h3>
    <form method="POST">
        {% if not otp_sent %}
            <input type="email" name="email" placeholder="الإيميل" required>
            <input type="password" name="password" placeholder="كلمة المرور (حرف كبير + رمز)" required>
            {% if error %}<p class="error">{{error}}</p>{% endif %}
            <button type="submit" name="action" value="send_otp">إرسال رمز التحقق</button>
        {% else %}
            <p>تم إرسال الرمز لبريدك</p>
            <input type="text" name="otp" placeholder="أدخل الرمز" required>
            <button type="submit" name="action" value="verify_reg">تأكيد التسجيل</button>
        {% endif %}
    </form>
    <a href="/login">لديك حساب؟ سجل دخولك</a>
</div>
'''

# --- كود صفحة التقييم (اللايكات السوداء) ---
rating_html = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>منصة التقييم</title>
    <style>
        body { font-family: sans-serif; background-color: #f4f6f9; margin: 0; padding: 5px; display: block; height: auto; }
        .main-container { display: flex; flex-direction: row; justify-content: space-between; gap: 8px; width: 100%; max-width: 600px; margin: 0 auto; }
        .column { background: white; padding: 10px 0; border-radius: 12px; width: 49%; box-sizing: border-box; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        h2 { text-align: center; font-size: 13px; background: #1e1e1e; color: white; padding: 8px; border-radius: 8px; margin: 0 5px 12px 5px; }
        .row { display: flex; align-items: center; justify-content: space-around; margin-bottom: 6px; padding: 2px 0; }
        .btn-wrapper { cursor: pointer; width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; border-radius: 8px; background: rgba(0,0,0,0.02); transition: all 0.1s ease; }
        .btn-emoji { font-size: 20px; opacity: 0.15; filter: grayscale(1); transition: all 0.1s ease; }
        .btn-wrapper.active { background: #e6e6e6; box-shadow: inset 3px 3px 6px #cfcfcf, inset -3px -3px 6px #ffffff; transform: scale(0.96); }
        .btn-wrapper.active .btn-emoji { opacity: 1; filter: grayscale(1) brightness(0); }
        .index-num { font-size: 9px; color: #ddd; width: 12px; text-align: center; }
        .logout { display: block; text-align: center; margin: 20px 0; color: #999; text-decoration: none; font-size: 11px; }
    </style>
</head>
<body>
    <div class="main-container">
        <div class="column">
            <h2 contenteditable="true">الطرف الأول</h2>
            {% for i in range(30) %}
            <div class="row"><span class="index-num">{{i+1}}</span><div class="btn-wrapper" onclick="toggle(this)"><span class="btn-emoji">👍🏻</span></div><div class="btn-wrapper" onclick="toggle(this)"><span class="btn-emoji">👎🏻</span></div></div>
            {% endfor %}
        </div>
        <div class="column">
            <h2 contenteditable="true">الطرف الثاني</h2>
            {% for i in range(30) %}
            <div class="row"><span class="index-num">{{i+1}}</span><div class="btn-wrapper" onclick="toggle(this)"><span class="btn-emoji">👍🏻</span></div><div class="btn-wrapper" onclick="toggle(this)"><span class="btn-emoji">👎🏻</span></div></div>
            {% endfor %}
        </div>
    </div>
    <a href="/logout" class="logout">تسجيل الخروج</a>
    <script>function toggle(el) { el.classList.toggle('active'); }</script>
</body>
</html>
'''

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        action = request.form.get('action')
        email = request.form.get('email')
        password = request.form.get('password')
        if action == 'send_otp':
            if not is_strong_pass(password):
                return render_template_string(register_html, error="كلمة المرور ضعيفة! (حرف كبير + رمز)")
            otp = str(random.randint(100000, 999999))
            session['reg_data'] = {'email': email, 'password': password, 'otp': otp}
            msg = Message('رمز تحقق التسجيل', sender=app.config['MAIL_USERNAME'], recipients=[email])
            msg.body = f'رمزك هو: {otp}'
            mail.send(msg)
            return render_template_string(register_html, otp_sent=True)
        elif action == 'verify_reg':
            if request.form.get('otp') == session.get('reg_data')['otp']:
                users_db[session['reg_data']['email']] = session['reg_data']['password']
                return "تم التسجيل! <a href='/login'>ادخل هنا</a>"
    return render_template_string(register_html)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email in users_db and users_db[email] == password:
            session['auth'] = True
            return redirect(url_for('index'))
        return render_template_string(login_html, error="بيانات خطأ")
    return render_template_string(login_html)

@app.route('/')
def index():
    if not session.get('auth'): return redirect(url_for('login'))
    return render_template_string(rating_html)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()
