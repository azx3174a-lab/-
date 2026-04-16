from flask import Flask, render_template_string, request, session, redirect, url_for
from flask_mail import Mail, Message
import random

app = Flask(__name__)
app.secret_key = 'some_secret_key'

# --- إعدادات الإيميل ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'azx3174a@gmail.com'
app.config['MAIL_PASSWORD'] = 'iymffmyvwijjmdqt'
mail = Mail(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    otp_sent = session.get('otp_sent', False)
    if request.method == 'POST':
        step = request.form.get('step')
        if step == 'send':
            email = request.form.get('email')
            otp = str(random.randint(100000, 999999))
            session['otp'] = otp
            try:
                msg = Message('رمز التحقق', sender=app.config['MAIL_USERNAME'], recipients=[email])
                msg.body = f'رمزك هو: {otp}'
                mail.send(msg)
                session['otp_sent'] = True
                return render_template_string(login_html, otp_sent=True)
            except Exception as e:
                return f"خطأ في الإرسال: تأكد من الـ 16 حرف والإيميل. الخطأ: {e}"
        
        elif step == 'verify':
            if request.form.get('otp') == session.get('otp'):
                session['auth'] = True
                return redirect(url_for('index'))
            return "الرمز خطأ!"
    return render_template_string(login_html, otp_sent=otp_sent)

@app.route('/')
def index():
    if not session.get('auth'): return redirect(url_for('login'))
    return render_template_string(rating_html)

# --- هنا تضع أكواد الـ HTML (login_html و rating_html) اللي أعطيتك إياها سابقاً ---

if __name__ == '__main__':
    app.run()
