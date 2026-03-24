from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    # قائمة الحروف العربية
    arabic_letters = [
        "أ", "ب", "ت", "ث", "ج", "ح", "خ", "د", "ذ", "ر", "ز", "س", "ش", "ص",
        "ض", "ط", "ظ", "ع", "غ", "ف", "ق", "ك", "ل", "م", "ن", "هـ", "و", "ي"
    ]
    
    # بناء مربعات الحروف برمجياً
    letters_html = "".join([f'<div class="cell">{char}</div>' for char in arabic_letters])

    html_content = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>شبكة الحروف العربية</title>
        <style>
            body {{
                background-color: #4B0082; /* خلفية الصفحة بنفسجي غامق */
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                font-family: 'Arial', sans-serif;
            }}
            .grid-container {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(80px, 1fr)); /* ترتيب تلقائي للمربعات */
                gap: 10px;
                width: 90%;
                max-width: 800px;
                padding: 20px;
            }}
            .cell {{
                background-color: #8A2BE2; /* لون المربع بنفسجي */
                color: white;
                aspect-ratio: 1 / 1; /* جعل المربع متساوي الأضلاع */
                display: flex;
                justify-content: center;
                align-items: center;
                font-size: 30px;
                font-weight: bold;
                border: 4px solid white; /* الأطراف البيضاء التي طلبتها */
                border-radius: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="grid-container">
            {letters_html}
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
