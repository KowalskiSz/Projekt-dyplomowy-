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
from Tdmscreator import * 


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
        self.filterTab.setColumnWidth(2,150)

        self.filterTab.setLineWidth(20)

        '''
        Damps and frequency table
        '''
        self.dampsTable.setColumnWidth(0,120)
        self.dampsTable.setColumnWidth(1,120)
        self.dampsTable.setLineWidth(20)

        '''
        Prevnting from starting testing with no data
        '''
        self.testStartButton.setEnabled(False)
        self.submitFilterButton.setEnabled(False)
        self.qrAcqButton.setEnabled(False)
        self.createtdmsButton.setEnabled(False)
        self.abortScanButton.setEnabled(False)

        '''
        Initialaize test values
        '''
        self.AIsampleRate= None
        self.AOsampleRate = None

        self.AIsampleSize = None
        self.AIsampleSize = None

        self.frequency = None
        self.finalDamps = None

        #Test variable used for tdms write
        self.testOutput = None

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
        self.dampPoints = None

        '''
        Ok button
        '''
        self.okTestButton.clicked.connect(self.okButtonFun)

        '''
        Generating tdms file button
        '''

        self.createtdmsButton.clicked.connect(self.createtdmsFile)

        '''
        progress bar initialization
        '''
        
        self.progressBar.reset()

       
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
        self.progressBar.setRange(0, len(self.frequency))

        self.acqAndTestThread.start()

        self.acqAndTestThread.dampPoints.connect(self.updatePlot)
        self.acqAndTestThread.finished.connect(self.testResult)
        self.acqAndTestThread.updateProgressBar.connect(self.updateProressBar)
        self.acqAndTestThread.finished.connect(self.popUpMessageTest)

    def testResult(self): 

        self.verObj = VerifyModule(self.filterBoundries)
        testResult, outList = self.verObj.verFun(self.dampPoints, self.frequency)
        
        
        self.dampsTable.setRowCount(len(outList))
        self.dampsTable.setColumnCount(2)


        for i in range(len(outList)): 
            
            dV = str(outList[i][0])
            fV = str(outList[i][1])
            self.dampsTable.setItem(i,0, QTableWidgetItem(dV))
            self.dampsTable.setItem(i,1, QTableWidgetItem(fV))
            #print(outList[i][0])
            

        if testResult == True: 
            self.testResultLabel.setText("Test Passed")
        else: 
            self.testResultLabel.setText("Test Failed")

    def updatePlot(self, vals): 
        
        #self.figure.clear()
        self.dampPoints = vals
        plt.plot(self.frequency, vals, label="Damping plot" )
        plt.plot(self.filterBoundries[:,0], self.filterBoundries[:,1], '--', label="High limit")
        plt.plot(self.filterBoundries[:,0], self.filterBoundries[:,2], '--', label="Low limit")
        #plt.axvline(x = , color = 'b', label = 'cutoff')
        
        plt.xscale('log')
        plt.set_facecolor('#EBEBEB')
        plt.grid(color="red", linewidth=0.7)
        plt.legend()
        self.canvas.draw()

        '''
        Updating final damps values
        '''
        self.finalDamps = vals

    def popUpMessageTest(self):
        msg = QMessageBox()
        msg.setWindowTitle("Testing complited!")
        msg.setText("Testing done!")
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)

        x = msg.exec_()
        

    def okButtonFun(self): 

        plt.plot([0],[0])
        self.canvas.draw()
        
        self.testResultLabel.clear()
        self.createtdmsButton.setEnabled(True)
        self.progressBar.reset()

        self.dampsTable.clear()
        

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
        self.abortScanButton.setEnabled(True)


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
        #self.QRThread.finished.connect(self.popUpQRMessage)
        #self.QRThread.finished.connect(lambda: self.dataBaseConnection(self.QRThread.data))

    def imageUpdateSlot(self, image): 

        self.camQR.setPixmap(QPixmap.fromImage(image))

        if self.QRThread.flag == True: 
            
            QTimer.singleShot(1000, self.clearLabel)
            self.QRThread.resutCheck(self.QRThread.data)

            if self.QRThread.fileName != 0:
                
                self.dataBaseConnection(self.QRThread.data)
                self.filterBoundries = self.QRThread.openDBFiles(self.QRThread.fileName)
                self.popUpQRMessage(self.QRThread.data)
            else:

                self.abortFlag == True
                self.popUpQRMessage("No in data base")
                   

            #self.resQRLabel.setText(self.QRThread.fileName)
    
    def popUpQRMessage(self, number): 
        
        #QtWidgets.QMessageBox.information(self, "Done", "Acqusition completed") 
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        
        msg.setWindowTitle("Filter Chosen")
        msg.setText(f"You have chosen filter number: {number}")
        
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
            #self.AOsampleSize = int(self.selectedFilterDic['AOSampleSize'])
            self.AOsampleSize = [int(i) for i in self.selectedFilterDic['AOSampleSize'].split(',')]

            self.frequency = [float(i) for i in self.selectedFilterDic['Frequency'].split(',')]

            
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
    Creating tdms file section 
    '''
        
    def createtdmsFile(self): 

        self._tdmsCreatorObject = Tdmscreator(self.frequency, self.finalDamps, self.selectedFilterDic["FilterID"], self.selectedFilterDic["Type"], 
        self.selectedFilterDic["DampInfo"], self.testOutput, self.filterBoundries[:,0], self.filterBoundries[:,1], self.filterBoundries[:,2])

        self._tdmsCreatorObject.createFile()

        msgg = QMessageBox()
        msgg.setIcon(QMessageBox.Information)
        
        msgg.setWindowTitle("File generated")
        msgg.setText(f"You file has been generated!")
        
        msgg.setStandardButtons(QMessageBox.Ok)

        msgg.exec_()




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

        self.sampleSizeAO = sampleSizeAO
        #self.sampleSizeAO = [1000] * 42 #Eozwiązanie tymczasowe 
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

        
        self.signalGen = SignalWriter(self.amplitude, sampleSizeAI, self.AOSetup) #Sample generowane 200
        self.signalRead = SignalReader(self.AISetup) #Zmieniony został atrybut sampleSize na dynamiczny

    
    def dampingCount(self, amps):
         
        for a in amps: 
            v = 20*(np.log10(a))
            self.results.put(v)

        return self.results

    def run(self): 
        
        for f, sr, sSize in zip (self.freq, self.sampleRateAI, self.sampleSizeAO): 

            self.progressVal = self.progressVal + 1
            self.updateProgressBar.emit(self.progressVal)

            self.signalGen.createTask(f, sr)
               
            self.signalRead.create_task(sr,sSize)

            self.signalGen.endGen()

            
            

            '''
            Poprawna akwizycja i obliczanie amplitud syg. dla 
            danej częstotliwości

            '''
            np_fft = np.fft.fft(self.signalRead.dataContainer[200:])
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

        # results = queue.Queue()   
        # for a in self.peaksVals: 
        #     v = 20*(np.log10(a))
        #     results.put(v)
        self.results = queue.Queue()
        self.res = self.dampingCount(self.peaksVals)

       

        self.finalList = []
        while not self.res.empty():
            
            self.finalList.append(self.res.get())

        self.dampPoints.emit(self.finalList)
        
        


if __name__ == "__main__": 

    app = QApplication(sys.argv)
    mainWidndow = MainWindow()
  

    #mainWidndow.setFixedWidth(1565)
    #mainWidndow.setFixedHeight(900)
    mainWidndow.show()

    sys.exit(app.exec_())




