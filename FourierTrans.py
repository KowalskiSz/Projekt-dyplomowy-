import numpy as np 
import matplotlib.pyplot as plt
from scipy import signal
from scipy.signal import find_peaks

def ampCount(): 
    #t0 = 0
    #t1 = 1
    #n_samples = 1000

    amplitude = 1
    sampleRate = [500]
    sampleSize = 1000
    freq = [100]

    amplitudes = list()
    frequencies = list()

    # xs = np.linspace(t0, t1, n_samples)
    # ys = 5 * np.sin(15 * 2 * np.pi * xs)
    for f, samR in zip (freq, sampleRate):

        x = np.arange(samR)
        y = [ amplitude*np.sin(2*np.pi* f * (i/samR)) for i in x]
        y_new = np.tile(y,1)

        samples = y_new[:sampleSize]

        np_fft = np.fft.fft(samples)
        amplitudes = 2 / sampleSize * np.abs(np_fft)
        #frequencies = np.fft.fftfreq(samR)
        peak, _ = find_peaks(amplitudes, distance=1)


    print(len(amplitudes))
    #print(len(frequencies))
    #print(len(y_new))
    #print(len(amplitudes)) 
    #print(amplitudes)
    print(np.amax(peak) / 1000)

    plt.plot(amplitudes)
    #plt.title("Find peaks inside a signal - Geeksforgeeks")
    plt.plot(peak, amplitudes[peak], "x", color = 'r')
    #plt.plot(np.zeros_like(x), "--", color="black")
    plt.show()

    #plt.plot(amplitudes)
    #plt.plot(samples)
    #plt.semilogx(frequencies, amplitudes)
    #plt.show()

    #frequencies = np.fft.fftfreq(n_samples) * n_samples * 1 / (t1 - t0)

    #plt.subplot(2, 1, 2)
    #plt.semilogx(frequencies[:len(frequencies) // 2], amplitudes[:len(np_fft) // 2])

    #plt.show()


ampCount()