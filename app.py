from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import os, psycopg2, base64, random
from psycopg2.extras import DictCursor

app = Flask(__name__)
app.secret_key = "eyin_fix_v42_final"

# !!! ضع رقم واتسابك هنا !!!
ADMIN_WHATSAPP = "966550963174" 

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS settings (id SERIAL PRIMARY KEY, key TEXT UNIQUE, value TEXT)")
        cur.execute("INSERT INTO settings (key, value) VALUES ('logo', '') ON CONFLICT (key) DO NOTHING")
        cur.execute("INSERT INTO settings (key, value) VALUES ('store_name', 'eyin') ON CONFLICT (key) DO NOTHING")
        cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, phone TEXT UNIQUE NOT NULL, password TEXT NOT NULL)")
        cur.execute("CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, name TEXT, price TEXT, image_url TEXT, description TEXT, whatsapp TEXT, user_id INTEGER)")
        conn.commit(); cur.close(); conn.close()
    except: pass

init_db()

def get_safe_settings():
    try:
        conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT key, value FROM settings")
        rows = cur.fetchall(); cur.close(); conn.close()
        res = {r['key']: r['value'] for r in rows}
        return res
    except: return {'store_name': 'eyin', 'logo': ''}

# القالب الأساسي - تم تبسيطه تماماً لمنع التعليق
HTML_LAYOUT = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ st['store_name'] }}</title>
    <style>
        :root { --bg: #0f172a; --card: #1e293b; --text: #f8fafc; --primary: #818cf8; }
        body { font-family: sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 15px; }
        .header { display: flex; justify-content: space-between; align-items: center; max-width: 1000px; margin: auto; border-bottom: 1px solid #334155; padding-bottom: 10px; }
        .auth-box { max-width: 380px; margin: 40px auto; text-align: center; }
        .slogan { font-size: 1.1rem; font-weight: bold; margin-bottom: 20px; padding: 15px; border: 2px solid var(--primary); border-radius: 15px; color: var(--primary); }
        .auth-card { background: var(--card); padding: 25px; border-radius: 20px; border: 1px solid #334155; }
        input, textarea { width: 100%; padding: 12px; margin: 8px 0; border-radius: 10px; border: 1px solid #334155; background: #0f172a; color: #fff; box-sizing: border-box; }
        .main-btn { width: 100%; padding: 12px; background: var(--primary); color: white; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; }
        .alert { background: #ef4444; color: white; padding: 10px; border-radius: 10px; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="header">
        <div style="display:flex; align-items:center; gap:10px;">
            {% if st['logo'] %}<img src="{{ st['logo'] }}" style="width:35px; height:35px; border-radius:50%;">{% endif %}
            <h2 style="margin:0;">{{ st['store_name'] }}</h2>
        </div>
        {% if session.get('user_id') %}
            <a href="/logout_user" style="color:red; text-decoration:none; font-size:12px;">خروج</a>
        {% endif %}
    </div>

    <div style="max-width:380px; margin:auto; margin-top:20px;">
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for message in messages %}
              <div class="alert">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}
    </div>

    {% block content %}{% endblock %}
</body>
</html>
"""

@app.route('/')
def index():
    if 'user_id' not in session: return redirect('/register')
    st = get_safe_settings()
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products ORDER BY id DESC"); prods = cur.fetchall(); cur.close(); conn.close()
    return render_template_string(HTML_LAYOUT.replace('{% block content %}{% endblock %}', '''
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; max-width: 1000px; margin: 20px auto;">
        {% for p in prods %}
        <div style="background: var(--card); border-radius: 20px; padding: 15px; border: 1px solid #334155;">
            <img src="{{p['image_url']}}" style="width:100%; height:180px; object-fit:contain;">
            <h3>{{p['name']}}</h3>
            <p style="color:var(--primary); font-weight:bold;">{{p['price']}} ريال</p>
            <a href="https://wa.me/{{p['whatsapp']}}" style="background:#22c55e; color:white; display:block; text-align:center; padding:10px; border-radius:10px; text-decoration:none; font-weight:bold;">واتساب</a>
        </div>
        {% endfor %}
    </div>
    '''), st=st, prods=prods)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        p = "966"+request.form.get('phone')
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE phone = %s", (p,))
        if cur.fetchone():
            flash('عذراً، هذا الرقم مسجل مسبقاً، سجل دخولك')
            cur.close(); conn.close(); return redirect('/login')
        cur.close(); conn.close()
        session['temp'] = {'p': p, 'pw': request.form.get('password'), 'otp': str(random.randint(1000,9999))}
        return redirect('/verify')
    return render_template_string(HTML_LAYOUT.replace('{% block content %}{% endblock %}', '''
    <div class="auth-box">
        <div class="slogan">عـيـن فراش لك و عـيـن لحافي</div>
        <div class="auth-card">
            <h2>إنشاء حساب</h2>
            <form method="post">
                966+ <input type="number" name="phone" placeholder="5xxxxxxxx" required>
                <input type="password" name="password" placeholder="كلمة المرور" required>
                <button type="submit" class="main-btn">تسجيل</button>
            </form>
            <p>لديك حساب؟ <a href="/login" style="color:var(--primary);">دخول</a></p>
        </div>
    </div>
    '''), st=get_safe_settings())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        p, pw = "966"+request.form.get('phone'), request.form.get('password')
        conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT * FROM users WHERE phone=%s AND password=%s", (p, pw))
        u = cur.fetchone(); cur.close(); conn.close()
        if u: session['user_id']=u['id']; session['user_phone']=u['phone']; return redirect('/')
        flash('الرقم أو كلمة المرور خطأ')
    return render_template_string(HTML_LAYOUT.replace('{% block content %}{% endblock %}', '''
    <div class="auth-box">
        <div class="slogan">عـيـن فراش لك و عـيـن لحافي</div>
        <div class="auth-card">
            <h2>دخول</h2>
            <form method="post">
                966+ <input type="number" name="phone" required>
                <input type="password" name="password" required>
                <button type="submit" class="main-btn">دخول</button>
            </form>
        </div>
    </div>
    '''), st=get_safe_settings())

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if 'temp' not in session: return redirect('/register')
    otp = session['temp']['otp']
    if request.method == 'POST':
        if request.form.get('otp') == otp:
            conn = get_db_connection(); cur = conn.cursor(); t = session['temp']
            cur.execute("INSERT INTO users (phone, password) VALUES (%s, %s)", (t['p'], t['pw']))
            conn.commit(); cur.close(); conn.close(); session.pop('temp')
            return redirect('/login')
    return render_template_string(HTML_LAYOUT.replace('{% block content %}{% endblock %}', f'''
    <div class="auth-box"><div class="auth-card">
        <h2>التحقق</h2>
        <a href="https://wa.me/{ADMIN_WHATSAPP}?text=كود:{otp}" target="_blank" style="background:#25d366; color:white; padding:12px; text-decoration:none; border-radius:10px; display:block; margin-bottom:10px;">اطلب الكود</a>
        <form method="post"><input type="number" name="otp" required><button type="submit" class="main-btn">تأكيد</button></form>
    </div></div>
    '''), st=get_safe_settings())

@app.route('/eyin-control', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == '317400': session['admin']=True
        elif session.get('admin'):
            conn = get_db_connection(); cur = conn.cursor()
            a = request.form.get('action')
            if a == 'update_logo':
                f = request.files['logo_file']; img = f"data:{f.content_type};base64,{base64.b64encode(f.read()).decode('utf-8')}"
                cur.execute("UPDATE settings SET value=%s WHERE key='logo'", (img,))
            elif a == 'update_name': cur.execute("UPDATE settings SET value=%s WHERE key='store_name'", (request.form.get('store_name'),))
            elif a == 'delete': cur.execute("DELETE FROM products WHERE id=%s", (request.form.get('id'),))
            conn.commit(); cur.close(); conn.close(); return redirect('/eyin-control')
    if not session.get('admin'): return '<form method="post">🔐 <input type="password" name="password"><button type="submit">دخول</button></form>'
    st = get_safe_settings(); conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products ORDER BY id DESC"); prods = cur.fetchall(); cur.close(); conn.close()
    return render_template_string('''<div dir="rtl" style="padding:20px; background:white; color:black;"><h2>الإدارة</h2><form method="post" enctype="multipart/form-data"><input type="hidden" name="action" value="update_logo"><input type="file" name="logo_file"><button type="submit">تحديث الشعار</button></form><hr><form method="post"><input type="hidden" name="action" value="update_name"><input type="text" name="store_name" value="{{st['store_name']}}"><button type="submit">حفظ الاسم</button></form><hr>{% for p in prods %}<div>{{p['name']}} <form method="post" style="display:inline;"><input type="hidden" name="action" value="delete"><input type="hidden" name="id" value="{{p['id']}}"><button type="submit">حذف</button></form></div>{% endfor %}</div>''', st=st, prods=prods)

@app.route('/logout_user')
def logout_user(): session.clear(); return redirect('/')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
