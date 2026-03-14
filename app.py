from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import os, psycopg2, base64, random
from psycopg2.extras import DictCursor

app = Flask(__name__)
app.secret_key = "eyin_master_v63_final"

# !!! ضع رقمك هنا للتحقق !!!
MY_PHONE = "966550963174"  

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS settings (id SERIAL PRIMARY KEY, key TEXT UNIQUE, value TEXT)")
        cur.execute("INSERT INTO settings (key, value) VALUES ('store_name', 'eyin') ON CONFLICT (key) DO NOTHING")
        cur.execute("INSERT INTO settings (key, value) VALUES ('logo', '') ON CONFLICT (key) DO NOTHING")
        cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username TEXT, phone TEXT UNIQUE NOT NULL, password TEXT NOT NULL, is_banned BOOLEAN DEFAULT FALSE)")
        cur.execute("CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, name TEXT, price TEXT, image_url TEXT, description TEXT, whatsapp TEXT, user_id INTEGER)")
        
        try:
            cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS username TEXT")
            cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_banned BOOLEAN DEFAULT FALSE")
            cur.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS description TEXT")
        except: conn.rollback()
            
        conn.commit(); cur.close(); conn.close()
    except Exception as e: print(f"Init Error: {e}")

init_db()

def get_st():
    try:
        conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT key, value FROM settings")
        res = {r['key']: r['value'] for r in cur.fetchall()}
        cur.close(); conn.close()
        return res
    except: return {'store_name': 'eyin', 'logo': ''}

