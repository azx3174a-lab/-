from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    # هذه هي محتويات الصفحة الفاضية، يمكنك تعديل النص بين الأقواس لاحقاً
    return "<h1>مرحباً بك في صفحتك الجديدة</h1><p>هذه الصفحة جاهزة للتعديل في أي وقت.</p>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
