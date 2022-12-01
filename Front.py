
from PyQt5 import QtCore, QtGui, QtWidgets
from pyqtgraph import PlotWidget
from PyQt5.QtCore import pyqtSlot
import sys

import queue
from scipy import signal
from scipy.signal import find_peaks

from ReaderDAQ import * 
from WriterDAQ import * 
from QRThread import * 

#import matplotlib.pyplot as plt


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1119, 849)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.graphicsView = PlotWidget(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(90, 290, 951, 461))
        self.graphicsView.setObjectName("graphicsView")

        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(90, 40, 351, 191))
        self.widget.setObjectName("widget")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.testAcqButton = QtWidgets.QPushButton(self.widget)
        self.testAcqButton.setObjectName("testAcqButton")
        self.testAcqButton.clicked.connect(self.button_Aqc)
        self.verticalLayout.addWidget(self.testAcqButton)

        self.otherFunButton = QtWidgets.QPushButton(self.widget)
        self.otherFunButton.setEnabled(True)
        self.otherFunButton.setObjectName("otherFunButton")
        self.otherFunButton.clicked.connect(self.QRFun)
        self.verticalLayout.addWidget(self.otherFunButton)

        self.widget1 = QtWidgets.QWidget(self.centralwidget)
        self.widget1.setGeometry(QtCore.QRect(570, 40, 461, 191))
        self.widget1.setObjectName("widget1")

        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget1)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.leabelNo1 = QtWidgets.QLabel(self.widget1)
        self.leabelNo1.setAutoFillBackground(True)
        self.leabelNo1.setObjectName("leabelNo1")

        self.verticalLayout_2.addWidget(self.leabelNo1)

        self.labelNo2 = QtWidgets.QLabel(self.widget1)
        self.labelNo2.setAutoFillBackground(True)
        self.labelNo2.setObjectName("labelNo2")

        self.verticalLayout_2.addWidget(self.labelNo2)
        MainWindow.setCentralWidget(self.centralwidget)
        
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    
    '''
    Sekcja QRCoda, tworzy wątek, zczytuje info z kamerki, 
    czyści kamerkę 

    '''
    
    def QRFun(self): 
        
        self.QRThread = QRThread()
        self.QRThread.start()

        self.labelNo2.clear()
        self.QRThread.ImageUpdate.connect(self.imageUpdateSlot)

        

    '''
    W funkcji następuje wywołanie funkcji dwóch funkcji: 
    -sprawdzenie rezutatu zczytania info z qrcodu 
    -zczytanie z pliku json info o danym filtrze oraz
    wyprintowanie info tymczasowo 
    '''
    def imageUpdateSlot(self, image): 
        self.leabelNo1.setPixmap(QPixmap.fromImage(image))

        if self.QRThread.flag == True: 
            #print("HERE")
            QTimer.singleShot(1000, self.clearLabel)

            self.QRThread.resutCheck(self.QRThread.data)
            print(self.QRThread.openDBFiles(self.QRThread.fileName))

            self.labelNo2.setText(self.QRThread.fileName)
         
    def clearLabel(self): 
        self.leabelNo1.clear()
    
    # def stopFeed(self): 
    #     print("Here one")
    #     if self.QRThread.flag == True:
    #         print("Here two")
    #         self.QRThread.stop()
            




    '''
    Sekcja Data Aqcusition
    
    '''
    def button_Aqc(self):

        self.testAcqButton.setEnabled(False)
        self.graphicsView.clear()

        self.acqWorker = acqThread()
        self.acqWorker.start()

        self.acqWorker.plotVals.connect(self.updatePlot)
        self.acqWorker.finished.connect(self.popUpMessage)
        #self.acqWorker.ampli.connect(self.testPlot)
        
    
    def updatePlot(self, vals):
        self.graphicsView.clear()
        self.graphicsView.plot(vals)  

    # def testPlot(self, amp):
    #     plt.plot(amp)
    #     plt.show()



    def popUpMessage(self): 
        self.testAcqButton.setEnabled(True)
        #QtWidgets.QMessageBox.information(self, "Done", "Acqusition completed") 
        msg = QMessageBox()
        msg.setWindowTitle("Acqusition")
        msg.setText("Acqusition done!")
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)

        x = msg.exec_()
        
    '''
    Tutaj jest kod dla samej akwizycji bez działania w osobnym wątku 
    '''
    # def button_Aqc(self):

    #     q = queue.Queue()
    #     '''
    #     Próba zrobienia koleji FIFO na wykres
    #     '''

    #     amplitude = 1
    #     sampleSize = 1000
    #     sampleRate = [400,800,1200]
    #     freq = [5,10,15]
    #     #tempBuff = np.empty(shape=(200,))

    #     self.testAcqButton.setEnabled(False)
        

    #     self.signalGen = SignalWriter(amplitude, sampleSize)
    #     self.signalRead = SignalReader(sampleSize)
        
    #     #Na test dwie/trzy częstotiwości, zmieniać trzeba również będzie sampple rate - działa ale read raczej do zrobienia w wątku
    #     for f, sr in zip (freq, sampleRate): 

    #         self.signalGen.createTask(f, sr)
    #         self.signalRead.create_task(sr)

    #         #np.append(tempBuff,self.signalRead.dataContainer)

    #         for val in self.signalRead.dataContainer: 
    #             q.put(val)

    #         self.signalGen.endGen()

    #     '''
    #     Próba wydobycia z kolejki wartości i przekazanie ich na wykres
    #     '''
    
    #     yVals = list() #Lista danych skolejkowanych FIFO
    #     while not q.empty():
        
    #         yVals.append(q.get())
    #         #print(q.get())
            
    #     print(len(yVals))
    #     print("Done Acquiring")
    
    #     #Wykres prosty
    #     self.graphicsView.clear()
    #     self.graphicsView.plot(yVals) 
     

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.testAcqButton.setText(_translate("MainWindow", "TEST Acquire"))
        self.otherFunButton.setText(_translate("MainWindow", "OtherFun"))
        self.leabelNo1.setText(_translate("MainWindow", "TextLabel"))
        self.labelNo2.setText(_translate("MainWindow", "TextLabel"))

