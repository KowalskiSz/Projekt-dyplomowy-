import cv2
#from numpy import empty, int32 
from pyzbar.pyzbar import decode
import numpy as np 
import json


class QRcodeReader():

    def scanCode(self):

        self.data = None
        self.dataList = list()
        self.trigger = False
        self.flag = False
        
        #Initialazing video capture and the frame settings
        print("initialozation")
        cap = cv2.VideoCapture(0)
        cap.set(3,640)
        cap.set(4,480) 

        self.trigger = True
        while self.trigger == True:

            succes, frame = cap.read()
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
                        break

                cv2.imshow('Test-cam', frame)
                key = cv2.waitKey(1)
 
                if len(self.dataList) >= 1:
                    self.flag == True
                    break
        
        print('Memory cleaning...')
        cap.release() #Relases camera
        cv2.destroyAllWindows() #Close the window

        #return self.data

    '''
    Tymczasowy sposób weryfikacji poprawności odczytanych danych
    Zaimplementuje chyba Json ze wszytskimi plikami filtrów 
    I będę szukać po nic
    '''
    def resutCheck(self, dataVal):

        self.flagDoneAqq = False
        self.fileName = None
        

        with open('FiltersData.json') as filter: 
            
            filterData = json.load(filter)
            
            for f in filterData['filter']:
                
                if f['QRnumCode'] == dataVal[5:]: #Rozwiązanie tymczasem - zła informacja na kodzie QR

                    self.flagDoneAqq = True
                   
                    self.fileName = f['fileName']
                    #print(fileName)
                    #return self.fileName
                else: 
                    continue

            if self.fileName == None: 
                print("Such filter does not exists")

        # if(type(dataVal) == str and len(dataVal) != 0 and '7777777777' in dataVal ): 
        #     #print(openFile())
        #     self.flagDoneAqq = True
        #     print("Dane poprawne, oczytane")

        # else: 
        #     print('Does not exists') 

    
    def openDBFiles(self, fName): 

        if self.flagDoneAqq == True:

            with open(f'Files/{fName}', 'r') as file: 
                lines = file.read().splitlines()
            file.close()
            return lines 

        else: 
            print("Unable to open the file")





# if __name__ == "__main__":

#     q = QRcodeReader()
#     q.scanCode()

#     q.resutCheck(q.data)
#     print(q.openDBFiles(q.fileName))







