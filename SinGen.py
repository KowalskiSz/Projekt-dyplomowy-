import numpy as np 
#import matplotlib.pyplot as plt

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

        self.sampleSize = int(self.SampleRate / self.frequency)
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


# if __name__ == "__main__":

#     sin = SinGen()
#     sinus = sin.generateWave(1,100,2000)
#     sin.fft(sinus)

#     fig, [ax1, ax2] = plt.subplots(nrows=2, ncols=1)
#     ax1.plot(sin.timeS, sinus, '.-')
#     ax2.plot(sin.fplot, sin.aPlot, '.-')
#     plt.show()

