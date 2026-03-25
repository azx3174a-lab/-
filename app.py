from flask import Flask, render_template_string
import threading
import time
import requests

app = Flask(__name__)

# نغز ذاتي (Keep-alive) عشان ما ينام المتجر
def keep_alive():
    url = "https://eyin.onrender.com"
    while True:
        try:
            requests.get(url, timeout=10)
        except:
            pass
        time.sleep(180)

# بيانات المنتجات (تقدر تعدلها براحتك)
products = [
    {"id": 1, "name": "منتج 1", "price": "100 SAR", "img": "https://via.placeholder.com/150"},
    {"id": 2, "name": "منتج 2", "price": "200 SAR", "img": "https://via.placeholder.com/150"},
    {"id": 3, "name": "منتج 3", "price": "150 SAR", "img": "https://via.placeholder.com/150"},
]

@app.route('/')
def index():
    html_template = """
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>متجري الإلكتروني</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f9; margin: 0; padding: 20px; }
            header { text-align: center; padding: 20px; background: #8A2BE2; color: white; border-radius: 10px; margin-bottom: 30px; }
            .container { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; max-width: 1200px; margin: auto; }
            .product-card { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; transition: 0.3s; }
            .product-card:hover { transform: translateY(-5px); }
            .product-card img { max-width: 100%; border-radius: 8px; }
            .product-card h3 { color: #333; }
            .product-card p { color: #8A2BE2; font-weight: bold; font-size: 1.2em; }
            .buy-btn { background: #8A2BE2; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; text-decoration: none; }
            .buy-btn:hover { background: #4B0082; }
        </style>
    </head>
    <body>
        <header>
            <h1>مرحباً بك في متجرنا</h1>
            <p>أفضل المنتجات بأفضل الأسعار</p>
        </header>
        <div class="container">
            {% for product in products %}
            <div class="product-card">
                <img src="{{ product.img }}" alt="{{ product.name }}">
                <h3>{{ product.name }}</h3>
                <p>{{ product.price }}</p>
                <button class="buy-btn">إضافة للسلة</button>
            </div>
            {% endfor %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, products=products)

if __name__ == "__main__":
    threading.Thread(target=keep_alive, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)
