from flask import Flask
import threading
import time
import requests

app = Flask(__name__)

# وظيفة النغز الذاتي لضمان عدم نوم السيرفر
def keep_alive():
    url = "https://eyin.onrender.com"
    while True:
        try:
            # إرسال طلب للموقع كل 180 ثانية
            requests.get(url)
            print("Ping successful: Site is awake.")
        except Exception as e:
            print(f"Ping failed: {e}")
        
        # الانتظار لمدة 180 ثانية (3 دقائق)
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
            :root {{
                --hex-width: 80px;
                --hex-height: 92px;
                --hex-color: #8A2BE2;
            }}
            body {{
                background-color: #4B0082;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
            }}
            .outer-frame {{
                position: relative;
                padding: 60px 80px;
                background-color: white;
                clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
                display: flex;
                justify-content: center;
                align-items: center;
                margin-top: -100px;
            }}
            .outer-frame::before {{
                content: "";
                position: absolute;
                inset: 10px;
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
                width: var(--hex-width);
                height: var(--hex-height);
                background-color: white;
                margin: 3px;
                clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
                display: flex;
                justify-content: center;
                align-items: center;
                position: relative;
                transform: skewX(-5deg);
            }}
            .hex::before {{
                content: "";
                position: absolute;
                width: 90%;
                height: 90%;
                background-color: var(--hex-color);
                clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
                z-index: 1;
            }}
            .hex span {{
                position: relative;
                z-index: 2;
                color: white;
                font-size: 28px;
                font-weight: bold;
                transform: skewX(5deg);
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
    # بدء خيط النغز في الخلفية عند تشغيل التطبيق
    threading.Thread(target=keep_alive, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)
