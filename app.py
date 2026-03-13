from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import os, psycopg2, base64, random
from psycopg2.extras import DictCursor

app = Flask(__name__)
app.secret_key = "eyin_profile_v51"

# !!! ضع رقمك هنا للتحقق !!!
MY_PHONE = "966550963174" 

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS settings (id SERIAL PRIMARY KEY, key TEXT UNIQUE, value TEXT)")
        cur.execute("INSERT INTO settings (key, value) VALUES ('logo', '') ON CONFLICT (key) DO NOTHING")
        cur.execute("INSERT INTO settings (key, value) VALUES ('store_name', 'eyin') ON CONFLICT (key) DO NOTHING")
        # تعديل جدول المستخدمين ليشمل الاسم
        cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username TEXT, phone TEXT UNIQUE NOT NULL, password TEXT NOT NULL)")
        cur.execute("CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, name TEXT, price TEXT, image_url TEXT, description TEXT, whatsapp TEXT, user_id INTEGER)")
        conn.commit(); cur.close(); conn.close()
    except: pass

init_db()

def get_st():
    try:
        conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT key, value FROM settings")
        res = {r['key']: r['value'] for r in cur.fetchall()}
        cur.close(); conn.close()
        return res
    except: return {'store_name': 'eyin', 'logo': ''}

