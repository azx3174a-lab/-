from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    # سنرسل رقم 30 للقالب لتكرار الأسطر 30 مرة
    return render_template('index.html', rows=30)

if __name__ == '__main__':
    app.run(debug=True)
