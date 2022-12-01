import cv2
#from numpy import empty, int32 
from pyzbar.pyzbar import decode
import numpy as np 
import json

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class QRThread(QThread): 
    
    ImageUpdate = pyqtSignal(QImage)
    
    def __init__(self):
        super().__init__()

        self.flag = False
        self.arrayOfData = list()
    
    def run(self): 

        self.data = None
        self.dataList = list()
        self.triggerThread = False
        self.flag = False

        print("initialozation")
        self.cap = cv2.VideoCapture(0)

        #cap.set(3,250)
        #cap.set(4,250)

        self.triggerThread = True
        while self.triggerThread == True:

            succes, frame = self.cap.read()
            if succes == True:
                for code in decode(frame):
                #print(code.type)
            
                    self.data = code.data.decode('utf-8')
                    self.dataList.append(self.data)

                    '''
                     Putting borders around the barcode on the screen
                    '''
                    pts = np.array([code.polygon], np.int32)
                    pts = pts.reshape((-1,1,2))
                    cv2.polylines(frame,[pts],True,(255,0,230),3)

                    '''
                    Exiting the loop with only one data object
                    '''
                   
                    if len(self.dataList) >= 1:
                        #print("Im here")
                        self.flag = True
                        break

                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
                FlippedImage = cv2.flip(Image,1)

                convertToQt = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
                pic = convertToQt.scaled(290, 290, Qt.KeepAspectRatio)
                self.ImageUpdate.emit(pic)

                if len(self.dataList) >= 1:
                    self.flag == True
                    break

        self.triggerThread = False
        self.cap.release() #Relases camera
        self.quit()

    def resutCheck(self, dataVal):

        self.flagDoneAqq = False
        self.fileName = None
        

        with open('FiltersData.json') as filter: 
            
            filterData = json.load(filter)
            
            for f in filterData['filter']:
                
                if f['QRnumCode'] == dataVal: #Rozwiązanie tymczasem - zła informacja na kodzie QR

                    self.flagDoneAqq = True
                   
                    self.fileName = f['fileName']
                    #print(fileName)
                    #return self.fileName
                else: 
                    continue

            if self.fileName == None: 
                print("Such filter does not exists")
    '''
    Tymczasowa funkcja przetwarzająca zczytany wynik 
    z kodu QR
    '''
    def openDBFiles(self, fName): 

        if self.flagDoneAqq == True:

            with open(f'Files/{fName}', 'r') as file: 
                
                lines = file.read().splitlines()
                #lines = file.readlines()
            
            file.close()

            '''
            Konwersja listy na liste list trzy elementowych 
            przeksztacić to w array 
            raczej zmianne klasy 
            '''
            listOfElements = list()
            for line in lines: 
                
                listOfElements.append(line.split())
            

            return listOfElements 

        else: 
            print("Unable to open the file")
    
    # def stop(self): 
    #     if len(self.dataList) >= 1:
    #         self.triggerThread = False
    #         self.cap.release() #Relases camera
    #         cv2.destroyAllWindows()
    #         self.quit()
    # def stop(self): 
         
    #      self.triggerThread = False
    #      self.quit()
    



                