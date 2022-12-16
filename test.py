import nidaqmx.system
import nidaqmx
import numpy as np
from nidaqmx.constants import AcquisitionType, RegenerationMode, FuncGenType
from nidaqmx.stream_writers import AnalogMultiChannelWriter, AnalogSingleChannelWriter
from WaveformGenerator import WaveGeneration
from nidaqmx._task_modules.channels.ao_channel import AOChannel
from nidaqmx._task_modules.channel_collection import ChannelCollection
import matplotlib.pyplot as plt

from ReaderDAQ import * 
from WriterDAQ import * 

import queue
import math

from scipy import signal
from scipy.signal import find_peaks
from verifyModue import * 


'''
Testy dla zgodności parametrów tłumienia z pliku i z rzeczywistości są ok
Testy wychodzą róznie, czasami wartości dla danych częstotliwości rozbiegają się nieznacznie np. +- 1/2 dB 
Można robić frontend z tym co jest tutaj w pliku jako sekwencją testującą 


'''
amplitude = 1
#Na razie zostawiam roboczy na czas pisania klasy weryfikacji
sampleSize = [1000] * 41 #+ [2000,2000,2000,2000,3000,3000,3000,3000,4000,4000,5000,5000,5000]

'''
Te wartości są ok dla filtórw: 
dolnorpzepustowe
górnoprzepustowe
Band-stop
'''
sampleRate = [200,400,800,1200,1600,2000,2400,2800,3200,3600,4000,4400,4800,5200,5600,6000,6400,6800,7200,7600,8000,8400,8800,9200,9600,10000,10400,16000,24000,32000,40000,48000,56000,62000,70000,78000,85000,100000]
freq = [1,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,200,300,400,500,600,700,800,900,1000,10000,25000]

'''
Band-pass
'''
#sampleRate = [400,400,800,1200,1600,2000,2400,2800,3200,3600,4000,4400,4800,5200,5600,6000,6400,6800,7200,7600,8000,8400,8800,9200,9600,10000,10400,16000,24000,26800,32000,40000,48000,56000,62000,70000,78000,85000,100000]
#freq = [1,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,200,235,300,400,500,600,700,800,900,1000,10000,25000]

'''
SampleRates - zwiększać proporcjonalnie do częstotliwości
I dla dużych częst. spokooojnie bo się psuje 
'''
#sampleRate = np.arange(400, 14400 ,400).tolist()
#freq = [5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,150,200,300,400,500,600,700,800,900,1000] 
frefLow1st = np.array([[1, 5, -5],[30, 5, -5],[40, 4, -6],[50, 1, -9],[100,-2,-19],[1000,-12,-49],[10000,-22,-79]])
frefLow2st = np.array([[1, 5, -5],[30, 4, -6],[40, 3, -8],[50, 1, -10],[100,-5,-25],[1000,-25,-75],[10000,-45,-125],[25000,-53,-145]])
frefHigh1st = np.array([[1, -16, -60],[50, 1, -9],[100, 4, -6],[1000, 5, -5],[10000,5,-5],[25000,5,-5]])
frefHigh2st = np.array([[1, -33, -96],[50, 1, -10],[100, 3, -8],[1000, 5, -5],[10000,5,-5],[25000,5,-5]])
frefBandStop2st = np.array([[1, 5, -5],[10, 1, -10],[30, 0, -50],[90, -20, -50],[300,1,-50],[700,5,-50],[1000,5,-10],[10000,5,-5],[25000,5,-5]])
frefBandStop1st = np.array([[1, -5, -5],[10, 1, -10],[30, 0, -40],[90, -20, -40],[300,1,-40],[700,5,-40],[1000,5,-10],[10000,5,-5],[25000,5,-5]])
frefBandPass1st = np.array([[1, -16, -61],[50, 1, -10],[235, 1, -10],[1000, -5, -29],[10000,-15,-59],[25000,-19,-71]])
frefBandPass2st = np.array([[1, -33, -100],[50, 1, -15],[235, 1, -15],[1000, -14, -47],[10000,-34,-97],[25000,-41,-116]])
 

