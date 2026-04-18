from flask import Blueprint, render_template_string, request, session, redirect, url_for
from models import db, Subscription

users_bp = Blueprint('users', __name__)

@users_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')
    
    # جلب اشتراكات المستخدم الحالي
    subs = Subscription.query.filter_by(user_id=session['user_id']).all()
    
    return render_template_string('''
        <div style="direction:rtl; padding:20px; font-family:sans-serif; text-align:center;">
            <h1>أهلاً بك في تطبيق الاشتراكات 👋</h1>
            <div style="background:#eee; padding:15px; border-radius:10px; margin-bottom:20px;">
                <h3>قائمة اشتراكاتك:</h3>
                {% if not subs %} <p>لا توجد اشتراكات حالياً.</p> {% endif %}
                <ul style="list-style:none; padding:0;">
                    {% for sub in subs %}
                    <li style="background:#fff; margin:5px; padding:10px; border-radius:5px;">
                        {{ sub.service_name }} - {{ sub.price }} ريال
                    </li>
                    {% endfor %}
                </ul>
            </div>
            <a href="/logout" style="color:red;">تسجيل خروج</a>
            {% if session.get('is_admin') %}
            <br><br>
            <a href="/admin/" style="background:gold; padding:10px; border-radius:5px; text-decoration:none; color:#000;">دخلت بصفتك مدير: اذهب للوحة التحكم</a>
            {% endif %}
        </div>
    ''', subs=subs)
