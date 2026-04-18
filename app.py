from flask import Flask, session, redirect, url_for, request, render_template_string
from models import db, User, Settings
from admin import admin_bp
from users import users_bp

app = Flask(__name__)
app.secret_key = 'super_secret_key_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)

# تسجيل الأقسام مع روابط واضحة
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(users_bp)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email'], password=request.form['password']).first()
        if user:
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            if user.is_admin:
                return redirect('/admin/') # يوديك للوحة التحكم غصب
            return redirect(url_for('users.index'))
    return '''<div style="direction:rtl; text-align:center; padding:50px; font-family:sans-serif;">
                <h2>تسجيل الدخول</h2>
                <form method="POST">
                    <input name="email" placeholder="الإيميل" style="padding:10px; margin:5px;"><br>
                    <input name="password" type="password" placeholder="الباسورد" style="padding:10px; margin:5px;"><br>
                    <button type="submit" style="padding:10px 20px; background:#222; color:#fff; border:none; border-radius:5px;">دخول</button>
                </form>
              </div>'''

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

with app.app_context():
    db.create_all()
    if not User.query.filter_by(email="admin@admin.com").first():
        db.session.add(User(email="admin@admin.com", password="123", is_admin=True))
        db.session.add(Settings())
        db.session.commit()

if __name__ == '__main__':
    app.run()
