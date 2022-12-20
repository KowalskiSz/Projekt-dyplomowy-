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
            
        self.outputArray = np.asarray(listOfElements, dtype=float)
        
        return self.outputArray 



# if __name__ == "__main__":

#     x = OpenJsonFilter()
#     l = x.openJson('000001')
#     print(l[:,0])
#     print(l[:,1])
#     print(l[:,2])
