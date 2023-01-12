'''
Importy klas bibliotek gównych 
obsłógi kamer orazdekodowania
'''
import cv2 
from pyzbar.pyzbar import decode
import numpy as np 
import json
'''
Importy klasy biblioteko Qt
'''
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

'''
Klasa odpowiedzialna za obsługę kamery oraz
dekodowanie kodu QR
dziedziczy po klasie QThread aby możliwe było 
zrealizowanie działania klasy w osobnym wątku 
QThread to klasa biblioteki PyQt5 posiadająca
metody obsługi wątków 
'''
class QRThread(QThread): 
    
    '''
    zmienne typu pyqtSignal umożliwiają emitowanie
    danych z wątku do aplikacji głównej 
    '''
    ImageUpdate = pyqtSignal(QImage)
    finishedTask = pyqtSignal()
    
    '''
    Konstruktor klasy
    '''
    def __init__(self):
        super().__init__()

        self.flag = False
        self.outputArray = None
        
    '''
    Przciążona metoda run klasy QThread 
    realizująca obsługę głównych funkcjonalności 
    wątku 
    '''
    def run(self): 

        '''
        zdefiniowanie flag określających 
        wykonanie czynności 
        '''
        self.data = None
        self.dataList = list()
        self.triggerThread = False
        self.flag = False

        print("initialozation")
        self.cap = cv2.VideoCapture(0)

        #cap.set(3,250)
        #cap.set(4,250)

        '''
        Pętla główna obsługująca działanie 
        kamery 
        '''
        self.triggerThread = True
        while self.triggerThread == True:

            '''
            Zczytytwanie danych z kamery
            '''
            succes, frame = self.cap.read()
            if succes == True:
                for code in decode(frame):
                
                    '''
                    metoda klasy pyzbar dekodująca
                    zawartość kodu QR
                    '''
                    self.data = code.data.decode('utf-8')
                    self.dataList.append(self.data)

                    '''
                    Nakładanie obramowania na odczytany QR
                    '''
                    pts = np.array([code.polygon], np.int32)
                    pts = pts.reshape((-1,1,2))
                    cv2.polylines(frame,[pts],True,(255,0,230),3)

                    '''
                    Opuszczanie pętli - zabezpiecznie 
                    przed zczytaniem więcej niż jednego kodu QR
                    '''
                   
                    if len(self.dataList) >= 1:
                        #print("Im here")
                        self.flag = True
                        break
                
                '''
                Konwersja obrazu odczytywanego z kamery na taki 
                aby możliwe było jego wyświetlenie na panelu czołowym
                '''
                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
                FlippedImage = cv2.flip(Image,1)

                convertToQt = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
                pic = convertToQt.scaled(290, 290, Qt.KeepAspectRatio)
                '''
                emitowanie gotowego obrazu na front
                '''
                self.ImageUpdate.emit(pic)

                if len(self.dataList) >= 1:
                    self.flag == True
                    break
        
        '''
        Zwalnianie zasobów kamery 
        '''
        self.triggerThread = False
        self.cap.release() #Relases camera
        self.quit()

    '''
    Metoda wykorzystująca plik Json zawierający pary 
    ID nazwa pliku z ogrnaiczeniami, aby zweryfikować poprawność 
    odczytanego i zdekodowanego kodu QR
    '''
    def resutCheck(self, dataVal):

        self.flagDoneAqq = False
        self.fileName = None
        

        with open('FiltersData.json') as filter: 
            
            filterData = json.load(filter)
            
            for f in filterData['filter']:
                
                if f['QRnumCode'] == dataVal: 

                    self.flagDoneAqq = True
                    self.fileName = f['fileName']
                    
                else: 
                    continue
                    
            '''
            Mechannizm za pomocą którego w przypadku 
            niezgodności kodu z danymi w bazie
            na panelu wyśitlany jest bład akwizycji kodu 
            '''
            if self.fileName == None: 
                self.fileName = 0
    
    '''
    metoda wywoływana w przypadku pozytywnego odczytania zawartości 
    kodu QR otwierjąca plik tesktowy z ograniczeniami 
    i zwracająca jego zawartość jako wektor
    '''
    def openDBFiles(self, fName): 

        if self.flagDoneAqq == True:

            '''
            Otwarcie pliku na podstawie sekwencji ID
            z kodu QR
            '''
            with open(f'Files/{fName}', 'r') as file: 
                
                lines = file.read().splitlines()
                #lines = file.readlines()
            
            file.close()

            '''
            Konwersja odczytanych danych z pliku na nparray tak jak wymaga tego 
            klasa verfiyModule 
            '''
            listOfElements = list()
            for line in lines: 
                
                listOfElements.append(line.split())
            
            self.outputArray = np.asarray(listOfElements, dtype=float)
            
        
            return self.outputArray 

        else: 
            print("Unable to open the file")
    

    



                