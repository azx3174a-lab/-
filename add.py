from flask import Flask, render_template_string, session, os

app = Flask(__name__)
app.secret_key = "huroof_ui_v1"

# --- تصميم CSS للشبكة السداسية ---
HEX_STYLE = """
<style>
    :root { --bg-color: #0f172a; --hex-default: #334155; --red-team: #ef4444; --green-team: #22c55e; --active: #f59e0b; }
    body { background-color: var(--bg-color); color: white; font-family: 'Cairo', sans-serif; display: flex; flex-direction: column; align-items: center; margin: 0; padding: 20px; }
    
    .grid { display: flex; flex-direction: column; align-items: center; margin-top: 30px; }
    .row { display: flex; justify-content: center; margin-bottom: -15px; } /* تداخل الصفوف */
    .row:nth-child(even) { margin-right: 70px; } /* إزاحة الصفوف الزوجية لعمل شكل الخلية */

    .hexagon {
        width: 100px; height: 115px; background-color: var(--hex-default);
        clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
        display: flex; align-items: center; justify-content: center;
        font-size: 2rem; font-weight: bold; cursor: pointer; transition: all 0.3s ease;
        margin: 5px; position: relative;
    }
    .hexagon:hover { transform: scale(1.1); filter: brightness(1.3); z-index: 10; }
    .hexagon.red { background-color: var(--red-team); box-shadow: 0 0 15px var(--red-team); }
    .hexagon.green { background-color: var(--green-team); box-shadow: 0 0 15px var(--green-team); }
    .hexagon.active { background-color: var(--active); color: black; }

    h1 { text-shadow: 0 0 10px #818cf8; margin-bottom: 5px; }
</style>
"""

LAYOUT = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>واجهة حروف مع عزيز</title>
    """ + HEX_STYLE + """
</head>
<body>
    <h1>🎮 حروف مع عزيز</h1>
    <p>اختر حرفاً لبدء التحدي</p>

    <div class="grid">
        <div class="row">
            <div class="hexagon">أ</div><div class="hexagon red">ب</div><div class="hexagon">ت</div><div class="hexagon">ث</div>
        </div>
        <div class="row">
            <div class="hexagon">ج</div><div class="hexagon active">ح</div><div class="hexagon green">خ</div><div class="hexagon">د</div>
        </div>
        <div class="row">
            <div class="hexagon">ذ</div><div class="hexagon">ر</div><div class="hexagon">ز</div><div class="hexagon">س</div>
        </div>
    </div>

    <script>
        // هنا سنضيف تفاعل الضغط على الحروف لاحقاً
        document.querySelectorAll('.hexagon').forEach(hex => {
            hex.onclick = () => {
                alert("تم اختيار حرف: " + hex.innerText);
            };
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(LAYOUT)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
