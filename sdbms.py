import sys
import sqlite3
from PyQt5 import QtGui
from PyQt5.QtWidgets import (
    QTableWidgetItem, QTableWidget, QComboBox, QVBoxLayout,
    QGridLayout, QDialog, QWidget, QPushButton, QApplication,
    QMainWindow, QMessageBox, QLabel, QLineEdit
)

# ─────────────────────────────────────────────
#  Credentials  (change these as needed)
# ─────────────────────────────────────────────
VALID_USERNAME = "admin"
VALID_PASSWORD = "admin123"

# ─────────────────────────────────────────────
#  Course / Department mappings
# ─────────────────────────────────────────────
DEPARTMENTS = [
    "Mechanical Engineering",
    "Chemical Engineering",
    "Software Engineering",
    "Biotech Engineering",
    "Computer Science and Engineering",
    "Information Technology",
]

YEARS = ["1st", "2nd", "3rd", "4th"]

COURSES = [
    "DBMS", "OS", "CN", "C++", "JAVA", "PYTHON",
    "THERMO", "MACHINE", "CELLS", "DS", "CRE",
    "MICROBES", "FERTILIZER", "PLANTS", "MOBILE APP",
]


# ─────────────────────────────────────────────
#  Database helper
# ─────────────────────────────────────────────
class DBHelper:
    """Opens a fresh connection for every operation — safe and simple."""

    DB_NAME = "sdms.db"

    @staticmethod
    def _get_conn():
        conn = sqlite3.connect(DBHelper.DB_NAME)
        c = conn.cursor()
        c.execute(
            "CREATE TABLE IF NOT EXISTS student("
            "sid INTEGER PRIMARY KEY, Sname TEXT, dept INTEGER, year INTEGER,"
            "course_a INTEGER, course_b INTEGER, course_c INTEGER)"
        )
        conn.commit()
        return conn, c

    @staticmethod
    def addStudent(sid, sname, dept, year, course_a, course_b, course_c):
        conn, c = DBHelper._get_conn()
        try:
            c.execute(
                "INSERT INTO student(sid, Sname, dept, year, course_a, course_b, course_c)"
                " VALUES (?,?,?,?,?,?,?)",
                (sid, sname, dept, year, course_a, course_b, course_c),
            )
            conn.commit()
            QMessageBox.information(None, "Success", "Student added successfully.")
        except sqlite3.IntegrityError:
            QMessageBox.warning(None, "Error", f"Roll No {sid} already exists.")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Could not add student:\n{e}")
        finally:
            conn.close()

    @staticmethod
    def searchStudent(sid):
        conn, c = DBHelper._get_conn()
        try:
            c.execute("SELECT * FROM student WHERE sid=?", (sid,))
            row = c.fetchone()
        finally:
            conn.close()

        if not row:
            QMessageBox.warning(None, "Error", f"No student found with Roll No {sid}.")
            return
        showStudent(list(row))

    @staticmethod
    def deleteRecord(sid):
        conn, c = DBHelper._get_conn()
        try:
            c.execute("DELETE FROM student WHERE sid=?", (sid,))
            if c.rowcount == 0:
                QMessageBox.warning(None, "Error", f"No student found with Roll No {sid}.")
            else:
                conn.commit()
                QMessageBox.information(None, "Success", "Student deleted successfully.")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Could not delete record:\n{e}")
        finally:
            conn.close()


