from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import os, psycopg2, base64, random
from psycopg2.extras import DictCursor

app = Flask(__name__)
app.secret_key = "eyin_otp_visible_v23"

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS settings (id SERIAL PRIMARY KEY, key TEXT UNIQUE, value TEXT)")
    cur.execute("INSERT INTO settings (key, value) VALUES ('logo', '') ON CONFLICT (key) DO NOTHING")
    cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, phone TEXT UNIQUE NOT NULL, password TEXT NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE CASCADE, name TEXT, price TEXT, image_url TEXT, description TEXT, whatsapp TEXT)")
    conn.commit(); cur.close(); conn.close()

init_db()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # أخذ الرقم وإضافة 966 تلقائياً
        phone_input = request.form.get('phone')
        full_phone = "966" + phone_input
        password = request.form.get('password')
        
        # توليد كود التحقق
        otp_code = str(random.randint(1000, 9999))
        
        # تخزين في الجلسة
        session['temp_user'] = {'phone': full_phone, 'password': password, 'otp': otp_code}
        
        return redirect(url_for('verify_otp'))
        
    return render_template_string('''
        <div dir="rtl" style="font-family:sans-serif; text-align:center; padding:50px;">
            <h2 style="color:#1e293b;">إنشاء حساب جديد بالرقم</h2>
            <form method="post" style="display:inline-block; width:90%; max-width:350px;">
                <div style="display:flex; align-items:center; background:#f1f5f9; border-radius:12px; padding:5px; margin-bottom:15px; border:1px solid #e2e8f0;">
                    <span style="padding:10px; font-weight:bold; color:#475569;">966+</span>
                    <input type="number" name="phone" placeholder="5xxxxxxxx" required style="flex-grow:1; border:none; background:none; padding:10px; outline:none; font-size:16px;">
                </div>
                <input type="password" name="password" placeholder="كلمة المرور" required style="width:100%; padding:15px; border-radius:12px; border:1px solid #e2e8f0; margin-bottom:20px; box-sizing:border-box;">
                <button type="submit" style="width:100%; padding:15px; background:#22c55e; color:white; border:none; border-radius:12px; font-weight:bold; cursor:pointer; font-size:16px;">تسجيل وإرسال كود</button>
            </form>
        </div>
    ''')

@app.route('/verify', methods=['GET', 'POST'])
def verify_otp():
    if 'temp_user' not in session: return redirect(url_for('register'))
    
    # جلب الكود من الجلسة لعرضه للمستخدم (للتجربة فقط)
    current_otp = session['temp_user']['otp']
    
    if request.method == 'POST':
        user_otp = request.form.get('otp')
        temp = session['temp_user']
        if user_otp == temp['otp']:
            conn = get_db_connection(); cur = conn.cursor()
            try:
                cur.execute("INSERT INTO users (phone, password) VALUES (%s, %s)", (temp['phone'], temp['password']))
                conn.commit()
                flash('✅ تم تفعيل الحساب بنجاح!', 'success')
                session.pop('temp_user')
                return redirect(url_for('login'))
            except:
                flash('❌ هذا الرقم مسجل بالفعل', 'error')
                return redirect(url_for('register'))
            finally: cur.close(); conn.close()
        else:
            flash('❌ كود التحقق خطأ', 'error')

    return render_template_string(f'''
        <div dir="rtl" style="font-family:sans-serif; text-align:center; padding:50px;">
            <div style="background:#fff9c4; padding:10px; border-radius:10px; margin-bottom:20px; display:inline-block; border:1px solid #fbc02d;">
                ⚠️ <b>وضع التجربة:</b> كود التحقق المرسل لجوالك هو: <span style="font-size:20px; color:red;">{current_otp}</span>
            </div>
            <h2>أدخل كود التحقق</h2>
            <form method="post" style="display:inline-block; width:300px;">
                <input type="number" name="otp" placeholder="----" required style="width:100%; padding:15px; text-align:center; font-size:28px; border-radius:12px; border:2px solid #4f46e5;">
                <button type="submit" style="width:100%; padding:15px; background:#4f46e5; color:white; border:none; border-radius:12px; font-weight:bold; margin-top:20px;">تأكيد</button>
            </form>
        </div>
    ''')

# --- بقية المسارات ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = "966" + request.form.get('phone')
        password = request.form.get('password')
        conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT * FROM users WHERE phone = %s AND password = %s", (phone, password))
        user = cur.fetchone(); cur.close(); conn.close()
        if user:
            session['user_id'] = user['id']; session['user_phone'] = user['phone']
            return redirect(url_for('index'))
        flash('❌ الرقم أو كلمة المرور خطأ', 'error')
    return render_template_string('''
        <div dir="rtl" style="font-family:sans-serif; text-align:center; padding:50px;">
            <h2>تسجيل الدخول</h2>
            <form method="post" style="display:inline-block; width:300px;">
                <div style="display:flex; align-items:center; background:#f1f5f9; border-radius:12px; padding:5px; margin-bottom:10px;">
                    <span style="padding:10px; font-weight:bold;">966+</span>
                    <input type="number" name="phone" placeholder="5xxxxxxxx" required style="flex-grow:1; border:none; background:none; padding:10px; outline:none;">
                </div>
                <input type="password" name="password" placeholder="كلمة المرور" required style="width:100%; padding:15px; border-radius:12px; border:1px solid #ddd; margin-bottom:10px;">
                <button type="submit" style="width:100%; padding:15px; background:#4f46e5; color:white; border:none; border-radius:12px; font-weight:bold;">دخول</button>
            </form>
            <p>جديد هنا؟ <a href="/register">أنشئ حسابك</a></p>
        </div>
    ''')

