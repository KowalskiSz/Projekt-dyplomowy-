import numpy as np 
#import matplotlib.pyplot as plt
import math
'''
Ten generator przebiegu zawsze generuje jeden cykl sinusa
'''
class WaveGeneration: 

    def __init__(self):
        
        self.outout_times = []
        self.lastFreq = 0 
        #self.resetCycle = False


    def generateWave(self, amplitude, freq, sampleRate, samplesPerChunk): 
        
        if self.lastFreq != freq:

            self.lastFreq = freq
            

            rad_per_sec = 2 * np.pi * freq
            chunks_per_sec = sampleRate / samplesPerChunk
            sec_per_chunk = 1 / chunks_per_sec

            #Array of time values 
            self.output_times = np.linspace(
                start=0, stop=sec_per_chunk, num=samplesPerChunk)

            #Creating output waveform 
            self.output_waveform = amplitude * np.sin(
                self.output_times * rad_per_sec)
            
            return self.output_waveform
        else: 
            pass

