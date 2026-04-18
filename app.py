from flask import Flask, session, redirect, url_for
from models import db, User
from admin import admin_bp # استدعاء ملف الإدارة

app = Flask(__name__)
app.secret_key = 'saudi_secret_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)

# --- الربط السحري ---
# أي رابط يبدأ بـ /admin سيروح لملف admin.py
app.register_blueprint(admin_bp, url_prefix='/admin')

@app.route('/')
def home():
    # إذا سجلت دخولك كأدمن، بيطلع لك رابط لوحة التحكم
    admin_link = ""
    if session.get('is_admin'):
        admin_link = '<br><br><a href="/admin/" style="color:gold; background:black; padding:10px; border-radius:5px; text-decoration:none;">دخول لوحة التحكم ⚙️</a>'
    
    return f'''
    <div style="direction:rtl; text-align:center; padding:50px; font-family:sans-serif;">
        <h1>هذه هي صفحتك البيضاء.. تم ربط لوحة التحكم ✅</h1>
        <p>جرب الدخول الآن.</p>
        {admin_link}
    </div>
    '''

# إنشاء قاعدة البيانات وأدمن تجريبي
with app.app_context():
    db.create_all()
    if not User.query.filter_by(email="admin@admin.com").first():
        db.session.add(User(email="admin@admin.com", password="123", is_admin=True))
        db.session.commit()

# صفحة بسيطة لتسجيل الدخول السريع للتجربة
@app.route('/dev-login')
def dev_login():
    session['user_id'] = 1
    session['is_admin'] = True
    return "تم تسجيل دخولك كمسؤول بنجاح! <a href='/'>ارجع للرئيسية</a>"

if __name__ == '__main__':
    app.run(debug=True)
