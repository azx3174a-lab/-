from flask import Flask, render_template_string, request, redirect, url_for, session
import os
import psycopg2
from psycopg2.extras import DictCursor
import base64

app = Flask(__name__)
app.secret_key = "eyin_secret_key_v10"

# !!! رقم واتسابك !!!
MY_WHATSAPP = "966550963174" 

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# --- الصفحة الرئيسية (بدون رابط إدارة) ---
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
            :root { --bg: #f8fafc; --card: #ffffff; --text: #1e293b; --muted: #64748b; --primary: #4f46e5; --border: #e2e8f0; }
            [data-theme="dark"] { --bg: #0f172a; --card: #1e293b; --text: #f8fafc; --muted: #94a3b8; --primary: #818cf8; --border: #334155; }
            body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; transition: 0.3s; }
            .header { display: flex; justify-content: space-between; align-items: center; max-width: 1100px; margin: auto; }
            .theme-btn { background: var(--card); border: 1px solid var(--border); cursor: pointer; padding: 10px; border-radius: 50%; font-size: 20px; color: var(--text); }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 25px; max-width: 1100px; margin: 40px auto; }
            .card { background: var(--card); padding: 25px; border-radius: 24px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); border: 1px solid var(--border); position: relative; }
            .card img { width: 110px; height: 110px; object-fit: contain; border-radius: 18px; margin-bottom: 15px; }
            .price { font-size: 26px; color: var(--primary); font-weight: bold; margin-bottom: 20px; }
            .btn-buy { background: #25d366; color: white; border: none; padding: 12px; border-radius: 12px; width: 100%; cursor: pointer; font-size: 1.1em; font-weight: bold; text-decoration: none; display: block; text-align: center; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1 style="margin:0;"> متجر عيـن</h1>
            <button class="theme-btn" onclick="toggleTheme()" id="theme-icon">🌙</button>
        </div>
        <div class="grid">
            {% for p in products %}
            <div class="card">
                <img src="{{ p['image_url'] or 'https://via.placeholder.com/150' }}">
                <h3>{{ p['name'] }}</h3>
                <p style="color: var(--muted); font-size: 0.95em; min-height: 45px;">{{ p['description'] or '' }}</p>
                <div class="price">{{ p['price'] }} ريال</div>
                <a href="https://wa.me/{{ whatsapp }}?text=أرغب في شراء: {{ p['name'] }}" class="btn-buy" target="_blank">شراء عبر واتساب</a>
            </div>
            {% endfor %}
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
            document.getElementById('theme-icon').innerText = savedTheme === 'dark' ? '☀️' : '🌙';
        </script>
    </body>
    </html>
    '''
    return render_template_string(html, products=products, whatsapp=MY_WHATSAPP)

# --- رابط لوحة التحكم السري (تغير من admin إلى eyin-control) ---
@app.route('/eyin-control', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == '317400':
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
        return '<div dir="rtl" style="text-align:center;padding:100px;"><h2>🔐 دخول خاص</h2><form method="post"><input type="password" name="password"><button type="submit">دخول</button></form></div>'

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products ORDER BY id ASC")
    products = cur.fetchall()
    cur.close()
    conn.close()

    return render_template_string('''
    <div dir="rtl" style="font-family: sans-serif; padding: 20px;">
        <h2>⚙️ لوحة التحكم السرية</h2>
        <table border="1" style="width:100%; border-collapse: collapse;">
            {% for p in products %}
            <tr>
                <form method="post" enctype="multipart/form-data">
                    <input type="hidden" name="id" value="{{ p['id'] }}">
                    <input type="hidden" name="existing_image" value="{{ p['image_url'] }}">
                    <td><input type="text" name="name" value="{{ p['name'] }}"></td>
                    <td><input type="number" name="price" value="{{ p['price'] }}"></td>
                    <td><textarea name="description">{{ p['description'] }}</textarea></td>
                    <td><img src="{{ p['image_url'] }}" width="40"><br><input type="file" name="image_file"></td>
                    <td>
                        <button type="submit" name="action" value="update">حفظ</button>
                        <button type="submit" name="action" value="delete">حذف</button>
                    </td>
                </form>
            </tr>
            {% endfor %}
        </table>
        <hr>
        <h3>اضافة منتج</h3>
        <form method="post" enctype="multipart/form-data">
            <input type="hidden" name="action" value="add">
            الاسم: <input type="text" name="name" required>
            السعر: <input type="number" name="price" required>
            الوصف: <input type="text" name="description">
            الصورة: <input type="file" name="image_file" required>
            <button type="submit">إضافة</button>
        </form>
        <br><a href="/">الخروج للمتجر</a>
    </div>
    ''', products=products)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
