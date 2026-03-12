from flask import Flask, render_template_string, request, redirect, url_for, session
import os
import psycopg2
from psycopg2.extras import DictCursor
import base64

app = Flask(__name__)
app.secret_key = "ein_store_2026_upload_secure"

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # تأكدنا أن الجدول جاهز لاستقبال نصوص الصور الطويلة
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
            body { font-family: 'Segoe UI', sans-serif; background: #f0f2f5; margin: 0; padding: 20px; text-align: center; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; max-width: 1000px; margin: auto; }
            .card { background: white; padding: 20px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
            .card img { width: 120px; height: 120px; object-fit: contain; border-radius: 15px; margin-bottom: 10px; }
            .price { font-size: 24px; color: #4338ca; font-weight: bold; }
            .btn-buy { background: #4338ca; color: white; border: none; padding: 10px; border-radius: 10px; width: 100%; cursor: pointer; }
            .admin-link { margin-top: 40px; display: inline-block; color: #94a3b8; text-decoration: none; }
        </style>
    </head>
    <body>
        <h1>🛒 متجر عيـن</h1>
        <div class="grid">
            {% for p in products %}
            <div class="card">
                <img src="{{ p['image_url'] or 'https://via.placeholder.com/150' }}">
                <h3>{{ p['name'] }}</h3>
                <p style="color:#64748b;">{{ p['description'] }}</p>
                <div class="price">{{ p['price'] }} ريال</div>
                <button class="btn-buy">شراء الآن</button>
            </div>
            {% endfor %}
        </div>
        <a href="/admin" class="admin-link">⚙️ لوحة التحكم</a>
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
            
            # معالجة الصورة المرفوعة
            image_data = request.form.get('existing_image')
            if 'image_file' in request.files:
                file = request.files['image_file']
                if file.filename != '':
                    # تحويل الصورة إلى Base64
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
        return '<div dir="rtl" style="text-align:center;padding:100px;"><h2>دخول الإدارة</h2><form method="post"><input type="password" name="password"><button type="submit">دخول</button></form></div>'

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products ORDER BY id ASC")
    products = cur.fetchall()
    cur.close()
    conn.close()

    return render_template_string('''
    <div dir="rtl" style="font-family: sans-serif; padding: 20px;">
        <h2>إدارة المنتجات (رفع مباشر)</h2>
        <table border="1" style="width:100%; border-collapse: collapse; text-align: center;">
            <tr style="background:#f1f5f9;"><th>المنتج</th><th>السعر</th><th>الصورة</th><th>تغيير الصورة</th><th>إجراء</th></tr>
            {% for p in products %}
            <tr>
                <form method="post" enctype="multipart/form-data">
                    <input type="hidden" name="action" value="update">
                    <input type="hidden" name="id" value="{{ p['id'] }}">
                    <input type="hidden" name="existing_image" value="{{ p['image_url'] }}">
                    <td><input type="text" name="name" value="{{ p['name'] }}"></td>
                    <td><input type="number" name="price" value="{{ p['price'] }}" style="width:50px;"></td>
                    <td><img src="{{ p['image_url'] }}" width="50"></td>
                    <td><input type="file" name="image_file" accept="image/*"></td>
                    <td><button type="submit">حفظ</button> | <button name="action" value="delete" style="color:red;">حذف</button></td>
                </form>
            </tr>
            {% endfor %}
        </table>
        <hr>
        <h3>➕ إضافة منتج جديد بصورة</h3>
        <form method="post" enctype="multipart/form-data" style="background:#f1f5f9; padding:20px; border-radius:10px;">
            <input type="hidden" name="action" value="add">
            الاسم: <input type="text" name="name" required>
            السعر: <input type="number" name="price" required>
            الوصف: <input type="text" name="description">
            اختيار الصورة: <input type="file" name="image_file" accept="image/*" required>
            <button type="submit">إضافة للمتجر</button>
        </form>
        <br><a href="/">العودة للمتجر</a>
    </div>
    ''', products=products)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
