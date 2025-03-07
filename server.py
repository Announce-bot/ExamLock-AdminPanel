from flask import Flask, request, jsonify, send_file
import os
import datetime

app = Flask(__name__)

students = {}  # Stores student screenshots & log info
logs_dir = "logs"

# Ensure logs directory exists
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

@app.route("/upload", methods=["POST"])
def upload_screenshot():
    """Receive student screenshots & log activities"""
    file = request.files['file']
    student_id = request.form['id']
    log_data = request.form.get('log', '')

    # Save screenshot
    save_path = f"static/{student_id}.png"
    file.save(save_path)
    students[student_id] = save_path

    # Save log data
    if log_data:
        log_filename = os.path.join(logs_dir, f"{student_id}.txt")
        with open(log_filename, "a") as log_file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"[{timestamp}] {log_data}\n")

    return "Screenshot & Log Received", 200

@app.route("/get_students", methods=["GET"])
def get_students():
    """Return the list of students being monitored"""
    return jsonify([{"id": ip, "screenshot": path} for ip, path in students.items()])

@app.route("/lock/<student_id>", methods=["POST"])
def lock_student(student_id):
    """Remotely lock a student’s screen"""
    os.system(f"shutdown /s /m \\\\{student_id} /t 5")
    return "Student Locked", 200

@app.route("/unlock/<student_id>", methods=["POST"])
def unlock_student(student_id):
    """Unlock a student’s screen"""
    return "Student Unlocked", 200

@app.route("/shutdown/<student_id>", methods=["POST"])
def shutdown_student(student_id):
    """Shutdown a student's PC"""
    os.system(f"shutdown /s /m \\\\{student_id} /t 0")
    return "Student Shutdown", 200

@app.route("/restart/<student_id>", methods=["POST"])
def restart_student(student_id):
    """Restart a student's PC"""
    os.system(f"shutdown /r /m \\\\{student_id} /t 0")
    return "Student Restarted", 200

@app.route("/get_logs/<student_id>", methods=["GET"])
def get_logs(student_id):
    """Fetch student security logs"""
    log_filename = os.path.join(logs_dir, f"{student_id}.txt")
    if os.path.exists(log_filename):
        return send_file(log_filename, as_attachment=True)
    else:
        return "No logs found", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
