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
        <title>مقارنة الجوال</title>
        <style>
            body { 
                font-family: sans-serif; 
                background-color: #f0f2f5; 
                margin: 0; 
                padding: 5px; 
                overflow-x: hidden;
            }
            .main-container {
                display: flex;
                flex-direction: row; /* إجبار الجنب لجنب */
                justify-content: space-between;
                gap: 5px;
                width: 100%;
            }
            .column { 
                background: white; 
                padding: 10px 5px; 
                border-radius: 8px; 
                width: 49%; /* عشان يضمن الثبات جنب بعض */
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                box-sizing: border-box;
            }
            h2 {
                text-align: center;
                font-size: 14px; /* تصغير الخط للجوال */
                background: #007bff;
                color: white;
                padding: 5px;
                border-radius: 5px;
                margin-top: 0;
            }
            .row { 
                display: flex; 
                align-items: center; 
                justify-content: space-between; 
                margin-bottom: 4px; 
                padding: 2px;
                border-bottom: 1px solid #f9f9f9; 
            }
            .stars { 
                cursor: pointer; 
                color: #ddd; 
                font-size: 16px; /* تصغير النجوم لتناسب عرض الجوال */
                direction: ltr; 
                display: flex;
            }
            .star.active { color: #ffc107; }
            .index-num {
                font-size: 10px;
                color: #999;
                min-width: 15px;
            }
        </style>
    </head>
    <body>
        <div class="main-container">
            <div class="column">
                <h2 contenteditable="true">الأول</h2>
                ''' + ''.join([f'<div class="row"><span class="index-num">{i+1}</span><div class="stars" onclick="mark(event)">{"<span class=\'star\'>★</span>"*5}</div></div>' for i in range(30)]) + '''
            </div>

            <div class="column">
                <h2 contenteditable="true">الثاني</h2>
                ''' + ''.join([f'<div class="row"><span class="index-num">{i+1}</span><div class="stars" onclick="mark(event)">{"<span class=\'star\'>★</span>"*5}</div></div>' for i in range(30)]) + '''
            </div>
        </div>

        <script>
            function mark(e) {
                if(e.target.classList.contains('star')) {
                    let s = e.target;
                    let parent = s.parentElement;
                    let all = Array.from(parent.children);
                    let index = all.indexOf(s);
                    
                    all.forEach((star, i) => {
                        if(i <= index) star.classList.add('active');
                        else star.classList.remove('active');
                    });
                }
            }
        </script>
    </body>
    </html>
    '''
    return html_content

if __name__ == '__main__':
    app.run()
