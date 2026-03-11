from flask import Flask, render_template_string, request, redirect, url_for, session
import os
import psycopg2
from psycopg2.extras import DictCursor

app = Flask(__name__)
app.secret_key = "ein_store_2026_secure"

# جلب رابط قاعدة البيانات من إعدادات Render
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # السطر التالي يمسح الجدول القديم ليبنيه من جديد بالخانات الجديدة (صور، وصف)
    # ملاحظة: بعد ما يشتغل الموقع، يفضل حذف السطر التالي لكي لا يمسح منتجاتك مستقبلاً 
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            price NUMERIC NOT NULL,
            description TEXT,
            image_url TEXT
        )
    ''')
    
    # إضافة المنتجات الأساسية تلقائياً عند أول تشغيل
    initial_products = [
        ('يوتيوب بريميوم', 3, 'اشتراك شهر كامل شامل الضمان', 'https://upload.wikimedia.org/wikipedia/commons/e/ef/Youtube_logo.png'),
        ('تيليجرام بريميوم', 5, 'تفعيل رسمي على رقمك الخاص', 'https://upload.wikimedia.org/wikipedia/commons/8/82/Telegram_logo.svg'),
        ('شاهد VIP', 15, 'باقة المسلسلات والأفلام بأعلى جودة', 'https://upload.wikimedia.org/wikipedia/commons/a/a2/Shahid_VOD_Logo.png')
    ]
    cur.executemany("INSERT INTO products (name, price, description, image_url) VALUES (%s, %s, %s, %s)", initial_products)
    
    conn.commit()
    cur.close()
    conn.close()

# تشغيل تهيئة القاعدة
init_db()

# --- واجهة المتجر الرئيسية ---
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
            body { font-family: 'Segoe UI', sans-serif; background: #f0f2f5; margin: 0; padding: 20px; text-align: center; }
            .container { max-width: 1000px; margin: auto; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 30px; }
            .card { background: white; padding: 20px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
            .card img { width: 120px; height: 120px; object-fit: contain; margin-bottom: 15px; border-radius: 15px; }
            .price { font-size: 26px; color: #4338ca; font-weight: bold; margin: 15px 0; }
            .btn-buy { background: #4338ca; color: white; border: none; padding: 12px; border-radius: 12px; width: 100%; cursor: pointer; font-size: 18px; font-weight: bold; }
            .btn-buy:hover { background: #3730a3; }
            .admin-link { margin-top: 50px; display: inline-block; color: #94a3b8; text-decoration: none; font-size: 14px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 style="color: #1e293b; font-size: 2.5em;">🛒 متجر عيـن</h1>
            <p style="color: #64748b;">أفضل الاشتراكات الرقمية بأقل الأسعار</p>
            <div class="grid">
                {% for p in products %}
                <div class="card">
                    <img src="{{ p['image_url'] or 'https://via.placeholder.com/150' }}">
                    <h3>{{ p['name'] }}</h3>
                    <p style="color: #64748b; font-size: 14px; height: 40px;">{{ p['description'] }}</p>
                    <div class="price">{{ p['price'] }} ريال</div>
                    <button class="btn-buy">شراء الآن</button>
                </div>
                {% endfor %}
            </div>
            <a href="/admin" class="admin-link">⚙️ لوحة التحكم</a>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html, products=products)

# --- لوحة التحكم ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == '123456': # كلمة مرورك
            session['logged_in'] = True
        elif 'logged_in' in session:
            conn = get_db_connection()
            cur = conn.cursor()
            action = request.form.get('action')
            
            if action == 'update':
                cur.execute("UPDATE products SET name=%s, price=%s, image_url=%s, description=%s WHERE id=%s", 
                            (request.form.get('name'), request.form.get('price'), request.form.get('image_url'), request.form.get('description'), request.form.get('id')))
            elif action == 'add':
                cur.execute("INSERT INTO products (name, price, image_url, description) VALUES (%s, %s, %s, %s)",
                            (request.form.get('name'), request.form.get('price'), request.form.get('image_url'), request.form.get('description')))
            elif action == 'delete':
                cur.execute("DELETE FROM products WHERE id=%s", (request.form.get('id'),))
                
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('admin'))

    if not session.get('logged_in'):
        return '<div dir="rtl" style="text-align:center;padding:100px;font-family:sans-serif;"><form method="post"><h2>دخول الإدارة</h2><input type="password" name="password" style="padding:10px;"><button type="submit" style="padding:10px;">دخول</button></form></div>'

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products ORDER BY id ASC")
    products = cur.fetchall()
    cur.close()
    conn.close()

    return render_template_string('''
    <div dir="rtl" style="font-family: sans-serif; padding: 20px; max-width: 1200px; margin: auto;">
        <h2>⚙️ إدارة منتجات متجر عين</h2>
        <table border="1" style="width:100%; border-collapse: collapse; text-align: center; margin-bottom: 30px;">
            <tr style="background: #f1f5f9;">
                <th>اسم المنتج</th><th>السعر</th><th>رابط الصورة</th><th>الوصف</th><th>إجراء</th>
            </tr>
            {% for p in products %}
            <tr>
                <form method="post">
                    <input type="hidden" name="action" value="update">
                    <input type="hidden" name="id" value="{{ p['id'] }}">
                    <td><input type="text" name="name" value="{{ p['name'] }}"></td>
                    <td><input type="number" name="price" value="{{ p['price'] }}" step="0.1" style="width:60px;"></td>
                    <td><input type="text" name="image_url" value="{{ p['image_url'] }}"></td>
                    <td><input type="text" name="description" value="{{ p['description'] }}"></td>
                    <td>
                        <button type="submit" style="background: #059669; color: white; border: none; padding: 5px 10px; border-radius: 5px;">حفظ</button>
                        <button name="action" value="delete" style="background: #dc2626; color: white; border: none; padding: 5px 10px; border-radius: 5px;">حذف</button>
                    </td>
                </form>
            </tr>
            {% endfor %}
        </table>

        <div style="background: #f8fafc; padding: 20px; border-radius: 15px; border: 1px solid #e2e8f0;">
            <h3>➕ إضافة منتج جديد</h3>
            <form method="post">
                <input type="hidden" name="action" value="add">
                <input type="text" name="name" placeholder="اسم المنتج" required>
                <input type="number" name="price" placeholder="السعر" required style="width:80px;">
                <input type="text" name="image_url" placeholder="رابط الصورة">
                <input type="text" name="description" placeholder="وصف قصير">
                <button type="submit" style="background: #4338ca; color: white; padding: 8px 20px; border-radius: 8px; border: none;">إضافة للمتجر</button>
            </form>
        </div>
        <br><a href="/">⬅️ العودة للمتجر</a> | <a href="/logout">تسجيل خروج</a>
    </div>
    ''', products=products)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
