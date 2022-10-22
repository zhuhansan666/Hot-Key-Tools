from PySide2.QtWidgets import QApplication, QMainWindow
import sys
from uis.ui_settings import Ui_HotKeyTools

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_HotKeyTools()
    ui.setupUi(MainWindow)
    MainWindow.setWindowTitle("热键工具")
    MainWindow.show()
    # MainWindow.events_table
    sys.exit(app.exec_())
