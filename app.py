from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    # الحروف العربية بنفس الترتيب والتوزيع 5، 5، 5، 5، 5، 3
    letters = [
        "أ", "ب", "ت", "ث", "ج",
        "ح", "خ", "د", "ذ", "ر",
        "ز", "س", "ش", "ص", "ض",
        "ط", "ظ", "ع", "غ", "ف",
        "ق", "ك", "ل", "م", "ن",
        "هـ", "و", "ي"
    ]
    
    rows_distribution = [5, 5, 5, 5, 5, 3]
    letters_iter = iter(letters)
    grid_html = ""
    
    for count in rows_distribution:
        grid_html += '<div class="hex-row">'
        for _ in range(count):
            try:
                char = next(letters_iter)
                # إضافة كلاس skew لإمالة الخلايا
                grid_html += f'<div class="hex skew"><span>{char}</span></div>'
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
            
            /* الإطار السداسي الكبير - تم إضافة margin-top سالبة لرفعه للأعلى */
            .outer-hex-frame {{
                position: relative;
                width: 680px; 
                height: 680px; 
                background-color: white; 
                clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
                display: flex;
                justify-content: center;
                align-items: center;
                /* رفعه للأعلى "حبتين" */
                margin-top: -50px; 
            }}
            
            .outer-hex-frame::before {{
                content: "";
                position: absolute;
                inset: 12px; 
                background-color: #8A2BE2;
                clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
                z-index: 0;
            }}
            
            .main-container {{
                position: relative;
                z-index: 1;
                display: flex;
                flex-direction: column;
                align-items: center;
                padding-left: 45px; 
                margin-top: 15px;
            }}
            
            .hex-row {{
                display: flex;
                justify-content: center;
                margin-top: -24px; 
            }}
            
            .hex-row:nth-child(even) {{
                transform: translateX(-43px); 
            }}
            
            .hex {{
                width: 80px;
                height: 92px;
                background-color: white;
                margin: 3px;
                clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
                display: flex;
                justify-content: center;
                align-items: center;
                position: relative;
                /* إضافة انتقال سلس للإمالة */
                transition: transform 0.3s ease; 
            }}
            
            /* كلاس جديد لإمالة الخلايا لليمين درجة واحدة */
            .hex.skew {{
                transform: skewX(-1deg); /* إمالة سالبة لليمين */
            }}
            
            /* الحفاظ على استقامة الحرف داخل الخلية المائلة */
            .hex.skew span {{
                transform: skewX(1deg); /* إمالة معاكسة للحرف */
            }}
            
            .hex::before {{
                content: "";
                position: absolute;
                width: 90%;
                height: 90%;
                background-color: #8A2BE2;
                clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
                z-index: 1;
            }}
            
            .hex span {{
                position: relative;
                z-index: 2;
                color: white;
                font-size: 30px;
                font-weight: bold;
                font-family: Arial, sans-serif;
                display: block; /* لضمان عمل التحويل */
            }}
        </style>
    </head>
    <body>
        <div class="outer-hex-frame">
            <div class="main-container">
                {grid_html}
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
