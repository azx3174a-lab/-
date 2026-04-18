from flask import Flask, session, redirect, url_for, request, render_template_string
from models import db, User

app = Flask(__name__)
app.secret_key = 'saudi_hero_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)

# --- لوحة التحكم (مدمجة) ---
@app.route('/admin/')
def admin_dashboard():
    if not session.get('is_admin'):
        return "⚠️ غير مسموح لك بالدخول", 403
    
    users_count = User.query.count()
    return render_template_string('''
        <div style="direction:rtl; text-align:center; font-family:sans-serif; padding:50px;">
            <h1>لوحة تحكم المدير 🛠️</h1>
            <p>عدد المستخدمين في القاعدة: {{ count }}</p>
            <hr>
            <a href="/">العودة للموقع</a> | <a href="/logout">تسجيل خروج</a>
        </div>
    ''', count=users_count)

# --- الصفحة الرئيسية ---
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect('/login')
    
    admin_btn = ""
    if session.get('is_admin'):
        admin_btn = '<br><br><a href="/admin/" style="background:gold; padding:10px; color:black; text-decoration:none;">دخول لوحة التحكم</a>'
    
    return f'''
        <div style="direction:rtl; text-align:center; padding:50px; font-family:sans-serif;">
            <h1>أهلاً بك في الصفحة الرئيسية 👋</h1>
            {admin_btn}
            <br><br><a href="/logout">خروج</a>
        </div>
    '''

# --- تسجيل الدخول ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            return redirect('/')
    return '''
        <div style="direction:rtl; text-align:center; padding:50px;">
            <form method="POST">
                <input name="email" placeholder="الإيميل" required><br><br>
                <input name="password" type="password" placeholder="الباسورد" required><br><br>
                <button type="submit">دخول</button>
            </form>
        </div>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# إنشاء البيانات الأساسية
with app.app_context():
    db.create_all()
    if not User.query.filter_by(email="admin@admin.com").first():
        db.session.add(User(email="admin@admin.com", password="123", is_admin=True))
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
