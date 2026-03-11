from flask import Flask, render_template_string
import os
import psycopg2

app = Flask(__name__)

def get_db_connection():
    # هذا السطر يقرأ الرابط اللي حطيناه في Render
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    return conn

@app.route('/')
def index():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # هنا سيحاول الكود جلب المنتجات من القاعدة
        # (سننشئ جدول المنتجات في الخطوة القادمة)
        cur.close()
        conn.close()
        status = "✅ متصل بقاعدة البيانات بنجاح!"
    except Exception as e:
        status = f"❌ خطأ في الاتصال: {e}"

    # تصميم بسيط جداً للمتجر
    html = f'''
    <body style="font-family: Arial; text-align: center; direction: rtl; padding: 50px;">
        <h1 style="color: #6366f1;">🛒 متجر عين</h1>
        <p style="font-size: 1.2em;">{status}</p>
        <hr>
        <div style="display: flex; justify-content: center; gap: 20px;">
            <div style="border: 1px solid #ddd; padding: 20px; border-radius: 10px;">
                <h3>منتج تجريبي 1</h3>
                <p>السعر: 100 ريال</p>
                <button style="background: #6366f1; color: white; border: none; padding: 10px 20px; border-radius: 5px;">أضف للسلة</button>
            </div>
        </div>
    </body>
    '''
    return render_template_string(html)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
