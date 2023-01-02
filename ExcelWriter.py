import xlsxwriter
from datetime import datetime

class ExcelWriter:

    def __init__(self,frequency, damping, filterID, filterType, coffFreq, testResult, frequencyDamp, dampsHigh,
                 dampsLow):

        self._dateNow = datetime.now()

        '''
        Frequency and damping values
        '''
        self._frequency = frequency
        self._damping = damping

        '''
        damping boundries values
        '''
        self._frequencyDamp = frequencyDamp
        self._dampsHigh = dampsHigh
        self._dampsLow = dampsLow

        '''
        Filter and test info
        '''
        self._testResult = testResult
        self._filterID = filterID
        self._filterType = filterType
        self._coffFreq = coffFreq

        self.indexOfData = None
        self.indexB = None

    def createFile(self):

        self._dateNow = self._dateNow.strftime("%d_%b_%Y_%H_%M_%S")

        self.workbook = xlsxwriter.Workbook(f"Excel/Excelfile{self._dateNow}.xlsx")

        self.worksheet = self.workbook.add_worksheet("Overall Info")
        self.datasheet = self.workbook.add_worksheet("Main Data")
        self.plotSheet = self.workbook.add_worksheet("Plot")

        self.f1 = self.workbook.add_format({'border': 2, 'border_color': 'green', 'bold': 'True', 'align': 'center'})
        self.f2 = self.workbook.add_format({'border': 2, 'border_color': 'red', 'bold': 'True', 'align': 'center'})

        self.bold = self.workbook.add_format({'bold': True})

        self.center = self.workbook.add_format()
        self.center.set_align('center')

        '''
        First worksheet code, with overall data 
        
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
        Writing main data into file
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
        Uploading raw frequency data
        '''
        for self.indexOfData, vals in enumerate(self._frequency):
            self.datasheet.write(self.indexOfData+1,0,vals,self.center)

        for index, vals in enumerate(self._damping):
            self.datasheet.write(index + 1, 1, vals, self.center)

        '''
        Damping boundries data
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
        Creating a plot of acquired data
        '''

        self.plot = self.workbook.add_chart({'type': 'scatter', 'subtype': 'straight'})
        self.plotBoundries = self.workbook.add_chart({'type': 'scatter', 'subtype': 'straight'})

        '''
        Creating seriaes of data to plot
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

        self.plot.set_title({'name': 'Damping plot'})
        
        self.plot.set_y_axis({'name': 'Dampimg [dB]'})
        self.plot.set_y_axis({'label_position': 'low'})

        self.plot.set_x_axis({'name': 'Frequency [Hz]'})

        self.plot.set_x_axis({'min': 0, 'max': 25000})
        self.plot.set_x_axis({'interval_tick': 10})
        self.plot.set_x_axis({'log_base': 10 })



        self.plot.set_size({'width': 1000, 'height': 500})

        self.plotSheet.insert_chart('C3', self.plot)



        self.workbook.close()

#
# if __name__ == "__main__":
#
# #     # (self, frequency, damping, filterID, filterType, coffFreq, testResult, frequencyDamp, dampsHigh,
# #     #  dampsLow):
#
#
#     obj = ExcelWriter([10,50,100,200,300,1000,10000,25000,26000], [9,8,7,6,5,4,3,2,1], 'ID', "Type", "2555", "Passed", [1,10,20,100,1000,10000,25000],
#                     [10,20,52,87,6,15,12],[4,8,7,10,4,8,8])
#
#     obj.createFile()