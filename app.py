from flask import Flask, render_template_string, request, redirect, url_for, session
import os
import psycopg2
from psycopg2.extras import DictCursor
import base64

app = Flask(__name__)
app.secret_key = "ein_store_2026_full_v3"

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # التأكد من وجود عمود الوصف والصور
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
            body { font-family: 'Segoe UI', sans-serif; background: #f8fafc; margin: 0; padding: 20px; text-align: center; color: #1e293b; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 25px; max-width: 1100px; margin: 40px auto; }
            .card { background: white; padding: 25px; border-radius: 24px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; transition: 0.3s; }
            .card:hover { transform: translateY(-5px); box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }
            .card img { width: 110px; height: 110px; object-fit: contain; border-radius: 18px; margin-bottom: 15px; }
            .card h3 { margin: 10px 0; font-size: 1.4em; }
            .desc { color: #64748b; font-size: 0.95em; min-height: 45px; margin-bottom: 15px; line-height: 1.5; }
            .price { font-size: 26px; color: #4f46e5; font-weight: bold; margin-bottom: 20px; }
            .btn-buy { background: #4f46e5; color: white; border: none; padding: 12px; border-radius: 12px; width: 100%; cursor: pointer; font-size: 1.1em; font-weight: 600; }
            .admin-link { margin-top: 60px; display: inline-block; color: #94a3b8; text-decoration: none; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <h1 style="font-size: 2.5em; margin-bottom: 10px;">🛒 متجر عيـن</h1>
        <p style="color: #64748b;">وجهتك الأولى للاشتراكات الرقمية الموثوقة</p>
        
        <div class="grid">
            {% for p in products %}
            <div class="card">
                <img src="{{ p['image_url'] or 'https://via.placeholder.com/150' }}">
                <h3>{{ p['name'] }}</h3>
                <div class="desc">{{ p['description'] or 'لا يوجد وصف متاح' }}</div>
                <div class="price">{{ p['price'] }} ريال</div>
                <button class="btn-buy">شراء الآن</button>
            </div>
            {% endfor %}
        </div>
        <a href="/admin" class="admin-link">⚙️ لوحة التحكم للإدارة</a>
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
            
            # معالجة الصورة
            image_data = request.form.get('existing_image')
            if 'image_file' in request.files:
                file = request.files['image_file']
                if file.filename != '':
                    encoded_string = base64.b64encode(file.read()).decode('utf-8')
                    image_data = f"data:{file.content_type};base64,{encoded_string}"

            if action == 'update':
                cur.execute("UPDATE products SET name=%s, price=%s, image_url=%s, description=%s WHERE id=%s", 
                            (request.form.get('name'), request.form.get('price'), image_data, request.form.get('description'), request.form.get('id')))
            elif action == 'add':
                cur.execute("INSERT INTO products (name, price, image_url, description) VALUES (%s, %s, %s, %s)",
                            (request.form.get('name'), request.form.get('price'), image_data, request.form.get('description')))
            elif action == 'delete':
                cur.execute("DELETE FROM products WHERE id=%s", (request.form.get('id'),))
                
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('admin'))

    if not session.get('logged_in'):
        return '<div dir="rtl" style="text-align:center;padding:100px;font-family:sans-serif;"><h2>دخول الإدارة</h2><form method="post"><input type="password" name="password" style="padding:8px;"><button type="submit" style="padding:8px 20px; cursor:pointer;">دخول</button></form></div>'

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products ORDER BY id ASC")
    products = cur.fetchall()
    cur.close()
    conn.close()

    return render_template_string('''
    <div dir="rtl" style="font-family: sans-serif; padding: 30px; max-width: 1200px; margin: auto;">
        <h2 style="border-bottom: 2px solid #eee; padding-bottom: 15px;">⚙️ التحكم بالمنتجات والوصف</h2>
        <table border="1" style="width:100%; border-collapse: collapse; text-align: center; margin-top: 20px;">
            <tr style="background:#f8fafc;">
                <th>المنتج</th><th>السعر</th><th>الوصف الحالي</th><th>الصورة</th><th>تحديث بيانات</th><th>إجراء</th>
            </tr>
            {% for p in products %}
            <tr style="border-bottom: 1px solid #eee;">
                <form method="post" enctype="multipart/form-data">
                    <input type="hidden" name="action" value="update">
                    <input type="hidden" name="id" value="{{ p['id'] }}">
                    <input type="hidden" name="existing_image" value="{{ p['image_url'] }}">
                    <td><input type="text" name="name" value="{{ p['name'] }}" style="width:100px;"></td>
                    <td><input type="number" name="price" value="{{ p['price'] }}" style="width:50px;"></td>
                    <td><textarea name="description" rows="2" style="width:180px;">{{ p['description'] }}</textarea></td>
                    <td><img src="{{ p['image_url'] }}" width="45" style="border-radius:5px;"></td>
                    <td><input type="file" name="image_file" accept="image/*" style="width:150px; font-size:10px;"></td>
                    <td>
                        <button type="submit" style="background:#059669; color:white; border:none; padding:8px 15px; border-radius:5px; cursor:pointer;">حفظ</button>
                        <button name="action" value="delete" style="background:#dc2626; color:white; border:none; padding:8px 15px; border-radius:5px; cursor:pointer; margin-top:5px;">حذف</button>
                    </td>
                </form>
            </tr>
            {% endfor %}
        </table>
        
        <div style="background:#f1f5f9; padding:25px; border-radius:15px; margin-top:40px;">
            <h3>➕ إضافة منتج جديد بوصف وصورة</h3>
            <form method="post" enctype="multipart/form-data">
                <input type="hidden" name="action" value="add">
                اسم المنتج: <input type="text" name="name" required style="margin:5px;">
                السعر: <input type="number" name="price" required style="width:70px; margin:5px;">
                <br>الوصف: <textarea name="description" placeholder="مثلاً: اشتراك لمدة سنة كاملة مع ضمان" style="width:90%; margin:10px 0;"></textarea>
                <br>اختيار الصورة: <input type="file" name="image_file" accept="image/*" required style="margin:10px 0;">
                <br><button type="submit" style="background:#4f46e5; color:white; padding:12px 30px; border-radius:10px; border:none; cursor:pointer; font-weight:bold;">إضافة المنتج للمتجر</button>
            </form>
        </div>
        <br><a href="/" style="color:#4f46e5; text-decoration:none;">⬅️ العودة لصفحة المتجر</a> | <a href="/logout" style="color:#dc2626;">خروج</a>
    </div>
    ''', products=products)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
