import numpy as np 

class VerifyModule(): 

    def __init__(self, filterList):

        self.filterList = filterList #Potraktujmy to jak matrix NxM

        self.rowAndCols = tuple()
        self.rowAndCols = np.shape(self.filterList)
        self.arrayOfVals = np.zeros(shape=self.rowAndCols[0], dtype=np.int8) 

    def verFun(self, damps, frequency):
        
        counter = 0 
        print(len(frequency))
        for i in range(len(frequency)):
        #for freq, damp in zip(frequency, damps): 
            if counter < self.rowAndCols[0]:


                if (frequency[i] == self.filterList[counter,0]).any(): 
                    
                    if damps[i] <= self.filterList[counter,1] and damps[i] >= self.filterList[counter,2]: 
                        #print(counter)
                        self.arrayOfVals[counter] = 1
                        counter = counter + 1
                    
                        
                    else:

                        self.arrayOfVals[counter] = 0
                        counter = counter + 1
                else: 
                    
                    continue
        
        result = np.max(self.arrayOfVals) == np.min(self.arrayOfVals)
        

        return result


# if __name__ == "__main__":


#     f= np.array([[0, 5, -5],[30, 5, -5],[40, 4, -6],[50, 1, -9]])
#     d = [1,2,3,4,3,1,7,8,9,10]
#     fr = [0,10,20,30,40,50,60,70,80,90]

#     ver = VerifyModule(f)

#     res = ver.verFun(d,fr)
#     print(res)
#     print(ver.arrayOfVals)

