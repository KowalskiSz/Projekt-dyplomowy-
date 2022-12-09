import numpy as np 


class OpenJsonFilter(): 

    def __init__(self):

        self.outputArray = None

    def openJson(self, fileNumber): 

        with open(f'Files/filtr_{fileNumber}.txt', 'r') as file: 
                    
                    lines = file.read().splitlines()
                    #lines = file.readlines()
                
        file.close()

        listOfElements = list()
            
        for line in lines: 
                
                listOfElements.append(line.split())
            
        self.outputArray = np.asarray(listOfElements, dtype=int)
        
        return self.outputArray 



# if __name__ == "__main__":

#     x = OpenJsonFilter()
#     print(x.openJson('000001'))
