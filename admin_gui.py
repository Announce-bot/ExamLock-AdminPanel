import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from io import BytesIO

# Change this to match your Admin Server IP
SERVER_URL = "http://192.168.0.186:5000"

class AdminPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Exam Admin Panel")
        self.setGeometry(200, 200, 600, 500)
        
        layout = QVBoxLayout()
        
        self.label = QLabel("Connected Students:")
        layout.addWidget(self.label)

        self.student_list = QListWidget()
        layout.addWidget(self.student_list)

        self.refresh_button = QPushButton("Refresh Students")
        self.refresh_button.clicked.connect(self.get_students)
        layout.addWidget(self.refresh_button)

        self.screenshot_label = QLabel("Student Screenshot:")
        layout.addWidget(self.screenshot_label)

        self.screenshot_display = QLabel()
        self.screenshot_display.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.screenshot_display)

        self.lock_button = QPushButton("Lock Student")
        self.lock_button.clicked.connect(self.lock_student)
        layout.addWidget(self.lock_button)

        self.unlock_button = QPushButton("Unlock Student")
        self.unlock_button.clicked.connect(self.unlock_student)
        layout.addWidget(self.unlock_button)

        self.shutdown_button = QPushButton("Shutdown Student")
        self.shutdown_button.clicked.connect(self.shutdown_student)
        layout.addWidget(self.shutdown_button)

        self.restart_button = QPushButton("Restart Student")
        self.restart_button.clicked.connect(self.restart_student)
        layout.addWidget(self.restart_button)

        self.get_logs_button = QPushButton("Download Logs")
        self.get_logs_button.clicked.connect(self.get_logs)
        layout.addWidget(self.get_logs_button)

        self.setLayout(layout)
        self.get_students()

    def get_students(self):
        """Retrieve the list of connected students from the server."""
        try:
            response = requests.get(f"{SERVER_URL}/get_students")
            if response.status_code == 200:
                students = response.json()
                self.student_list.clear()
                for student in students:
                    self.student_list.addItem(student["id"])
                QMessageBox.information(self, "Success", "Student list updated.")
            else:
                QMessageBox.warning(self, "Error", "Failed to retrieve students.")
        except:
            QMessageBox.critical(self, "Error", "Could not connect to Admin Server.")

    def lock_student(self):
        """Lock the selected student."""
        student = self.get_selected_student()
        if student:
            requests.post(f"{SERVER_URL}/lock/{student}")
            QMessageBox.information(self, "Locked", f"{student} has been locked.")

    def unlock_student(self):
        """Unlock the selected student."""
        student = self.get_selected_student()
        if student:
            requests.post(f"{SERVER_URL}/unlock/{student}")
            QMessageBox.information(self, "Unlocked", f"{student} has been unlocked.")

    def shutdown_student(self):
        """Shutdown the selected student."""
        student = self.get_selected_student()
        if student:
            requests.post(f"{SERVER_URL}/shutdown/{student}")
            QMessageBox.warning(self, "Shutdown", f"{student} is shutting down.")

    def restart_student(self):
        """Restart the selected student."""
        student = self.get_selected_student()
        if student:
            requests.post(f"{SERVER_URL}/restart/{student}")
            QMessageBox.information(self, "Restarted", f"{student} is restarting.")

    def get_logs(self):
        """Download logs from the selected student."""
        student = self.get_selected_student()
        if student:
            response = requests.get(f"{SERVER_URL}/get_logs/{student}")
            if response.status_code == 200:
                log_path = f"{student}_log.txt"
                with open(log_path, "wb") as f:
                    f.write(response.content)
                QMessageBox.information(self, "Logs Downloaded", f"Logs saved as {log_path}")
            else:
                QMessageBox.warning(self, "Error", "No logs available.")

    def get_selected_student(self):
        """Get the currently selected student from the list."""
        selected_item = self.student_list.currentItem()
        if selected_item:
            return selected_item.text()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a student.")
            return None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminPanel()
    window.show()
    sys.exit(app.exec_())
