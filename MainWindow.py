import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizeGrip, QMessageBox, QWidget
from PyQt5.QtCore import QCoreApplication


import nidaqmx
import nidaqmx.system
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
from ExcelWriter import * 
from CSVWriter import * 

from numpy import random

'''
Klasa głowna aplikacji, 
w niej zawarte są wszystkie funkcjonalności programu 
sama klasa dziedziczy po QMainWindow celem możliwości korzystania 
z jej atrybutów
'''
class MainWindow(QMainWindow): 
    
    '''
    Konstruktor klasy - odpowada za inicjlaizacje całego okna 
    oraz wszytskich jego elementów, jak i funkcji z nimi powiązanych, które
    umorzliwają ich działanie 
    '''
    def __init__(self): 
        super(MainWindow,self).__init__()
        '''
        Załadowanie graficznej częsci frontu, zaprojetowanej 
        w designerze i zapisaej jako plik .ui 
        '''
        loadUi("FrontPanel.ui",self)
        
        self.setWindowTitle("Filter Tester")

        '''
        Sekcja inicjalizująca plot widget na froncie 
        jako obiekt klasy FigureCanvas z biblioteki 
        Matplotlib
        '''

        self.horizantalLayout = QHBoxLayout(self.plotFrame)
        self.horizantalLayout.setObjectName('horizantalLayout')


        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        self.horizantalLayout.addWidget(self.canvas)

        '''
        Algorytm komunikacji aplikacji z NI MAX
        Celem pozyskania informacji o zainstalowanych 
        urządzeniach pomiarowych 
        '''

        system = nidaqmx.system.System.local()
        self.devices = list()

        for device in system.devices:
    
            print(device.name)
            self.devices.append(device.name)

        self.comboBoxDevNames.clear()       # delete all items from comboBox
        self.comboBoxDevNames.addItems(self.devices)



        '''
        Inicjalizacja tabeli z informacjami o
        załadownym filtrze
        '''
        self.filterTab.setColumnWidth(0,80)
        self.filterTab.setColumnWidth(1,150)
        self.filterTab.setColumnWidth(2,150)

        self.filterTab.setLineWidth(20)

        '''
        Inicjalizacja tabeli tłumień i częstotliwości 
        '''
        self.dampsTable.setColumnWidth(0,120)
        self.dampsTable.setColumnWidth(1,120)
        self.dampsTable.setLineWidth(20)

        '''
        Funkcje wyszarzania przycisków przy starcie aplikacji 
        '''
        self.testStartButton.setEnabled(False)
        self.submitFilterButton.setEnabled(False)
        self.qrAcqButton.setEnabled(False)
        self.createtdmsButton.setEnabled(False)
        self.abortScanButton.setEnabled(False)
        self.okTestButton.setEnabled(False)
        self.createXlsxFile.setEnabled(False)
        self.csvButton.setEnabled(False)

        '''
        Inicjalizacja zmiennych wykorzystwanych w pomiarach
        oraz tescie
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
        Pozyskiwanie danych list rozwijanych 
        przy inicjalizacji sprzętu DAQ
        '''
        self.comboSetUpAI = None
        self.comboSetUpAO = None 

        self.DAQsetButton.clicked.connect(self.daqSet)
        self.cancelSetupButton.clicked.connect(self.cancelSetup)

        '''
        Zmienne przechowujące wartości graniczne oraz
        tłumienie 
        '''

        self.filterBoundries = None
        self.dampPoints = None

        '''
        Slot przycisku OK
        '''
        self.okTestButton.clicked.connect(self.okButtonFun)

        '''
        Slot przycisku TDMS
        '''

        self.createtdmsButton.clicked.connect(self.createtdmsFile)

        '''
       Slot przycisku Excel FIle
        '''
        self.createXlsxFile.clicked.connect(self.createExcelFile)

        '''
        slot przycisku CSV
        '''
        self.csvButton.clicked.connect(self.createCsvFile)

        '''
        inicjalizacja paska stau testu
        '''
        
        self.progressBar.reset()
        self.progressBar.hide()


        # self.testButton.clicked.connect(self.testfun)

       
        '''
        Sekcja obsługi QR kodu
        '''
        self.abortFlag = False #Flag to prevent the abort qr read error
       
        self.qrAcqButton.clicked.connect(self.QRFun)
        self.abortScanButton.clicked.connect(self.abortFun)
        
       
        '''
        Sekcja wyboru filtra przez listę rozwijaną 
        '''
        self.selectedFilterNumber = None
        self.selectedFilterDic = None

        self.submitFilterButton.clicked.connect(self.submitSelectedFilter)
        self.submitFilterButton.clicked.connect(self.popUpMessage)
        
        self.submitFilterButton.clicked.connect(lambda: self.dataBaseConnection(self.selectedFilterNumber))

        '''
        Slot przycisku startu testu
        '''

        self.testStartButton.clicked.connect(self.acquireTest)


        '''
        Slot przyscisku zamykającego aplkacje 
        '''
        self.exitButton.clicked.connect(self.closeAppFun)

    
    '''
    metoda obsługująca działanie wątku akwizycji testu
    '''
    def acquireTest(self): 

        self.testStartButton.setEnabled(False)
        self.progressBar.show()

        self.acqAndTestThread = AcqAndTestThread(1, self.AISampleSize, self.AIsampleRate, 
        self.AOsampleSize, self.AOsampleRate, self.frequency, self.filterBoundries, self.comboSetUpAO, self.comboSetUpAI)
        self.progressBar.setRange(0, len(self.frequency))

        self.acqAndTestThread.start()

        self.acqAndTestThread.dampPoints.connect(self.updatePlot)
        self.acqAndTestThread.finished.connect(self.testResult)
        self.acqAndTestThread.updateProgressBar.connect(self.updateProressBar)
        self.acqAndTestThread.finished.connect(self.popUpMessageTest)

    '''
    Metoda weryfikacji poprawności testu
    '''
    def testResult(self): 

        self.verObj = VerifyModule(self.filterBoundries)
        testResult, outList = self.verObj.verFun(self.dampPoints, self.frequency)
        self.okTestButton.setEnabled(True)
        
        
        self.dampsTable.setRowCount(len(outList))
        self.dampsTable.setColumnCount(2)
        self.createtdmsButton.setEnabled(True)
        self.createXlsxFile.setEnabled(True)
        self.csvButton.setEnabled(True)


        for i in range(len(outList)): 
            
            dV = str(outList[i][0])
            fV = str(outList[i][1])
            self.dampsTable.setItem(i,0, QTableWidgetItem(dV))
            self.dampsTable.setItem(i,1, QTableWidgetItem(fV))
            #print(outList[i][0])
            

        if testResult == True: 
            self.testResultLabel.setText("Test Passed")
            self.testOutput = "Passed"
        else: 
            self.testResultLabel.setText("Test Failed")
            self.testOutput = "Failed"

    '''
    Metoda obsługująca wyświetlanie wykresu 
    '''
    def updatePlot(self, vals): 
        
        self.figure.clear()
        self.dampPoints = vals
        plt.plot(self.frequency, vals, label="Damping plot" )
        plt.plot(self.filterBoundries[:,0], self.filterBoundries[:,1], '--', label="High limit")
        plt.plot(self.filterBoundries[:,0], self.filterBoundries[:,2], '--', label="Low limit")
        #plt.axvline(x = , color = 'b', label = 'cutoff')
        
        plt.xscale('log')
        #plt.set_facecolor('#EBEBEB')
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
        
    '''
    Metoda czyszcząca pamięć oraz resetująca 
    do ustawień początkowych 
    '''
    def okButtonFun(self): 
        
        self.figure.clear()
        self.canvas.draw()

        self.testResultLabel.clear()
        self.progressBar.reset()

        self.filterTab.clearContents()
        self.dampsTable.clearContents()
        

        self.AIsampleRate= None
        self.AOsampleRate = None

        self.AIsampleSize = None
        self.AIsampleSize = None

        self.frequency = None
        self.finalDamps = None

        self.testOutput = None

        self.comboSetUpAI = None
        self.comboSetUpAO = None 

        self.abortFlag = False

        self.finalDamps = None


        self.selectedFilterNumber = None
        self.selectedFilterDic = None

        self.testStartButton.setEnabled(False)
        self.submitFilterButton.setEnabled(False)
        self.qrAcqButton.setEnabled(False)
        self.createtdmsButton.setEnabled(False)
        self.abortScanButton.setEnabled(False)
        self.okTestButton.setEnabled(False)
        self.createXlsxFile.setEnabled(False)
        self.csvButton.setEnabled(False)

        self.DAQsetButton.setEnabled(True)
        self.progressBar.hide()

        



   
    '''
    meotoda aktulalizacji paska postępu
    '''

    def updateProressBar(self, val): 
        
        self.progressBar.setValue(val)

    


    '''
    Metoda obsługująca wybór DAQ oraz wejść i wyjść
    '''
    def daqSet(self):

        self.deviceName = self.comboBoxDevNames.currentText()
        self.comboSetUpI = self.comboBoxAI.currentText()
        self.comboSetUpO = self.comboBoxAO.currentText()

        self.comboSetUpAI = f"{self.deviceName}/{self.comboSetUpI}"
        self.comboSetUpAO = f"{self.deviceName}/{self.comboSetUpO}"

        print(self.comboSetUpAI)
        print(self.comboSetUpAO)

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
    Sekcja metody obsługującej działanie 
    skanera QR
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

    '''
    Metoda obsługująca wyświetlanie rejstrowanego 
    obrazu przez kamerę na froncie
    '''
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
                self.popUpQRMessage("that does not exist")
                   

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

    '''
    Metoda przerwania akwizycji wizji 
    '''
    def abortFun(self): 

        self.abortFlag = True
        self.QRThread.terminate()

        self.QRThread.cap.release()
        self.camQR.clear()

    '''
    Wybór filtra jako elementu listy rozwijanej 
    '''

    def submitSelectedFilter(self): 
        
        self.selectedFilterNumber = self.filterFindCombobox.currentText()
        openJson = OpenJsonFilter()

        self.filterBoundries = openJson.openJson(self.selectedFilterNumber) #getting vals from json file - boundries
        
        

        
    '''
    Metoda obsługi bazy danych  
    '''
    def dataBaseConnection(self, filterNumber): 

        if not self.abortFlag: #saves from not executing qr read by aborting the process
            self._dataBaseInst = DatabaseReader(filterNumber)
            self._dataBaseInst.exeFun()

            '''
            Inicjalizacja zmiennej typy dict, która przechowuje informacja
            pobrane w bazy danych, które wykorzystywane są w programie
            '''
            self.selectedFilterDic = self._dataBaseInst.dataDic

            self.filterTab.setItem(0, 0, QTableWidgetItem(self._dataBaseInst.dataDic["FilterID"]))
            self.filterTab.setItem(0, 1, QTableWidgetItem(self._dataBaseInst.dataDic["Type"]))
            self.filterTab.setItem(0, 2, QTableWidgetItem(self._dataBaseInst.dataDic["DampInfo"]))
            self.testStartButton.setEnabled(True)

            '''
            Konwersja danych z bazy z tyou string na odpowienie typy urzytskowe
            '''
            self.AIsampleRate = [int(i) for i in self.selectedFilterDic['AISampleRate'].split(',')]
            self.AISampleSize = int(self.selectedFilterDic['AISampleSize'])

            self.AOsampleRate = [int(i) for i in self.selectedFilterDic['AOSampleRate'].split(',')]
            #self.AOsampleSize = int(self.selectedFilterDic['AOSampleSize'])
            self.AOsampleSize = [int(i) for i in self.selectedFilterDic['AOSampleSize'].split(',')]

            self.frequency = [float(i) for i in self.selectedFilterDic['Frequency'].split(',')]

            
        else: 
            return 0 
        
    '''
    Popup zwracający na frontpanel informacje o aktulanie wybranym filtrze
    '''
    def popUpMessage(self): 
        
        #QtWidgets.QMessageBox.information(self, "Done", "Acqusition completed") 
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        
        msg.setWindowTitle("Filter Chosen")
        msg.setText(f"You have chosen filter number: {self.selectedFilterNumber}")
        
        msg.setStandardButtons(QMessageBox.Ok)

        msg.exec_()


    '''
    Metoda generujaca plik tdms po 
    instancji obiektu klasy Tdmscreator 
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
    Metoda generujaca plik xlsx po 
    instancji bietu klasy ExcelWriter 
    '''
    def createExcelFile(self): 

        self._xlsxwriterObj = ExcelWriter(self.frequency, self.finalDamps, self.selectedFilterDic["FilterID"], self.selectedFilterDic["Type"], 
        self.selectedFilterDic["DampInfo"], self.testOutput, self.filterBoundries[:,0], self.filterBoundries[:,1], self.filterBoundries[:,2])

        self._xlsxwriterObj.createFile()

        msex = QMessageBox()
        msex.setIcon(QMessageBox.Information)
        
        msex.setWindowTitle("Excel file generated")
        msex.setText(f"You Excel file has been generated!")
        
        msex.setStandardButtons(QMessageBox.Ok)

        msex.exec_()


    '''
    Metoda generujaca plik csv po 
    instancji bietu klasy CSVwriter 
    '''
    def createCsvFile(self):

        self._csvwriterobj = CSVwriter(self.frequency, self.finalDamps)
        self._csvwriterobj.createFile()

        msexcsv = QMessageBox()
        msexcsv.setIcon(QMessageBox.Information)
        
        msexcsv.setWindowTitle("CSV file generated")
        msexcsv.setText(f"You CSV file has been generated!")
        
        msexcsv.setStandardButtons(QMessageBox.Ok)

        msexcsv.exec_()




    '''
    metoda obsługująca event zamknięcia aplikacji poprzez "X"
    '''
    def closeAppFun(self): 
        QCoreApplication.instance().quit()

    '''
    Definicja eventu
    '''
    def closeEvent(self, event): 
        reply = QMessageBox.question(self, 'Window Close', 'Do you really want to exit?', 
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes: 
            event.accept()
        else: 
            event.ignore()


'''
Klasa obsługująca wątek odpowiedzialny za akwizycję i generacje
sygnału testującego
'''
class AcqAndTestThread(QtCore.QThread): 

    '''
    Zdefiniwanie zmiennych pyqtSignal pozwalających 
    na wysyłanie danch z wątku do klasy Main
    '''
    dampPoints = pyqtSignal(list)
    testResult = pyqtSignal(bool)
    updateProgressBar = pyqtSignal(int)

    '''
    Konstruktor klasy przyjmujący dane 
    definiujące sposób genracji i akwizycji 
    Dane pobierane są z bazy danych  
    '''
    def __init__(self, amp, sampleSizeAI, sampleRateAI, sampleSizeAO, sampleRateAO, frequency, damps, AOSetup, AISetup):
        super().__init__() 
        


        self.amplitude = amp
        self.sampleSizeAI = sampleSizeAI
        self.sampleRateAI = sampleRateAI

        self.sampleSizeAO = sampleSizeAO
       
        self.sampleRateAO = sampleRateAO

        self.freq = frequency
        self.damps = damps

        self.AOSetup = AOSetup
        self.AISetup = AISetup

        self.progressVal = 0 

        '''
        Inicjalizacja kolejek FIFO na dane wyjściowe
        '''
        self.q = queue.Queue()
        self.qAmps = queue.Queue()
        

        self.yVals = list() 
        self.peaksVals = list()

        '''
        Tworzenie obiektów instancji klas generacji i akwizycji sygnału  
        '''
        self.signalGen = SignalWriter(self.amplitude, sampleSizeAI, self.AOSetup) 
        self.signalRead = SignalReader(self.AISetup) 

    '''
    metoda wyliczająca tłumienie 
    sygnału na podstawie amplitudy
    '''
    def dampingCount(self, amps):
         
        for a in amps: 
            v = 20*(np.log10(a/1))
            self.results.put(v)

        return self.results

    '''
    przeciążenie metody run wątku
    sekwencja odbywa się jako kolejne iteracje pętli 
    do któej przekazywane są welkości niezbędne generacji i odczytowi 
    częstotliowść, częst. próbkowania, wielkości buforów
    '''
    def run(self): 
        
        for f, sr, sSize in zip (self.freq, self.sampleRateAI, self.sampleSizeAO): 

            self.progressVal = self.progressVal + 1
            self.updateProgressBar.emit(self.progressVal)

            '''
            Sekwencja generacji i awizycji na metodach 
            klas Write i Read
            '''
            self.signalGen.createTask(f, sr)
               
            self.signalRead.create_task(sr,sSize)

            self.signalGen.endGen()

            '''
            Poprawna akwizycja i obliczanie amplitud syg. dla 
            danej częstotliwości
            Wykorzystano metode klasy scipy do FFT oraz 
            znajdowania wartości szczytowej danej części sygnału 

            '''
            np_fft = np.fft.fft(self.signalRead.dataContainer[200:]) #Wycięcie z otrzymanych wartości sygnału 200 pierwszyc próbek 
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


        self.results = queue.Queue()
        self.res = self.dampingCount(self.peaksVals)

       

        '''
        Zwracanie końcowej listy otrzymanych punktów 
        tłumienia sygnału po wszytkich iteracjach pętli głównej 
        '''
        self.finalList = []
        while not self.res.empty():
            
            self.finalList.append(self.res.get())

        self.dampPoints.emit(self.finalList)
        
'''
Wywołanie klasy Main
'''        
if __name__ == "__main__": 

    '''
    Stworzenie instancji klasy MainWindow 
    przy włączeniu sesji programu 
    '''
    app = QApplication(sys.argv)
    mainWidndow = MainWindow()
  
    mainWidndow.show()

    sys.exit(app.exec_())




