from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    # كود HTML بصفحة فاضية وخلفية بنفسجية
    html_content = """
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>صفحتي البنفسجية</title>
        <style>
            body {
                background-color: #8A2BE2; /* هذا هو اللون البنفسجي */
                margin: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                color: white;
                font-family: sans-serif;
            }
        </style>
    </head>
    <body>
        <h1>هذه هي الصفحة باللون البنفسجي 💜</h1>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
