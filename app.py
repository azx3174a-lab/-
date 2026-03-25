from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
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
            
            /* الإطار السداسي الكبير - ضبط الحجم ليتناسب مع المحتوى */
            .outer-hex-frame {{
                position: relative;
                width: 600px; /* زيادة العرض */
                height: 600px; /* زيادة الارتفاع */
                background-color: white; /* لون الإطار الأبيض */
                clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            
            .outer-hex-frame::before {{
                content: "";
                position: absolute;
                inset: 10px; /* سمك الإطار الأبيض */
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
                /* إزاحة خفيفة لليسار لتعويض الـ transform الخاص بالصفوف */
                padding-right: 40px; 
                margin-top: 20px;
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
                font-size: 28px;
                font-weight: bold;
                font-family: Arial;
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
