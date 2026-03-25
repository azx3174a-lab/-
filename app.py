from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    # الحروف العربية
    letters = [
        "أ", "ب", "ت", "ث", "ج", "ح", "خ", "د", "ذ", "ر", "ز", "س", "ش", "ص",
        "ض", "ط", "ظ", "ع", "غ", "ف", "ق", "ك", "ل", "م", "ن", "هـ", "و", "ي"
    ]
    
    # إنشاء الخلايا
    cells_html = "".join([f'<div class="hb-item"><span>{l}</span></div>' for l in letters])

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
            .hb-container {{
                display: flex;
                flex-wrap: wrap;
                width: 600px; /* يمكنك تكبير العرض لزيادة عدد الخلايا في الصف */
                padding-left: 50px;
            }}
            .hb-item {{
                position: relative;
                width: 100px; 
                height: 115px;
                background-color: #8A2BE2; /* لون الخلية */
                margin: 2px;
                clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
                display: flex;
                justify-content: center;
                align-items: center;
                transition: 0.3s;
                border: 4px solid white; /* حدود بيضاء (تظهر بسبب الـ clip-path كأطراف) */
            }}
            /* إضافة إطار أبيض داخلي للمحاكاة */
            .hb-item::after {{
                content: "";
                position: absolute;
                inset: 5px;
                background: inherit;
                clip-path: inherit;
                z-index: 1;
            }}
            .hb-item span {{
                position: relative;
                z-index: 2;
                color: white;
                font-size: 40px;
                font-weight: bold;
                font-family: Arial;
            }}
            /* سر التداخل: إزاحة الصفوف الزوجية */
            .hb-container {{
                display: grid;
                grid-template-columns: repeat(5, 105px); /* 5 خلايا في كل صف */
                grid-gap: 5px;
            }}
            .hb-item:nth-child(10n+6), 
            .hb-item:nth-child(10n+7), 
            .hb-item:nth-child(10n+8), 
            .hb-item:nth-child(10n+9), 
            .hb-item:nth-child(10n+10) {{
                transform: translateX(55px); /* إزاحة الصف الثاني */
                margin-top: -30px; /* رفع الصف للأعلى ليحدث التداخل */
            }}
            .hb-item:nth-child(n+6) {{
                margin-top: -30px; /* تداخل جميع الصفوف بعد الأول */
            }}
        </style>
    </head>
    <body>
        <div class="hb-container">
            {cells_html}
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
