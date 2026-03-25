from flask import Flask
import threading
import time
import requests

app = Flask(__name__)

# وظيفة "النغز" لإبقاء الموقع مستيقظاً
def keep_alive():
    while True:
        try:
            # استبدل هذا الرابط برابط موقعك الفعلي على Render
            url = "https://eyin.onrender.com" 
            requests.get(url)
            print("Pinging the app to keep it awake...")
        except Exception as e:
            print(f"Ping failed: {e}")
        
        # انتظر 10 دقائق (600 ثانية) قبل النغزة التالية
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
                grid_html += f'<div class="hex skew"><span>{char}</span></div>'
            except StopIteration:
                break
        grid_html += '</div>'

    # (هنا يوضع كود الـ HTML والـ CSS اللي ضبطناه في المرة السابقة)
    # ملاحظة: تأكد من نسخ قسم html_content كاملاً من الرد السابق
    html_content = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <style>
            /* كود الـ CSS السابق هنا */
            body {{ background-color: #4B0082; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
            .outer-hex-frame {{ position: relative; width: 680px; height: 680px; background-color: white; clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%); display: flex; justify-content: center; align-items: center; margin-top: -80px; }}
            .outer-hex-frame::before {{ content: ""; position: absolute; inset: 12px; background-color: #8A2BE2; clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%); z-index: 0; }}
            .main-container {{ position: relative; z-index: 1; display: flex; flex-direction: column; align-items: center; padding-left: 45px; margin-top: 15px; }}
            .hex-row {{ display: flex; justify-content: center; margin-top: -24px; }}
            .hex-row:nth-child(even) {{ transform: translateX(-43px); }}
            .hex {{ width: 80px; height: 92px; background-color: white; margin: 3px; clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%); display: flex; justify-content: center; align-items: center; position: relative; }}
            .hex.skew {{ transform: skewX(-10deg); }}
            .hex.skew span {{ transform: skewX(10deg); display: block; }}
            .hex::before {{ content: ""; position: absolute; width: 90%; height: 90%; background-color: #8A2BE2; clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%); z-index: 1; }}
            .hex span {{ position: relative; z-index: 2; color: white; font-size: 30px; font-weight: bold; font-family: Arial, sans-serif; }}
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
    # تشغيل خيط (Thread) النغز الذاتي في الخلفية
    threading.Thread(target=keep_alive, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)
