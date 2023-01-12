import numpy as np 

'''
Klasa obsługująca odczyt danych 
granicznych dla filtra z pliku tekstowego 
oraz wpisywanie ich w typ zmiannej array 
'''
class OpenJsonFilter(): 

    '''
    konstrutor definiujący pusty zasób 
    na dane odczytane z pliku
    '''
    def __init__(self):

        self.outputArray = None

    '''
    Metoda obsługująca sczytanie danych 
    z pliku tekstowego na podstawnie id filtra 
    '''
    def openJson(self, fileNumber): 

        with open(f'Files/filtr_{fileNumber}.txt', 'r') as file: 
                    
                    lines = file.read().splitlines()
                    #lines = file.readlines()
                
        file.close()

        '''
        Organizacja odczytanych danych w typ danych 
        array klasy np
        '''
        listOfElements = list()
            
        for line in lines: 
                
                listOfElements.append(line.split())
            
        self.outputArray = np.asarray(listOfElements, dtype=float)
        
        return self.outputArray 

