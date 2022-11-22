import numpy as np 
#import matplotlib.pyplot as plt
import math

class SinGenAnt:

    def __init__(self): 

        self.x1 = 0
        self.y1 = 0



    def generateWave(self, amplitude, freq, sampleRate, sampleSize):

        T = 1/freq
        Ts = 1/sampleRate

        x = np.arange(sampleRate)
        y = [ amplitude*np.sin(2*np.pi*freq * (i/sampleRate)) for i in x]
        y_new = np.tile(y,1)

    
        self.x1 = x[:sampleSize]/freq
        self.y1 = y[:sampleSize]

        samples = y_new[:sampleSize]

        return samples

        


# if __name__ == "__main__":

#     sin = SinGenAnt()
#     samples = sin.generateWave(1,50,1000,100) 

#     plt.plot(samples)
#     plt.show()