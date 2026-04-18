import random
from flask import Flask, session, redirect, url_for, request, render_template_string
from flask_mail import Mail, Message
from models import db, User

app = Flask(__name__)
app.secret_key = 'saudi_secure_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

# --- إعدادات الإيميل (Gmail مثال) ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'azx3174a@gmail.com' # إيميلك هنا
app.config['MAIL_PASSWORD'] = 'mjmkqpoxtrqwkmqf'   # باسورد التطبيق من جوجل
app.config['MAIL_DEFAULT_SENDER'] = 'your-email@gmail.com'

mail = Mail(app)
db.init_app(app)

# مخزن مؤقت للرموز (في المشاريع الكبيرة نستخدم قاعدة بيانات أو Redis)
codes_storage = {}

# --- صفحة طلب رمز التحقق ---
@app.route('/send-code', methods=['POST'])
def send_code():
    email = request.form.get('email')
    if not email: return "أدخل الإيميل أولاً"
    
    # توليد رمز من 6 أرقام
    code = str(random.randint(100000, 999999))
    codes_storage[email] = code
    
    try:
        msg = Message("رمز التحقق الخاص بك", recipients=[email])
        msg.body = f"مرحباً، رمز التحقق لإنشاء حسابك هو: {code}"
        mail.send(msg)
        return "✅ تم إرسال الرمز لبريدك الإلكتروني"
    except Exception as e:
        return f"❌ فشل الإرسال: {str(e)}"

# --- صفحة إنشاء حساب جديد ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_code = request.form.get('verify_code')

        if email in codes_storage and codes_storage[email] == user_code:
            if User.query.filter_by(email=email).first():
                message = "❌ الإيميل مسجل مسبقاً"
            else:
                new_user = User(email=email, password=password)
                db.session.add(new_user)
                db.session.commit()
                del codes_storage[email] # حذف الرمز بعد الاستخدام
                return '✅ تم التسجيل! <a href="/login">سجل دخولك</a>'
        else:
            message = "❌ رمز التحقق غير صحيح أو لم تطلبه بعد"

    return render_template_string('''
        <div style="direction:rtl; text-align:center; padding:50px; font-family:sans-serif;">
            <h2>إنشاء حساب برمز تحقق إيميل</h2>
            <p style="color:red;">{{ msg }}</p>
            
            <input id="email" type="email" placeholder="الإيميل" style="padding:10px; width:200px;">
            <button onclick="sendCode()" id="btnSend" style="padding:10px;">أرسل الرمز</button>
            <p id="status"></p>

            <form method="POST" style="margin-top:20px;">
                <input name="email" id="email_hidden" type="hidden">
                <input name="password" type="password" placeholder="كلمة المرور" required style="padding:10px; margin:5px;"><br>
                <input name="verify_code" placeholder="أدخل الرمز الذي وصلك" required style="padding:10px; margin:5px;"><br>
                <button type="submit" style="padding:10px 20px; background:green; color:white; border:none;">تأكيد وإنشاء الحساب</button>
            </form>
        </div>

        <script>
        function sendCode() {
            var email = document.getElementById('email').value;
            document.getElementById('email_hidden').value = email;
            var btn = document.getElementById('btnSend');
            btn.disabled = true; btn.innerText = "جاري الإرسال...";
            
            fetch('/send-code', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'email=' + encodeURIComponent(email)
            })
            .then(response => response.text())
            .then(data => {
                document.getElementById('status').innerText = data;
                btn.innerText = "إعادة إرسال"; btn.disabled = false;
            });
        }
        </script>
    ''', msg=message)

# --- تسجيل الدخول (كما هو) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email'], password=request.form['password']).first()
        if user:
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            return redirect('/')
    return 'صفحة الدخول (طبق كود login السابق هنا)'

@app.route('/')
def home():
    if 'user_id' not in session: return redirect('/login')
    return f"مرحباً بك! <a href='/logout'>خروج</a>"

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
