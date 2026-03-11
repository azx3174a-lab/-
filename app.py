from flask import Flask, render_template_string, request, redirect, url_for, session
import os
import psycopg2
from psycopg2.extras import DictCursor

app = Flask(__name__)
app.secret_key = "ein_store_secret_123" # مفتاح لتأمين لوحة التحكم

# رابط قاعدة البيانات من Render
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# إنشاء الجداول وإضافة المنتجات الأولية إذا كانت فارغة
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            price NUMERIC NOT NULL,
            description TEXT
        )
    ''')
    cur.execute("SELECT COUNT(*) FROM products")
    if cur.fetchone()[0] == 0:
        products = [
            ('يوتيوب بريميوم', 3, 'اشتراك شهر كامل شامل الضمان'),
            ('تيليجرام بريميوم', 5, 'تفعيل رسمي على رقمك الخاص'),
            ('شاهد VIP', 15, 'باقة المسلسلات والأفلام بأعلى جودة')
        ]
        cur.executemany("INSERT INTO products (name, price, description) VALUES (%s, %s, %s)", products)
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
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>متجر عين | للمنتجات الرقمية</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f7f6; margin: 0; padding: 20px; text-align: center; }
            .container { max-width: 900px; margin: auto; }
            h1 { color: #4338ca; margin-bottom: 30px; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
            .card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: 0.3s; }
            .card:hover { transform: translateY(-5px); }
            .price { font-size: 24px; color: #059669; font-weight: bold; margin: 10px 0; }
            button { background: #4338ca; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-size: 16px; width: 100%; }
            button:hover { background: #3730a3; }
            .admin-link { margin-top: 50px; display: block; color: #999; text-decoration: none; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛒 متجر عيـن</h1>
            <div class="grid">
                {% for p in products %}
                <div class="card">
                    <div style="font-size: 50px;">📦</div>
                    <h3>{{ p['name'] }}</h3>
                    <p>{{ p['description'] }}</p>
                    <div class="price">{{ p['price'] }} ريال</div>
                    <button>شراء الآن</button>
                </div>
                {% endfor %}
            </div>
            <a href="/admin" class="admin-link">دخول الإدارة</a>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html, products=products)

# --- لوحة التحكم ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == '123456': # كلمة مرورك السرية (غيرها لاحقاً)
            session['logged_in'] = True
        elif 'logged_in' in session:
            # تعديل سعر أو منتج
            conn = get_db_connection()
            cur = conn.cursor()
            p_id = request.form.get('id')
            new_price = request.form.get('price')
            cur.execute("UPDATE products SET price = %s WHERE id = %s", (new_price, p_id))
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('admin'))
    
    if not session.get('logged_in'):
        return '''
        <div style="text-align:center; padding: 50px;">
            <form method="post">
                <h2>دخول الإدارة</h2>
                <input type="password" name="password" placeholder="كلمة المرور">
                <button type="submit">دخول</button>
            </form>
        </div>
        '''
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products ORDER BY id ASC")
    products = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template_string('''
    <div dir="rtl" style="font-family: Arial; padding: 20px;">
        <h2>لوحة تحكم متجر عين</h2>
        <table border="1" style="width:100%; text-align:center;">
            <tr><th>المنتج</th><th>السعر الحالي</th><th>تعديل السعر</th></tr>
            {% for p in products %}
            <tr>
                <td>{{ p['name'] }}</td>
                <td>{{ p['price'] }} ريال</td>
                <td>
                    <form method="post" style="display:inline;">
                        <input type="hidden" name="id" value="{{ p['id'] }}">
                        <input type="number" name="price" step="0.1" value="{{ p['price'] }}">
                        <button type="submit">تحديث</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </table>
        <br><a href="/">العودة للمتجر</a> | <a href="/logout">تسجيل خروج</a>
    </div>
    ''', products=products)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