LAYOUT = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ st['store_name'] }}</title>
    <style>
        :root { --bg: #0f172a; --card: #1e293b; --text: #f8fafc; --primary: #818cf8; --border: #334155; }
        [data-theme="light"] { --bg: #ffffff; --card: #f8fafc; --text: #1e293b; --primary: #4f46e5; --border: #e2e8f0; }
        body { font-family: sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 15px; transition: 0.3s; min-height: 100vh; }
        .header { display: flex; justify-content: space-between; align-items: center; max-width: 1000px; margin: auto; border-bottom: 1px solid var(--border); padding-bottom: 10px; }
        .grid { display: flex; flex-direction: column; gap: 12px; max-width: 800px; margin: 20px auto; }
        .card { background: var(--card); border-radius: 15px; padding: 12px; border: 1px solid var(--border); display: flex; flex-direction: row-reverse; align-items: center; gap: 15px; }
        .card img { width: 95px; height: 95px; border-radius: 12px; object-fit: cover; background: #2d3748; }
        .card-info { flex: 1; display: flex; flex-direction: column; text-align: right; overflow: hidden; }
        .prod-name { color: var(--text) !important; margin: 0; font-size: 1.1rem; font-weight: bold; }
        .prod-desc { font-size: 0.85rem; color: gray; margin: 3px 0; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
        .main-btn { width: 100%; padding: 12px; background: var(--primary); color: white; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; margin-top: 10px; }
        input, textarea { width: 100%; padding: 12px; margin: 8px 0; border-radius: 10px; border: 1px solid var(--border); background: var(--bg); color: var(--text); box-sizing: border-box; font-family: inherit; }
        .admin-table { width: 100%; border-collapse: collapse; margin-top: 15px; background: var(--card); color: var(--text); font-size: 12px; border-radius: 10px; overflow: hidden; }
        .admin-table th, .admin-table td { padding: 10px; border: 1px solid var(--border); text-align: center; }
    </style>
</head>
<body data-theme="dark">
    <div class="header">
        <div style="display:flex; align-items:center; gap:10px;">
            {% if st['logo'] %}<img src="{{ st['logo'] }}" style="width:35px; height:35px; border-radius:50%; object-fit:cover;">{% endif %}
            <h2 style="margin:0;">{{ st['store_name'] }}</h2>
        </div>
        <div style="display:flex; gap:12px; align-items:center;">
            {% if session.get('user_id') %}
                <a href="/profile" style="text-decoration:none; font-size:20px;">👤</a>
                <button onclick="document.getElementById('addModal').style.display='flex'" style="background:var(--primary); color:white; border:none; padding:5px 10px; border-radius:8px; cursor:pointer;">+</button>
            {% endif %}
            <button onclick="document.body.setAttribute('data-theme', document.body.getAttribute('data-theme')==='dark'?'light':'dark')" style="cursor:pointer; border:none; background:none; font-size:18px;">🌙</button>
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
        desc = p['description'] if p['description'] else ""
        html += f'''<div class="card"><img src="{p['image_url']}"><div class="card-info">
        <h3 class="prod-name">{p['name']}</h3>
        <p class="prod-desc">{desc}</p>
        <p style="margin:2px 0; font-size:11px; color:gray;">بواسطة: {p['username']}</p>
        <div style="color:var(--primary); font-weight:bold;">{p['price']} ريال</div>
        <a href="https://wa.me/{p['whatsapp']}" style="color:#22c55e; text-decoration:none; font-size:13px; font-weight:bold; margin-top:5px;">💬 تواصل</a>
        </div></div>'''
    return render_template_string(LAYOUT.replace('{% block content %}{% endblock %}', html + '</div>' + 
    '<div id="addModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); align-items:center; justify-content:center; z-index:100;"><div style="background:var(--card); padding:20px; border-radius:20px; width:90%; max-width:400px;">'
    '<h3>نشر إعلان جديد</h3><form action="/add_public" method="post" enctype="multipart/form-data">'
    '<input type="text" name="name" placeholder="المنتج" required>'
    '<textarea name="description" placeholder="وصف المنتج (اختياري)" rows="3"></textarea>'
    '<input type="number" name="price" placeholder="السعر" required>'
    '<input type="file" name="image_file" required>'
    '<button type="submit" class="main-btn">نشر</button><button type="button" onclick="document.getElementById(\'addModal\').style.display=\'none\'" style="width:100%; background:none; border:none; color:gray; cursor:pointer;">إلغاء</button></form></div></div>'), st=st)

# لوحة التحكم وباقي المسارات تظل كما هي لضمان استقرار النظام
@app.route('/eyin-control', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == '317400': session['admin']=True
        elif session.get('admin'):
            conn = get_db_connection(); cur = conn.cursor(); a = request.form.get('action'); u_id = request.form.get('user_id')
            if a == 'update_settings':
                cur.execute("UPDATE settings SET value=%s WHERE key='store_name'", (request.form.get('store_name'),))
                if 'logo_file' in request.files and request.files['logo_file'].filename != '':
                    f = request.files['logo_file']; img = f"data:{f.content_type};base64,{base64.b64encode(f.read()).decode('utf-8')}"; cur.execute("UPDATE settings SET value=%s WHERE key='logo'", (img,))
            elif a == 'ban_user': cur.execute("UPDATE users SET is_banned=TRUE WHERE id=%s", (u_id,))
            elif a == 'unban_user': cur.execute("UPDATE users SET is_banned=FALSE WHERE id=%s", (u_id,))
            elif a == 'delete_user': cur.execute("DELETE FROM products WHERE user_id=%s", (u_id,)); cur.execute("DELETE FROM users WHERE id=%s", (u_id,))
            conn.commit(); cur.close(); conn.close(); return redirect('/eyin-control')
    if not session.get('admin'): return render_template_string(LAYOUT.replace('{% block content %}{% endblock %}', '<div style="max-width:350px; margin:40px auto; text-align:center;"><h2>دخول الإدارة</h2><form method="post"><input type="password" name="password" placeholder="كلمة السر" required><button type="submit" class="main-btn">دخول</button></form></div>'), st=get_st())
    st = get_st(); conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor); cur.execute("SELECT u.*, (SELECT COUNT(*) FROM products WHERE user_id=u.id) as p_count FROM users u ORDER BY u.id DESC")
    users = cur.fetchall(); cur.close(); conn.close()
    u_html = "".join([f'<tr><td>{u["username"]}</td><td>{u["phone"]}</td><td>{u["p_count"]}</td><td><form method="post" style="display:inline;"><input type="hidden" name="user_id" value="{u["id"]}"><input type="hidden" name="action" value="{"unban_user" if u["is_banned"] else "ban_user"}"><button type="submit" style="background:none; border:none; color:var(--primary); cursor:pointer;">{"فك" if u["is_banned"] else "حظر"}</button></form><form method="post" style="display:inline;"><input type="hidden" name="user_id" value="{u["id"]}"><input type="hidden" name="action" value="delete_user"><button type="submit" style="color:red; background:none; border:none; cursor:pointer;" onclick="return confirm(\'مسح؟\')">مسح</button></form></td></tr>' for u in users])
    return render_template_string(LAYOUT.replace('{% block content %}{% endblock %}', f'<div style="max-width:800px; margin:auto; padding:10px;"><h3>⚙️ الإعدادات</h3><form method="post" enctype="multipart/form-data"><input type="hidden" name="action" value="update_settings">الاسم: <input type="text" name="store_name" value="{st["store_name"]}"><br>الشعار: <input type="file" name="logo_file"><button type="submit" class="main-btn">حفظ</button></form><hr><h3>👤 المستخدمين</h3><table class="admin-table"><thead><tr><th>الاسم</th><th>الجوال</th><th>📌</th><th>أمر</th></tr></thead><tbody>{u_html}</tbody></table><br><a href="/" style="color:var(--primary); text-decoration:none;">⬅️ عودة</a></div>'), st=st)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        p = "966"+request.form.get('phone')
        session['temp'] = {'u': request.form.get('username'), 'p': p, 'pw': request.form.get('password'), 'otp': str(random.randint(1000,9999))}
        return redirect('/verify')
    return render_template_string(LAYOUT.replace('{% block content %}{% endblock %}', '<div style="max-width:350px; margin:40px auto; text-align:center;"><h2>إنشاء حساب</h2><form method="post"><input type="text" name="username" placeholder="اسم المستخدم" required><input type="number" name="phone" placeholder="جوال 5" required><input type="password" name="password" placeholder="كلمة المرور" required><button type="submit" class="main-btn">سجل</button></form><p>عندك حساب؟ <a href="/login" class="auth-link">سجل دخول</a></p></div>'), st=get_st())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        p, pw = "966"+request.form.get('phone'), request.form.get('password')
        conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor); cur.execute("SELECT * FROM users WHERE phone=%s AND password=%s", (p, pw))
        u = cur.fetchone(); cur.close(); conn.close()
        if u:
            if u.get('is_banned'): return "محظور"
            session['user_id']=u['id']; session['username']=u['username']; session['user_phone']=u['phone']; return redirect('/')
    return render_template_string(LAYOUT.replace('{% block content %}{% endblock %}', '<div style="max-width:350px; margin:40px auto; text-align:center;"><h2>دخول</h2><form method="post">966+ <input type="number" name="phone" required placeholder="5xxxxxxxx"><input type="password" name="password" required><button type="submit" class="main-btn">دخول</button></form><p>ما عندك حساب؟ <a href="/register" class="auth-link">اشتراك</a></p></div>'), st=get_st())

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if 'temp' not in session: return redirect('/register')
    otp = session['temp']['otp']; wa = f"https://wa.me/{MY_PHONE}?text=كود: {otp}"
    if request.method == 'POST' and request.form.get('otp') == otp:
        conn = get_db_connection(); cur = conn.cursor(); t = session['temp']
        cur.execute("INSERT INTO users (username, phone, password) VALUES (%s, %s, %s)", (t['u'], t['p'], t['pw']))
        conn.commit(); cur.close(); conn.close(); session.pop('temp'); return redirect('/login')
    return render_template_string(LAYOUT.replace('{% block content %}{% endblock %}', f'<div style="text-align:center; padding:40px;"><h2>تفعيل</h2><a href="{wa}" target="_blank" style="background:#25d366; color:white; padding:15px; display:block; text-decoration:none; border-radius:10px;">كود واتساب</a><form method="post"><input type="number" name="otp" required><button type="submit" class="main-btn">تأكيد</button></form></div>'), st=get_st())

@app.route('/profile')
def profile():
    if 'user_id' not in session: return redirect('/login')
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor); cur.execute("SELECT * FROM products WHERE user_id=%s ORDER BY id DESC", (session['user_id'],))
    prods = cur.fetchall(); cur.close(); conn.close()
    html = f'<div style="text-align:center; padding:20px;"><h2>{session.get("username")}</h2><a href="/logout_user" style="color:red; font-size:13px;">خروج</a></div><div class="grid">'
    for p in prods:
        html += f'<div class="card"><img src="{p["image_url"]}"><div class="card-info"><h3 class="prod-name">{p["name"]}</h3><p class="prod-desc">{p["description"] if p["description"] else ""}</p><form action="/delete_product" method="post"><input type="hidden" name="id" value="{p["id"]}"><button type="submit" style="color:red; background:none; border:none; cursor:pointer;">حذف</button></form></div></div>'
    return render_template_string(LAYOUT.replace('{% block content %}{% endblock %}', html + '</div>'), st=get_st())

@app.route('/add_public', methods=['POST'])
def add_public():
    if 'user_id' not in session: return redirect('/login')
    f = request.files['image_file']; img = f"data:{f.content_type};base64,{base64.b64encode(f.read()).decode('utf-8')}"
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO products (user_id, name, price, image_url, whatsapp, description) VALUES (%s, %s, %s, %s, %s, %s)", (session['user_id'], request.form.get('name'), request.form.get('price'), img, session['user_phone'], request.form.get('description')))
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
