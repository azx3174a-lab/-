from flask import Blueprint, request, redirect, session, render_template_string, base64
import psycopg2, os
from psycopg2.extras import DictCursor

# تعريف الـ Blueprint
admin_bp = Blueprint('admin_bp', __name__)

def get_db_connection():
    return psycopg2.connect(os.environ.get('DATABASE_URL'), sslmode='require')

@admin_bp.route('/eyin-control', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        # نظام قفل اللوحة
        if request.form.get('password') == '317400':
            session['admin'] = True
            return redirect('/eyin-control')
        
        elif session.get('admin'):
            conn = get_db_connection(); cur = conn.cursor()
            action = request.form.get('action')
            
            # 1. تحديث الشعار
            if action == 'update_logo':
                f = request.files['logo_file']
                if f:
                    img_data = f"data:{f.content_type};base64,{base64.b64encode(f.read()).decode('utf-8')}"
                    cur.execute("UPDATE settings SET value=%s WHERE key='logo'", (img_data,))
            
            # 2. تحديث اسم المتجر
            elif action == 'update_name':
                cur.execute("UPDATE settings SET value=%s WHERE key='store_name'", (request.form.get('store_name'),))
            
            # 3. حذف منتج
            elif action == 'delete':
                cur.execute("DELETE FROM products WHERE id=%s", (request.form.get('id'),))
            
            conn.commit(); cur.close(); conn.close()
            return redirect('/eyin-control')
            
    if not session.get('admin'):
        return '<div dir="rtl" style="text-align:center; padding-top:100px; font-family:sans-serif;">🔐 لوحة محصنة<br><br><form method="post"><input type="password" name="password" placeholder="كلمة المرور" style="padding:10px; border-radius:10px; border:1px solid #ddd;"><button type="submit" style="padding:10px 20px; background:#4f46e5; color:white; border:none; border-radius:10px; margin-right:5px; cursor:pointer;">دخول</button></form></div>'
    
    # جلب البيانات الحالية للوحة
    conn = get_db_connection(); cur = conn.cursor(cursor_factory=DictCursor)
    cur.execute("SELECT * FROM products ORDER BY id DESC"); prods = cur.fetchall()
    cur.execute("SELECT value FROM settings WHERE key='store_name'"); st_name = cur.fetchone()
    cur.close(); conn.close()
    
    return render_template_string('''
    <div dir="rtl" style="padding:20px; font-family:sans-serif; max-width:600px; margin:auto; background:#f8fafc; color:#1e293b; min-height:100vh; border-radius:20px; box-shadow:0 0 20px rgba(0,0,0,0.1);">
        <h2 style="color:#4f46e5;">🛠️ إدارة متجر عين</h2>
        <p style="font-size:12px; color:gray;">(هذه اللوحة تعمل من ملف منفصل admin.py)</p>
        
        <div style="background:white; padding:15px; border-radius:15px; margin-bottom:20px; border:1px solid #e2e8f0;">
            <h3>🖼️ الهوية البصرية (الشعار)</h3>
            <form method="post" enctype="multipart/form-data">
                <input type="hidden" name="action" value="update_logo">
                <input type="file" name="logo_file" required style="margin-bottom:10px;">
                <button type="submit" style="width:100%; padding:10px; background:#4f46e5; color:white; border:none; border-radius:10px; cursor:pointer;">تحديث الشعار</button>
            </form>
        </div>

        <div style="background:white; padding:15px; border-radius:15px; margin-bottom:20px; border:1px solid #e2e8f0;">
            <h3>📝 اسم المتجر</h3>
            <form method="post">
                <input type="hidden" name="action" value="update_name">
                <input type="text" name="store_name" value="{{name}}" required style="width:100%; padding:10px; margin-bottom:10px; border-radius:10px; border:1px solid #ddd;">
                <button type="submit" style="width:100%; padding:10px; background:#10b981; color:white; border:none; border-radius:10px; cursor:pointer;">حفظ الاسم الجديد</button>
            </form>
        </div>

        <hr style="border:0; border-top:1px solid #e2e8f0; margin:20px 0;">
        
        <h3>📦 التحكم بالمنتجات ({{prods|length}})</h3>
        {% for p in prods %}
        <div style="display:flex; justify-content:space-between; align-items:center; background:white; padding:10px; border-radius:10px; margin-bottom:10px; border:1px solid #e2e8f0;">
            <span>{{p['name']}}</span>
            <form method="post" onsubmit="return confirm('هل أنت متأكد من الحذف؟')">
                <input type="hidden" name="action" value="delete">
                <input type="hidden" name="id" value="{{p['id']}}">
                <button type="submit" style="color:#ef4444; background:none; border:1px solid #ef4444; padding:5px 10px; border-radius:8px; cursor:pointer;">حذف 🗑️</button>
            </form>
        </div>
        {% endfor %}
        <br>
        <a href="/" style="display:block; text-align:center; text-decoration:none; color:#4f46e5; font-weight:bold;">⬅️ العودة للمتجر الرئيسي</a>
    </div>
    ''', prods=prods, name=st_name['value'] if st_name else 'eyin')
