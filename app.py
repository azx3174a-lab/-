from flask import Flask, render_template_string, request, session, redirect, url_for
from flask_mail import Mail, Message
import random
import re

app = Flask(__name__)
app.secret_key = 'secure_key_99'

# --- إعدادات الإيميل ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'azx3174a@gmail.com' # إيميلك هنا
app.config['MAIL_PASSWORD'] = 'iymffmyvwijjmdqt'    # الـ 16 حرف هنا
mail = Mail(app)

# قاعدة بيانات مؤقتة في الذاكرة (ستحذف عند ريستارت السيرفر)
users_db = {} 

# دالة التحقق من قوة كلمة المرور
def is_strong_pass(password):
    if len(password) < 6: return False
    has_upper = re.search(r'[A-Z]', password)
    has_symbol = re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
    return has_upper and has_symbol

# --- الستايل الموحد للصفحات ---
common_style = '''
<style>
    body { font-family: sans-serif; background: #f0f2f5; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; direction: rtl; }
    .card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align: center; width: 85%; max-width: 350px; }
    input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; text-align: center; }
    button { width: 100%; padding: 12px; background: #222; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; margin-top: 10px; }
    .error { color: red; font-size: 12px; margin: 5px 0; }
    a { display: block; margin-top: 15px; font-size: 13px; color: #007bff; text-decoration: none; }
</style>
'''

# --- صفحة إنشاء الحساب ---
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

# --- صفحة تسجيل الدخول ---
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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        action = request.form.get('action')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if action == 'send_otp':
            if not is_strong_pass(password):
                return render_template_string(register_html, error="كلمة المرور ضعيفة! يجب أن تحتوي على حرف كبير ورمز.")
            
            otp = str(random.randint(100000, 999999))
            session['reg_data'] = {'email': email, 'password': password, 'otp': otp}
            
            msg = Message('رمز تحقق التسجيل', sender=app.config['MAIL_USERNAME'], recipients=[email])
            msg.body = f'رمز التحقق الخاص بك هو: {otp}'
            mail.send(msg)
            return render_template_string(register_html, otp_sent=True)
            
        elif action == 'verify_reg':
            user_otp = request.form.get('otp')
            reg_data = session.get('reg_data')
            if user_otp == reg_data['otp']:
                users_db[reg_data['email']] = reg_data['password']
                return "تم إنشاء الحساب بنجاح! <a href='/login'>اضغط هنا لتسجيل الدخول</a>"
            return render_template_string(register_html, otp_sent=True, error="الرمز خطأ")
            
    return render_template_string(register_html)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email in users_db and users_db[email] == password:
            session['auth'] = True
            return redirect(url_for('index'))
        return render_template_string(login_html, error="الإيميل أو كلمة المرور خطأ")
        
    return render_template_string(login_html)

@app.route('/')
def index():
    if not session.get('auth'): return redirect(url_for('login'))
    # هنا تضع كود صفحة التقييم (rating_html) السابق
    return "تم تسجيل دخولك بنجاح! (هنا تظهر صفحة اللايكات)"

if __name__ == '__main__':
    app.run()
