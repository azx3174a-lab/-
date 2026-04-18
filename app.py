from flask import Flask, session, render_template_string
from models import db, User

app = Flask(__name__)
app.secret_key = 'my_secret_key' # ضروري عشان تسجيل الدخول
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)

@app.route('/')
def home():
    return "<h1>هذه هي صفحتك البيضاء.. ابدأ الإبداع الآن 🚀</h1>"

# إنشاء قاعدة البيانات تلقائياً
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
