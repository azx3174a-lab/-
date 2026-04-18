from flask import Flask, session, redirect, url_for, request, render_template_string
from models import db, User, Settings
from admin import admin_bp
from users import users_bp

app = Flask(__name__)
app.secret_key = 'super_secret_key_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)

# تسجيل الأقسام (Blueprints)
app.register_blueprint(admin_bp)
app.register_blueprint(users_bp)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email'], password=request.form['password']).first()
        if user:
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            return redirect(url_for('users.index'))
    return '''<form method="POST" style="text-align:center; padding:50px;">
                <input name="email" placeholder="الإيميل"><br>
                <input name="password" type="password" placeholder="الباسورد"><br>
                <button type="submit">دخول</button>
              </form>'''

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

with app.app_context():
    db.create_all()
    # تأكد من وجود أدمن
    if not User.query.filter_by(email="admin@admin.com").first():
        db.session.add(User(email="admin@admin.com", password="123", is_admin=True))
        db.session.add(Settings())
        db.session.commit()

if __name__ == '__main__':
    app.run()
