from flask import Flask, request, render_template, jsonify, Response
import subprocess
import os
import signal

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

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, preexec_fn=os.setsid)
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
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)  # Use process group to terminate
        process.wait()  # Ensure termination
    return jsonify({'status': 'Command started'})

@app.route('/stream-output', methods=['GET'])
def stream_output():
    return Response(run_command_generator(), mimetype='text/event-stream')

@app.route('/stop-command', methods=['POST'])
def stop_command():
    global process
    if process and process.poll() is None:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)  # Send SIGTERM to all processes in the group
            process.wait(timeout=5)  # Wait up to 5 seconds for termination
        except subprocess.TimeoutExpired:
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)  # Force kill if not terminated
        process = None
        return jsonify({'output': 'Command terminated'})
    return jsonify({'output': 'No running command to terminate'})

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
