from PySide6.QtWidgets import QApplication

from gui.mainwindow import MainWindow

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec())