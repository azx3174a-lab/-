from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import os
import psycopg2
from psycopg2.extras import DictCursor
import base64
from datetime import datetime

app = Flask(__name__)
app.secret_key = "eyin_comments_v19"

DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # جدول الإعدادات والمنتجات
    cur.execute("CREATE TABLE IF NOT EXISTS settings (id SERIAL PRIMARY KEY, key TEXT UNIQUE, value TEXT)")
    cur.execute("INSERT INTO settings (key, value) VALUES ('logo', '') ON CONFLICT (key) DO NOTHING")
    cur.execute("CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, name TEXT, price TEXT, image_url TEXT, description TEXT, whatsapp TEXT, delete_code TEXT)")
    # جدول التعليقات الجديد
    cur.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id SERIAL PRIMARY KEY, 
            product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
            author TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    
    # معالجة حذف المنتج (للمستخدم بالكود)
    if request.method == 'POST' and request.form.get('action') == 'delete':
        product_id = request.form.get('id')
        user_code = request.form.get('user_code')
        cur.execute("SELECT delete_code FROM products WHERE id = %s", (product_id,))
        res = cur.fetchone()
        if res and res['delete_code'] == user_code:
            cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
            conn.commit()
            flash('✅ تم حذف المنتج بنجاح', 'success')
        else:
            flash('❌ الكود السري غير صحيح', 'error')
        return redirect(url_for('index'))

    cur.execute("SELECT * FROM products ORDER BY id DESC")
    products = cur.fetchall()
    
    # جلب التعليقات لكل منتج
    cur.execute("SELECT * FROM comments ORDER BY created_at ASC")
    all_comments = cur.fetchall()
    
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
        <title>متجر عين - التفاعلي</title>
        <style>
            :root { --bg: #f8fafc; --card: #ffffff; --text: #1e293b; --muted: #64748b; --primary: #4f46e5; --border: #e2e8f0; }
            [data-theme="dark"] { --bg: #0f172a; --card: #1e293b; --text: #f8fafc; --muted: #94a3b8; --primary: #818cf8; --border: #334155; }
            body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 15px; transition: 0.3s; }
            .header { display: flex; justify-content: space-between; align-items: center; max-width: 1000px; margin: auto; }
            .logo-img { width: 40px; height: 40px; border-radius: 50%; object-fit: cover; border: 2px solid var(--primary); }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; max-width: 1000px; margin: 30px auto; }
            .card { background: var(--card); border-radius: 20px; border: 1px solid var(--border); overflow: hidden; display: flex; flex-direction: column; }
            .p-content { padding: 20px; flex-grow: 1; }
            .p-content img { width: 100%; height: 200px; object-fit: contain; border-radius: 15px; }
            
            /* قسم التعليقات */
            .comments-section { background: var(--bg); padding: 15px; border-top: 1px solid var(--border); font-size: 14px; }
            .comment-item { background: var(--card); padding: 8px 12px; border-radius: 10px; margin-bottom: 8px; border: 1px solid var(--border); }
            .comment-author { font-weight: bold; color: var(--primary); font-size: 12px; }
            .comment-form { display: flex; gap: 5px; margin-top: 10px; }
            .comment-form input { flex-grow: 1; padding: 5px; border-radius: 5px; border: 1px solid var(--border); font-size: 13px; }
            .comment-btn { background: var(--primary); color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer; }
            
            .btn-buy { background: #25d366; color: white; text-decoration: none; display: block; text-align: center; padding: 10px; border-radius: 10px; font-weight: bold; margin-top: 10px; }
            .delete-area { padding: 10px; border-top: 1px solid var(--border); display: flex; gap: 5px; }
            .add-btn { background: var(--primary); color: white; border: none; padding: 8px 16px; border-radius: 10px; cursor: pointer; font-weight: bold; }
            .modal { display: none; position: fixed; z-index: 100; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.6); align-items: center; justify-content: center; }
            .modal-content { background: var(--card); padding: 25px; border-radius: 20px; width: 90%; max-width: 400px; }
            input, textarea { width: 100%; padding: 10px; margin: 5px 0; border-radius: 8px; border: 1px solid var(--border); background: var(--bg); color: var(--text); box-sizing: border-box; }
        </style>
    </head>
    <body>
        <div class="header">
            <div style="display:flex; align-items:center; gap:10px;">
                {% if logo_url %}<img src="{{ logo_url }}" class="logo-img">{% endif %}
                <h2 style="margin:0;">متجر عيـن</h2>
            </div>
            <button class="add-btn" onclick="document.getElementById('addModal').style.display='flex'">+ أضف إعلان</button>
        </div>

        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}{% for c, m in messages %}<div style="text-align:center; padding:10px; color:{{ 'green' if c=='success' else 'red' }};">{{ m }}</div>{% endfor %}{% endif %}
        {% endwith %}

        <div class="grid">
            {% for p in products %}
            <div class="card">
                <div class="p-content">
                    <img src="{{ p['image_url'] or 'https://via.placeholder.com/150' }}">
                    <h3 style="margin:10px 0 5px 0;">{{ p['name'] }}</h3>
                    <div style="font-weight:bold; color:var(--primary); font-size:1.2rem;">{{ p['price'] }} ريال</div>
                    <p style="color:var(--muted); font-size:0.9rem;">{{ p['description'] }}</p>
                    <a href="https://wa.me/{{ p['whatsapp'] }}" class="btn-buy" target="_blank">تواصل عبر الواتساب</a>
                </div>

                <div class="comments-section">
                    <div id="comments-list-{{ p['id'] }}">
                        {% for c in all_comments if c['product_id'] == p['id'] %}
                        <div class="comment-item">
                            <div class="comment-author">{{ c['author'] }}</div>
                            <div>{{ c['content'] }}</div>
                        </div>
                        {% endfor %}
                    </div>
                    <form action="/add_comment" method="post" class="comment-form">
                        <input type="hidden" name="product_id" value="{{ p['id'] }}">
                        <input type="text" name="author" placeholder="اسمك" required style="width: 30%;">
                        <input type="text" name="content" placeholder="اكتب تعليقك أو استفسارك..." required>
                        <button type="submit" class="comment-btn">ارسل</button>
                    </form>
                </div>

                <div class="delete-area">
                    <form method="post" style="display:flex; gap:5px; width:100%;">
                        <input type="hidden" name="id" value="{{ p['id'] }}">
                        <input type="hidden" name="action" value="delete">
                        <input type="password" name="user_code" placeholder="كود الحذف" required style="font-size:11px; padding:3px;">
                        <button type="submit" style="background:#ef4444; color:white; border:none; padding:3px 8px; border-radius:5px; cursor:pointer; font-size:11px;">حذف المنتج</button>
                    </form>
                </div>
            </div>
            {% endfor %}
        </div>

        <div id="addModal" class="modal">
            <div class="modal-content">
                <h3>نشر إعلان جديد</h3>
                <form action="/add_public" method="post" enctype="multipart/form-data">
                    <input type="text" name="name" placeholder="اسم السلعة" required>
                    <input type="number" name="price" placeholder="السعر" required>
                    <textarea name="description" placeholder="وصف السلعة..."></textarea>
                    <input type="text" name="whatsapp" placeholder="رقم واتسابك (966...)" required>
                    <input type="password" name="delete_code" placeholder="كود سري لحذف إعلانك" required>
                    <input type="file" name="image_file" required>
                    <button type="submit" class="add-btn" style="width:100%; margin-top:10px;">نشر الآن</button>
                    <button type="button" onclick="document.getElementById('addModal').style.display='none'" style="background:none; border:none; color:var(--muted); width:100%; margin-top:10px; cursor:pointer;">إلغاء</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html, products=products, all_comments=all_comments, logo_url=logo_url)

