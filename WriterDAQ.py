
import nidaqmx
import numpy as np
from nidaqmx.constants import AcquisitionType, RegenerationMode, FuncGenType
from nidaqmx.stream_writers import AnalogMultiChannelWriter, AnalogSingleChannelWriter
from WaveformGenerator import WaveGeneration
from nidaqmx._task_modules.channels.ao_channel import AOChannel
from nidaqmx._task_modules.channel_collection import ChannelCollection

'''
Drugi sposób generacji sinusa
'''
from SinGenAnt import SinGenAnt
from SinGen import SinGen



class SignalWriter(): 

    #incoming_data = QtCore.pyqtSignal(object)

    def __init__(self, amplitude, sampleSize):
        
        self.amplitude = amplitude
        self.sampleSize = sampleSize
        

        self.frequency = 0
        self.sampleRate = 0
        #self.xtimes = 0 
        #self.overAllBuf = np.empty(shape=(200,1))


        #self.wave_gen = WaveGeneration()
        #self.wave_gen = SinGenAnt()
        self.wave_gen = SinGen()
        

    
    def callback(self):

        
        #while self.task.wait_until_done():
        #self.output_waveform = self.wave_gen.generateWave(self.amplitude, freq, self.sampleRate, self.sampleSize)
        #self.output_waveform = self.wave_gen.generateWave(self.amplitude, freq, self.sampleRate, self.sampleSize)
        self.output_waveform = self.wave_gen.generateWave(self.amplitude, self.frequency, self.sampleRate)
        self.writer = AnalogSingleChannelWriter(self.task.out_stream, auto_start=True)
        #self.xtimes = self.wave_gen.outout_times
        self.writer.write_many_sample(self.output_waveform)
            
        print("Creating signal...")
            

    def endGen(self):

        #self.task.wait_until_done()
        self.task.stop()
        self.task.close()

    def createTask(self, freq, sampleRate):

       
        self.sampleRate = sampleRate 
        self.frequency = freq

        try: 
            self.task = nidaqmx.Task()
        except OSError:
            print("DAQ is not connected, task could not be created")
            return 

        self.task.ao_channels.add_ao_voltage_chan("Dev1/ao0", max_val=5, min_val=-5)
        #self.task.ao_channels.add_ao_func_gen_chan("Dev1/ao0", type=FuncGenType.SINE,freq=100.0, amplitude=1.0, offset=0.0) #TUTAJ SKOŃCZONE
        #buffer_lenght = self.sampleSize

        self.task.timing.cfg_samp_clk_timing(
            rate=self.sampleRate,
            samps_per_chan=self.sampleSize,  #buffer_lenght 
            # Sample mode: Tells it to continuously output whatever is in the buffer
            sample_mode=AcquisitionType.CONTINUOUS,
        ) 

        #self.task.out_stream.output_buf_size = buffer_lenght
        #self.task.out_stream.timeout=5000
        self.callback()







# if __name__ == "__main__": 

    # signal = SignalWriter(1,100)

    # getFreq = [10,20,45,100]
    # getSampleRates = [100,500,1000,2000]

    # for f,s in zip(getFreq,getSampleRates): 

    #     signal.createTask(f,s)
    #     np.append(overAllBuf,signal.output_waveform)

    # #print(signal.output_waveform)
    # #print(np.size(signal.output_waveform))
    # '''
    # Ta sekcja plus pętla jest tylko na próbe, trzeba wymyślić jak składować te danw 
    # wyjściowe 
    # '''
    
    # print("Done")

    # print(overAllBuf)

    # print(overAllBuf.size)
    # print(overAllBuf.shape)
    # '''
    # Dla pojedyńczego wywołania createTask działą ok, jednak dla pętli z różnymi 
    # freq i sampleRate nie działa kompletnie 
    # '''


    