import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizeGrip, QMessageBox, QWidget
from PyQt5.QtCore import QCoreApplication


import nidaqmx
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from ReaderDAQ import * 
from WriterDAQ import * 

import queue

import math

from scipy import signal
from scipy.signal import find_peaks
from verifyModue import * 

from QRThread import * 
from DataBaseClass import * 
from OpenFilterJson import * 

class MainWindow(QMainWindow): 
    def __init__(self): 
        super(MainWindow,self).__init__()
        loadUi("FrontPanel.ui",self)
        

        self.setWindowTitle("Filter Tester")

        '''
        Section to initialaize plot widget on main screen
        '''

        self.horizantalLayout = QHBoxLayout(self.plotFrame)
        self.horizantalLayout.setObjectName('horizantalLayout')


        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        self.horizantalLayout.addWidget(self.canvas)



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
        self.submitFilterButton.setEnabled(False)
        self.qrAcqButton.setEnabled(False)


        '''
        Initialaize test values
        '''
        self.AIsampleRate= None
        self.AOsampleRate = None

        self.AIsampleSize = None
        self.AIsampleSize = None

        self.frequency = None

        '''
        ComboBox values init
        getting values from comboboxes function
        '''
        self.comboSetUpAI = None
        self.comboSetUpAO = None 

        self.DAQsetButton.clicked.connect(self.daqSet)
        self.cancelSetupButton.clicked.connect(self.cancelSetup)

        '''
        Variable for the filter boundries data
        '''

        self.filterBoundries = None

        '''
        Ok button
        '''
        self.okTestButton.clicked.connect(self.okButtonFun)

        '''
        progress bar initialization
        '''
        
        

       
        '''
        QRcode reader section
        '''
        self.abortFlag = False #Flag to prevent the abort qr read error
       
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
        Test class and testing algorythm call
        '''

        self.testStartButton.clicked.connect(self.acquireTest)


        '''
        Close button event handling
        '''
        self.exitButton.clicked.connect(self.closeAppFun)

    
    '''
    acquire signal and test section 
    '''
    def acquireTest(self): 

        self.testStartButton.setEnabled(False)

        self.acqAndTestThread = AcqAndTestThread(1, self.AISampleSize, self.AIsampleRate, 
        self.AOsampleSize, self.AOsampleRate, self.frequency, self.filterBoundries, self.comboSetUpAO, self.comboSetUpAI)

        self.acqAndTestThread.start()

        self.acqAndTestThread.dampPoints.connect(self.updatePlot)
        self.acqAndTestThread.testResult.connect(self.testResult)
        self.acqAndTestThread.updateProgressBar.connect(self.updateProressBar)

    def testResult(self, val): 

        if val == True: 
            self.testResultLabel.setText("Test Passed")
        else: 
            self.testResultLabel.setText("Test Failed")

    def updatePlot(self, vals): 
        
        self.figure.clear()
        plt.plot(self.frequency, vals)
        plt.xscale('log')
        plt.grid()
        self.canvas.draw()

    def okButtonFun(self): 

        self.figure.clear()
        self.testResultLabel.clear()
        

    def updateProressBar(self, val): 
        
        self.progressBar.setValue(val)




    '''
    Daq setup functions section
    '''
    def daqSet(self):

        self.comboSetUpAI = self.comboBoxAI.currentText()
        self.comboSetUpAO = self.comboBoxAO.currentText()

        self.DAQsetButton.setEnabled(False)
        self.submitFilterButton.setEnabled(True)
        self.qrAcqButton.setEnabled(True)


    def cancelSetup(self): 

        self.comboSetUpAI = None
        self.comboSetUpAO = None 
        self.DAQsetButton.setEnabled(True)
        self.submitFilterButton.setEnabled(False)
        

    '''
    QRCode reader section
    '''

    def QRFun(self): 
        
        self.camQR.setText("Initilaizaton")
        self.QRThread = QRThread()
        self.QRThread.start()

        #self.camQR.clear()
        #self.resQRLabel.clear()
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

        self.abortFlag = True
        self.QRThread.terminate()

        self.QRThread.cap.release()
        self.camQR.clear()

    '''
    Combobox filter section
    '''

    def submitSelectedFilter(self): 
        
        self.selectedFilterNumber = self.filterFindCombobox.currentText()
        openJson = OpenJsonFilter()

        self.filterBoundries = openJson.openJson(self.selectedFilterNumber) #getting vals from json file - boundries
        

        
    '''
    Database section - creating instace of an obj, 
    writing info into table
    '''
    def dataBaseConnection(self, filterNumber): 

        if not self.abortFlag: #saves from not executing qr read by aborting the process
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
            self.testStartButton.setEnabled(True)

            self.AIsampleRate = [int(i) for i in self.selectedFilterDic['AISampleRate'].split(',')]
            self.AISampleSize = int(self.selectedFilterDic['AISampleSize'])

            self.AOsampleRate = [int(i) for i in self.selectedFilterDic['AOSampleRate'].split(',')]
            self.AOsampleSize = int(self.selectedFilterDic['AOSampleSize'])

            self.frequency = [int(i) for i in self.selectedFilterDic['Frequency'].split(',')]

            
        else: 
            return 0 
        
    
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


'''
Data acqusition and test sequence thread class
'''
class AcqAndTestThread(QtCore.QThread): 

    dampPoints = pyqtSignal(list)
    testResult = pyqtSignal(bool)
    updateProgressBar = pyqtSignal(int)

    def __init__(self, amp, sampleSizeAI, sampleRateAI, sampleSizeAO, sampleRateAO, frequency, damps, AOSetup, AISetup):
        super().__init__() 

        self.amplitude = amp
        self.sampleSizeAI = sampleSizeAI
        self.sampleRateAI = sampleRateAI

        #self.sampleSizeAO = sampleSizeAO
        self.sampleSizeAO = [1000] * 41 #Eozwiązanie tymczasowe 
        self.sampleRateAO = sampleRateAO

        self.freq = frequency
        self.damps = damps

        self.AOSetup = AOSetup
        self.AISetup = AISetup

        self.progressVal = 0 

        self.q = queue.Queue()
        self.qAmps = queue.Queue()

        self.yVals = list() 
        self.peaksVals = list()

        self.dampTest = VerifyModule(damps)

        self.signalGen = SignalWriter(amp, sampleSizeAI, self.AOSetup) #Sample generowane 200
        self.signalRead = SignalReader(self.AISetup) #Zmieniony został atrybut sampleSize na dynamiczny

  
    def run(self): 

        for f, sr, sSize in zip (self.freq, self.sampleRateAI, self.sampleSizeAO): 

            self.signalGen.createTask(f, sr)
               
            self.signalRead.create_task(sr,sSize)

            self.signalGen.endGen()

            '''
            Poprawna akwizycja i obliczanie amplitud syg. dla 
            danej częstotliwości

            '''
            np_fft = np.fft.fft(self.signalRead.dataContainer[100:])
            amplitudes = (np.abs(np_fft) / sSize) 
            aPlot = 2 * amplitudes[0:int(sSize/2 + 1)]
        
            peak = find_peaks(aPlot, height=0)
            heights = peak[1]['peak_heights']
            maxVals = list(map(float, heights))


            curAmp = np.amax(maxVals)
            self.qAmps.put(curAmp)

        
        '''
        Kolejkowanie otrzymanych wartości amplitud
        '''
        while not self.qAmps.empty(): 

            self.peaksVals.append(self.qAmps.get())

        results = queue.Queue()   
        for a in self.peaksVals: 
            v = 20*(np.log10(a))
            results.put(v)

        self.finalList = list()
        while not results.empty():
            self.finalList.append(results.get())

        #Wywołanie funkcji sprawdzającej porawność testu dla danego filtra
        self.resDamp = self.dampTest.verFun(self.finalList,self.freq)

        self.dampPoints.emit(self.finalList)
        self.testResult.emit(self.resDamp)
        self.updateProgressBar.emit(self.progressVal)

        self.progressVal = self.progressVal + 1 


if __name__ == "__main__": 

    app = QApplication(sys.argv)
    mainWidndow = MainWindow()
  

    mainWidndow.setFixedWidth(1300)
    mainWidndow.setFixedHeight(900)
    mainWidndow.show()

    sys.exit(app.exec_())




