from flask import Flask
import os
import psycopg2

app = Flask(__name__)

# الربط مع قاعدة البيانات اللي أضفتها في Render
db_url = os.environ.get('DATABASE_URL')

@app.route('/')
def home():
    try:
        conn = psycopg2.connect(db_url)
        return "<h1>مرحباً بك في متجر عين</h1><p>الموقع متصل بقاعدة البيانات بنجاح!</p>"
    except:
        return "<h1>مرحباً بك في متجر عين</h1><p>الموقع يعمل، لكن يحتاج ضبط اتصال القاعدة.</p>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
