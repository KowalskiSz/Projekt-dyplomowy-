import xlsxwriter
from datetime import datetime

'''
Klasa generująca plik xlsx, na podsatwie metod biblioteki 
xlsxwriter
'''
class ExcelWriter:

    '''
    Konstruktor przyjmujący wymagane do zapisu w plik 
    dane 
    '''
    def __init__(self,frequency, damping, filterID, filterType, coffFreq, testResult, frequencyDamp, dampsHigh,
                 dampsLow):
        
        '''
        Wydobycie aktualnej dokładej daty 
        '''
        self._dateNow = datetime.now()

        '''
        Zdefiniwanie zmiennych na 
        częstotliowść oraz tłumienie otrzymane z testu
        '''
        self._frequency = frequency
        self._damping = damping

        '''
        Zmienne na dane z pliku
        z ograniczeniami filtra
        '''
        self._frequencyDamp = frequencyDamp
        self._dampsHigh = dampsHigh
        self._dampsLow = dampsLow

        '''
        Zmienne na informacje o badanym 
        filtrze oraz wyniku testu 
        '''
        self._testResult = testResult
        self._filterID = filterID
        self._filterType = filterType
        self._coffFreq = coffFreq

        self.indexOfData = None
        self.indexB = None

    '''
    metoda określająca generacje wszystkich wymaganych 
    struktur orazgenerująca główny plik 
    '''
    def createFile(self):

        '''
        konwersja danych daty na string
        '''
        self._dateNow = self._dateNow.strftime("%d_%b_%Y_%H_%M_%S")

        '''
        Stworzenie objektu definiującego cały workbook 
        '''
        self.workbook = xlsxwriter.Workbook(f"Excel/Excelfile{self._dateNow}.xlsx")

        '''
        zdefiniwanie w workbooku wszytskich worksheetów - 
        zakładek
        '''
        self.worksheet = self.workbook.add_worksheet("Overall Info")
        self.datasheet = self.workbook.add_worksheet("Main Data")
        self.plotSheet = self.workbook.add_worksheet("Plot")

        '''
        Zdefiniwanie formatowania pliku (tabele, pogrubienia itd.)
        '''
        self.f1 = self.workbook.add_format({'border': 2, 'border_color': 'green', 'bold': 'True', 'align': 'center'})
        self.f2 = self.workbook.add_format({'border': 2, 'border_color': 'red', 'bold': 'True', 'align': 'center'})

        self.bold = self.workbook.add_format({'bold': True})

        self.center = self.workbook.add_format()
        self.center.set_align('center')

        '''
        Dane dla pierwszego worksheetu 
        
        '''
        self.worksheet.write('A2', "Filter ID", self.bold)
        self.worksheet.write('B2', self._filterID,self.f2)

        self.worksheet.write('A4', "Filter Type", self.bold)
        self.worksheet.write('B4', self._filterType,self.f2)

        self.worksheet.write('A6', "Cutoff Frequency", self.bold)
        self.worksheet.write('B6', self._coffFreq,self.f2)

        self.worksheet.write('A8', "Test result", self.bold)
        self.worksheet.write('B8', self._testResult,self.f2)

        self.worksheet.set_column(0,0,15)
        self.worksheet.set_column(0,1,20)

        '''
        Wpisywanie danych głwnych dotyczących 
        filtra do pliku
        '''

        self.datasheet.write('A1', "Frequency [Hz]", self.f2)
        self.datasheet.write('B1', "Damping [dB]",self.f2)

        self.datasheet.write("D1", "Frequency of boundries [Hz]", self.f2)
        self.datasheet.write("E1", "Low boundries [dB]", self.f2)
        self.datasheet.write("F1", "High boundries [dB]", self.f2)

        self.datasheet.set_column(0, 0, 15)
        self.datasheet.set_column(1,1,15)
        self.datasheet.set_column(3,3,25)
        self.datasheet.set_column(4, 4, 25)
        self.datasheet.set_column(5, 5, 25)



        '''
        Nadpisywanie wartości pozyskiwanych przy 
        teście do pliku 
        '''
        for self.indexOfData, vals in enumerate(self._frequency):
            self.datasheet.write(self.indexOfData+1,0,vals,self.center)

        for index, vals in enumerate(self._damping):
            self.datasheet.write(index + 1, 1, vals, self.center)

        '''
        Dane dotyczące wartości granicznch oraz ich zapis 
        '''
        for self.indexB, vals in enumerate(self._frequencyDamp):
            self.datasheet.write(self.indexB+1,3, vals, self.center)

        #Low values of boundries
        for index, vals in enumerate(self._dampsLow):
            self.datasheet.write(index+1, 4, vals, self.center)

        #High values of boundries
        for index, vals in enumerate(self._dampsHigh):
            self.datasheet.write(index+1, 5, vals, self.center)


        '''
        CGenerowanie wykresu na podstawie zebranych dancych pomiarowych 
        '''

        self.plot = self.workbook.add_chart({'type': 'scatter', 'subtype': 'straight'})
        self.plotBoundries = self.workbook.add_chart({'type': 'scatter', 'subtype': 'straight'})

        '''
        Tworzenie serii da wykresu 
        '''

        self.plot.add_series({
            'categories': ['Main Data',1,0,self.indexOfData+1,0],
            'values': ['Main Data',1,1,self.indexOfData+1,1],
            'name' : "Damping plot",
            'line' : {'color': 'green'}
        })
        self.plot.add_series({
            'categories': ['Main Data', 1, 3, self.indexB + 1, 3],
            'values': ['Main Data', 1, 4, self.indexB + 1, 4],
            'line': {'color': 'yellow'},
            'name' : "Boundries Low"
        })

        self.plot.add_series({
            'categories': ['Main Data', 1, 3, self.indexB + 1, 3],
            'values': ['Main Data', 1, 5, self.indexB + 1, 5],
            'line': {'color': 'yellow'},
            'name': "Boundries High"
        })

        '''
        Edycja osi wykresu oraz jego wielkośći 
        '''
        self.plot.set_title({'name': 'Damping plot'})
        
        self.plot.set_y_axis({'name': 'Dampimg [dB]'})
        self.plot.set_y_axis({'label_position': 'low'})

        self.plot.set_x_axis({'name': 'Frequency [Hz]'})

        self.plot.set_x_axis({'min': 0, 'max': 25000})
        self.plot.set_x_axis({'interval_tick': 10})
        self.plot.set_x_axis({'log_base': 10 })



        self.plot.set_size({'width': 1000, 'height': 500})

        self.plotSheet.insert_chart('C3', self.plot)


        '''
        Zapis do pliku, zwolnienie zasobów
        '''
        self.workbook.close()

