from flask import Flask
import threading
import time
import requests

app = Flask(__name__)

# نغز ذاتي كل 180 ثانية
def keep_alive():
    url = "https://eyin.onrender.com"
    while True:
        try:
            requests.get(url, timeout=10)
        except:
            pass
        time.sleep(180)

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
                font-family: sans-serif;
            }}

            /* الإطار السداسي الكبير الموزون */
            .outer-frame {{
                position: relative;
                padding: 80px 100px;
                background-color: white;
                /* شكل سداسي منتظم للإطار */
                clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%);
                display: flex;
                justify-content: center;
                align-items: center;
                margin-top: -40px;
            }}

            .outer-frame::before {{
                content: "";
                position: absolute;
                inset: 12px;
                background-color: #8A2BE2;
                clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%);
                z-index: 0;
            }}

            .main-container {{
                position: relative;
                z-index: 1;
                display: flex;
                flex-direction: column;
                align-items: center;
                /* موازنة الإزاحة الأفقية */
                margin-right: -42px; 
            }}

            .hex-row {{
                display: flex;
                justify-content: center;
                /* تداخل رأسي دقيق لركوب الزوايا */
                margin-top: -22px; 
            }}

            .hex-row:nth-child(even) {{
                /* إزاحة نصف عرض الخلية بالضبط */
                transform: translateX(-43px); 
            }}

            /* الخلية السداسية الصغير */
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
                /* ميل خفيف لليمين حبة واحدة */
                transform: skewX(-2deg);
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
                /* عكس الميل للحرف ليظهر مستقيماً */
                transform: skewX(2deg);
                display: block;
            }}
        </style>
    </head>
    <body>
        <div class="outer-frame">
            <div class="main-container">
                {grid_html}
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    threading.Thread(target=keep_alive, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)
