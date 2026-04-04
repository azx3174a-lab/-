import os
from flask import Flask, render_template_string, request, send_file
from PIL import Image
import io

app = Flask(__name__)
# رفع الحد الأقصى للملفات لـ 200 ميجابايت عشان الـ 100 صورة
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024 

html_ui = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>محول الصور الذكي 📸</title>
    <style>
        body { font-family: sans-serif; background: #f0f2f5; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .card { background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); width: 90%; max-width: 400px; text-align: center; }
        .upload-btn { background: #007bff; color: white; padding: 15px; border-radius: 10px; display: block; cursor: pointer; margin: 20px 0; font-weight: bold; }
        .convert-btn { background: #28a745; color: white; border: none; padding: 15px; width: 100%; border-radius: 10px; font-weight: bold; cursor: pointer; font-size: 1.1em; }
        input[type="file"] { display: none; }
        #status { color: #555; margin-top: 10px; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="card">
        <h2>تحويل الصور إلى PDF 📄</h2>
        <form action="/convert" method="post" enctype="multipart/form-data">
            <label class="upload-btn">
                اختر الصور (أي عدد) 📷
                <input type="file" name="images" multiple accept="image/*" onchange="document.getElementById('status').innerText = 'تم اختيار ' + this.files.length + ' صورة'">
            </label>
            <div id="status">لم يتم اختيار صور بعد</div>
            <button type="submit" class="convert-btn">تحويل وتحميل الآن ✨</button>
        </form>
    </div>
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
        return "الرجاء اختيار ملفات!", 400

    image_list = []
    for file in files:
        try:
            img = Image.open(file)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            image_list.append(img)
        except:
            continue

    if not image_list:
        return "خطأ في معالجة الصور!", 400

    pdf_io = io.BytesIO()
    image_list[0].save(pdf_io, format="PDF", save_all=True, append_images=image_list[1:])
    pdf_io.seek(0)
    
    return send_file(pdf_io, mimetype='application/pdf', as_attachment=True, download_name='my_document.pdf')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
