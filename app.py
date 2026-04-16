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
        <title>تقييم احترافي</title>
        <style>
            body { 
                font-family: sans-serif; 
                background-color: #f0f2f5; 
                margin: 0; 
                padding: 5px; 
            }
            .main-container {
                display: flex;
                flex-direction: row;
                justify-content: space-between;
                gap: 8px;
                width: 100%;
                max-width: 600px;
                margin: 0 auto;
            }
            .column { 
                background: #ffffff; 
                padding: 10px 2px; 
                border-radius: 15px; 
                width: 49%; 
                box-sizing: border-box;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            }
            h2 {
                text-align: center;
                font-size: 14px;
                background: #222;
                color: white;
                padding: 10px;
                border-radius: 10px;
                margin: 0 5px 15px 5px;
            }
            .row { 
                display: flex; 
                align-items: center; 
                justify-content: space-around; 
                margin-bottom: 8px; 
                padding: 5px 0;
            }
            .btn-eval { 
                cursor: pointer; 
                font-size: 20px; 
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 10px;
                background: rgba(0, 0, 0, 0.03); /* خلفية خفيفة جداً */
                opacity: 0.3; 
                transition: all 0.1s ease;
                filter: grayscale(1);
                user-select: none;
            }
            
            /* شكل الزر وهو "مضغوط" */
            .btn-eval.active { 
                opacity: 1; 
                filter: grayscale(1) brightness(0); /* تحويل الإيموجي للون الأسود */
                background: #e0e0e0;
                box-shadow: inset 4px 4px 8px #bebebe, 
                            inset -4px -4px 8px #ffffff; /* تأثير الضغط للداخل */
                transform: scale(0.95); /* تصغير بسيط يوحي بالضغط */
            }
            
            .index-num {
                font-size: 10px;
                color: #ccc;
                width: 15px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="main-container">
            <div class="column">
                <h2 contenteditable="true">الطرف الأول</h2>
                ''' + ''.join([f'<div class="row"><span class="index-num">{i+1}</span><div class="btn-eval" onclick="toggle(this)">👍🏻</div><div class="btn-eval" onclick="toggle(this)">👎🏻</div></div>' for i in range(30)]) + '''
            </div>
            <div class="column">
                <h2 contenteditable="true">الطرف الثاني</h2>
                ''' + ''.join([f'<div class="row"><span class="index-num">{i+1}</span><div class="btn-eval" onclick="toggle(this)">👍🏻</div><div class="btn-eval" onclick="toggle(this)">👎🏻</div></div>' for i in range(30)]) + '''
            </div>
        </div>

        <script>
            function toggle(el) {
                el.classList.toggle('active');
            }
        </script>
    </body>
    </html>
    '''
    return html_content

if __name__ == '__main__':
    app.run()
