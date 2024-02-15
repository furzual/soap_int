from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def main():
    num=10
    return render_template('index.html',num=num)