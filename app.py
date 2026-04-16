from flask import Flask, render_template_string, request, session, redirect, url_for
from flask_mail import Mail, Message
import random

app = Flask(__name__)
app.secret_key = 'my_secret_123' # مفتاح تشفير الجلسة

# --- إعدادات الإيميل (تأكد من الـ 16 حرف بدون مسافات) ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'azx3174a@gmail.com' # إيميلك هنا
app.config['MAIL_PASSWORD'] = 'iymffmyvwijjmdqt'    # الـ 16 حرف هنا
mail = Mail(app)

# --- واجهة تسجيل الدخول ---
login_html = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تسجيل دخول</title>
    <style>
        body { font-family: sans-serif; background: #f0f2f5; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align: center; width: 85%; max-width: 350px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; text-align: center; font-size: 16px; }
        button { width: 100%; padding: 12px; background: #222; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
        .error { color: red; font-size: 12px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="card">
        <h3>قفل الوصول</h3>
        <form method="POST">
            {% if not otp_sent %}
                <p>أدخل إيميلك لإرسال رمز التحقق</p>
                <input type="email" name="user_email" placeholder="example@gmail.com" required>
                <button type="submit" name="action" value="send">إرسال الرمز</button>
            {% else %}
                <p>تم إرسال الرمز لإيميلك</p>
                <input type="text" name="otp" placeholder="أدخل الرمز" required>
                <button type="submit" name="action" value="verify">تحقق ودخول</button>
            {% endif %}
        </form>
    </div>
</body>
</html>
'''

# --- واجهة صفحة التقييم (اللايكات السوداء) ---
rating_html = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>منصة التقييم</title>
    <style>
        body { font-family: sans-serif; background-color: #f4f6f9; margin: 0; padding: 5px; }
        .main-container { display: flex; flex-direction: row; justify-content: space-between; gap: 8px; width: 100%; max-width: 600px; margin: 0 auto; }
        .column { background: white; padding: 10px 0; border-radius: 12px; width: 49%; box-sizing: border-box; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        h2 { text-align: center; font-size: 13px; background: #1e1e1e; color: white; padding: 8px; border-radius: 8px; margin: 0 5px 12px 5px; }
        .row { display: flex; align-items: center; justify-content: space-around; margin-bottom: 6px; padding: 2px 0; }
        .btn-wrapper { cursor: pointer; width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; border-radius: 8px; background: rgba(0,0,0,0.02); transition: all 0.1s ease; }
        .btn-emoji { font-size: 20px; opacity: 0.15; filter: grayscale(1); transition: all 0.1s ease; }
        .btn-wrapper.active { background: #e6e6e6; box-shadow: inset 3px 3px 6px #cfcfcf, inset -3px -3px 6px #ffffff; transform: scale(0.96); }
        .btn-wrapper.active .btn-emoji { opacity: 1; filter: grayscale(1) brightness(0); }
        .index-num { font-size: 9px; color: #ddd; width: 12px; text-align: center; }
        .logout { display: block; text-align: center; margin-top: 20px; color: #999; text-decoration: none; font-size: 11px; }
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    otp_sent = session.get('otp_sent', False)
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'send':
            email = request.form.get('user_email')
            otp = str(random.randint(100000, 999999))
            session['otp'] = otp
            try:
                msg = Message('رمز الدخول لموقعك', sender=app.config['MAIL_USERNAME'], recipients=[email])
                msg.body = f'رمز التحقق الخاص بك هو: {otp}'
                mail.send(msg)
                session['otp_sent'] = True
                return render_template_string(login_html, otp_sent=True)
            except Exception as e:
                return f"حدث خطأ في الإرسال: {e}"
        
        elif action == 'verify':
            if request.form.get('otp') == session.get('otp'):
                session['auth'] = True
                return redirect(url_for('index'))
            return "الرمز غير صحيح، حاول مرة أخرى."
            
    return render_template_string(login_html, otp_sent=otp_sent)

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
