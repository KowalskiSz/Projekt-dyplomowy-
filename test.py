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


'''
Próby wydają się być OK, następuje zmiana amplitudy sygnału z każdyą zmianą nastaw, 


'''
amplitude = 1
sampleSize = 1000
sampleRate = [400,800,1200,1600,2000,2400,2800,3200,3600,4000,4400,4800,5200,5600,6000,6400,6800,7200,7600,8000,8400,8800,9200,9600,10000,20000,25000,30000,35000,40000,45000]
freq = [5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,200,300,400,500]


q = queue.Queue()
qAmps = queue.Queue()

yVals = list() 
peaksVals = list()


signalGen = SignalWriter(amplitude, 200)
signalRead = SignalReader(sampleSize)

for f, sr in zip (freq, sampleRate): 

    signalGen.createTask(f, sr)
               
    signalRead.create_task(sr)

    signalGen.endGen()

    np_fft = np.fft.fft(signalRead.dataContainer[250:])
    #amplitudes = 2 / sampleSize * np.abs(np_fft)
    amplitudes = (np.abs(np_fft) / sampleSize)            
    amplitudes=list(amplitudes)
    #print(type(amplitudes))
    #print(amplitudes)
    peak = find_peaks(amplitudes, height=0)
    heights = peak[1]['peak_heights']
    maxVals = list(map(float, heights))
    newMaxVals = [x / 1000 for x in maxVals]
    
    #print(heights)
    #print(len(heights))
    curAmp = np.amax(newMaxVals)
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

while not qAmps.empty(): 
    peaksVals.append(qAmps.get())

#print(peaksVals)

results = queue.Queue()
def dampingCount(amps):
    for a in amps: 
        results.put(20*(math.log10(a/1)))

    return results

res = dampingCount(peaksVals)

finalList = list()
while not res.empty():
    finalList.append(res.get())

#print(finalList)


plt.plot(freq,finalList)
plt.show()
'''
Wykres tłumenia jest zły, 
nie wiem dlaczego tak wychodzi, 
sekwencja testująca wydaje się być poprawna 
Może trzeba będzie spróbować robić test jednym cyklem siunusoidy 

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