@app.route('/')
def index():
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products ORDER BY id DESC"); products = cur.fetchall()
    cur.execute("SELECT value FROM settings WHERE key = 'logo'"); logo = cur.fetchone()
    cur.close(); conn.close(); logo_url = logo['value'] if logo else ""
    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>متجر عين</title>
        <style>
            :root { --bg: #ffffff; --card: #f8fafc; --text: #1e293b; --primary: #4f46e5; }
            body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 15px; }
            .header { display: flex; justify-content: space-between; align-items: center; max-width: 1000px; margin: auto; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; max-width: 1000px; margin: 20px auto; }
            .card { background: var(--card); border-radius: 20px; border: 1px solid #e2e8f0; padding: 15px; }
            .btn-buy { background: #22c55e; color: white; text-decoration: none; display: block; text-align: center; padding: 12px; border-radius: 12px; font-weight: bold; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="header">
            <div style="display:flex; align-items:center; gap:10px;">
                {% if logo_url %}<img src="{{ logo_url }}" width="40" height="40" style="border-radius:50%;">{% endif %}
                <h2 style="margin:0;">متجر عيـن</h2>
            </div>
            <div>
                {% if session.get('user_id') %}
                    <button onclick="document.getElementById('addModal').style.display='flex'" style="background:var(--primary); color:white; border:none; padding:8px 12px; border-radius:10px;">+ إعلان</button>
                    <a href="/logout_user" style="color:red; font-size:12px; margin-right:10px;">خروج</a>
                {% else %}
                    <a href="/login" style="text-decoration:none; color:var(--primary); font-weight:bold;">دخول</a>
                {% endif %}
            </div>
        </div>
        <div class="grid">
            {% for p in products %}
            <div class="card">
                <img src="{{ p['image_url'] or 'https://via.placeholder.com/150' }}" style="width:100%; height:200px; object-fit:contain; border-radius:10px;">
                <h3>{{ p['name'] }}</h3>
                <div style="font-weight:bold; color:var(--primary);">{{ p['price'] }} ريال</div>
                <p style="font-size:0.9rem; opacity:0.8;">{{ p['description'] }}</p>
                <a href="https://wa.me/{{ p['whatsapp'] }}" class="btn-buy" target="_blank">واتساب</a>
            </div>
            {% endfor %}
        </div>
        <div id="addModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.7); align-items:center; justify-content:center; z-index:100;">
            <div style="background:var(--card); padding:20px; border-radius:20px; width:90%; max-width:400px;">
                <h3>نشر إعلان جديد</h3>
                <form action="/add_public" method="post" enctype="multipart/form-data">
                    <input type="text" name="name" placeholder="اسم المنتج" required style="width:100%; padding:10px; margin:5px 0; border-radius:8px; border:1px solid #ddd;">
                    <input type="number" name="price" placeholder="السعر" required style="width:100%; padding:10px; margin:5px 0; border-radius:8px; border:1px solid #ddd;">
                    <textarea name="description" placeholder="وصف السلعة" style="width:100%; padding:10px; margin:5px 0; border-radius:8px; border:1px solid #ddd;"></textarea>
                    <input type="file" name="image_file" required style="margin:10px 0;">
                    <button type="submit" style="width:100%; padding:12px; background:var(--primary); color:white; border:none; border-radius:10px; font-weight:bold;">نشر الإعلان</button>
                    <button type="button" onclick="document.getElementById('addModal').style.display='none'" style="width:100%; background:none; border:none; color:#999; margin-top:10px;">إلغاء</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    ''', products=products, logo_url=logo_url)

@app.route('/logout_user')
def logout_user():
    session.clear(); return redirect(url_for('index'))

@app.route('/add_public', methods=['POST'])
def add_public():
    if 'user_id' not in session: return redirect(url_for('login'))
    name, price, desc = request.form.get('name'), request.form.get('price'), request.form.get('description')
    img_data = ""
    if 'image_file' in request.files:
        f = request.files['image_file']
        img_data = f"data:{f.content_type};base64,{base64.b64encode(f.read()).decode('utf-8')}"
    conn = get_db_connection(); cur = conn.cursor()
    cur.execute("INSERT INTO products (user_id, name, price, image_url, description, whatsapp) VALUES (%s, %s, %s, %s, %s, %s)", 
                (session['user_id'], name, price, img_data, desc, session['user_phone']))
    conn.commit(); cur.close(); conn.close()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
