from flask import Blueprint, render_template_string, request, session, redirect, url_for
from models import db, User, Settings

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin', methods=['GET', 'POST'])
def dashboard():
    if not session.get('is_admin'): return "غير مسموح لك", 403
    
    settings = Settings.query.first()
    if request.method == 'POST':
        settings.app_icon_url = request.form['icon_url']
        db.session.commit()
        return "تم تحديث الأيقونة بنجاح! <a href='/admin'>عودة</a>"
    
    users_count = User.query.count()
    return render_template_string('''
        <div style="direction:rtl; text-align:center; padding:20px; font-family:sans-serif;">
            <h2>لوحة تحكم المسؤول 🛠️</h2>
            <p>عدد المستخدمين: {{ count }}</p>
            <form method="POST">
                <input name="icon_url" value="{{ icon }}" style="width:80%; padding:10px;">
                <button type="submit" style="padding:10px 20px;">تحديث الأيقونة</button>
            </form>
            <br><a href="/">العودة للرئيسية</a>
        </div>
    ''', count=users_count, icon=settings.app_icon_url)
