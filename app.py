from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import os
import psycopg2
from psycopg2.extras import DictCursor
import base64

app = Flask(__name__)
app.secret_key = "eyin_description_v18"

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS settings (id SERIAL PRIMARY KEY, key TEXT UNIQUE, value TEXT)")
    cur.execute("INSERT INTO settings (key, value) VALUES ('logo', '') ON CONFLICT (key) DO NOTHING")
    cur.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS whatsapp TEXT")
    cur.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS delete_code TEXT")
    cur.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS description TEXT")
    conn.commit()
    cur.close()
    conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    
    if request.method == 'POST' and request.form.get('action') == 'delete':
        product_id = request.form.get('id')
        user_code = request.form.get('user_code')
        cur.execute("SELECT delete_code FROM products WHERE id = %s", (product_id,))
        result = cur.fetchone()
        if result and result['delete_code'] == user_code:
            cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
            conn.commit()
            flash('✅ تم حذف المنتج بنجاح', 'success')
        else:
            flash('❌ الكود السري غير صحيح', 'error')
        return redirect(url_for('index'))

    cur.execute("SELECT * FROM products ORDER BY id DESC")
    products = cur.fetchall()
    cur.execute("SELECT value FROM settings WHERE key = 'logo'")
    logo = cur.fetchone()
    cur.close()
    conn.close()
    logo_url = logo['value'] if logo and logo['value'] else ""
    
    html = '''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>متجر عين</title>
        <style>
            :root { --bg: #f8fafc; --card: #ffffff; --text: #1e293b; --muted: #64748b; --primary: #4f46e5; --border: #e2e8f0; }
            [data-theme="dark"] { --bg: #0f172a; --card: #1e293b; --text: #f8fafc; --muted: #94a3b8; --primary: #818cf8; --border: #334155; }
            body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; transition: 0.3s; }
            .header { display: flex; justify-content: space-between; align-items: center; max-width: 1100px; margin: auto; }
            .logo-section { display: flex; align-items: center; gap: 12px; }
            .logo-img { width: 45px; height: 45px; object-fit: cover; border-radius: 50%; border: 2px solid var(--primary); }
            .add-btn { background: var(--primary); color: white; border: none; padding: 10px 20px; border-radius: 12px; cursor: pointer; font-weight: bold; }
            .theme-btn { background: var(--card); border: 1px solid var(--border); cursor: pointer; padding: 10px; border-radius: 50%; font-size: 20px; color: var(--text); }
            .alert { padding: 15px; border-radius: 10px; max-width: 1100px; margin: 10px auto; text-align: center; font-weight: bold; }
            .alert-success { background: #dcfce7; color: #166534; }
            .alert-error { background: #fee2e2; color: #991b1b; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 25px; max-width: 1100px; margin: 40px auto; }
            .card { background: var(--card); padding: 20px; border-radius: 24px; border: 1px solid var(--border); }
            .card img { width: 100%; height: 180px; object-fit: contain; border-radius: 18px; margin-bottom: 15px; }
            .product-desc { color: var(--muted); font-size: 0.9rem; line-height: 1.4; margin-bottom: 15px; min-height: 40px; }
            .btn-buy { background: #25d366; color: white; border: none; padding: 10px; border-radius: 10px; width: 100%; text-decoration: none; display: block; text-align: center; font-weight: bold; margin-bottom: 15px; }
            .delete-box { border-top: 1px solid var(--border); padding-top: 10px; display: flex; gap: 5px; }
            .delete-input { font-size: 12px; padding: 5px; border: 1px solid #ef4444; border-radius: 5px; width: 100%; }
            .delete-btn { background: #ef4444; color: white; border: none; font-size: 12px; padding: 5px 10px; border-radius: 5px; cursor: pointer; }
            .modal { display: none; position: fixed; z-index: 100; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.6); align-items: center; justify-content: center; }
            .modal-content { background: var(--card); padding: 30px; border-radius: 20px; width: 90%; max-width: 400px; }
            input, textarea { width: 100%; padding: 10px; margin: 8px 0; border-radius: 8px; border: 1px solid var(--border); background: var(--bg); color: var(--text); box-sizing: border-box; }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo-section">
                {% if logo_url %}<img src="{{ logo_url }}" class="logo-img">{% endif %}
                <h1 style="margin:0; font-size: 1.3rem;">متجر عيـن</h1>
            </div>
            <div>
                <button class="add-btn" onclick="document.getElementById('addModal').style.display='flex'">+ أضف منتجك</button>
                <button class="theme-btn" onclick="toggleTheme()" id="theme-icon">🌙</button>
            </div>
        </div>

        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for category, message in messages %}
              <div class="alert alert-{{ category }}">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        <div class="grid">
            {% for p in products %}
            <div class="card">
                <img src="{{ p['image_url'] or 'https://via.placeholder.com/150' }}">
                <h3 style="margin: 0;">{{ p['name'] }}</h3>
                <div style="font-size: 20px; color: var(--primary); font-weight: bold; margin: 10px 0;">{{ p['price'] }} ريال</div>
                
                <div class="product-desc">{{ p['description'] or 'لا يوجد وصف لهذا المنتج' }}</div>
                
                <a href="https://wa.me/{{ p['whatsapp'] }}" class="btn-buy" target="_blank">واتساب البائع</a>
                <div class="delete-box">
                    <form method="post" style="display:flex; gap:5px; width:100%;">
                        <input type="hidden" name="id" value="{{ p['id'] }}">
                        <input type="hidden" name="action" value="delete">
                        <input type="password" name="user_code" placeholder="كود الحذف" class="delete-input" required>
                        <button type="submit" class="delete-btn">حذف</button>
                    </form>
                </div>
            </div>
            {% endfor %}
        </div>

        <div id="addModal" class="modal">
            <div class="modal-content">
                <h3>إضافة إعلان جديد</h3>
                <form action="/add_public" method="post" enctype="multipart/form-data">
                    <input type="text" name="name" placeholder="ماذا تبيع؟" required>
                    <input type="number" name="price" placeholder="السعر" required>
                    <textarea name="description" placeholder="اكتب وصفاً مختصراً للمنتج (المقاس، الحالة، إلخ...)" rows="3"></textarea>
                    <input type="text" name="whatsapp" placeholder="رقم واتسابك (966...)" required>
                    <input type="password" name="delete_code" placeholder="كود سري للحذف" required>
                    <input type="file" name="image_file" required>
                    <button type="submit" class="add-btn" style="width:100%; margin-top:10px;">نشر الآن</button>
                    <button type="button" onclick="document.getElementById('addModal').style.display='none'" style="background:none; border:none; color:var(--muted); width:100%; margin-top:10px; cursor:pointer;">إلغاء</button>
                </form>
            </div>
        </div>

        <script>
            function toggleTheme() {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                document.getElementById('theme-icon').innerText = newTheme === 'dark' ? '☀️' : '🌙';
            }
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
        </script>
    </body>
    </html>
    '''
    return render_template_string(html, products=products, logo_url=logo_url)

