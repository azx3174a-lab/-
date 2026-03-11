from flask import Flask, render_template_string, request, redirect, url_for, session
import os
import psycopg2
from psycopg2.extras import DictCursor

app = Flask(__name__)
app.secret_key = "ein_store_secret_secure"

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
    cur.execute("SELECT COUNT(*) FROM products")
    if cur.fetchone()[0] == 0:
        # صور افتراضية للمنتجات الرقمية
        products = [
            ('يوتيوب بريميوم', 3, 'اشتراك شهر كامل شامل الضمان', 'https://upload.wikimedia.org/wikipedia/commons/e/ef/Youtube_logo.png'),
            ('تيليجرام بريميوم', 5, 'تفعيل رسمي على رقمك الخاص', 'https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg'),
            ('شاهد VIP', 15, 'باقة المسلسلات والأفلام بأعلى جودة', 'https://upload.wikimedia.org/wikipedia/commons/a/a2/Shahid_VOD_Logo.png')
        ]
        cur.executemany("INSERT INTO products (name, price, description, image_url) VALUES (%s, %s, %s, %s)", products)
    conn.commit()
    cur.close()
    conn.close()

init_db()

# --- واجهة المتجر ---
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
    <html dir="rtl">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>متجر عين | للمنتجات الرقمية</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; background: #f8fafc; margin: 0; padding: 20px; text-align: center; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; max-width: 1000px; margin: auto; }
            .card { background: white; padding: 20px; border-radius: 20px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }
            .card img { width: 100px; height: 100px; object-fit: contain; margin-bottom: 15px; border-radius: 10px; }
            .price { font-size: 24px; color: #4f46e5; font-weight: bold; }
            button { background: #4f46e5; color: white; border: none; padding: 12px; border-radius: 10px; width: 100%; cursor: pointer; font-weight: bold; }
            .admin-btn { margin-top: 40px; display: inline-block; color: #64748b; text-decoration: none; font-size: 13px; }
        </style>
    </head>
    <body>
        <h1>🛒 متجر عيـن للمنتجات الرقمية</h1>
        <div class="grid">
            {% for p in products %}
            <div class="card">
                <img src="{{ p['image_url'] or 'https://via.placeholder.com/100' }}" alt="product">
                <h3>{{ p['name'] }}</h3>
                <p style="color: #64748b; font-size: 14px;">{{ p['description'] }}</p>
                <div class="price">{{ p['price'] }} ريال</div>
                <button>شراء الآن</button>
            </div>
            {% endfor %}
        </div>
        <a href="/admin" class="admin-btn">لوحة التحكم</a>
    </body>
    </html>
    '''
    return render_template_string(html, products=products)

# --- لوحة التحكم ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == '123456':
            session['logged_in'] = True
        elif 'logged_in' in session:
            conn = get_db_connection()
            cur = conn.cursor()
            action = request.form.get('action')
            
            if action == 'update':
                cur.execute("UPDATE products SET name=%s, price=%s, image_url=%s WHERE id=%s", 
                            (request.form.get('name'), request.form.get('price'), request.form.get('image_url'), request.form.get('id')))
            elif action == 'add':
                cur.execute("INSERT INTO products (name, price, image_url, description) VALUES (%s, %s, %s, %s)",
                            (request.form.get('name'), request.form.get('price'), request.form.get('image_url'), 'وصف المنتج الجديد'))
            elif action == 'delete':
                cur.execute("DELETE FROM products WHERE id=%s", (request.form.get('id'),))
                
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('admin'))

    if not session.get('logged_in'):
        return '<div style="text-align:center;padding:100px;"><form method="post"><h2>قفل الإدارة</h2><input type="password" name="password"><button type="submit">دخول</button></form></div>'

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products ORDER BY id ASC")
    products = cur.fetchall()
    cur.close()
    conn.close()

    return render_template_string('''
    <div dir="rtl" style="font-family: sans-serif; padding: 20px;">
        <h2>التحكم بالمنتجات</h2>
        <table border="1" style="width:100%; border-collapse: collapse; text-align: center;">
            <tr style="background: #f1f5f9;"><th>المنتج</th><th>السعر</th><th>رابط الصورة</th><th>إجراء</th></tr>
            {% for p in products %}
            <tr>
                <form method="post">
                    <input type="hidden" name="action" value="update">
                    <input type="hidden" name="id" value="{{ p['id'] }}">
                    <td><input type="text" name="name" value="{{ p['name'] }}"></td>
                    <td><input type="number" name="price" value="{{ p['price'] }}" step="0.1" style="width:60px;"></td>
                    <td><input type="text" name="image_url" value="{{ p['image_url'] }}" style="width:200px;"></td>
                    <td><button type="submit">حفظ</button> | <button name="action" value="delete" style="color:red;">حذف</button></td>
                </form>
            </tr>
            {% endfor %}
        </table>
        <hr>
        <h3>إضافة منتج جديد</h3>
        <form method="post" style="background:#f1f5f9; padding:15px; border-radius:10px;">
            <input type="hidden" name="action" value="add">
            اسم المنتج: <input type="text" name="name" required>
            السعر: <input type="number" name="price" required style="width:60px;">
            رابط الصورة: <input type="text" name="image_url" placeholder="http://...">
            <button type="submit">إضافة المنتج</button>
        </form>
        <br><a href="/">العودة للمتجر</a> | <a href="/logout">خروج</a>
    </div>
    ''', products=products)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
