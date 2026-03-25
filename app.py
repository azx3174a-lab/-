from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    # الحروف العربية بالترتيب والتوزيع الذي حددته
    letters = [
        "أ", "ب", 
        "ت", "ث", "ج", 
        "ح", "خ", "د", "ذ", 
        "ر", "ز", "س", "ش", "ص", 
        "ض", "ط", "ظ", "ع", "غ", "ف", 
        "ق", "ك", "ل", "م", "ن", 
        "هـ", "و", "ي"
    ]
    
    # التوزيع: صف 2، ثم 3، ثم 4، ثم 5، ثم 6، ثم 5، ثم 3 (المجموع 28)
    rows_distribution = [2, 3, 4, 5, 6, 5, 3]
    
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
        <title>خلية الحروف العربية</title>
        <style>
            body {{
                background-color: #4B0082; /* لون الخلفية العام بنفسجي غامق */
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                font-family: 'Arial', sans-serif;
            }}
            .main-container {{
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 20px;
            }}
            .hex-row {{
                display: flex;
                justify-content: center;
                margin-top: -22px; /* هذا السطر هو سر تداخل الخلايا بشكل سداسي */
            }}
            .hex {{
                width: 80px;
                height: 92px;
                background-color: white; /* لون الإطار (الأطراف البيضاء) */
                margin: 2px;
                clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
                display: flex;
                justify-content: center;
                align-items: center;
                position: relative;
            }}
            .hex::before {{
                content: "";
                position: absolute;
                width: 90%; /* حجم اللون الداخلي مقارنة بالإطار الأبيض */
                height: 90%;
                background-color: #8A2BE2; /* اللون البنفسجي الأساسي للخلية */
                clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
                z-index: 1;
            }}
            .hex span {{
                position: relative;
                z-index: 2;
                color: white;
                font-size: 28px;
                font-weight: bold;
            }}
            /* تحسين العرض على الجوال */
            @media (max-width: 500px) {{
                .hex {{ width: 50px; height: 58px; }}
                .hex span {{ font-size: 18px; }}
                .hex-row {{ margin-top: -14px; }}
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