# ─────────────────────────────────────────────
#  Show student details in a table dialog
# ─────────────────────────────────────────────
def showStudent(data):
    sid    = data[0]
    sname  = data[1]
    dept   = DEPARTMENTS[data[2]] if 0 <= data[2] < len(DEPARTMENTS) else "Unknown"
    year   = YEARS[data[3]]       if 0 <= data[3] < len(YEARS)       else "Unknown"
    ca     = COURSES[data[4]]     if 0 <= data[4] < len(COURSES)     else "Unknown"
    cb     = COURSES[data[5]]     if 0 <= data[5] < len(COURSES)     else "Unknown"
    cc     = COURSES[data[6]]     if 0 <= data[6] < len(COURSES)     else "Unknown"

    rows = [
        ("Roll No",     str(sid)),
        ("Name",        sname),
        ("Department",  dept),
        ("Year",        year),
        ("Slot A",      ca),
        ("Slot B",      cb),
        ("Slot C",      cc),
    ]

    table = QTableWidget(len(rows), 2)
    table.setHorizontalHeaderLabels(["Field", "Value"])
    table.horizontalHeader().setStretchLastSection(True)
    table.verticalHeader().setVisible(False)

    for r, (field, value) in enumerate(rows):
        table.setItem(r, 0, QTableWidgetItem(field))
        table.setItem(r, 1, QTableWidgetItem(value))

    dialog = QDialog()
    dialog.setWindowTitle("Student Details")
    dialog.resize(500, 300)
    layout = QVBoxLayout(dialog)
    layout.addWidget(table)
    dialog.exec_()


