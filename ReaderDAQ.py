
import nidaqmx
import numpy as np
from nidaqmx.constants import AcquisitionType
from nidaqmx.stream_readers import AnalogMultiChannelReader, AnalogSingleChannelReader
import time
from PyQt5.QtCore import QThread, pyqtSignal



'''
Klasa reader odpowiada za akwizyjce sygnału 
na wyjściu z filtra
'''
class SignalReader(): 

    '''
    konstruktor klasy przyjmuje nastawy fizyczne DAQ
    '''
    def __init__(self, AISetup):
        super().__init__()

        self.reader = None
        self.is_running = False
        self.is_done = False

        self.AISetup = AISetup

        #self.sample_rate = sample_rate
        #self.sample_size = sample_size
        #self.ui_queue = ui_queue
        #self.dataContainer = np.empty(shape=(self.sample_size,),dtype=np.float64)

    '''
    meotda inicjalizująca kanał na DAQ do akwizycji danych 
    przyjmuje częstotliość próbkowania sygnału oraz
    wielkość bufora na zebrne dane
    '''
    def create_task(self, sample_rate, sample_size): 
        
        '''
        Zdefiniowanie bufora danych 
        jako pustego wektora klasy np 
        '''
        self.dataContainer = np.empty(shape=(sample_size,),dtype=np.float64)

        try: 
            self.task = nidaqmx.Task()
        except: 
            print("Do daq device")
            return

        try: 
            self.task.ai_channels.add_ai_voltage_chan(self.AISetup) 
        except: 
            print("No such channel exists")
            return

        '''
        Przekazanie częstotliości próbkowania 
        żadanej wielkości zczytywanych danych oraz
        okrślenie typu akwizycji jako FINITE
        '''
        self.task.timing.cfg_samp_clk_timing(rate=sample_rate, sample_mode=AcquisitionType.FINITE,samps_per_chan=sample_size)
        
        print("Starting taks")
        self.task.start()
        self.reader = AnalogSingleChannelReader(self.task.in_stream)
        
        '''
        metoda wyzwalająca akwizycję
        określa masymalną ilość próbek 
        wpisywanych w bufor 
        '''
        self.reader.read_many_sample(data=self.dataContainer, number_of_samples_per_channel=sample_size)

        '''
        metoda zwlaniająca zasoby 
        kiedy warunki akwyzycji są spełnione
        '''
        if self.task.is_task_done():

            print("Closing tasks")
            self.task.stop()
            self.task.close()
        

 