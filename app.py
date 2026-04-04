import os
from flask import Flask, render_template_string, request, send_file
from PIL import Image
import io

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # حد أقصى 100 ميجابايت للرفع

# --- واجهة الموقع ---
html_ui = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>محول الصور الذكي 📸</title>
    <style>
        body { font-family: sans-serif; background: #f4f7f6; display: flex; justify-content: center; padding: 20px; }
        .card { background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); max-width: 500px; width: 100%; text-align: center; }
        h2 { color: #333; }
        .upload-area { border: 2px dashed #007bff; padding: 30px; border-radius: 15px; margin: 20px 0; cursor: pointer; background: #f8fbff; }
        input[type="file"] { display: none; }
        .btn { background: #007bff; color: white; border: none; padding: 12px 25px; border-radius: 10px; font-weight: bold; cursor: pointer; width: 100%; font-size: 1.1em; }
        .btn:hover { background: #0056b3; }
        .footer-note { font-size: 0.8em; color: #777; margin-top: 15px; }
        #file-count { margin-top: 10px; font-weight: bold; color: #28a745; }
    </style>
</head>
<body>
    <div class="card">
        <h2>تحويل الصور إلى PDF 📄</h2>
        <p>ارفع أي عدد من الصور لدمجها في ملف واحد</p>
        
        <form action="/convert" method="post" enctype="multipart/form-data">
            <label class="upload-area" for="images">
                <span>اضغط هنا لاختيار الصور 📷</span>
                <input type="file" name="images" id="images" multiple accept="image/*" onchange="updateCount()">
                <div id="file-count"></div>
            </label>
            
            <button type="submit" class="btn">تحويل وتحميل PDF الآن</button>
        </form>
        
        <div class="footer-note">
            * يدعم JPG, PNG, WEBP وغيرها.<br>
            * لا يوجد حد لعدد الصور.
        </div>
    </div>

    <script>
        function updateCount() {
            const input = document.getElementById('images');
            const countDiv = document.getElementById('file-count');
            countDiv.innerText = "تم اختيار " + input.files.length + " صورة";
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_ui)

@app.route('/convert', methods=['POST'])
def convert():
    files = request.files.getlist('images')
    if not files or files[0].filename == '':
        return "يرجى اختيار صور أولاً!", 400

    image_list = []
    
    for file in files:
        img = Image.open(file)
        # تحويل الصورة إلى RGB (ضروري لملفات PDF)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        image_list.append(img)

    # إنشاء ملف PDF في الذاكرة
    pdf_io = io.BytesIO()
    if image_list:
        image_list[0].save(pdf_io, format="PDF", save_all=True, append_images=image_list[1:])
        pdf_io.seek(0)
        
    return send_file(pdf_io, mimetype='application/pdf', as_attachment=True, download_name='converted_images.pdf')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
