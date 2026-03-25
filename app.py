from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    # قائمة الحروف العربية مرتبة
    arabic_letters = [
        "أ", "ب", "ت", "ث", "ج", "ح", "خ", "د", "ذ", "ر", "ز", "س", "ش", "ص",
        "ض", "ط", "ظ", "ع", "غ", "ف", "ق", "ك", "ل", "م", "ن", "هـ", "و", "ي"
    ]
    
    # بناء الخلايا السداسية برمجياً
    # كل حرف يوضع داخل div يحمل كلاس hex لإنشاء الشكل وكلاس hex-content لتموضع الحرف
    letters_html = "".join([
        f'<div class="hex"><div class="hex-content">{char}</div></div>' 
        for char in arabic_letters
    ])

    html_content = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>قرص عسل الحروف العربية</title>
        <style>
            body {{
                background-color: #4B0082; /* خلفية الصفحة بنفسجي غامق */
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                font-family: 'Arial', sans-serif;
                overflow: hidden; /* لمنع شريط التمرير إذا خرج التصميم قليلاً */
            }}

            /* الحاوية الرئيسية لشبكة قرص العسل */
            .honeycomb {{
                display: flex;
                flex-wrap: wrap;
                width: 90%;
                max-width: 1000px;
                transform: translateX(-2.5%); /* موازنة الشبكة في المنتصف */
                padding: 50px 0;
            }}

            /* تنسيق الشكل السداسي الأساسي */
            .hex {{
                position: relative;
                width: 100px; /* عرض الخلية */
                height: 57.74px; /* الارتفاع المحسوب للشكل السداسي (width * 0.5774) */
                background-color: #8A2BE2; /* لون الخلية بنفسجي */
                margin: 28.87px 2px; /* هوامش لضبط التداخل السداسي */
                border-left: solid 5px white; /* الحدود البيضاء */
                border-right: solid 5px white;
                box-sizing: border-box;
                display: flex;
                align-items: center;
                justify-content: center;
            }}

            /* المثلثات العلوية والسفلية لإنشاء الشكل السداسي */
            .hex:before,
            .hex:after {{
                content: "";
                position: absolute;
                z-index: 1;
                width: 70.71px; /* (100 / sqrt(2)) */
                height: 70.71px;
                transform: scaleY(0.5774) rotate(-45deg);
                background-color: inherit;
                left: 9.64px; /* (100 - 70.71) / 2 - 5(border)/sqrt(2) approx */
            }}

            .hex:before {{
                top: -35.36px;
                border-top: solid 7.07px white; /* حدود علوية بيضاء */
                border-right: solid 7.07px white;
            }}

            .hex:after {{
                bottom: -35.36px;
                border-bottom: solid 7.07px white; /* حدود سفلية بيضاء */
                border-left: solid 7.07px white;
            }}

            /* تنسيق محتوى الحرف داخل الخلية */
            .hex-content {{
                position: absolute;
                z-index: 2; /* لضمان ظهور الحرف فوق المثلثات */
                color: white;
                font-size: 40px;
                font-weight: bold;
                top: -20px; /* تعديل تموضع الحرف رأسياً ليظهر في المنتصف */
            }}

            /* تأثير تحريك الصفوف لإنشاء تداخل قرص العسل (Hexagonal Tiling) */
            /* نطبق الإزاحة على الخلايا بناءً على ترتيبها لإنشاء تداخل بين الصفوف */
            .honeycomb .hex:nth-child(n+1) {{
                 /* حسابات معقدة لضبط تموضع كل خلية لتتداخل مع جاراتها */
            }}
            
            /* تبسيط التداخل: نجعل الحاوية flex وعناصرها تترتب برفق، 
               التداخل الحقيقي يتطلب حسابات دقيقة لكل عنصر أو استخدام CSS Grid متقدم،
               لذا سنستخدم طريقة أبسط للحصول على مظهر مشابه جداً */
            
            .honeycomb {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
                gap: 5px; /* فجوة صغيرة بين الخلايا */
                justify-items: center;
            }}
            
            .hex {{
                margin: 30px 0; /* ضبط الهوامش لتقريب الخلايا رأسياً */
            }}

        </style>
    </head>
    <body>
        <div class="honeycomb">
            {letters_html}
        </div>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)