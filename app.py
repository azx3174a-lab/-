from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    # كود HTML يعرض خلية حروف بنفسجية بأطراف بيضاء في منتصف الصفحة
    html_content = """
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>خلية حروف بنفسجية</title>
        <style>
            body {
                background-color: #8A2BE2; /* لون الخلفية البنفسجي */
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                font-family: Arial, sans-serif;
            }
            .hex-cell {
                width: 150px;
                height: 173.2px; /* الارتفاع لإنشاء شكل سداسي متساوي الأضلاع */
                background-color: #9370DB; /* لون الخلية البنفسجي */
                position: relative;
                border: 10px solid white; /* الأطراف البيضاء */
                box-sizing: border-box; /* لضمان أن الأطراف لا تزيد حجم الخلية */
                clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
                display: flex;
                justify-content: center;
                align-items: center;
                font-size: 70px;
                color: white; /* لون الحرف */
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="hex-cell">P</div>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
