from PySide6.QtGui import QPalette, QColor

DUMMY_COURSES = [
    "CSE 2100 - Software Development",
    "CSE 2101 - Data Structures & Algorithms",
    "CSE 2102 - Object Oriented Programming",
    "CSE 2103 - Discrete Mathematics",
    "CSE 2104 - Digital Electronics"
]

CLASS_SLOTS = [
    "8.00 AM - 8.50 AM",
    "8.50 AM - 9.40 AM",
    "9.40 AM - 10.30 AM",
    "10.50 AM - 11.40 AM",
    "11.40 AM - 12.30 PM",
    "12.30 PM - 1.20 PM",
    "2.30 PM - 3.20 PM",
    "3.20 PM - 4.10 PM",
    "4.10 PM - 5.00 PM"
]

LAB_SLOTS = [
    "8.00 AM - 10.30 AM",
    "10.50 AM - 1.20 PM",
    "2.30 PM - 5.00 PM"
]

DIALOG_STYLE = """
    QDialog, QWidget {
        background-color: #1e293b;
        color: #ffffff;
    }
    QLabel {
        color: #ffffff;
        background-color: transparent;
        font-size: 13px;
        font-weight: bold;
    }
    QLineEdit, QComboBox, QDateEdit {
        background-color: #0f172a;
        color: #ffffff;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 13px;
    }
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
        border: 1px solid #3b82f6;
    }
    QComboBox QAbstractItemView {
        background-color: #0f172a;
        color: #ffffff;
        selection-background-color: #2563eb;
    }
    QPushButton {
        background-color: #2563eb;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 8px;
        font-weight: bold;
        font-size: 14px;
    }
    QPushButton:hover {
        background-color: #1d4ed8;
    }
"""

TABLE_STYLE = """
    QTableWidget {
        background-color: #ffffff;
        border: 1px solid #cbd5e0;
        border-radius: 8px;
        gridline-color: #e2e8f0;
    }
    QHeaderView::section {
        background-color: #1e293b;
        color: #ffffff;
        font-weight: bold;
        font-size: 13px;
        padding: 10px;
        border: none;
        border-right: 1px solid #334155;
    }
    QTableWidget::item {
        color: #1e293b;
        font-size: 13px;
        padding: 8px;
    }
"""

def setup_dark_dialog(dialog):
    """Applies QPalette and stylesheet to ensure clean dark styling on Windows dialogs."""
    palette = dialog.palette()
    palette.setColor(QPalette.Window, QColor("#1e293b"))
    palette.setColor(QPalette.WindowText, QColor("#ffffff"))
    palette.setColor(QPalette.Base, QColor("#0f172a"))
    palette.setColor(QPalette.Text, QColor("#ffffff"))
    palette.setColor(QPalette.Button, QColor("#2563eb"))
    palette.setColor(QPalette.ButtonText, QColor("#ffffff"))
    dialog.setPalette(palette)
    dialog.setStyleSheet(DIALOG_STYLE)


def show_dark_message_box(parent, icon, title, message):
    """Shows a dark-themed QMessageBox styled consistently with Login and CT message boxes."""
    from PySide6.QtWidgets import QMessageBox
    msg = QMessageBox(parent)
    msg.setIcon(icon)
    msg.setWindowTitle(title)
    msg.setText(message)

    palette = msg.palette()
    palette.setColor(QPalette.Window, QColor("#1e293b"))
    palette.setColor(QPalette.WindowText, QColor("#ffffff"))
    palette.setColor(QPalette.Base, QColor("#1e293b"))
    palette.setColor(QPalette.Text, QColor("#ffffff"))
    palette.setColor(QPalette.Button, QColor("#2563eb"))
    palette.setColor(QPalette.ButtonText, QColor("#ffffff"))
    msg.setPalette(palette)

    msg.setStyleSheet("""
        QMessageBox, QDialog, QWidget {
            background-color: #1e293b;
            color: #ffffff;
        }
        QLabel {
            color: #ffffff;
            background-color: transparent;
            font-size: 14px;
        }
        QPushButton {
            background-color: #2563eb;
            color: #ffffff;
            border: none;
            border-radius: 6px;
            padding: 8px 20px;
            font-weight: bold;
            font-size: 13px;
            min-width: 70px;
        }
        QPushButton:hover {
            background-color: #1d4ed8;
        }
    """)
    msg.exec()

