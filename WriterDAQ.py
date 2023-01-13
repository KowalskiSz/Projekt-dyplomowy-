
import nidaqmx
import numpy as np
from nidaqmx.constants import AcquisitionType, RegenerationMode, FuncGenType
from nidaqmx.stream_writers import AnalogMultiChannelWriter, AnalogSingleChannelWriter

from nidaqmx._task_modules.channels.ao_channel import AOChannel
from nidaqmx._task_modules.channel_collection import ChannelCollection


from SinGen import SinGen

'''
Klasa odpowiedzialna za generowanie sygnału wyjściowego, poprzez
komunikcje z DAQ
'''
class SignalWriter(): 

    
    '''
    Konstruktor klasy przyjmujący parametry sygnału: 
    amplituda, wielkość bufora oraz fizyczne nasawy 
    DAQ
    '''
    def __init__(self, amplitude, sampleSize, daqSetup):
        
        self.amplitude = amplitude
        self.sampleSize = sampleSize

        self.frequency = 0
        self.sampleRate = 0
        #self.xtimes = 0 
        #self.overAllBuf = np.empty(shape=(200,1))

        self.isConnented = None
        #self.wave_gen = WaveGeneration()
        #self.wave_gen = SinGenAnt()
        self.wave_gen = SinGen()
        self.daqSetup = daqSetup
        

    '''
    metoda callback przyjmuje nastawy sygnału sinusoidalnego 
    do generacji oraz otiwera samą generację na DAQ
    '''
    def callback(self):

        self.output_waveform = self.wave_gen.generateWave(self.amplitude, self.frequency, self.sampleRate)
        self.writer = AnalogSingleChannelWriter(self.task.out_stream, auto_start=True)
        self.writer.write_many_sample(self.output_waveform)
            
        print("Creating signal...")
            
    '''
    metoda zwalniająca zasoby
    '''
    def endGen(self):

        self.task.stop()
        self.task.close()

    '''
    Metoda przyjmująca częstotliość generowanego sygnału
    oraz częstotliowść próbkowania syganłu 
    '''
    def createTask(self, freq, sampleRate):

       
        self.sampleRate = sampleRate 
        self.frequency = freq

        '''
        Utowrzenie instancji klasy Task określającej 
        parametry wyjścia karty DAQ
        '''
        try: 
            self.task = nidaqmx.Task()
        
        except OSError:
            print("DAQ is not connected, task could not be created")
            self.isConnented = False

            return 
        '''
        wywołanie metody na obiekcie task określającej
        charakter generowanego sygnału 
        '''
        self.task.ao_channels.add_ao_voltage_chan(self.daqSetup , max_val=5, min_val=-5)
    
        '''
        metoda określająca częstotliowść próbkowania sygnalu,
        wielkośc bufora na wygenerowane próbki oraz
        typ akwizycji jako CONTINUOUS
        '''
        self.task.timing.cfg_samp_clk_timing(
            rate=self.sampleRate,
            samps_per_chan=self.sampleSize,  #wielkość bufora 
            # Sample mode: Tutaj sygnał generowanyj jest ciągle, aż do momentu przerwania taska
            sample_mode=AcquisitionType.CONTINUOUS,
        ) 

        '''
        wywołanie funkcji callback 
        '''
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


    