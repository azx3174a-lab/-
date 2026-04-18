import random
from flask import Flask, session, redirect, url_for, request, render_template_string
from flask_mail import Mail, Message
from models import db, User

app = Flask(__name__)
app.secret_key = 'saudi_secure_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

# --- إعدادات الإيميل (Gmail مثال) ---
# ملاحظة: لازم تطلع "كلمة مرور التطبيق" من جوجل عشان يشتغل الإرسال
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'azx3174a@gmail.com' # إيميلك هنا
app.config['MAIL_PASSWORD'] = 'mjmkqpoxtrqwkmqf'   # باسورد التطبيق من جوجل
app.config['MAIL_DEFAULT_SENDER'] = 'your-email@gmail.com'

mail = Mail(app)
db.init_app(app)

codes_storage = {}

# --- ستايل مشترك للصفحات ---
STYLE = '''
<style>
    body { direction: rtl; font-family: sans-serif; background: #f4f7f6; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
    .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: 100%; max-width: 350px; text-align: center; }
    input { width: 90%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 6px; }
    button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; }
    button:disabled { background: #ccc; }
    a { color: #007bff; text-decoration: none; font-size: 14px; }
    .error { color: red; font-size: 14px; margin-bottom: 10px; }
</style>
'''

# --- إرسال الرمز للإيميل ---
@app.route('/send-code', methods=['POST'])
def send_code():
    email = request.form.get('email')
    if not email: return "أدخل الإيميل"
    code = str(random.randint(100000, 999999))
    codes_storage[email] = code
    try:
        msg = Message("رمز التحقق الخاص بك", recipients=[email])
        msg.body = f"مرحباً، رمز التحقق لإنشاء حسابك هو: {code}"
        mail.send(msg)
        return "✅ تم إرسال الرمز لبريدك"
    except: return "❌ فشل الإرسال (تأكد من إعدادات الإيميل)"

# --- إنشاء حساب ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ""
    if request.method == 'POST':
        email, pw, code = request.form.get('email'), request.form.get('password'), request.form.get('verify_code')
        if email in codes_storage and codes_storage[email] == code:
            if not User.query.filter_by(email=email).first():
                db.session.add(User(email=email, password=pw))
                db.session.commit()
                return redirect(url_for('login'))
            msg = "الإيميل مسجل مسبقاً"
        else: msg = "رمز التحقق غير صحيح"
    
    return render_template_string(STYLE + '''
        <div class="card">
            <h2>إنشاء حساب</h2>
            <p class="error">{{ m }}</p>
            <input id="em" type="email" placeholder="الإيميل">
            <button onclick="send()" id="btn">أرسل الرمز</button>
            <form method="POST" style="margin-top:10px;">
                <input name="email" id="em_h" type="hidden">
                <input name="password" type="password" placeholder="كلمة المرور" required>
                <input name="verify_code" placeholder="رمز التحقق من الإيميل" required>
                <button type="submit" style="background: #28a745;">تأكيد التسجيل</button>
            </form>
            <br><a href="/login">لديك حساب؟ دخول</a>
        </div>
        <script>
        function send() {
            var e = document.getElementById('em').value;
            document.getElementById('em_h').value = e;
            fetch('/send-code', {method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded'}, body: 'email='+encodeURIComponent(e)})
            .then(r => r.text()).then(d => alert(d));
        }
        </script>
    ''', m=msg)

# --- تسجيل الدخول ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ""
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email'], password=request.form['password']).first()
        if user:
            session['user_id'], session['is_admin'] = user.id, user.is_admin
            return redirect(url_for('home'))
        msg = "خطأ في الإيميل أو الباسورد"
    
    return render_template_string(STYLE + '''
        <div class="card">
            <h2>تسجيل الدخول</h2>
            <p class="error">{{ m }}</p>
            <form method="POST">
                <input name="email" type="email" placeholder="الإيميل" required>
                <input name="password" type="password" placeholder="كلمة المرور" required>
                <button type="submit">دخول</button>
            </form>
            <br><a href="/register">ليس لديك حساب؟ سجل الآن</a>
        </div>
    ''', m=msg)

@app.route('/')
def home():
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    btn = '<br><a href="/admin/" style="background:gold;padding:10px;display:inline-block;border-radius:5px;color:black;">لوحة التحكم</a>' if session.get('is_admin') else ""
    return render_template_string(STYLE + f'<div class="card"><h3>أهلاً {user.email}</h3>{btn}<br><br><a href="/logout">خروج</a></div>')

@app.route('/admin/')
def admin():
    if not session.get('is_admin'): return "ممنوع", 403
    return render_template_string(STYLE + '<div class="card"><h2>لوحة التحكم 🛠️</h2><a href="/">الرئيسية</a></div>')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

with app.app_context():
    db.create_all()
    if not User.query.filter_by(email="admin@admin.com").first():
        db.session.add(User(email="admin@admin.com", password="123", is_admin=True))
        db.session.commit()