q = queue.Queue()
qAmps = queue.Queue()

yVals = list() 
peaksVals = list()


signalGen = SignalWriter(amplitude, 200, 'Dev1/ao0') #Sample generowane 200
signalRead = SignalReader('Dev1/ai0') #Zmieniony został atrybut sampleSize na dynamiczny 
dampTest = VerifyModule(frefLow2st)

for f, sr, sSize in zip (freq, sampleRate, sampleSize): 

    signalGen.createTask(f, sr)
               
    signalRead.create_task(sr,sSize)

    signalGen.endGen()

    '''
    Poprawna akwizycja i obliczanie amplitud syg. dla 
    danej częstotliwości

    '''
    np_fft = np.fft.fft(signalRead.dataContainer[200:])
    #amplitudes = 2 / sampleSize * np.abs(np_fft)
    amplitudes = (np.abs(np_fft) / sSize) 

    aPlot = 2 * amplitudes[0:int(sSize/2 + 1)]

    #amplitudes=list(amplitudes)
    
    
    #print(type(amplitudes))
    #print(amplitudes)
    peak = find_peaks(aPlot, height=0)
    heights = peak[1]['peak_heights']
    maxVals = list(map(float, heights))
    #newMaxVals = [x / 1000 for x in maxVals]
    
    #print(heights)
    #print(len(heights))
    curAmp = np.amax(maxVals)
    qAmps.put(curAmp)

    #print(curAmp)
    # for a in peak:
    #     qAmps.put(np.amax(a) / 1000)

    # for val in signalRead.dataContainer:

    #     q.put(val)

    #signalGen.endGen()

    # while not q.empty():

    #     yVals.append(q.get())

    # while not qAmps.empty(): 
    #     peaksVals.append(qAmps.get())      

# plt.plot(heights)
# plt.show()
'''
Kolejkowanie otrzymanych wartości amplitud
'''
while not qAmps.empty(): 

    peaksVals.append(qAmps.get())

#print(peaksVals)

results = queue.Queue()

'''
Funkcja do obliczania tłumnienia
'''
def dampingCount(amps):
    for a in amps: 
        v = 20*(np.log10(a))
        results.put(v)

    return results

res = dampingCount(peaksVals)

finalList = list()
while not res.empty():
    finalList.append(res.get())

#Wywołanie funkcji sprawdzającej porawność testu dla danego filtra
print(dampTest.verFun(finalList,freq))


plt.plot(freq[:-1],finalList[:-1])
plt.xscale('log')
plt.grid()
plt.show()

'''
Wykres tłumenia jest poprawny,  
sekwencja testująca wydaje się być poprawna, 
trzeba zmienić wartości sampleRate dla wyższych częstotliwości
Trzeba dodać weryfikacje poprawności testu dla wartości z plików .txt 
'''

















# def generateWave(amplitude, freq, sampleRate):

#         amplitude = amplitude
#         freq = freq
#         SampleRate = sampleRate

#         sampleSize = int(SampleRate / freq)
#         tStep = 1/SampleRate

#         timeS = np.linspace(0, ((sampleSize-1) * tStep), sampleSize)
#         sineWave = amplitude * np.sin(2 * np.pi * freq * timeS)

#         return sineWave, timeS
        


# task = nidaqmx.Task()
# task.ao_channels.add_ao_voltage_chan("Dev1/ao0", max_val=5, min_val=-5)

# #buffer_lenght = 1000
# task.timing.cfg_samp_clk_timing(
#     rate=400,
#     samps_per_chan=1000,
#     sample_mode=AcquisitionType.CONTINUOUS,
#     ) 

# #task.out_stream.output_buf_size = buffer_lenght
# writer = AnalogSingleChannelWriter(task.out_stream)
# sine, time = generateWave(1,5,400)

# writer.write_many_sample(sine)

# task.start()






# fig, ax1 = plt.subplots(nrows=1, ncols=1)
# ax1.plot(time, sine, '.-')
# plt.show()
