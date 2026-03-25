from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    # ترتيب الحروف المربع اللي طلبته أول (555553)
    letters = [
        "أ", "ب", "ت", "ث", "ج",
        "ح", "خ", "د", "ذ", "ر",
        "ز", "س", "ش", "ص", "ض",
        "ط", "ظ", "ع", "غ", "ف",
        "ق", "ك", "ل", "م", "ن",
        "هـ", "و", "ي"
    ]
    
    # التوزيع على الصفوف
    rows_distribution = [5, 5, 5, 5, 5, 3]
    
    letters_iter = iter(letters)
    grid_html = ""
    
    for count in rows_distribution:
        # نضيف كلاس hex-row لعنصر div الخاص بالصف
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
                background-color: #4B0082; /* خلفية بنفسجي غامق */
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
                /* إضافة حشوة للمحتوى لضمان عدم ملامسة الحواف */
                padding: 20px;
            }}
            .hex-row {{
                display: flex;
                justify-content: center;
                /* تقليل الهامش العلوي ليحدث تداخل رأسي */
                margin-top: -24px; 
            }}
            
            /* سر التداخل: إزاحة الصفوف الزوجية (2, 4, 6) يساراً */
            .hex-row:nth-child(even) {{
                transform: translateX(-40px); /* نصف عرض الخلية السداسية */
            }}
            
            /* تنسيق السداسي الأساسي */
            .hex {{
                width: 80px;
                height: 92px;
                background-color: white; /* لون الإطار البيضاء */
                margin: 2px;
                /* قص الشكل ليصبح سداسياً */
                clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
                display: flex;
                justify-content: center;
                align-items: center;
                position: relative;
            }}
            
            /* اللون البنفسجي الداخلي */
            .hex::before {{
                content: "";
                position: absolute;
                width: 90%; /* حجم اللون الداخلي مقارنة بالإطار الأبيض */
                height: 90%;
                background-color: #8A2BE2; /* اللون البنفسجي للخلية */
                clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
                z-index: 1;
            }}
            
            /* تنسيق الحرف */
            .hex span {{
                position: relative;
                z-index: 2;
                color: white;
                font-size: 30px;
                font-weight: bold;
                font-family: Arial, sans-serif;
            }}
            
            /* تنسيق خاص للصف الأخير ليظهر بشكل جميل */
            .hex-row:last-child {{
                margin-left: 20px; /* موازنة إزاحة الصفوف الزوجية */
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
