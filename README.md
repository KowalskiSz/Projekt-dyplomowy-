# Analog filter tester
The application is entirely based on Python and the special library (nidaqmx) provided by National Instruments so that it can communicate with the DAQ equipment in order to acquire data from real electric object (the RC filter)  
Frontend of the app is written with PyQt 5 along with Matplotlib library to visualize the results of a tests (as Bode diagram).  
In addition, to perform mathematical operations like FFT or generating the sine wave, packeges like SciPy and NumPy were also widely used.  
  
The app allows to save collected data in three different ways - the TDMS file, CSV file and xlsx file where additionally implemented script (in python) to generate plot and organise data to be better sorted. 
