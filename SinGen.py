import numpy as np 
#import matplotlib.pyplot as plt



from scipy import signal
from scipy.signal import find_peaks

class SinGen(): 

    def __init__(self):

        self.SampleRate = 0 
        self.tStep = 0 
        self.frequency = 0 
        self.amplitude = 0

        self.timeS = 0

        self.f = 0
        self.fStep = 0

    def generateWave(self, amplitude, freq, sampleRate):

        self.amplitude = amplitude
        self.frequency = freq
        self.SampleRate = sampleRate

        '''
        Added in case of dividing by 0 - for signal with 0 Hz frequnecy 
        '''
        if freq == 0: 
            self.sampleSize = 1000
        else:
            self.sampleSize = 10 * int(self.SampleRate / self.frequency)
        #print(self.sampleSize)
        #self.sampleSize = 1000
        self.tStep = 1/self.SampleRate

        self.timeS = np.linspace(0, ((self.sampleSize-1) * self.tStep), self.sampleSize)
        sineWave = self.amplitude * np.sin(2 * np.pi * self.frequency * self.timeS)

        return sineWave

    def fft(self, sine): 

        self.fStep = self.SampleRate / self.sampleSize
        self.f = np.linspace(0, (self.sampleSize - 1) * self.fStep, self.sampleSize)

        np_fft = np.fft.fft(sine)
        #a = 2 / self.sampleSize * np.abs(np_fft)
        a = np.abs(np_fft) / self.sampleSize

        self.fplot = self.f[0:int(self.sampleSize/2 + 1)]
        self.aPlot = 2 * a[0:int(self.sampleSize/2 + 1)]
        self.aPlot[0] = self.aPlot[0] / 2

        return a 


# if __name__ == "__main__":

#     sin = SinGen()
#     sinus = sin.generateWave(1,50,2000)
#     sin.fft(sinus)

#     peak = find_peaks(sin.aPlot, height=0)
#     heights = peak[1]['peak_heights']
#     maxVals = list(map(float, heights))

#     #newMaxVals = [x for x in maxVals]

#     #print(type(sin.aPlot))
    
#     #print(maxVals)
#     #print(len(heights))
#     curAmp = np.amax(maxVals)
#     print(curAmp)

#     fig, [ax1, ax2] = plt.subplots(nrows=2, ncols=1)
#     ax1.plot(sin.timeS, sinus, '.-')
#     ax2.plot(sin.fplot, sin.aPlot, '.-')
#     plt.show()

