
import nidaqmx
import numpy as np
from nidaqmx.constants import AcquisitionType
from nidaqmx.stream_readers import AnalogMultiChannelReader, AnalogSingleChannelReader
import time
from PyQt5.QtCore import QThread, pyqtSignal




class SignalReader(): 

    #incomingData = pyqtSignal(object)


    def __init__(self):
        super().__init__()

        self.reader = None
        self.is_running = False
        self.is_done = False

        #self.sample_rate = sample_rate

        #self.sample_size = sample_size

        #self.ui_queue = ui_queue

        #self.dataContainer = np.empty(shape=(self.sample_size,),dtype=np.float64)

    '''
    Nie do końca wiem o co z tym chodzi, możliwe że trzeba to będzie rozważyć 
    w kontekście całej apki na pyqt5 żeby ta funcja była 
    '''
    # def run(self): 
        
    #     self.create_task()
    #     #self.is_running = True
       
    #     self.reader.read_many_sample(data=self.dataContainer, number_of_samples_per_channel=self.sample_size)
    #     self.incomingData.emit(self.dataContainer)
       
    #     if self.task.is_task.done():

    #         print("Closing taks")
    #         self.task.stop()
    #         self.task.close()

        

    def create_task(self, sample_rate, sample_size): 
        '''
        Create read task from daq
        '''
        '''
        Zmieniona została inicjalizacja dataContainera z konstruktora na wywołanie dynamiczne w funkcji 
        W sumie to chyba do zmiany początowej z init z konstruktora 
        '''
        
        self.dataContainer = np.empty(shape=(sample_size,),dtype=np.float64)

        try: 
            self.task = nidaqmx.Task()
        except: 
            print("Do daq device")
            return

        try: 
            self.task.ai_channels.add_ai_voltage_chan("Dev1/ai0") 
        except: 
            print("No such channel exists")
            return

            
        self.task.timing.cfg_samp_clk_timing(rate=sample_rate, sample_mode=AcquisitionType.FINITE,samps_per_chan=sample_size)
        #self.task.in_stream.input_buf_size = 4000
        
        print("Starting taks")
        self.task.start()
        self.reader = AnalogSingleChannelReader(self.task.in_stream)

        self.reader.read_many_sample(data=self.dataContainer, number_of_samples_per_channel=sample_size)

        
        
       
        if self.task.is_task_done():

            print("Closing tasks")
            self.task.stop()
            self.task.close()
        

'''
Jeżeli jest newData to on 4 razy robi aquire po 1000 samplu dla 4 
różnych sample rate, 
A bez tego to robi dla jednego sample rate 1000 sampli i tyle 
'''

#newData = np.empty(shape=(4000,), dtype=np.float64)
# rates = [400,800,1200,1600]
# reader = SignalReader(1000)

# for r in rates: 

#     #np.append(newData,reader.create_task(r))
#     reader.create_task(r)

# print(reader.dataContainer)
# print(reader.dataContainer.size)

#print(newData)
#print(newData.size)
 