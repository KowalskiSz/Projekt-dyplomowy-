import csv
from datetime import datetime


'''
Klasa generująca plik csv, który zawiera 
dwa pola danych 
'''
class CSVwriter:
    '''
    Konstrukotr klasy przyjmującu częstotliowość ora tłumienie 
    jako wyniki testu 
    '''
    def __init__(self, frequency, damping):

        '''
        Wywałnie klasy datetime celem 
        pozyskania aktulanego czasu i daty 
        do wykorzystania jak nazwa pliku
        '''
        self._dateNow = datetime.now()


        '''
        Zmienne przechoujące częstotliwość
        oraz tłumienie
        '''
        self._frequency = frequency
        self._damping = damping


    '''
    metoda tworząca plik, na podstawie przekazanych 
    danych 
    '''
    def createFile(self):

        '''
        Zdefiniwanie nagłówków kolumn 
        '''
        self._fieldNames = ["frequency", "damping"]
        self._dateNow = self._dateNow.strftime("%d_%b_%Y_%H_%M_%S")

        with open(f'CSV/CSVFile{self._dateNow}.csv', 'w', newline='') as csvFile:

            '''
            Metoda zapisu w oparciu o instancję 
            obiektu klasy DuctWriter
            '''
            self._csvWrite = csv.DictWriter(csvFile, fieldnames=self._fieldNames)
            self._csvWrite.writeheader()


            '''
            pętla wpisująca dane do pliku jako 
            para key value
            '''
            for i in range(len(self._frequency)):
                self._csvWrite.writerow({"frequency" : self._frequency[i], "damping" : self._damping[i]})

            