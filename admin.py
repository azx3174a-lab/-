from flask import Blueprint, render_template_string, request, session, redirect, url_for
from models import db, User, Settings

# تعريف القسم
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
def dashboard():
    # التحقق من الصلاحيات
    if not session.get('is_admin'):
        return "غير مسموح لك بالدخول", 403
    
    settings = Settings.query.first()
    users_count = User.query.count()
    
    return render_template_string('''
        <div style="direction:rtl; text-align:center; padding:20px; font-family:sans-serif; background:#f4f4f4; min-height:100vh;">
            <h2>لوحة تحكم المسؤول 🛠️</h2>
            <div style="background:#fff; padding:20px; border-radius:10px; display:inline-block; box-shadow:0 2px 10px rgba(0,0,0,0.1);">
                <p>إحصائيات سريعة:</p>
                <h3 style="color:blue;">عدد المستخدمين: {{ count }}</h3>
            </div>
            <br><br>
            <a href="/logout" style="color:red;">تسجيل خروج</a>
            <br><br>
            <a href="/" style="text-decoration:none; color:#555;">العودة للموقع الأساسي</a>
        </div>
    ''', count=users_count)
