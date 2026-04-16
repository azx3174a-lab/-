from flask import Flask, render_template_string, request, session, redirect, url_for
from flask_mail import Mail, Message
import random

app = Flask(__name__)
app.secret_key = 'super-secret-key'

# --- إعدادات الإيميل المرسل (حط بياناتك هنا عشان النظام يرسل للناس) ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'azx3174@gmail.com' # إيميلك اللي بيرسل للناس
app.config['MAIL_PASSWORD'] = 'fldnzsuiguxsajux' # الرمز الـ 16 حرف اللي بتجيبه من جوجل
mail = Mail(app)

# --- واجهة تسجيل الدخول ---
login_page = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تسجيل دخول</title>
    <style>
        body { font-family: sans-serif; background: #f0f2f5; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align: center; width: 85%; max-width: 350px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; text-align: center; }
        button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h3>مرحباً بك</h3>
        <form method="POST">
            {% if not otp_sent %}
                <p>أدخل إيميلك ليصلك رمز التحقق</p>
                <input type="email" name="user_email" placeholder="email@example.com" required>
                <button type="submit" name="step" value="send">إرسال الرمز</button>
            {% else %}
                <p>تم إرسال الرمز إلى إيميلك</p>
                <input type="text" name="otp" placeholder="أدخل الرمز المكون من 6 أرقام" required>
                <button type="submit" name="step" value="verify">دخول</button>
            {% endif %}
        </form>
    </div>
</body>
</html>
'''

# (باقي كود صفحة التقييم والراوتات هو نفسه اللي فوق)