# القالب مع زر الملف الشخصي
LAYOUT = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ st['store_name'] }}</title>
    <style>
        :root { --bg: #0f172a; --card: #1e293b; --text: #f8fafc; --primary: #818cf8; --border: #334155; }
        [data-theme="light"] { --bg: #ffffff; --card: #f8fafc; --text: #1e293b; --primary: #4f46e5; --border: #e2e8f0; }
        body { font-family: sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 15px; transition: 0.3s; }
        .header { display: flex; justify-content: space-between; align-items: center; max-width: 1000px; margin: auto; border-bottom: 1px solid var(--border); padding-bottom: 10px; }
        .grid { display: flex; flex-direction: column; gap: 12px; max-width: 800px; margin: 20px auto; }
        .card { background: var(--card); border-radius: 15px; padding: 12px; border: 1px solid var(--border); display: flex; flex-direction: row-reverse; align-items: center; gap: 15px; }
        .card img { width: 90px; height: 90px; border-radius: 12px; object-fit: cover; }
        .card-info { flex: 1; display: flex; flex-direction: column; text-align: right; }
        .prod-name { color: #ffffff !important; margin: 0; font-size: 1.1rem; font-weight: bold; }
        .auth-box { max-width: 380px; margin: 40px auto; text-align: center; }
        .auth-card { background: var(--card); padding: 30px; border-radius: 25px; border: 1px solid var(--border); }
        input { width: 100%; padding: 12px; margin: 10px 0; border-radius: 10px; border: 1px solid var(--border); background: var(--bg); color: var(--text); box-sizing: border-box; }
        .main-btn { width: 100%; padding: 12px; background: var(--primary); color: white; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; }
        .profile-header { text-align: center; padding: 20px; background: var(--card); border-radius: 20px; margin-bottom: 20px; border: 1px solid var(--border); }
    </style>
</head>
<body data-theme="dark">
    <div class="header">
        <div style="display:flex; align-items:center; gap:10px;">
            <h2 style="margin:0;">{{ st['store_name'] }}</h2>
        </div>
        <div style="display:flex; gap:12px; align-items:center;">
            {% if session.get('user_id') %}
                <a href="/profile" style="text-decoration:none; color:var(--text); font-size:18px;">👤</a>
                <button onclick="document.getElementById('addModal').style.display='flex'" style="background:var(--primary); border:none; color:white; padding:6px 10px; border-radius:8px; cursor:pointer;">+</button>
                <a href="/logout_user" style="color:#ef4444; text-decoration:none; font-size:12px;">خروج</a>
            {% endif %}
        </div>
    </div>
    {% block content %}{% endblock %}
</body>
</html>
"""

@app.route('/')
def index():
    if 'user_id' not in session: return redirect('/register')
    st = get_st(); conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT p.*, u.username FROM products p JOIN users u ON p.user_id = u.id ORDER BY p.id DESC")
    prods = cur.fetchall(); cur.close(); conn.close()
    
    html = '<div class="grid">'
    for p in prods:
        html += f'''<div class="card"><img src="{p['image_url']}"><div class="card-info">
        <h3 class="prod-name">{p['name']}</h3>
        <p style="margin:2px 0; font-size:12px; color:gray;">بواسطة: {p['username']}</p>
        <div style="color:#818cf8; font-weight:bold;">{p['price']} ريال</div>
        <a href="https://wa.me/{p['whatsapp']}" style="color:#22c55e; text-decoration:none; font-size:13px; margin-top:5px;">💬 تواصل</a>
        </div></div>'''
    return render_template_string(LAYOUT.replace('{% block content %}{% endblock %}', html + '</div>' + 
    '<div id="addModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); align-items:center; justify-content:center; z-index:100;"><div style="background:var(--card); padding:20px; border-radius:20px; width:90%; max-width:400px;">'
    '<h3>نشر إعلان</h3><form action="/add_public" method="post" enctype="multipart/form-data"><input type="text" name="name" placeholder="اسم المنتج" required><input type="number" name="price" placeholder="السعر" required><input type="file" name="image_file" required><button type="submit" class="main-btn">نشر</button><button type="button" onclick="this.parentElement.parentElement.parentElement.style.display=\'none\'" style="width:100%; margin-top:10px; background:none; border:none; color:gray;">إلغاء</button></form></div></div>'), st=st)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        p = "966"+request.form.get('phone')
        session['temp'] = {'u': request.form.get('username'), 'p': p, 'pw': request.form.get('password'), 'otp': str(random.randint(1000,9999))}
        return redirect('/verify')
    return render_template_string(LAYOUT.replace('{% block content %}{% endblock %}', '''
    <div class="auth-box"><div class="auth-card"><h2>إنشاء حساب</h2><form method="post">
    <input type="text" name="username" placeholder="اسم المستخدم (مثلاً: أبو فهد)" required>
    <input type="number" name="phone" placeholder="رقم الجوال 5xxxxxxxx" required>
    <input type="password" name="password" placeholder="كلمة المرور" required>
    <button type="submit" class="main-btn">سجل الآن</button></form><p>لديك حساب؟ <a href="/login">دخول</a></p></div></div>'''), st=get_st())

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if 'temp' not in session: return redirect('/register')
    otp = session['temp']['otp']; wa = f"https://wa.me/{MY_PHONE}?text=كود تفعيل حساب {session['temp']['u']}: {otp}"
    if request.method == 'POST' and request.form.get('otp') == otp:
        conn = get_db_connection(); cur = conn.cursor(); t = session['temp']
        cur.execute("INSERT INTO users (username, phone, password) VALUES (%s, %s, %s)", (t['u'], t['p'], t['pw']))
        conn.commit(); cur.close(); conn.close(); session.pop('temp'); return redirect('/login')
    return render_template_string(LAYOUT.replace('{% block content %}{% endblock %}', f'<div class="auth-box"><div class="auth-card"><h2>تفعيل</h2><a href="{wa}" target="_blank" style="background:#25d366; color:white; padding:15px; display:block; text-decoration:none; border-radius:10px; margin-bottom:15px;">اطلب الكود</a><form method="post"><input type="number" name="otp" placeholder="أدخل الكود"><button type="submit" class="main-btn">تأكيد</button></form></div></div>'), st=get_st())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        p, pw = "966"+request.form.get('phone'), request.form.get('password')
        conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT * FROM users WHERE phone=%s AND password=%s", (p, pw))
        u = cur.fetchone(); cur.close(); conn.close()
        if u: session['user_id']=u['id']; session['username']=u['username']; session['user_phone']=u['phone']; return redirect('/')
    return render_template_string(LAYOUT.replace('{% block content %}{% endblock %}', '<div class="auth-box"><div class="auth-card"><h2>دخول</h2><form method="post">966+ <input type="number" name="phone" required><input type="password" name="password" required><button type="submit" class="main-btn">دخول</button></form></div></div>'), st=get_st())

@app.route('/profile')
def profile():
    if 'user_id' not in session: return redirect('/login')
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products WHERE user_id=%s ORDER BY id DESC", (session['user_id'],))
    prods = cur.fetchall(); cur.close(); conn.close()
    
    profile_html = f'''
    <div style="max-width:800px; margin:auto;">
        <div class="profile-header">
            <div style="font-size:50px;">👤</div>
            <h2 style="margin:10px 0;">{session.get('username')}</h2>
            <p style="color:gray;">{session.get('user_phone')}</p>
        </div>
        <h3 style="padding-right:10px;">إعلاناتي ({len(prods)})</h3>
        <div class="grid">
    '''
    for p in prods:
        profile_html += f'''<div class="card"><img src="{p['image_url']}"><div class="card-info">
        <h3 class="prod-name">{p['name']}</h3><div style="color:#818cf8;">{p['price']} ريال</div>
        <form action="/delete_product" method="post" style="margin-top:10px;"><input type="hidden" name="id" value="{p['id']}"><button type="submit" style="background:none; border:1px solid #ef4444; color:#ef4444; padding:5px 10px; border-radius:8px; cursor:pointer;">حذف الإعلان 🗑️</button></form>
        </div></div>'''
    return render_template_string(LAYOUT.replace('{% block content %}{% endblock %}', profile_html + '</div></div>'), st=get_st())

@app.route('/add_public', methods=['POST'])
def add_public():
    if 'user_id' not in session: return redirect('/login')
    f = request.files['image_file']; img = f"data:{f.content_type};base64,{base64.b64encode(f.read()).decode('utf-8')}"
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO products (user_id, name, price, image_url, whatsapp) VALUES (%s, %s, %s, %s, %s)", (session['user_id'], request.form.get('name'), request.form.get('price'), img, session['user_phone']))
    conn.commit(); cur.close(); conn.close(); return redirect('/')

@app.route('/delete_product', methods=['POST'])
def delete_product():
    if 'user_id' in session:
        conn = get_db_connection(); cur = conn.cursor(); cur.execute("DELETE FROM products WHERE id=%s AND user_id=%s", (request.form.get('id'), session['user_id'])); conn.commit(); cur.close(); conn.close()
    return redirect('/profile')

@app.route('/logout_user')
def logout_user(): session.clear(); return redirect('/')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
