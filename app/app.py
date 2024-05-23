from flask import Flask, render_template, url_for, redirect

app = Flask(__name__)


@app.route("/")
def index():
    titulo= "Amaury"
    return render_template('index.html')

@app.route("/layout")
def layout():
    return render_template('layout.html')

@app.route("/aboutUs")
def aboutUs():
    return render_template ('aboutUs.html')

@app.route("/dashboard")
def dashboard():    
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)