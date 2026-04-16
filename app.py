from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    html_content = '''
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>تقييم لايكات مطور</title>
        <style>
            body { 
                font-family: sans-serif; 
                background-color: #f4f6f9; 
                margin: 0; 
                padding: 5px; 
                user-select: none;
            }
            .main-container {
                display: flex;
                flex-direction: row;
                justify-content: space-between;
                gap: 5px;
                width: 100%;
                max-width: 600px;
                margin: 0 auto;
            }
            .column { 
                background: white; 
                padding: 10px 0; 
                border-radius: 12px; 
                width: 49%; 
                box-sizing: border-box;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            h2 {
                text-align: center;
                font-size: 13px;
                background: #1e1e1e;
                color: white;
                padding: 8px;
                border-radius: 8px;
                margin: 0 5px 12px 5px;
            }
            .row { 
                display: flex; 
                align-items: center; 
                justify-content: space-around; 
                margin-bottom: 6px; 
                padding: 2px 0;
            }
            
            /* المربع (الزر) في حالته العادية */
            .btn-wrapper {
                cursor: pointer; 
                width: 38px;
                height: 38px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 8px;
                background: rgba(0, 0, 0, 0.01); /* خلفية شبه معدومة */
                transition: all 0.1s ease;
            }
            
            /* الإيموجي في حالته العادية: شفاف */
            .btn-emoji {
                font-size: 20px;
                opacity: 0.15; /* شفافية عالية جداً */
                filter: grayscale(1) brightness(1); /* طبيعي */
                transition: all 0.1s ease;
            }

            /* --- حالة الضغط (عند التفعيل) --- */
            
            /* المربع (الزر) يضغط للداخل ويصبح رمادياً */
            .btn-wrapper.active { 
                background: #e6e6e6; /* رمادي فاتح للخلفية */
                box-shadow: inset 3px 3px 6px #cfcfcf, 
                            inset -3px -3px 6px #ffffff; /* تأثير الضغط لداخل المربع */
                transform: scale(0.96); /* تصغير بسيط يوحي بالضغط المادي */
            }
            
            /* الإيموجي يصبح أسود سادة وواضحاً */
            .btn-wrapper.active .btn-emoji { 
                opacity: 1; /* تصبح واضحة تماماً */
                filter: grayscale(1) brightness(0); /* يجبر الإيموجي على التحول للون الأسود السادة */
            }

            .index-num {
                font-size: 9px;
                color: #ddd;
                width: 12px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="main-container">
            <div class="column">
                <h2 contenteditable="true">الطرف الأول</h2>
                ''' + ''.join([f'<div class="row"><span class="index-num">{i+1}</span><div class="btn-wrapper" onclick="toggle(this)"><span class="btn-emoji">👍🏻</span></div><div class="btn-wrapper" onclick="toggle(this)"><span class="btn-emoji">👎🏻</span></div></div>' for i in range(30)]) + '''
            </div>

            <div class="column">
                <h2 contenteditable="true">الطرف الثاني</h2>
                ''' + ''.join([f'<div class="row"><span class="index-num">{i+1}</span><div class="btn-wrapper" onclick="toggle(this)"><span class="btn-emoji">👍🏻</span></div><div class="btn-wrapper" onclick="toggle(this)"><span class="btn-emoji">👎🏻</span></div></div>' for i in range(30)]) + '''
            </div>
        </div>

        <script>
            function toggle(el) {
                // تفعيل المربع
                el.classList.toggle('active');
            }
        </script>
    </body>
    </html>
    '''
    return html_content

if __name__ == '__main__':
    app.run()