@app.route('/add_public', methods=['POST'])
def add_public():
    name, price, whatsapp, delete_code, description = request.form.get('name'), request.form.get('price'), request.form.get('whatsapp'), request.form.get('delete_code'), request.form.get('description')
    image_data = ""
    if 'image_file' in request.files:
        file = request.files['image_file']
        if file.filename != '':
            encoded_string = base64.b64encode(file.read()).decode('utf-8')
            image_data = f"data:{file.content_type};base64,{encoded_string}"
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO products (name, price, image_url, whatsapp, delete_code, description) VALUES (%s, %s, %s, %s, %s, %s)", (name, price, image_data, whatsapp, delete_code, description))
    conn.commit()
    cur.close()
    conn.close()
    flash('✅ تم نشر إعلانك بنجاح!', 'success')
    return redirect(url_for('index'))

@app.route('/eyin-control', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == '317400':
            session['logged_in'] = True
        elif 'logged_in' in session:
            conn = get_db_connection()
            cur = conn.cursor()
            action = request.form.get('action')
            if action == 'update_logo':
                file = request.files['logo_file']
                encoded_string = base64.b64encode(file.read()).decode('utf-8')
                logo_data = f"data:{file.content_type};base64,{encoded_string}"
                cur.execute("UPDATE settings SET value=%s WHERE key='logo'", (logo_data,))
            elif action == 'admin_delete':
                product_id = request.form.get('id')
                cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('admin'))
            
    if not session.get('logged_in'):
        return '<div dir="rtl" style="text-align:center;padding:100px;"><h2>🔐 دخول خاص</h2><form method="post"><input type="password" name="password"><button type="submit">دخول</button></form></div>'

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products ORDER BY id DESC")
    products = cur.fetchall()
    cur.close()
    conn.close()

    return render_template_string('''
    <div dir="rtl" style="font-family: sans-serif; padding: 20px; max-width: 900px; margin: auto;">
        <h2 style="text-align:center;">🛠️ لوحة الإدارة</h2>
        <div style="background: #eee; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <h3>🖼️ شعار المنصة</h3>
            <form method="post" enctype="multipart/form-data">
                <input type="hidden" name="action" value="update_logo">
                <input type="file" name="logo_file" required>
                <button type="submit">تحديث الشعار</button>
            </form>
        </div>
        <h3>📦 التحكم في المنتجات</h3>
        <table border="1" style="width:100%; border-collapse: collapse; background: white;">
            <tr style="background:#f4f4f4;"><th>المنتج</th><th>الوصف</th><th>السعر</th><th>الإجراء</th></tr>
            {% for p in products %}
            <tr>
                <td style="padding:10px;">{{ p['name'] }}</td>
                <td style="padding:10px; font-size: 0.8rem;">{{ p['description'] }}</td>
                <td style="text-align:center;">{{ p['price'] }}</td>
                <td style="text-align:center;">
                    <form method="post">
                        <input type="hidden" name="id" value="{{ p['id'] }}">
                        <input type="hidden" name="action" value="admin_delete">
                        <button type="submit" style="background:red; color:white; border:none; padding:5px 10px; border-radius:5px; cursor:pointer;" onclick="return confirm('حذف؟')">حذف 🗑️</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </table>
        <br><a href="/">⬅️ العودة للمتجر</a>
    </div>
    ''', products=products)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
