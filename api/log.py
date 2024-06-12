from flask import Flask, render_template

app = Flask(__name__)

@app.route('/logs')
def show_logs():
    with open('logs.log', 'r') as f:
        logs = f.readlines()
    return render_template('logs.html', logs=logs)

if __name__ == '__main__':
    app.run(debug=True)
