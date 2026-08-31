import sys
# from database.database import create_tables      ##Should work after Implementing Database
from PySide6.QtWidgets import QApplication
from ui.login_window import LoginWindow

def main():
    # Initialize database
        #Remaining
    # create_tables()  
        #Should work after Implementing Database
    
    app = QApplication(sys.argv)
    # Set global style
    app.setStyle("Fusion")
    
    login_window = LoginWindow()
    login_window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

