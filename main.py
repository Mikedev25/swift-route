from PyQt5.QtWidgets import *
from function import *
from ui import *

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
 
 
if __name__ == "__main__":
    main()