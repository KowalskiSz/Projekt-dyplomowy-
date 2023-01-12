from nptdms import TdmsWriter, RootObject, GroupObject, ChannelObject
from datetime import datetime

'''
Klasa obsługująca generację plku TDMS
na podstawie metod biblioteki npTDMS
'''
class Tdmscreator:

    '''
    Konstruktor przyjmujący wymagane do zapisu w plik 
    dane 
    '''
    def __init__(self, frequency, damping, filterID, filterType, coffFreq, testResult, frequencyDamp, dampsHigh,
                 dampsLow):

        '''
        Wydobycie aktualnej dokładej daty 
        '''
        self._dateNow = datetime.now()

        '''
        Zdefiniwanie zmiennych na 
        częstotliowść oraz tłumienie otrzymane z testu
        '''
        self._frequency = frequency
        self._damping = damping

        '''
        Zmienne na dane z pliku
        z ograniczeniami filtra
        '''
        self._frequencyDamp = frequencyDamp
        self._dampsHigh = dampsHigh
        self._dampsLow = dampsLow

        '''
        Zmienne na informacje o badanym 
        filtrze oraz wyniku testu 
        '''
        self._testResult = testResult
        self._filterID = filterID
        self._filterType = filterType
        self._coffFreq = coffFreq

        self.setTrueflag = False


    '''
    metoda generująca główny plik
    '''
    def createFile(self):

        '''
        Konwerscja danych daty na string aby 
        były możiwie do wykorzystania przy zapisie 
        '''
        self._dateNow = self._dateNow.strftime("%d_%b_%Y_%H_%M_%S")
        '''
        Root object - zdefinicja w pliku tdms, 
        jest jedna na cały plik 
        '''
        self.root_object = RootObject(properties={
            "Filter ID": f"{self._filterID}",
            "Filter Type": f"{self._filterType}",
            "Cutoff Frequency": f"{self._coffFreq}",
            "Test Result": f"{self._testResult}"
        })
        '''
        group objects - zdefiniwanie grup w pliku zawierających dane
        tłumienia oraz czestotliwości
        '''
        self.group_object_Bode = GroupObject("Bode Diagram", properties={
            "Frequency": "Hz",
            "Damping": "dB",
        })

        self.group_object_DampBoundries = GroupObject("Damping Boundries", properties={"Frequency": "Hz",
            "Damping": "dB"})


        self.channel_object_frequancy = ChannelObject("Bode Diagram", "Frequency [Hz]", self._frequency, properties=None)
        self.chanel_object_damping = ChannelObject("Bode Diagram", "Damping [dB]", self._damping, properties=None )

        self.channel_object_dampFrequency = ChannelObject("Damping Boundries", "Frequency [Hz]", self._frequencyDamp, properties=None)
        self.channel_object_dampHigh = ChannelObject("Damping Boundries", "Damping High Value [dB]", self._dampsHigh,
                                                          properties=None)
        self.channel_object_dampLow =  ChannelObject("Damping Boundries", "Damping Low Value [dB]", self._dampsLow,
                                                          properties=None)

        '''
        Zapisa zdefiowanych sruktur do głównego 
        pliku z rozszerzeniem tdms
        '''
        with TdmsWriter(f"Tdms/TdmsFile{self._dateNow}.tdms") as tdms_writer:

            tdms_writer.write_segment([
                self.root_object,

                self.group_object_Bode,
                self.channel_object_frequancy,
                self.chanel_object_damping,

                self.group_object_DampBoundries,
                self.channel_object_dampFrequency,
                self.channel_object_dampHigh,
                self.channel_object_dampLow
            ])