@app.route('/add_comment', methods=['POST'])
def add_comment():
    p_id = request.form.get('product_id')
    author = request.form.get('author')
    content = request.form.get('content')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO comments (product_id, author, content) VALUES (%s, %s, %s)", (p_id, author, content))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

@app.route('/add_public', methods=['POST'])
def add_public():
    name, price, whatsapp, code, desc = request.form.get('name'), request.form.get('price'), request.form.get('whatsapp'), request.form.get('delete_code'), request.form.get('description')
    img_data = ""
    if 'image_file' in request.files:
        f = request.files['image_file']
        if f.filename != '':
            encoded = base64.b64encode(f.read()).decode('utf-8')
            img_data = f"data:{f.content_type};base64,{encoded}"
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO products (name, price, image_url, whatsapp, delete_code, description) VALUES (%s, %s, %s, %s, %s, %s)", (name, price, img_data, whatsapp, code, desc))
    conn.commit()
    cur.close()
    conn.close()
    flash('✅ تم النشر بنجاح!', 'success')
    return redirect(url_for('index'))

@app.route('/eyin-control', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == '317400':
            session['logged_in'] = True
        elif 'logged_in' in session:
            conn = get_db_connection()
            cur = conn.cursor()
            act = request.form.get('action')
            if act == 'admin_delete':
                cur.execute("DELETE FROM products WHERE id = %s", (request.form.get('id'),))
            elif act == 'delete_comment':
                cur.execute("DELETE FROM comments WHERE id = %s", (request.form.get('id'),))
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('admin'))
    
    if not session.get('logged_in'):
        return '<div dir="rtl" style="text-align:center;padding:100px;"><form method="post">🔐 <input type="password" name="password"><button type="submit">دخول</button></form></div>'

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products ORDER BY id DESC")
    prods = cur.fetchall()
    cur.execute("SELECT comments.*, products.name as p_name FROM comments JOIN products ON comments.product_id = products.id ORDER BY created_at DESC")
    comms = cur.fetchall()
    cur.close()
    conn.close()

    return render_template_string('''
    <div dir="rtl" style="font-family:sans-serif; padding:20px; max-width:800px; margin:auto;">
        <h2>🛠️ إدارة متجر عين</h2>
        <h3>💬 أحدث التعليقات (للرقابة)</h3>
        {% for c in comms %}
        <div style="border:1px solid #ddd; padding:10px; margin-bottom:5px;">
            <strong>{{ c['author'] }}:</strong> {{ c['content'] }} <small>(على: {{ c['p_name'] }})</small>
            <form method="post" style="display:inline;"><input type="hidden" name="action" value="delete_comment"><input type="hidden" name="id" value="{{ c['id'] }}"><button type="submit" style="color:red; background:none; border:none; cursor:pointer;">[حذف التعليق]</button></form>
        </div>
        {% endfor %}
        <hr>
        <h3>📦 المنتجات</h3>
        {% for p in prods %}
        <div style="margin-bottom:5px;">{{ p['name'] }} - <form method="post" style="display:inline;"><input type="hidden" name="action" value="admin_delete"><input type="hidden" name="id" value="{{ p['id'] }}"><button type="submit" style="color:red;">حذف المنتج</button></form></div>
        {% endfor %}
        <br><a href="/">العودة للمتجر</a>
    </div>
    ''', comms=comms, prods=prods)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
