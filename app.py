from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import os, psycopg2, base64, random
from psycopg2.extras import DictCursor

app = Flask(__name__)
app.secret_key = "eyin_complete_v50"

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
        cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, phone TEXT UNIQUE NOT NULL, password TEXT NOT NULL)")
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

# القالب الكامل مع الوضع الداكن
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
        
        /* تنسيق المنتجات الجديد (صورة يمين واسم أبيض) */
        .grid { display: flex; flex-direction: column; gap: 12px; max-width: 800px; margin: 20px auto; }
        .card { 
            background: var(--card); border-radius: 15px; padding: 12px; border: 1px solid var(--border); 
            display: flex; flex-direction: row-reverse; align-items: center; gap: 15px;
        }
        .card img { width: 90px; height: 90px; border-radius: 12px; object-fit: cover; background: #2d3748; }
        .card-info { flex: 1; display: flex; flex-direction: column; text-align: right; }
        .prod-name { color: #ffffff !important; margin: 0 0 5px 0; font-size: 1.1rem; font-weight: bold; }
        .prod-price { color: var(--primary); font-weight: bold; }
        
        .auth-box { max-width: 380px; margin: 40px auto; text-align: center; }
        .slogan { font-size: 1.1rem; font-weight: bold; margin-bottom: 25px; padding: 15px; border: 2px solid var(--primary); border-radius: 15px; color: var(--primary); background: rgba(129, 140, 248, 0.1); }
        .auth-card { background: var(--card); padding: 30px; border-radius: 25px; border: 1px solid var(--border); }
        input, textarea { width: 100%; padding: 12px; margin: 10px 0; border-radius: 10px; border: 1px solid var(--border); background: var(--bg); color: var(--text); box-sizing: border-box; }
        .main-btn { width: 100%; padding: 12px; background: var(--primary); color: white; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body data-theme="dark">
    <div class="header">
        <div style="display:flex; align-items:center; gap:10px;">
            {% if st['logo'] %}<img src="{{ st['logo'] }}" style="width:40px; height:40px; border-radius:50%;">{% endif %}
            <h2 style="margin:0;">{{ st['store_name'] }}</h2>
        </div>
        <div style="display:flex; gap:10px; align-items:center;">
            {% if session.get('user_id') %}
                <a href="/my-ads" style="color:var(--primary); font-weight:bold; text-decoration:none; font-size:14px;">إعلاناتي</a>
                <button onclick="document.getElementById('addModal').style.display='flex'" style="background:var(--primary); border:none; color:white; padding:8px 12px; border-radius:10px; cursor:pointer; font-weight:bold;">+ إعلان</button>
                <a href="/logout_user" style="color:red; text-decoration:none; font-size:12px;">خروج</a>
            {% endif %}
            <button onclick="toggleTheme()" id="themeBtn" style="cursor:pointer; border-radius:50%; width:35px; height:35px; border:none; background:var(--card); color:var(--text);">🌙</button>
        </div>
    </div>
    {% block content %}{% endblock %}
    <script>
        function toggleTheme() {
            const b = document.body;
            const isDark = b.getAttribute('data-theme') === 'dark';
            const newTheme = isDark ? 'light' : 'dark';
            b.setAttribute('data-theme', newTheme);
            document.getElementById('themeBtn').innerText = isDark ? '☀️' : '🌙';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    if 'user_id' not in session: return redirect('/register')
    st = get_st(); conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products ORDER BY id DESC"); prods = cur.fetchall(); cur.close(); conn.close()
    
    products_html = ""
    for p in prods:
        products_html += f'''
        <div class="card">
            <img src="{p['image_url']}" alt="product">
            <div class="card-info">
                <h3 class="prod-name">{p['name']}</h3>
                <div class="prod-price">{p['price']} ريال</div>
                <a href="https://wa.me/{p['whatsapp']}" style="color:#22c55e; text-decoration:none; font-size:13px; font-weight:bold; margin-top:8px;">💬 تواصل الآن</a>
            </div>
        </div>
        '''
    
    return render_template_string(LAYOUT.replace('{% block content %}{% endblock %}', f'''
    <div class="grid">{products_html}</div>
    <div id="addModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); align-items:center; justify-content:center; z-index:100;">
        <div style="background:var(--card); padding:20px; border-radius:20px; width:90%; max-width:400px;">
            <h3>نشر إعلان جديد</h3>
            <form action="/add_public" method="post" enctype="multipart/form-data">
                <input type="text" name="name" placeholder="اسم المنتج" required>
                <input type="number" name="price" placeholder="السعر" required>
                <textarea name="description" placeholder="وصف بسيط"></textarea>
                <input type="file" name="image_file" required>
                <button type="submit" class="main-btn">نشر الآن</button>
                <button type="button" onclick="document.getElementById('addModal').style.display='none'" style="width:100%; margin-top:10px; background:none; border:none; color:gray; cursor:pointer;">إلغاء</button>
            </form>
        </div>
    </div>
    '''), st=st)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        p = "966"+request.form.get('phone')
        session['temp'] = {'p': p, 'pw': request.form.get('password'), 'otp': str(random.randint(1000,9999))}
        return redirect('/verify')
    return render_template_string(LAYOUT.replace('{% block content %}{% endblock %}', '''
    <div class="auth-box"><div class="slogan">عـيـن فراش لك و عـيـن لحافي</div><div class="auth-card">
    <h2>إنشاء حساب</h2><form method="post">966+ <input type="number" name="phone" required placeholder="5xxxxxxxx"><input type="password" name="password" required placeholder="كلمة المرور"><button type="submit" class="main-btn">تسجيل</button></form><p>لديك حساب؟ <a href="/login">دخول</a></p></div></div>
    '''), st=get_st())

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if 'temp' not in session: return redirect('/register')
    otp = session['temp']['otp']; wa = f"https://wa.me/{MY_PHONE}?text=كود تفعيل متجر عين: {otp}"
    if request.method == 'POST':
        if request.form.get('otp') == otp:
            conn = get_db_connection(); cur = conn.cursor(); t = session['temp']
            cur.execute("INSERT INTO users (phone, password) VALUES (%s, %s)", (t['p'], t['pw']))
            conn.commit(); cur.close(); conn.close(); session.pop('temp'); return redirect('/login')
    return render_template_string(LAYOUT.replace('{% block content %}{% endblock %}', f'''
    <div class="auth-box"><div class="auth-card"><h2>تحقق من الرقم</h2>
    <a href="{wa}" target="_blank" style="background:#25d366; color:white; padding:15px; display:block; text-decoration:none; border-radius:10px; font-weight:bold; margin-bottom:20px; text-align:center;">💬 اطلب الكود واتساب</a>
    <form method="post"><input type="number" name="otp" required placeholder="أدخل الكود هنا"><button type="submit" class="main-btn">تأكيد التفعيل</button></form></div></div>
    '''), st=get_st())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        p, pw = "966"+request.form.get('phone'), request.form.get('password')
        conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor); cur.execute("SELECT * FROM users WHERE phone=%s AND password=%s", (p, pw))
        u = cur.fetchone(); cur.close(); conn.close()
        if u: session['user_id']=u['id']; session['user_phone']=u['phone']; return redirect('/')
    return render_template_string(LAYOUT.replace('{% block content %}{% endblock %}', '''
    <div class="auth-box"><div class="slogan">عـيـن فراش لك و عـيـن لحافي</div><div class="auth-card"><h2>دخول</h2><form method="post">966+ <input type="number" name="phone" required><input type="password" name="password" required><button type="submit" class="main-btn">دخول</button></form></div></div>
    '''), st=get_st())

@app.route('/eyin-control', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == '317400': session['admin']=True
        elif session.get('admin'):
            conn = get_db_connection(); cur = conn.cursor(); a = request.form.get('action')
            if a == 'update_logo':
                f = request.files['logo_file']; img = f"data:{f.content_type};base64,{base64.b64encode(f.read()).decode('utf-8')}"; cur.execute("UPDATE settings SET value=%s WHERE key='logo'", (img,))
            elif a == 'update_name': cur.execute("UPDATE settings SET value=%s WHERE key='store_name'", (request.form.get('store_name'),))
            elif a == 'delete': cur.execute("DELETE FROM products WHERE id=%s", (request.form.get('id'),))
            conn.commit(); cur.close(); conn.close(); return redirect('/eyin-control')
    if not session.get('admin'): return '<form method="post" style="text-align:center; padding:100px;">🔐 <input type="password" name="password"><button type="submit">دخول</button></form>'
    st = get_st(); conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor); cur.execute("SELECT * FROM products ORDER BY id DESC"); prods = cur.fetchall(); cur.close(); conn.close()
    return render_template_string('''<div dir="rtl" style="padding:20px; background:white; color:black; min-height:100vh;"><h2>إدارة المتجر</h2><form method="post" enctype="multipart/form-data"><input type="hidden" name="action" value="update_logo">🖼️ الشعار: <input type="file" name="logo_file"><button type="submit">تحديث</button></form><hr><form method="post"><input type="hidden" name="action" value="update_name">📝 الاسم: <input type="text" name="store_name" value="{{st['store_name']}}"><button type="submit">حفظ</button></form><hr>{% for p in prods %}<div>{{p['name']}} <form method="post" style="display:inline;"><input type="hidden" name="action" value="delete"><input type="hidden" name="id" value="{{p['id']}}"><button type="submit" style="color:red; cursor:pointer;">حذف</button></form></div>{% endfor %}</div>''', st=st, prods=prods)

@app.route('/my-ads')
def my_ads():
    if 'user_id' not in session: return redirect('/login')
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor); cur.execute("SELECT * FROM products WHERE user_id=%s ORDER BY id DESC", (session['user_id'],)); prods = cur.fetchall(); cur.close(); conn.close()
    return render_template_string(LAYOUT.replace('{% block content %}{% endblock %}', '''
    <h2 style="text-align:center;">📦 إعلاناتي</h2>
    <div class="grid">
        {% for p in prods %}
        <div class="card">
            <img src="{{p['image_url']}}">
            <div class="card-info">
                <h3 class="prod-name">{{p['name']}}</h3>
                <form action="/delete_product" method="post"><input type="hidden" name="id" value="{{p['id']}}"><button type="submit" style="background:red; color:white; border:none; padding:5px 10px; border-radius:5px; cursor:pointer;">حذف الإعلان</button></form>
            </div>
        </div>
        {% endfor %}
    </div>
    '''), st=get_st(), prods=prods)

@app.route('/add_public', methods=['POST'])
def add_public():
    if 'user_id' not in session: return redirect('/login')
    f = request.files['image_file']; img = f"data:{f.content_type};base64,{base64.b64encode(f.read()).decode('utf-8')}"; conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO products (user_id, name, price, image_url, description, whatsapp) VALUES (%s, %s, %s, %s, %s, %s)", (session['user_id'], request.form.get('name'), request.form.get('price'), img, request.form.get('description'), session['user_phone']))
    conn.commit(); cur.close(); conn.close(); return redirect('/')

@app.route('/delete_product', methods=['POST'])
def delete_product():
    if 'user_id' in session:
        conn = get_db_connection(); cur = conn.cursor(); cur.execute("DELETE FROM products WHERE id=%s AND user_id=%s", (request.form.get('id'), session['user_id'])); conn.commit(); cur.close(); conn.close()
    return redirect('/my-ads')

@app.route('/logout_user')
def logout_user(): session.clear(); return redirect('/')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
