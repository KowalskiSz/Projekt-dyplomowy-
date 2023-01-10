import csv
from datetime import datetime

class CSVwriter:
    '''
        This class creates a CSV file containing only data that is being collected
        on the output of app - output damping and frequency points.

    '''
    def __init__(self, frequency, damping):


        self._dateNow = datetime.now()


        '''
        Frequency and damping values
        '''
        self._frequency = frequency
        self._damping = damping



    def createFile(self):

        self._fieldNames = ["frequency", "damping"]
        self._dateNow = self._dateNow.strftime("%d_%b_%Y_%H_%M_%S")

        with open(f'CSV/CSVFile{self._dateNow}.csv', 'w', newline='') as csvFile:
            self._csvWrite = csv.DictWriter(csvFile, fieldnames=self._fieldNames)

            self._csvWrite.writeheader()


            '''
            Writing testing data - frequency and damping
            '''
            for i in range(len(self._frequency)):
                self._csvWrite.writerow({"frequency" : self._frequency[i], "damping" : self._damping[i]})

            # self._csvWrite.writerow({"filter ID" : self._filterID, "filter Type" : self._filterType,
            #                          "cofFreq" : self._coffFreq, "test result" : self._testResult})


# if __name__ == "__main__":


#     obj = CSVwriter([10,50,100,200,300,1000,10000,25000,26000],[9,8,7,6,5,4,3,2,1],
#                     )

#     obj.createFile()