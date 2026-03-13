from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import os, psycopg2, base64, random
from psycopg2.extras import DictCursor

app = Flask(__name__)
app.secret_key = "eyin_stable_v26_fixed"

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS settings (id SERIAL PRIMARY KEY, key TEXT UNIQUE, value TEXT)")
    cur.execute("INSERT INTO settings (key, value) VALUES ('logo', '') ON CONFLICT (key) DO NOTHING")
    cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, phone TEXT UNIQUE NOT NULL, password TEXT NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, user_id INTEGER, name TEXT, price TEXT, image_url TEXT, description TEXT, whatsapp TEXT)")
    conn.commit(); cur.close(); conn.close()

init_db()

# القالب الموحد للوضع الداكن (بسيط جداً لمنع الأخطاء)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root { --bg: #ffffff; --card: #f8fafc; --text: #1e293b; --primary: #4f46e5; --btn-bg: #000; --btn-text: #fff; }
        [data-theme="dark"] { --bg: #0f172a; --card: #1e293b; --text: #f8fafc; --primary: #818cf8; --btn-bg: #fff; --btn-text: #000; }
        body { font-family: sans-serif; background: var(--bg); color: var(--text); padding: 15px; transition: 0.3s; }
        .header { display: flex; justify-content: space-between; max-width: 1000px; margin: auto; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; max-width: 1000px; margin: 20px auto; }
        .card { background: var(--card); border-radius: 15px; padding: 15px; border: 1px solid #ddd; }
        .theme-btn { background: var(--btn-bg); color: var(--btn-text); border: none; width: 35px; height: 35px; border-radius: 50%; cursor: pointer; }
    </style>
</head>
<body data-theme="light">
    <div class="header">
        <h2>متجر عيـن</h2>
        <div style="display:flex; gap:10px; align-items:center;">
            {% if session.get('user_id') %}
                <a href="/my-ads">إعلاناتي</a>
                <a href="/logout_user" style="color:red;">خروج</a>
            {% else %}
                <a href="/login">دخول</a>
            {% endif %}
            <button class="theme-btn" onclick="toggleTheme()" id="t-btn">🌙</button>
        </div>
    </div>
    {% block content %}{% endblock %}
    <script>
        function toggleTheme() {
            const b = document.body;
            const t = b.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            b.setAttribute('data-theme', t);
            localStorage.setItem('theme', t);
            document.getElementById('t-btn').innerText = t === 'dark' ? '☀️' : '🌙';
        }
        document.body.setAttribute('data-theme', localStorage.getItem('theme') || 'light');
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products ORDER BY id DESC"); prods = cur.fetchall(); cur.close(); conn.close()
    return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}', '''
    <div class="grid">
        {% for p in prods %}
        <div class="card">
            <img src="{{p['image_url']}}" style="width:100%; height:180px; object-fit:contain;">
            <h3>{{p['name']}}</h3>
            <p>{{p['price']}} ريال</p>
            <a href="https://wa.me/{{p['whatsapp']}}" style="background:green; color:white; display:block; text-align:center; padding:10px; border-radius:10px; text-decoration:none;">واتساب</a>
        </div>
        {% endfor %}
    </div>
    '''), prods=prods)

# لوحة التحكم السرية
@app.route('/eyin-control', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == '317400': session['admin'] = True
        elif session.get('admin') and request.form.get('action') == 'delete':
            conn = get_db_connection(); cur = conn.cursor()
            cur.execute("DELETE FROM products WHERE id = %s", (request.form.get('id'),))
            conn.commit(); cur.close(); conn.close()
            return redirect('/eyin-control')
    if not session.get('admin'):
        return '<div dir="rtl" style="text-align:center; padding-top:100px;">🔐 <form method="post"><input type="password" name="password"><button type="submit">دخول</button></form></div>'
    
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products ORDER BY id DESC"); prods = cur.fetchall(); cur.close(); conn.close()
    return render_template_string('''<div dir="rtl"><h2>لوحة الإدارة</h2><hr>{% for p in prods %}<div>{{p['name']}} <form method="post" style="display:inline;"><input type="hidden" name="action" value="delete"><input type="hidden" name="id" value="{{p['id']}}"><button type="submit">حذف</button></form></div>{% endfor %}<br><a href="/">عودة</a></div>''', prods=prods)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        p, pw = "966"+request.form.get('phone'), request.form.get('password')
        conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT * FROM users WHERE phone=%s AND password=%s", (p, pw))
        u = cur.fetchone(); cur.close(); conn.close()
        if u: session['user_id']=u['id']; session['user_phone']=u['phone']; return redirect('/')
    return render_template_string(HTML_TEMPLATE.replace('{% block content %}{% endblock %}', '<div style="text-align:center; padding:50px;"><form method="post">966+ <input type="number" name="phone" required><br><input type="password" name="password" required><br><button type="submit">دخول</button></form></div>'))

@app.route('/logout_user')
def logout_user(): session.clear(); return redirect('/')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
