from flask import Flask, render_template_string, request, redirect, url_for, session
import os
import psycopg2
from psycopg2.extras import DictCursor
import base64

app = Flask(__name__)
app.secret_key = "ein_store_2026_dark_mode_v5"

# !!! ضع رقم واتسابك هنا (مثال: 966500000000) !!!
MY_WHATSAPP = "966550963174" 

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            price NUMERIC NOT NULL,
            description TEXT,
            image_url TEXT
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

init_db()

# --- واجهة المتجر الرئيسية مع ميزة الوضع الداكن ---
@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products ORDER BY id ASC")
    products = cur.fetchall()
    cur.close()
    conn.close()
    
    html = '''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>متجر عين</title>
        <style>
            :root {
                --bg-color: #f8fafc;
                --card-bg: #ffffff;
                --text-main: #1e293b;
                --text-muted: #64748b;
                --primary: #4f46e5;
                --border: #e2e8f0;
            }
            [data-theme="dark"] {
                --bg-color: #0f172a;
                --card-bg: #1e293b;
                --text-main: #f8fafc;
                --text-muted: #94a3b8;
                --primary: #818cf8;
                --border: #334155;
            }
            body { 
                font-family: 'Segoe UI', sans-serif; 
                background: var(--bg-color); 
                color: var(--text-main);
                margin: 0; padding: 20px; 
                transition: background 0.3s, color 0.3s;
            }
            .header { display: flex; justify-content: space-between; align-items: center; max-width: 1100px; margin: auto; }
            .theme-btn { 
                background: var(--card-bg); border: 1px solid var(--border); 
                cursor: pointer; padding: 10px; border-radius: 50%; width: 45px; height: 45px;
                display: flex; align-items: center; justify-content: center; font-size: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 25px; max-width: 1100px; margin: 40px auto; }
            .card { 
                background: var(--card-bg); padding: 25px; border-radius: 24px; 
                box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); border: 1px solid var(--border); 
            }
            .card img { width: 110px; height: 110px; object-fit: contain; border-radius: 18px; margin-bottom: 15px; }
            .price { font-size: 26px; color: var(--primary); font-weight: bold; margin-bottom: 20px; }
            .btn-buy { background: #25d366; color: white; border: none; padding: 12px; border-radius: 12px; width: 100%; cursor: pointer; font-size: 1.1em; font-weight: bold; text-decoration: none; display: block; }
            .admin-link { margin-top: 60px; display: inline-block; color: var(--text-muted); text-decoration: none; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1 style="margin:0;">🛒 متجر عيـن</h1>
            <button class="theme-btn" onclick="toggleTheme()" id="theme-icon">🌙</button>
        </div>
        
        <div class="grid">
            {% for p in products %}
            <div class="card">
                <img src="{{ p['image_url'] or 'https://via.placeholder.com/150' }}">
                <h3>{{ p['name'] }}</h3>
                <p style="color: var(--text-muted); font-size: 0.95em; min-height: 45px;">{{ p['description'] or 'اشتراك رقمي مميز' }}</p>
                <div class="price">{{ p['price'] }} ريال</div>
                <a href="https://wa.me/{{ whatsapp }}?text=أهلاً متجر عين، أرغب في شراء: {{ p['name'] }}" class="btn-buy" target="_blank">شراء عبر واتساب</a>
            </div>
            {% endfor %}
        </div>
        <center><a href="/admin" class="admin-link">⚙️ لوحة الإدارة</a></center>

        <script>
            function toggleTheme() {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                document.getElementById('theme-icon').innerText = newTheme === 'dark' ? '☀️' : '🌙';
            }
            // استعادة الثيم المفضل عند التحميل
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
            document.getElementById('theme-icon').innerText = savedTheme === 'dark' ? '☀️' : '🌙';
        </script>
    </body>
    </html>
    '''
    return render_template_string(html, products=products, whatsapp=MY_WHATSAPP)

# --- لوحة التحكم (تبقى كما هي لسهولة الإدارة) ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == '123456':
            session['logged_in'] = True
        elif 'logged_in' in session:
            conn = get_db_connection()
            cur = conn.cursor()
            action = request.form.get('action')
            
            image_data = request.form.get('existing_image')
            if 'image_file' in request.files:
                file = request.files['image_file']
                if file.filename != '':
                    encoded_string = base64.b64encode(file.read()).decode('utf-8')
                    image_data = f"data:{file.content_type};base64,{encoded_string}"

            if action == 'add':
                cur.execute("INSERT INTO products (name, price, image_url, description) VALUES (%s, %s, %s, %s)",
                            (request.form.get('name'), request.form.get('price'), image_data, request.form.get('description')))
            elif action == 'update':
                cur.execute("UPDATE products SET name=%s, price=%s, image_url=%s, description=%s WHERE id=%s", 
                            (request.form.get('name'), request.form.get('price'), image_data, request.form.get('description'), request.form.get('id')))
            elif action == 'delete':
                cur.execute("DELETE FROM products WHERE id = %s", (request.form.get('id'),))
            
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('admin'))

    if not session.get('logged_in'):
        return '<div dir="rtl" style="text-align:center;padding:100px;"><h2>دخول الإدارة</h2><form method="post"><input type="password" name="password"><button type="submit">دخول</button></form></div>'

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products ORDER BY id ASC")
    products = cur.fetchall()
    cur.close()
    conn.close()

    return render_template_string('''
    <div dir="rtl" style="font-family: sans-serif; padding: 20px;">
        <h2>⚙️ إدارة المتجر</h2>
        <table border="1" style="width:100%; border-collapse: collapse;">
            <tr style="background:#eee;"><th>المنتج</th><th>السعر</th><th>الوصف</th><th>الصورة</th><th>إجراء</th></tr>
            {% for p in products %}
            <tr>
                <form method="post" enctype="multipart/form-data">
                    <input type="hidden" name="id" value="{{ p['id'] }}">
                    <input type="hidden" name="existing_image" value="{{ p['image_url'] }}">
                    <td><input type="text" name="name" value="{{ p['name'] }}" style="width:100px;"></td>
                    <td><input type="number" name="price" value="{{ p['price'] }}" style="width:50px;"></td>
                    <td><textarea name="description">{{ p['description'] }}</textarea></td>
                    <td><img src="{{ p['image_url'] }}" width="40"><br><input type="file" name="image_file" style="font-size:10px;"></td>
                    <td>
                        <button type="submit" name="action" value="update" style="background:green; color:white;">حفظ</button>
                        <button type="submit" name="action" value="delete" style="background:red; color:white;" onclick="return confirm('حذف؟')">حذف</button>
                    </td>
                </form>
            </tr>
            {% endfor %}
        </table>
        <div style="background:#f1f5f9; padding:20px; border-radius:10px; margin-top:20px;">
            <h3>➕ إضافة منتج جديد</h3>
            <form method="post" enctype="multipart/form-data">
                <input type="hidden" name="action" value="add">
                الاسم: <input type="text" name="name" required>
                السعر: <input type="number" name="price" required style="width:60px;">
                الوصف: <input type="text" name="description">
                الصورة: <input type="file" name="image_file" accept="image/*" required>
                <button type="submit">إضافة</button>
            </form>
        </div>
        <br><a href="/">العودة للمتجر</a>
    </div>
    ''', products=products)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
