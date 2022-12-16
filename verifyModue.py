import numpy as np 

class VerifyModule(): 

    def __init__(self, filterList):

        self.filterList = filterList #Potraktujmy to jak matrix NxM
        self.damp = None
        self.frequency = None
        self.result = False
        self.counter = 0

        self.rowAndCols = None
        self.rowAndCols = np.shape(self.filterList)
        self.arrayOfVals = np.zeros(shape=self.rowAndCols[0], dtype=np.int8)
        #print(self.filterList) 

    
    def verFun(self, damps, frequency):
        
        self.counter = 0
        self.damps = damps
        self.frequency = frequency
        #print(len(frequency))
        for i in range(len(self.frequency)):
        #for freq, damp in zip(frequency, damps): 
            if self.counter < self.rowAndCols[0]:


                if (self.frequency[i] == self.filterList[self.counter,0]).any(): 
                    
                    if self.damps[i] <= self.filterList[self.counter,1] and self.damps[i] >= self.filterList[self.counter,2]: 
                       
                        self.arrayOfVals[self.counter] = 1
                        self.counter = self.counter + 1
                        #print(f'{self.damps[i]}, {self.frequency[i]}')
                        #print(i)
                    
                        
                    else:

                        self.arrayOfVals[self.counter] = 0
                        self.counter = self.counter + 1
                        #print(f'{self.damps[i]}, {self.frequency[i]}')
                        #print(i)
                else: 
                    
                    continue
        
        if np.all((self.arrayOfVals == 0)):
            self.result = False
        else:    
            self.result = np.max(self.arrayOfVals) == np.min(self.arrayOfVals)
        
        print(self.arrayOfVals)
        

        return self.result


# if __name__ == "__main__":


#     f= np.array([[0, 5, -5],[30, 5, -5],[40, 4, -6],[50, 1, -9]])
#     d = [1,2,3,4,3,1,7,8,9,10]
#     fr = [0,10,20,30,40,50,60,70,80,90]

#     ver = VerifyModule(f)

#     res = ver.verFun(d,fr)
#     print(res)
#     print(ver.arrayOfVals)

