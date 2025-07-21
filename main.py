from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

import sys

from core.session import Session
from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("./media/logo.png"))

    session = Session()

    main_window = MainWindow(session)
    main_window.show()

    sys.exit(app.exec())