# ─────────────────────────────────────────────
#  Login dialog
# ─────────────────────────────────────────────
class Login(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login — SDMS")
        self.setFixedSize(300, 150)

        self.userLabel = QLabel("Username")
        self.passLabel = QLabel("Password")
        self.textName  = QLineEdit(self)
        self.textPass  = QLineEdit(self)
        self.textPass.setEchoMode(QLineEdit.Password)   # hide password input

        self.btnLogin  = QPushButton("Login", self)
        self.btnLogin.clicked.connect(self.handleLogin)
        self.btnLogin.setDefault(True)

        grid = QGridLayout(self)
        grid.addWidget(self.userLabel, 0, 0)
        grid.addWidget(self.textName,  0, 1)
        grid.addWidget(self.passLabel, 1, 0)
        grid.addWidget(self.textPass,  1, 1)
        grid.addWidget(self.btnLogin,  2, 0, 1, 2)

    def handleLogin(self):
        if (self.textName.text() == VALID_USERNAME and
                self.textPass.text() == VALID_PASSWORD):
            self.accept()
        else:
            QMessageBox.warning(self, "Login Failed", "Incorrect username or password.")
            self.textPass.clear()
            self.textPass.setFocus()


# ─────────────────────────────────────────────
#  Add student dialog
# ─────────────────────────────────────────────
def _make_course_combo(parent):
    combo = QComboBox(parent)
    for c in COURSES:
        combo.addItem(c)
    return combo


class AddStudent(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Student Details")
        self.resize(500, 320)

        # Widgets
        self.rollText  = QLineEdit(self)
        self.nameText  = QLineEdit(self)

        self.yearCombo   = QComboBox(self)
        for y in YEARS:
            self.yearCombo.addItem(y)

        self.branchCombo = QComboBox(self)
        for d in DEPARTMENTS:
            self.branchCombo.addItem(d)

        self.cACombo = _make_course_combo(self)
        self.cBCombo = _make_course_combo(self)
        self.cCCombo = _make_course_combo(self)

        self.btnAdd    = QPushButton("Add", self)
        self.btnReset  = QPushButton("Reset", self)
        self.btnCancel = QPushButton("Cancel", self)

        for btn in (self.btnAdd, self.btnReset, self.btnCancel):
            btn.setFixedHeight(30)

        # Layout
        grid = QGridLayout(self)
        labels = ["Roll No", "Name", "Current Year", "Branch", "Slot A", "Slot B", "Slot C"]
        widgets = [
            self.rollText, self.nameText, self.yearCombo,
            self.branchCombo, self.cACombo, self.cBCombo, self.cCCombo,
        ]
        for i, (lbl, wgt) in enumerate(zip(labels, widgets), start=1):
            grid.addWidget(QLabel(lbl), i, 0)
            grid.addWidget(wgt,         i, 1)

        grid.addWidget(self.btnReset,  9, 0)
        grid.addWidget(self.btnAdd,    9, 1)
        grid.addWidget(self.btnCancel, 9, 2)

        self.btnAdd.clicked.connect(self.addStudent)
        self.btnReset.clicked.connect(self.reset)
        self.btnCancel.clicked.connect(self.close)

    def reset(self):
        self.rollText.clear()
        self.nameText.clear()
        self.yearCombo.setCurrentIndex(0)
        self.branchCombo.setCurrentIndex(0)
        self.cACombo.setCurrentIndex(0)
        self.cBCombo.setCurrentIndex(0)
        self.cCCombo.setCurrentIndex(0)

    def addStudent(self):
        roll_text = self.rollText.text().strip()
        name_text = self.nameText.text().strip()

        if not roll_text.isdigit():
            QMessageBox.warning(self, "Input Error", "Roll No must be a number.")
            return
        if not name_text:
            QMessageBox.warning(self, "Input Error", "Name cannot be empty.")
            return

        DBHelper.addStudent(
            int(roll_text),
            name_text,
            self.branchCombo.currentIndex(),
            self.yearCombo.currentIndex(),
            self.cACombo.currentIndex(),
            self.cBCombo.currentIndex(),
            self.cCCombo.currentIndex(),
        )


# ─────────────────────────────────────────────
#  Roll-number input dialog (reusable)
# ─────────────────────────────────────────────
class RollDialog(QDialog):
    def __init__(self, title, btn_label, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(300, 120)

        self.label    = QLabel("Enter Roll No of the student:")
        self.editRoll = QLineEdit(self)
        self.btnOk    = QPushButton(btn_label, self)
        self.btnOk.setDefault(True)

        vbox = QVBoxLayout(self)
        vbox.addWidget(self.label)
        vbox.addWidget(self.editRoll)
        vbox.addWidget(self.btnOk)

    def getRoll(self):
        text = self.editRoll.text().strip()
        if not text.isdigit():
            QMessageBox.warning(self, "Input Error", "Please enter a valid numeric Roll No.")
            return None
        return int(text)


# ─────────────────────────────────────────────
#  Main window
# ─────────────────────────────────────────────
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Database Management System")
        self.setFixedSize(420, 300)

        # Logo / user image
        picLabel = QLabel(self)
        picLabel.setScaledContents(True)
        pixmap = QtGui.QPixmap("user.png")
        if not pixmap.isNull():
            picLabel.setPixmap(pixmap)
        else:
            picLabel.setText("[ No Image ]")
            picLabel.setAlignment(__import__("PyQt5.QtCore", fromlist=["Qt"]).Qt.AlignCenter)

        # Buttons
        btnEnter  = QPushButton("Enter Student Details", self)
        btnShow   = QPushButton("Show Student Details",  self)
        btnDelete = QPushButton("Delete Record",          self)

        for btn in (btnEnter, btnShow, btnDelete):
            font = btn.font()
            font.setPointSize(12)
            btn.setFont(font)
            btn.setFixedHeight(45)

        btnEnter.clicked.connect(self.enterStudent)
        btnShow.clicked.connect(self.showStudentDialog)
        btnDelete.clicked.connect(self.deleteRecordDialog)

        # Layout
        grid = QGridLayout()
        grid.addWidget(picLabel,  0, 0, 1, 2)
        grid.addWidget(btnEnter,  1, 0)
        grid.addWidget(btnDelete, 1, 1)
        grid.addWidget(btnShow,   2, 0, 1, 2)

        container = QWidget()
        container.setLayout(grid)
        self.setCentralWidget(container)

    def enterStudent(self):
        dlg = AddStudent()
        dlg.exec_()

    def showStudentDialog(self):
        dlg = RollDialog("Show Student", "Search")
        dlg.btnOk.clicked.connect(lambda: self._doSearch(dlg))
        dlg.exec_()

    def deleteRecordDialog(self):
        dlg = RollDialog("Delete Record", "Delete")
        dlg.btnOk.clicked.connect(lambda: self._doDelete(dlg))
        dlg.exec_()

    def _doSearch(self, dlg):
        roll = dlg.getRoll()
        if roll is not None:
            dlg.accept()
            DBHelper.searchStudent(roll)

    def _doDelete(self, dlg):
        roll = dlg.getRoll()
        if roll is not None:
            reply = QMessageBox.question(
                self, "Confirm Delete",
                f"Are you sure you want to delete Roll No {roll}?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                dlg.accept()
                DBHelper.deleteRecord(roll)


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)

    login = Login()
    if login.exec_() == QDialog.Accepted:
        window = Window()
        window.show()
        sys.exit(app.exec_())