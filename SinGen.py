import numpy as np 

from scipy import signal
from scipy.signal import find_peaks

'''
Klasa generująca dyskrety przebieg sinusoidalny 
podawany na wyjście DAQ 
klasa generuje jeden cykl, który jest powielany w ramach 
generacji na karcie DAQ
'''
class SinGen(): 

    '''
    Konstruktor klasy zawiera dane potrzebne 
    do stworzenia przebiegu
    '''
    def __init__(self):

        self.SampleRate = 0 
        self.tStep = 0 
        self.frequency = 0 
        self.amplitude = 0

        self.timeS = 0

        self.f = 0
        self.fStep = 0

    '''
    Metoda generacji przymująca wielkości 
    określające przebieg 
    '''
    def generateWave(self, amplitude, freq, sampleRate):

        self.amplitude = amplitude
        self.frequency = freq
        self.SampleRate = sampleRate

        '''
        Sama generacja odbywa się poprzez algorytm 
        wykorzystujący funkcje biblioteki 
        Numpy 
        '''
        if freq == 0: 
            self.sampleSize = 1000
        else:
            self.sampleSize = int(self.SampleRate / self.frequency)
        
        self.tStep = 1/self.SampleRate

        self.timeS = np.linspace(0, ((self.sampleSize-1) * self.tStep), self.sampleSize)
        sineWave = self.amplitude * np.sin(2 * np.pi * self.frequency * self.timeS)

        return sineWave




