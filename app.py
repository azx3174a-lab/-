from flask import Flask
import threading
import time
import requests

app = Flask(__name__)

# --- 1. وظيفة النغز الذاتي (Self-Ping) ---
def keep_alive():
    # الرابط الخاص بك كما طلبته
    url = "https://eyin.onrender.com"
    while True:
        try:
            # نغز الموقع كل 180 ثانية (3 دقائق)
            requests.get(url, timeout=10)
            print("Ping successful: Site is active.")
        except Exception as e:
            print(f"Ping failed: {e}")
        
        time.sleep(180)

@app.route('/')
def home():
    # --- 2. ترتيب الحروف والتوزيع ---
    letters = [
        "أ", "ب", "ت", "ث", "ج",
        "ح", "خ", "د", "ذ", "ر",
        "ز", "س", "ش", "ص", "ض",
        "ط", "ظ", "ع", "غ", "ف",
        "ق", "ك", "ل", "م", "ن",
        "هـ", "و", "ي"
    ]
    
    # توزيع الصفوف: 5، 5، 5، 5، 5، 3
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

    # --- 3. التصميم (CSS) الموزون بدقة ---
    html_content = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>Eyin Hex Grid</title>
        <style>
            body {{
                background-color: #4B0082;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                overflow: hidden; /* يمنع ظهور أشرطة التمرير */
            }}
            
            /* الإطار الكبير: مطاطي يتبع حجم الحروف */
            .outer-frame {{
                position: relative;
                display: inline-flex;
                flex-direction: column;
                align-items: center;
                padding: 80px 100px; /* مساحة أمان لمنع خروج الحروف */
                background-color: white;
                clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
                margin-top: -60px; /* رفع الإطار للأعلى */
            }}
            
            /* الطبقة البنفسجية داخل الإطار الكبير */
            .outer-frame::before {{
                content: "";
                position: absolute;
                inset: 12px; /* سمك الإطار الأبيض الخارجي */
                background-color: #8A2BE2;
                clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
                z-index: 0;
            }}
            
            /* الحاوية الداخلية موزونة لتعويض الإزاحة */
            .main-container {{
                position: relative;
                z-index: 1;
                display: flex;
                flex-direction: column;
                align-items: center;
                padding-left: 43px; /* موازنة إزاحة الصفوف الزوجية بدقة */
            }}
            
            .hex-row {{
                display: flex;
                justify-content: center;
                margin-top: -24px; /* تداخل الخلايا رأسياً */
            }}
            
            /* إزاحة الصفوف الزوجية (الثاني، الرابع، السادس) */
            .hex-row:nth-child(even) {{
                transform: translateX(-43px);
            }}
            
            /* تنسيق السداسي الصغير */
            .hex {{
                width: 80px;
                height: 92px;
                background-color: white; /* إطار الخلية الصغير */
                margin: 3px;
                clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
                display: flex;
                justify-content: center;
                align-items: center;
                position: relative;
                transform: skewX(-5deg); /* الإمالة لليمين كما طلبت */
            }}
            
            .hex::before {{
                content: "";
                position: absolute;
                width: 90%;
                height: 90%;
                background-color: #8A2BE2; /* قلب الخلية البنفسجي */
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
                transform: skewX(5deg); /* تعديل ميل الحرف ليبقى مستقيماً */
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
    # تشغيل النغز الذاتي في الخلفية
    threading.Thread(target=keep_alive, daemon=True).start()
    # تشغيل السيرفر
    app.run(host='0.0.0.0', port=8080)
