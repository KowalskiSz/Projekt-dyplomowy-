import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizeGrip, QMessageBox
from PyQt5.QtCore import QCoreApplication

from QRThread import * 
from DataBaseClass import * 


class MainWindow(QMainWindow): 
    def __init__(self): 
        super(MainWindow,self).__init__()
        loadUi("FrontPanel.ui",self)

        self.setWindowTitle("Filter Tester")
      

        '''
        Filter table initialozation
        '''
        self.filterTab.setColumnWidth(0,80)
        self.filterTab.setColumnWidth(1,150)
        self.filterTab.setColumnWidth(2,120)

        self.filterTab.setLineWidth(20)
        '''
        Prevnting from starting testing with no data
        '''
        self.testStartButton.setEnabled(False)
       

        '''
        ComboBox values init
        getting values from comboboxes function
        '''
        self.comboSetUpAI = None
        self.comboSetUpAO = None 

        '''
        Variable for the filter boundries data
        '''

        self.filterBoundries = None

        self.DAQsetButton.clicked.connect(self.daqSet)
        self.cancelSetupButton.clicked.connect(self.cancelSetup)

       
        '''
        QRcode reader section
        '''
        self.qrAcqButton.clicked.connect(self.QRFun)
        
        self.abortScanButton.clicked.connect(self.abortFun)
       
        '''
        Submit chosen filter by selecting with combobox
        '''
        self.selectedFilterNumber = None
        self.selectedFilterDic = None

        self.submitFilterButton.clicked.connect(self.submitSelectedFilter)
        self.submitFilterButton.clicked.connect(self.popUpMessage)
        
        self.submitFilterButton.clicked.connect(lambda: self.dataBaseConnection(self.selectedFilterNumber))



        '''
        Close button event handling
        '''
        self.exitButton.clicked.connect(self.closeAppFun)

    '''
    Daq setup functions section
    '''
    def daqSet(self):

        self.comboSetUpAI = self.comboBoxAI.currentText()
        self.comboSetUpAO = self.comboBoxAO.currentText()

        self.DAQsetButton.setEnabled(False)


    def cancelSetup(self): 

        self.comboSetUpAI = None
        self.comboSetUpAO = None 
        self.DAQsetButton.setEnabled(True)

    '''
    QRCode reader section
    '''

    def QRFun(self): 
        
        self.camQR.setText("Initilaizaton")
        self.QRThread = QRThread()
        self.QRThread.start()

        #self.camQR.clear()
        self.resQRLabel.clear()
        self.QRThread.ImageUpdate.connect(self.imageUpdateSlot)
        self.QRThread.finished.connect(self.popUpQRMessage)
        self.QRThread.finished.connect(lambda: self.dataBaseConnection(self.QRThread.data))

    def imageUpdateSlot(self, image): 

        self.camQR.setPixmap(QPixmap.fromImage(image))

        if self.QRThread.flag == True: 
            
            QTimer.singleShot(1000, self.clearLabel)

            self.QRThread.resutCheck(self.QRThread.data)
            self.filterBoundries = self.QRThread.openDBFiles(self.QRThread.fileName)

            #self.resQRLabel.setText(self.QRThread.fileName)
    
    def popUpQRMessage(self): 
        
        #QtWidgets.QMessageBox.information(self, "Done", "Acqusition completed") 
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        
        msg.setWindowTitle("Filter Chosen")
        msg.setText(f"You have chosen filter number: {self.QRThread.data}")
        
        msg.setStandardButtons(QMessageBox.Ok)

        x = msg.exec_()


    def clearLabel(self): 

        self.camQR.clear()

    def abortFun(self): 

        self.QRThread.terminate()
        self.QRThread.cap.release()
        self.camQR.clear()

    '''
    Combobox filter section
    '''

    def submitSelectedFilter(self): 
        
        self.selectedFilterNumber = self.filterFindCombobox.currentText()
        
    '''
    Database section - creating instace of an obj, 
    writing info into table
    '''
    def dataBaseConnection(self, filterNumber): 

        self._dataBaseInst = DatabaseReader(filterNumber)
        self._dataBaseInst.exeFun()

        '''
        Setting up a variable that holds info about filter
        used next to initialize the test  
        '''
        self.selectedFilterDic = self._dataBaseInst.dataDic

        self.filterTab.setItem(0, 0, QTableWidgetItem(self._dataBaseInst.dataDic["FilterID"]))
        self.filterTab.setItem(0, 1, QTableWidgetItem(self._dataBaseInst.dataDic["Type"]))
        self.filterTab.setItem(0, 2, QTableWidgetItem(self._dataBaseInst.dataDic["DampInfo"]))
        
    
    def popUpMessage(self): 
        
        #QtWidgets.QMessageBox.information(self, "Done", "Acqusition completed") 
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        
        msg.setWindowTitle("Filter Chosen")
        msg.setText(f"You have chosen filter number: {self.selectedFilterNumber}")
        
        msg.setStandardButtons(QMessageBox.Ok)

        msg.exec_()

        
    
    '''
    Database and table section
    '''
        



    '''
    Closing app by clicking the Exit button
    '''
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




