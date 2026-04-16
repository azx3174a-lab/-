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
        <title>تقييم لايكات</title>
        <style>
            body { 
                font-family: sans-serif; 
                background-color: #f8f9fa; 
                margin: 0; 
                padding: 5px; 
                overflow-x: hidden;
            }
            .main-container {
                display: flex;
                flex-direction: row;
                justify-content: space-between;
                gap: 5px;
                width: 100%;
            }
            .column { 
                background: rgba(255, 255, 255, 0.8); 
                padding: 10px 2px; 
                border-radius: 12px; 
                width: 49%; 
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                box-sizing: border-box;
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            h2 {
                text-align: center;
                font-size: 13px;
                background: #343a40;
                color: white;
                padding: 8px;
                border-radius: 8px;
                margin: 0 5px 10px 5px;
                contenteditable: true;
            }
            .row { 
                display: flex; 
                align-items: center; 
                justify-content: space-around; 
                margin-bottom: 6px; 
                padding: 4px 0;
                border-bottom: 1px solid rgba(0,0,0,0.03); 
            }
            .btn-eval { 
                cursor: pointer; 
                font-size: 18px; 
                opacity: 0.2; /* شفافة جداً في البداية */
                transition: all 0.2s ease;
                filter: grayscale(1); /* بدون ألوان في البداية */
                user-select: none;
            }
            .btn-eval.active { 
                opacity: 1; /* تصبح واضحة عند الضغط */
                filter: grayscale(0); /* ترجع ألوان الإيموجي الأصلية */
                transform: scale(1.2);
            }
            .index-num {
                font-size: 9px;
                color: #bbb;
                width: 12px;
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
                // تفعيل أو إلغاء تفعيل الزر عند الضغط
                el.classList.toggle('active');
                
                // اختيارياً: لو تبي يختار واحد فقط (إما لايك أو ديسلايك) في السطر الواحد، فعل الكود اللي تحت:
                /*
                let siblings = el.parentElement.querySelectorAll('.btn-eval');
                siblings.forEach(s => { if(s !== el) s.classList.remove('active'); });
                */
            }
        </script>
    </body>
    </html>
    '''
    return html_content

if __name__ == '__main__':
    app.run()
