from flask import Blueprint, render_template_string, session, redirect

# تعريف القسم الخاص بالمسؤول
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
def dashboard():
    # التأكد أن الشخص اللي داخل هو الإدارة
    if not session.get('is_admin'):
        return "⚠️ الوصول ممنوع: هذه المنطقة للمسؤولين فقط.", 403
    
    return render_template_string('''
        <div style="direction:rtl; text-align:center; font-family:sans-serif; padding:50px; background:#f0f2f5; min-height:100vh;">
            <h1 style="color:#1c1e21;">لوحة تحكم المسؤول 🛠️</h1>
            <div style="background:white; padding:30px; border-radius:15px; display:inline-block; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <p style="font-size:18px;">مرحباً بك في المنطقة الخاصة</p>
                <hr>
                <p>هنا ستظهر إحصائيات المستخدمين والتحكم الكامل قريباً.</p>
                <br>
                <a href="/" style="color:#1877f2; text-decoration:none;">⬅️ العودة للموقع الرئيسي</a>
            </div>
        </div>
    ''')
