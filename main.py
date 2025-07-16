from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow

import sys

from core.session import Session
from ui.feature_splitting_window import FeatureSplittingWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("./media/logo.png"))

    session = Session()

    window = FeatureSplittingWindow(session)

    mwindow = QMainWindow()
    mwindow.setWindowTitle("Plate Splitting - GPlates Utilities")
    mwindow.setCentralWidget(window)
    mwindow.resize(900, 400)

    mwindow.show()

    sys.exit(app.exec())