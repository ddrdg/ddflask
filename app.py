from flask import Flask, request, render_template, jsonify, Response
import subprocess

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for using session
process = None
command = None

@app.route('/')
def index():
    return render_template('index.html')

def run_command_generator():
    global process, command
    if not command:
        yield "data: No command found\n\n"
        return

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        for stdout_line in iter(process.stdout.readline, ""):
            yield f"data: {stdout_line}\n\n"
        process.stdout.close()
        process.wait()
    except Exception as e:
        yield f"data: An error occurred: {str(e)}\n\n"

@app.route('/start-command', methods=['POST'])
def start_command():
    global process, command
    param1 = request.form.get('param1')
    param2 = request.form.get('param2')
    param3 = request.form.get('param3')

    command = f"./bgmi {param1} {param2} {param3} 500"
    if process and process.poll() is None:
        process.terminate()
    return jsonify({'status': 'Command started'})

@app.route('/stream-output', methods=['GET'])
def stream_output():
    return Response(run_command_generator(), mimetype='text/event-stream')

@app.route('/start-command', methods=['POST'])
def start_command():
    global process
    if process and process.poll() is None:
        process.terminate()
        process.wait()  # Wait for process termination
    process = subprocess.Popen("./your_command_here", shell=True)
    return jsonify({'status': 'Command started'})

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
