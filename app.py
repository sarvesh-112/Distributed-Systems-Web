from flask import Flask, render_template, jsonify, request
from flask import send_from_directory, abort
from flask_socketio import SocketIO, emit
import threading
import subprocess
import time
import sys
import os

# ======================================
# CREATE FLASK APP
# ======================================

app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/static"
)

app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, cors_allowed_origins="*")

PYTHON_EXEC = sys.executable

# ======================================
# GLOBAL RMI SERVER PROCESS (AUTO-START)
# ======================================

rmi_server_process = None

def ensure_rmi_server_running():
    global rmi_server_process

    if rmi_server_process is None or rmi_server_process.poll() is not None:
        rmi_dir = os.path.abspath("programs/rmi_java")

        rmi_server_process = subprocess.Popen(
            ["java", "-cp", rmi_dir, "RMIServer"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Give RMI server time to bind to registry
        time.sleep(2)

# ======================================
# HOME
# ======================================

@app.route("/")
def home():
    return render_template("index.html")

# ======================================
# SOCKET DEMO
# ======================================

@app.route("/socket")
def socket_page():
    return render_template("socket.html")


@app.route("/socket/run", methods=["POST"])
def run_socket_demo():
    try:
        data = request.get_json()
        message = data.get("message", "Hello from Web UI")

        server_path = "programs/socket/server.py"
        client_path = "programs/socket/client.py"

        server_process = subprocess.Popen(
            [PYTHON_EXEC, server_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        time.sleep(1)

        client_process = subprocess.run(
            [PYTHON_EXEC, client_path, message],
            capture_output=True,
            text=True
        )

        time.sleep(1)
        server_process.terminate()

        return jsonify({
            "server_output": server_process.stdout.read(),
            "client_output": client_process.stdout
        })

    except Exception as e:
        return jsonify({"error": str(e)})

# ======================================
# P2P FILE LIST + DOWNLOAD
# ======================================

@app.route("/p2p")
def p2p_page():
    return render_template("p2p.html")


@app.route("/p2p/files")
def list_p2p_files():
    folder_path = "shared_data/shared_folder"

    if not os.path.exists(folder_path):
        return jsonify({"files": []})

    files = [
        f for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f))
    ]

    return jsonify({"files": files})


@app.route("/p2p/download/<filename>")
def download_p2p_file(filename):
    folder_path = "shared_data/shared_folder"
    file_path = os.path.join(folder_path, filename)

    if not os.path.exists(file_path):
        abort(404)

    return send_from_directory(folder_path, filename, as_attachment=True)

# ======================================
# RPC SERVICES
# ======================================

@app.route("/rpc")
def rpc_page():
    return render_template("rpc.html")


@app.route("/rpc/tax", methods=["POST"])
def rpc_tax():
    income = float(request.json.get("income", 0))

    if income <= 250000:
        result = "No tax"
    elif income <= 500000:
        result = f"Tax: {0.05 * income}"
    else:
        result = f"Tax: {0.10 * income}"

    return jsonify({"result": result})


@app.route("/rpc/cgpa", methods=["POST"])
def rpc_cgpa():
    marks = [float(m) for m in request.json.get("marks", [])]
    total = sum(marks)
    max_marks = len(marks) * 100
    cgpa = (total / max_marks) * 10 if max_marks else 0
    return jsonify({"result": round(cgpa, 2)})


@app.route("/rpc/voting", methods=["POST"])
def rpc_voting():
    age = int(request.json.get("age", 0))
    return jsonify({
        "result": "Eligible to vote" if age >= 18 else "Not eligible to vote"
    })

# ======================================
# SHARED MEMORY DASHBOARD
# ======================================

shared_value = 0

def shared_memory_updater():
    global shared_value
    while True:
        shared_value += 1
        time.sleep(2)

threading.Thread(target=shared_memory_updater, daemon=True).start()


@app.route("/shared-memory")
def shared_memory_page():
    return render_template("shared_memory.html")


@app.route("/shared-memory/value")
def get_shared_value():
    return jsonify({"value": shared_value})


@app.route("/shared-memory/increment", methods=["POST"])
def increment_shared_value():
    global shared_value
    shared_value += 5
    return jsonify({"value": shared_value})

# ======================================
# WEBSOCKET CHAT
# ======================================

@app.route("/chat")
def chat_page():
    return render_template("chat.html")


@socketio.on("send_message")
def handle_send_message(data):
    username = data.get("username", "Anonymous")
    message = data.get("message", "")

    emit(
        "receive_message",
        {"username": username, "message": message},
        broadcast=True
    )

# ======================================
# JAVA RMI FILE UPLOAD (AUTO-START SERVER)
# ======================================

@app.route("/rmi")
def rmi_page():
    return render_template("rmi.html")


@app.route("/rmi/upload", methods=["POST"])
def rmi_upload():
    try:
        ensure_rmi_server_running()

        file = request.files["file"]

        upload_dir = "shared_data"
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.abspath(os.path.join(upload_dir, file.filename))
        file.save(file_path)

        rmi_dir = os.path.abspath("programs/rmi_java")

        result = subprocess.run(
            ["java", "-cp", rmi_dir, "RMIClient", file_path],
            capture_output=True,
            text=True
        )

        if result.stderr:
            return jsonify({"output": result.stderr.strip()})

        return jsonify({"output": result.stdout.strip()})

    except Exception as e:
        return jsonify({"output": str(e)})
    
@app.route("/rmi/files")
def rmi_files():
    folder = "shared_data/rmi_received"
    os.makedirs(folder, exist_ok=True)

    files = [
        f for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f))
    ]

    return jsonify({"files": files})


@app.route("/rmi/download/<filename>")
def rmi_download(filename):
    folder = "shared_data/rmi_received"
    return send_from_directory(folder, filename, as_attachment=True)

# ======================================
# RUN APP
# ======================================

if __name__ == "__main__":
    socketio.run(app, debug=True)
