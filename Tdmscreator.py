from nptdms import TdmsWriter, RootObject, GroupObject, ChannelObject
from datetime import datetime


class Tdmscreator:

    def __init__(self, frequency, damping, filterID, filterType, coffFreq, testResult, frequencyDamp, dampsHigh,
                 dampsLow):

        self._dateNow = datetime.now()

        '''
        Frequency and damping values
        '''
        self._frequency = frequency
        self._damping = damping

        '''
        damping boundries values
        '''
        self._frequencyDamp = frequencyDamp
        self._dampsHigh = dampsHigh
        self._dampsLow = dampsLow

        '''
        Filter and test info
        '''
        self._testResult = testResult
        self._filterID = filterID
        self._filterType = filterType
        self._coffFreq = coffFreq

        self.setTrueflag = False


    def createFile(self):

        self._dateNow = self._dateNow.strftime("%d_%b_%Y_%H_%M_%S")
        '''
        Root object - only one in the file
        '''
        self.root_object = RootObject(properties={
            "Filter ID": f"{self._filterID}",
            "Filter Type": f"{self._filterType}",
            "Cutoff Frequency": f"{self._coffFreq}",
            "Test Result": f"{self._testResult}"
        })
        '''
        group objects - three of them; to damping data, to high bound freq, low band freq
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






# #
# if __name__ == "__main__":

#     # (self, frequency, damping, filterID, filterType, coffFreq, testResult, frequencyDamp, dampsHigh,
#     #  dampsLow):

# #
#     obj = Tdmscreator([1,2,3,4,5,6], [9,8,7,6,5,4,3,2,1], 'ID', "Type", "2555", "Passed", [4,4,4,4,4,4],
#                       [5,5,5,5,5,5,5], [4,4,4,4,4,4,4,8])
#     obj.createFile()

