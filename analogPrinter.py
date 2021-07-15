# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 11:38:44 2020

@author: Arric Hamilton (2310737H) & Ishan Patel (2298968P)
The original pyFirmata was written by Tino de Bruijn. The realtime sampling / callback has been added by Bernd Porr.
"""
from pyfirmata2 import Arduino
import time
import numpy as np
PORT = Arduino.AUTODETECT
import iir_filter as IIR
import scipy.signal as sig
import matplotlib.pyplot as plt
import win32com.client as comclt
wsh= comclt.Dispatch("WScript.Shell")
wsh.AppActivate("Chrome") # selects chrome 

# It uses a callback operation so that timing is precise and
# the main program can just go to sleep.

class AnalogPrinter:
    def __init__(self):
        # sampling rate: 20Hz
        self.samplingRate = 20
        self.timestamp = 0
        self.board = Arduino(PORT)
        self.samples=0
        self.i=0
        self.jump=np.zeros(1000)
        self.oldt=0
        self.data=np.zeros(1000)

    def start(self):
        self.board.analog[0].register_callback(self.myPrintCallback) #callback everytime data captured
        self.board.samplingOn(1000 / self.samplingRate)
        self.board.analog[0].enable_reporting()

    def myPrintCallback(self, data):
        #prints sampled data and stores filtered samples
        output=yn.doFilter(data) #IIR Filter
        print("%f,%f" % (self.timestamp, data))
        self.timestamp += (1 / self.samplingRate)
        self.samples+=1 #incremented every callback
        self.data[self.i]=output #stores data for analysis
        if (output>0.01 and self.timestamp-self.oldt>0.25 and self.timestamp>5): #peak detection
            self.jump[self.i]=1
            wsh.SendKeys(" ") 
            #we could write to a stepper motor here!
            self.oldt=self.timestamp
        self.i+=1
        
    def stop(self):
        self.board.samplingOff()
        self.board.exit()
        
def coeffHP(f,fs):
    """
    Calculates the highpass coefficients for the IIR class

    Parameters
    ----------
    f : Highpass cutoff - MUST be normalized to fs
    fs : Sampling frequency

    """
    w=2*np.pi*f/fs #digital frequency scaled to pi
    ohm=2*fs*np.tan(w/2) #prewarped freq
    C=1.414*ohm #sqrt2*prewarped freq
    D=ohm**2 #prewarped freq^2
    coeffs=np.zeros(6)
    
    #calculates coeffs - see report for derivation
    coeffs[3]=1.0
    coeffs[4]=(2*D-2)/(1+C+D)
    coeffs[5]=(1-C+D)/(1+C+D)
    coeffs[0]=1/(1+C+D)
    coeffs[1]=-2/(1+C+D)
    coeffs[2]=coeffs[0]
    return coeffs
    
analogPrinter = AnalogPrinter()

fs=analogPrinter.samplingRate
f1=0.1/fs #normalized

#coeffs_chain=sig.butter(4,f1*2,btype='high',output='sos') #chain filter coeffs
coeffs_2=coeffHP(f1,fs)
#yn=IIR.IIRFilter(coeffs_chain)
yn=IIR.IIR2Filter(coeffs_2)

print("Let's print data from Arduino's analogue pins for 30secs.")
analogPrinter.start() #data acquisition
time.sleep(10) # acquires for 30s
analogPrinter.stop() #stops DAQ and closes SERCOM
analogPrinter.data=np.resize(analogPrinter.data,analogPrinter.samples) #resizes to include only the captured points
print("finished with n samples:")
print(analogPrinter.samples)

#UNCOMMENT TO PERFORM JUMP COUNTER
"""
time = np.linspace(0., len(analogPrinter.data)/fs, len(analogPrinter.data))
analogPrinter.jump=np.resize(analogPrinter.jump,len(time))
plt.plot(time,analogPrinter.jump)
plt.title('Jumps against time')
plt.ylabel('Jump')
plt.xlabel('Time [s]')
plt.show()
"""