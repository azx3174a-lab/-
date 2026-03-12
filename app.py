from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import os, psycopg2, base64, random
from psycopg2.extras import DictCursor

app = Flask(__name__)
app.secret_key = "eyin_master_v29"

# !!! ضع رقم واتسابك هنا !!!
ADMIN_WHATSAPP = "966550963174" 

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def fix_db():
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS settings (id SERIAL PRIMARY KEY, key TEXT UNIQUE, value TEXT)")
    cur.execute("INSERT INTO settings (key, value) VALUES ('logo', '') ON CONFLICT (key) DO NOTHING")
    cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, phone TEXT UNIQUE NOT NULL, password TEXT NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, name TEXT, price TEXT, image_url TEXT, description TEXT, whatsapp TEXT)")
    try: cur.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id) ON DELETE CASCADE")
    except: pass
    conn.commit(); cur.close(); conn.close()

fix_db()

# --- القالب الأساسي لجميع الصفحات ---
BASE_HTML = '''
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>متجر عين</title>
    <style>
        :root { --bg: #ffffff; --card: #f8fafc; --text: #1e293b; --border: #e2e8f0; --primary: #4f46e5; --btn-bg: #000000; --btn-text: #ffffff; }
        [data-theme="dark"] { --bg: #0f172a; --card: #1e293b; --text: #f8fafc; --border: #334155; --primary: #818cf8; --btn-bg: #ffffff; --btn-text: #000000; }
        body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 15px; transition: 0.3s; min-height: 100vh; }
        .header { display: flex; justify-content: space-between; align-items: center; max-width: 1000px; margin: auto; padding: 10px 0; border-bottom: 1px solid var(--border); }
        .theme-btn { background: var(--btn-bg); color: var(--btn-text); border: none; cursor: pointer; width: 40px; height: 40px; border-radius: 50%; font-size: 20px; display: flex; align-items: center; justify-content: center; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; max-width: 1000px; margin: 20px auto; }
        .card { background: var(--card); border-radius: 20px; border: 1px solid var(--border); padding: 15px; }
        .btn-buy { background: #22c55e; color: white; text-decoration: none; display: block; text-align: center; padding: 12px; border-radius: 12px; font-weight: bold; }
        .add-btn { background: var(--primary); color: white; border: none; padding: 10px 15px; border-radius: 12px; cursor: pointer; font-weight: bold; }
        input, textarea { width: 100%; padding: 12px; margin: 8px 0; border-radius: 10px; border: 1px solid var(--border); background: var(--bg); color: var(--text); box-sizing: border-box; }
    </style>
</head>
<body data-theme="light">
    <div class="header">
        <div style="display:flex; align-items:center; gap:10px;">
            <h2 style="margin:0;">متجر عيـن</h2>
        </div>
        <div style="display:flex; gap:12px; align-items:center;">
            {% if session.get('user_id') %}
                <a href="{{ url_for('my_ads') }}" style="text-decoration:none; color:var(--primary); font-weight:bold;">إعلاناتي</a>
                <button onclick="document.getElementById('addModal').style.display='flex'" class="add-btn">+ إعلان</button>
                <a href="{{ url_for('logout_user') }}" style="color:red; font-size:12px; text-decoration:none;">خروج</a>
            {% else %}
                <a href="{{ url_for('login') }}" style="text-decoration:none; color:var(--primary); font-weight:bold;">دخول</a>
            {% endif %}
            <button class="theme-btn" onclick="toggleTheme()" id="theme-icon">🌙</button>
        </div>
    </div>
    {% block content %}{% endblock %}
    <script>
        function toggleTheme() {
            const current = document.body.getAttribute('data-theme');
            const target = current === 'dark' ? 'light' : 'dark';
            document.body.setAttribute('data-theme', target);
            localStorage.setItem('theme', target);
            document.getElementById('theme-icon').innerText = target === 'dark' ? '☀️' : '🌙';
        }
        document.body.setAttribute('data-theme', localStorage.getItem('theme') || 'light');
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products ORDER BY id DESC"); products = cur.fetchall()
    cur.close(); conn.close()
    return render_template_string(BASE_HTML + '''
    {% block content %}
    <div class="grid">
        {% for p in products %}
        <div class="card">
            <img src="{{ p['image_url'] or 'https://via.placeholder.com/150' }}" style="width:100%; height:180px; object-fit:contain; border-radius:12px;">
            <h3>{{ p['name'] }}</h3>
            <div style="font-weight:bold; color:var(--primary);">{{ p['price'] }} ريال</div>
            <p style="font-size:0.9rem; opacity:0.8;">{{ p['description'] }}</p>
            <a href="https://wa.me/{{ p['whatsapp'] }}" class="btn-buy" target="_blank">واتساب</a>
        </div>
        {% endfor %}
    </div>
    <div id="addModal" style="display:none; position:fixed; z-index:100; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.7); align-items:center; justify-content:center;">
        <div style="background:var(--card); padding:25px; border-radius:25px; width:90%; max-width:400px;">
            <h3>نشر إعلان جديد</h3>
            <form action="{{ url_for('add_public') }}" method="post" enctype="multipart/form-data">
                <input type="text" name="name" placeholder="ماذا تبيع؟" required>
                <input type="number" name="price" placeholder="السعر" required>
                <textarea name="description" placeholder="وصف المنتج..."></textarea>
                <input type="file" name="image_file" required>
                <button type="submit" class="add-btn" style="width:100%; padding:15px; margin-top:10px;">نشر الآن</button>
                <button type="button" onclick="document.getElementById('addModal').style.display='none'" style="width:100%; background:none; border:none; color:gray; margin-top:10px;">إلغاء</button>
            </form>
        </div>
    </div>
    {% endblock %}
    ''', products=products)

# --- لوحة التحكم السرية (Admin) ---
@app.route('/eyin-control', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == '317400': session['admin_logged'] = True
        elif session.get('admin_logged'):
            conn = get_db_connection(); cur = conn.cursor()
            if request.form.get('action') == 'delete':
                cur.execute("DELETE FROM products WHERE id = %s", (request.form.get('id'),))
                conn.commit()
            cur.close(); conn.close()
            return redirect(url_for('admin'))
    if not session.get('admin_logged'):
        return '<div dir="rtl" style="text-align:center; padding:100px;">🔐 <form method="post"><input type="password" name="password"><button type="submit">دخول</button></form></div>'
    
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products ORDER BY id DESC"); prods = cur.fetchall()
    cur.close(); conn.close()
    return render_template_string('''<div dir="rtl" style="padding:20px; font-family:sans-serif;"><h2>🛠️ لوحة تحكم الإدارة</h2><hr>
        {% for p in prods %}
        <div style="border-bottom:1px solid #ddd; padding:10px; display:flex; justify-content:space-between;">
            <span>{{ p['name'] }} - {{ p['price'] }} ريال</span>
            <form method="post"><input type="hidden" name="id" value="{{ p['id'] }}"><input type="hidden" name="action" value="delete"><button type="submit" style="color:red;">حذف نهائي</button></form>
        </div>
        {% endfor %}
        <br><a href="/">العودة للمتجر</a></div>''', prods=prods)

# --- تسجيل الدخول والتحقق (Auth) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = "966" + request.form.get('phone')
        conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT * FROM users WHERE phone = %s AND password = %s", (phone, request.form.get('password')))
        user = cur.fetchone(); cur.close(); conn.close()
        if user: session['user_id'] = user['id']; session['user_phone'] = user['phone']; return redirect(url_for('index'))
    return render_template_string(BASE_HTML + '''{% block content %}<div style="text-align:center; padding:50px;"><h2>دخول</h2><form method="post" style="max-width:300px; margin:auto;">966+ <input type="number" name="phone" required><input type="password" name="password" required><button type="submit" class="add-btn" style="width:100%;">دخول</button></form><p>جديد؟ <a href="/register">سجل هنا</a></p></div>{% endblock %}''')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_phone = "966" + request.form.get('phone')
        otp = str(random.randint(1000, 9999))
        session['temp_user'] = {'phone': full_phone, 'password': request.form.get('password'), 'otp': otp}
        return redirect(url_for('verify_otp'))
    return render_template_string(BASE_HTML + '''{% block content %}<div style="text-align:center; padding:50px;"><h2>تسجيل</h2><form method="post" style="max-width:300px; margin:auto;">966+ <input type="number" name="phone" required><input type="password" name="password" required><button type="submit" class="add-btn" style="width:100%;">التالي</button></form></div>{% endblock %}''')

@app.route('/verify', methods=['GET', 'POST'])
def verify_otp():
    if 'temp_user' not in session: return redirect(url_for('register'))
    otp = session['temp_user']['otp']
    wa_link = f"https://wa.me/{ADMIN_WHATSAPP}?text=كود تفعيل متجر عين لرقبي هو: {otp}"
    if request.method == 'POST':
        if request.form.get('otp') == otp:
            conn = get_db_connection(); cur = conn.cursor(); t = session['temp_user']
            cur.execute("INSERT INTO users (phone, password) VALUES (%s, %s)", (t['phone'], t['password']))
            conn.commit(); cur.close(); conn.close(); session.pop('temp_user'); return redirect(url_for('login'))
    return render_template_string(BASE_HTML + f'''{% block content %}<div style="text-align:center; padding:50px;"><a href="{wa_link}" target="_blank" style="background:#25d366; color:white; padding:15px; text-decoration:none; border-radius:10px;">💬 اطلب الكود عبر واتساب</a><form method="post" style="margin-top:20px;"><input type="number" name="otp" placeholder="الكود هنا" required><button type="submit" class="add-btn">تأكيد</button></form></div>{% endblock %}''')

@app.route('/my-ads')
def my_ads():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products WHERE user_id = %s ORDER BY id DESC", (session['user_id'],))
    prods = cur.fetchall(); cur.close(); conn.close()
    return render_template_string(BASE_HTML + '''{% block content %}<div style="max-width:1000px; margin:auto; padding:20px;"><h2>إعلاناتي الشخصية</h2><div class="grid">{% for p in prods %}<div class="card"><img src="{{p['image_url']}}" style="width:100%; height:150px; object-fit:contain;"><h3>{{p['name']}}</h3><form action="/delete_product" method="post"><input type="hidden" name="id" value="{{p['id']}}"><button type="submit" style="background:red; color:white; border:none; width:100%; padding:10px; border-radius:10px;">حذف</button></form></div>{% endfor %}</div></div>{% endblock %}''', prods=prods)

@app.route('/add_public', methods=['POST'])
def add_public():
    if 'user_id' not in session: return redirect(url_for('login'))
    img = f"data:{request.files['image_file'].content_type};base64,{base64.b64encode(request.files['image_file'].read()).decode('utf-8')}"
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO products (user_id, name, price, image_url, description, whatsapp) VALUES (%s, %s, %s, %s, %s, %s)", 
                (session['user_id'], request.form.get('name'), request.form.get('price'), img, request.form.get('description'), session['user_phone']))
    conn.commit(); cur.close(); conn.close(); return redirect(url_for('index'))

@app.route('/delete_product', methods=['POST'])
def delete_product():
    if 'user_id' in session:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("DELETE FROM products WHERE id = %s AND user_id = %s", (request.form.get('id'), session['user_id']))
        conn.commit(); cur.close(); conn.close()
    return redirect(url_for('my_ads'))

@app.route('/logout_user')
def logout_user(): session.clear(); return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
