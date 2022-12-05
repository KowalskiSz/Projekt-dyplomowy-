import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizeGrip, QMessageBox
from PyQt5.QtCore import QCoreApplication


class MainWindow(QMainWindow): 
    def __init__(self): 
        super(MainWindow,self).__init__()
        loadUi("FrontPanel.ui",self)

        self.setWindowTitle("Filter Tester")
      

        '''
        Filter table initialozation
        '''
        self.filterTab.setColumnWidth(0,80)
        self.filterTab.setColumnWidth(1,80)
        self.filterTab.setColumnWidth(2,85)

        self.filterTab.setLineWidth(20)
        self.testStartButton.setEnabled(False)



        '''
        Close button event handling
        '''
        self.exitButton.clicked.connect(self.closeAppFun)

    def closeAppFun(self): 
        QCoreApplication.instance().quit()

    '''
    Exiting app by clicking cross
    '''
    def closeEvent(self, event): 
        reply = QMessageBox.question(self, 'Window Close', 'Do you really want to exit?', 
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes: 
            event.accept()
        else: 
            event.ignore()

if __name__ == "__main__": 

    app = QApplication(sys.argv)
    mainWidndow = MainWindow()
  

    mainWidndow.setFixedWidth(1300)
    mainWidndow.setFixedHeight(900)
    mainWidndow.show()

    sys.exit(app.exec_())