'''
Klasa związania z akwizycją danych, napisana w osobnym wątku 
'''
class acqThread(QtCore.QThread): 
        
        plotVals = pyqtSignal(list) #Sygnał emitowany z wątku do funkcji z plotem
        ampli = pyqtSignal(list)

        ampPeaks = pyqtSignal(list) 
        

        def __init__(self):
            super().__init__() 

            '''
            To są ustawienia wprowadzone na sztywno, 
            będą one inicjowane z bazy danych 
            '''

            self.amplitude = 1
            self.sampleSize = 1000
            self.sampleRate = [400,400,800,1200,1600,2000,2400,2800,3200,3600,4000,4400,4800,5200,5600,6000,6400,6800,7200,7600,8000,8400,8800,9200,9600,10000,10400,16000,24000,32000,40000,48000,56000,62000,70000,78000,85000,100000]
            self.freq = [1,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,200,300,400,500,600,700,800,900,1000,10000,25000]


            '''
            Lista i kolejka do obsługi poprawnej danych wyjściowych 
            '''
            self.yVals = list() 
            self.peaksVals = list()

            self.q = queue.Queue()
            self.qAmps = queue.Queue()

        def run(self):

            self.signalGen = SignalWriter(self.amplitude, self.sampleSize)
            self.signalRead = SignalReader()
            

            for f, sr in zip (self.freq, self.sampleRate): 

                self.signalGen.createTask(f, sr)
               
                self.signalRead.create_task(sr,self.sampleSize)

                self.signalGen.endGen()

                #Oczyt amplitudy syganału
                np_fft = np.fft.fft(self.signalRead.dataContainer)
                #amplitudes = 2 / self.sampleSize * np.abs(np_fft)
                amplitudes = np.abs(np_fft) / self.sampleSize
                
                amplitudes=list(amplitudes)
                peak, _ = find_peaks(amplitudes, distance=1)
                print(peak)
                self.qAmps.put(np.amax(peak) / 1000)
                #print(np.amax(peak) / 1000)

                self.ampli.emit(amplitudes)
                
                for val in self.signalRead.dataContainer:

                    self.q.put(val)

                

            
            while not self.q.empty():

                self.yVals.append(self.q.get())

            while not self.qAmps.empty(): 
                self.peaksVals.append(self.qAmps.get())            
            
            #print(self.peaksVals)
            
            self.plotVals.emit(self.yVals)
            self.ampPeaks.emit(self.peaksVals)
            
            



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    MainWindow.show()
    sys.exit(app.exec_())


'''
-Zaczać baze danych
-Testy na real hardware
-Implementacja fft
'''
