# from flask import Flask, render_template

# app = Flask(__name__)

# @app.route("/")
# def hello_world():
#     return render_template("index.html", title="Hello")

from flask import Flask, request, render_template, jsonify
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run-command', methods=['POST'])
def run_command():
    param1 = request.form.get('param1')
    param2 = request.form.get('param2')
    param3 = request.form.get('param3')
    
    # Construct the command using the parameters
    command = f"./bgmi {param1} {param2} {param3} 500"
    # full_command = f"./bgmi {target} {port} {time} 500"
    
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        output = e.output
    return jsonify({'output': output})

if __name__ == '__main__':
    app.run(debug=True)

