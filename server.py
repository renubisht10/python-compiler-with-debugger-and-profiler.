from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import time
import psutil
import sys
import io
import traceback

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def index():
    return render_template('index.html')

# Helper to run shell commands (not used in this version)
def run_command(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout + result.stderr
    except Exception as e:
        return str(e)

# ----------------------------
# ROUTE: RUN PYTHON CODE
# ----------------------------
def execute_python(code):
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    try:
        exec(code, {})
        output = redirected_output.getvalue()
    except Exception as e:
        output = traceback.format_exc()
    finally:
        sys.stdout = old_stdout
    return output

@app.route('/run', methods=['POST'])
def run_code():
    data = request.get_json()
    code = data['code']

    output = execute_python(code)
    return jsonify({'output': output})

# --------------------------
# ROUTE: DEBUG PYTHON CODE
# --------------------------
@app.route('/debug', methods=['POST'])
def debug_code():
    data = request.get_json()
    code = data['code']

    breakpoints = []
    variables = {}
    redirected_output = sys.stdout = io.StringIO()
    try:
        compiled = compile(code, '<user_code>', 'exec')
        local_vars = {}
        exec(compiled, {}, local_vars)
        lines = code.splitlines()
        breakpoints = [f"Line {i + 1}" for i in range(len(lines))]
        variables = {k: repr(v) for k, v in local_vars.items() if not k.startswith('__')}
    except AssertionError as ae:
        breakpoints = ["AssertionError: A test failed."]
    except SyntaxError as se:
        breakpoints = [f"Line {se.lineno} - SyntaxError: {se.msg}"]
    except Exception as e:
        breakpoints = [f"Error: {str(e)}"]
    finally:
        sys.stdout = sys.__stdout__

    return jsonify({
        'breakpoints': breakpoints,
        'variables': variables
    })

# ----------------------------
# ROUTE: PROFILE PYTHON CODE
# ----------------------------
@app.route('/profile', methods=['POST'])
def profile_code():
    data = request.get_json()
    code = data['code']

    start_time = time.time()
    process = psutil.Process()
    start_memory = process.memory_info().rss
    try:
        exec(code, {})
    except Exception as e:
        return jsonify({'error': traceback.format_exc()})
    end_time = time.time()
    end_memory = process.memory_info().rss

    return jsonify({
        'execTime': f'{(end_time - start_time):.4f} seconds',
        'memUsage': f'{(end_memory - start_memory) / 1024:.2f} KB'
    })

if __name__ == '__main__':
    app.run(debug=True)
