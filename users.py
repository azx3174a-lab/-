from flask import Blueprint, render_template_string, request, session, redirect, url_for
from models import db, Subscription

users_bp = Blueprint('users', __name__)

@users_bp.route('/')
def index():
    if 'user_id' not in session: return redirect(url_for('login'))
    subs = Subscription.query.filter_by(user_id=session['user_id']).all()
    return render_template_string('''
        <div style="direction:rtl; padding:20px; font-family:sans-serif;">
            <h3>اشتراكاتي 💳</h3>
            <ul>
                {% for sub in subs %}
                <li>{{ sub.service_name }} - {{ sub.price }} ريال (ينتهي: {{ sub.expiry_date }})</li>
                {% endfor %}
            </ul>
            <form action="/add_sub" method="POST">
                <input name="name" placeholder="الخدمة" required>
                <input name="price" type="number" placeholder="السعر" required>
                <input name="date" type="date" required>
                <button type="submit">إضافة</button>
            </form>
            <br><a href="/logout">خروج</a>
        </div>
    ''', subs=subs)

@users_bp.route('/add_sub', methods=['POST'])
def add_sub():
    new_sub = Subscription(user_id=session['user_id'], service_name=request.form['name'],
                           price=request.form['price'], expiry_date=request.form['date'])
    db.session.add(new_sub)
    db.session.commit()
    return redirect(url_for('users.index'))
