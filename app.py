from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    # كود الصفحة مباشرة هنا عشان ما نضيع في المجلدات
    html_content = '''
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>منصة التقييم</title>
        <style>
            body { font-family: sans-serif; background-color: #f4f4f9; padding: 20px; }
            .container { display: flex; justify-content: space-around; gap: 20px; }
            .column { background: white; padding: 15px; border-radius: 10px; width: 45%; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 5px; border-bottom: 1px solid #eee; }
            .stars { cursor: pointer; color: #ccc; font-size: 20px; direction: ltr; }
            .star.active { color: #ffcc00; }
            @media (max-width: 600px) { .container { flex-direction: column; } .column { width: 100%; } }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="column">
                <h2 contenteditable="true">الاسم الأول</h2>
                ''' + ''.join([f'<div class="row"><span>{i+1}</span><div class="stars" onclick="mark(event)">{"<span class=\'star\'>★</span>"*5}</div></div>' for i in range(30)]) + '''
            </div>
            <div class="column">
                <h2 contenteditable="true">الاسم الثاني</h2>
                ''' + ''.join([f'<div class="row"><span>{i+1}</span><div class="stars" onclick="mark(event)">{"<span class=\'star\'>★</span>"*5}</div></div>' for i in range(30)]) + '''
            </div>
        </div>
        <script>
            function mark(e) {
                if(e.target.classList.contains('star')) {
                    let s = e.target;
                    let parent = s.parentElement;
                    let all = parent.children;
                    let found = false;
                    for(let i=4; i>=0; i--) {
                        if(all[i] == s || found) { all[i].classList.add('active'); found = true; }
                        else { all[i].classList.remove('active'); }
                    }
                }
            }
        </script>
    </body>
    </html>
    '''
    return html_content

if __name__ == '__main__':
    app.run()
