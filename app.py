from flask import Flask, send_from_directory, render_template

app = Flask(__name__)

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('assets', filename)

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()
