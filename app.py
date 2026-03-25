from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    # ترتيب الحروف لتناسب شكل السداسي الكبير (3, 4, 5, 6, 5, 4, 1) = 28 حرفاً
    # هذا الترتيب يوزع الحروف العربية الـ 28 على شكل سداسي متناسق
    letters = [
        "أ", "ب", "ت", 
        "ث", "ج", "ح", "خ", 
        "د", "ذ", "ر", "ز", "س", 
        "ش", "ص", "ض", "ط", "ظ", "ع",
        "غ", "ف", "ق", "ك", "ل",
        "م", "ن", "هـ", "و",
        "ي"
    ]
    
    # توزيع الحروف على الصفوف لعمل الشكل السداسي الكبير
    rows = [3, 4, 5, 6, 5, 4, 1] 
    letters_iter = iter(letters)
    grid_html = ""
    
    for count in rows:
        grid_html += '<div class="hex-row">'
        for _ in range(count):
            try:
                char = next(letters_iter)
                grid_html += f'<div class="hex"><span>{char}</span></div>'
            except StopIteration:
                break
        grid_html += '</div>'

    html_content = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                background-color: #4B0082;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
            }}
            .main-container {{
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            .hex-row {{
                display: flex;
                justify-content: center;
                margin-top: -26px; /* لتداخل الصفوف رأسياً */
            }}
            .hex {{
                width: 100px;
                height: 110px;
                background-color: #8A2BE2;
                margin: 2px;
                clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
                display: flex;
                justify-content: center;
                align-items: center;
                position: relative;
            }}
            /* رسم الإطار الأبيض النحيف */
            .hex::before {{
                content: "";
                position: absolute;
                width: 92%;
                height: 92%;
                background-color: #8A2BE2;
                clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
                z-index: 1;
            }}
            /* تلوين الأطراف باللون الأبيض */
            .hex {{
                background-color: white; 
            }}
            .hex span {{
                position: relative;
                z-index: 2;
                color: white;
                font-size: 35px;
                font-weight: bold;
                font-family: Arial;
            }}
        </style>
    </head>
    <body>
        <div class="main-container">
            {grid_html}
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
