"""
Created on Wed Nov 18 11:38:44 2020

@author: Arric Hamilton (2310737H) & Ishan Patel (2298968P)
The original pyFirmata was written by Tino de Bruijn. The realtime sampling / callback has been added by Bernd Porr.
SEE LICENSE FILE
"""
from pyfirmata2 import Arduino
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import iir_filter as IIR
import win32com.client as comclt
wsh= comclt.Dispatch("WScript.Shell")
wsh.AppActivate("Chrome") # selects chrome 

# Realtime oscilloscope at a sampling rate of 20Hz
# It displays analog channel 0.
PORT = Arduino.AUTODETECT

# Creates a scrolling data display
class RealtimePlotWindow:
    def __init__(self,title,x,y,scale):
        # create a plot window
        self.fig, self.ax = plt.subplots()
        self.ax.set_title(title)
        self.ax.set_xlabel(x)
        self.ax.set_ylabel(y)
        # that's our plotbuffer
        self.plotbuffer = np.zeros(500)
        # create an empty line
        self.line, = self.ax.plot(self.plotbuffer)
        self.ax.set_ylim(scale[0], scale[1])
        # That's our ringbuffer which accumluates the samples
        # It's emptied every time when the plot window below
        # does a repaint
        self.ringbuffer = []
        # start the animation
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=100)

    # updates the plot
    def update(self, data):
        # add new data to the buffer
        self.plotbuffer = np.append(self.plotbuffer, self.ringbuffer)
        # only keep the 500 newest ones and discard the old ones
        self.plotbuffer = self.plotbuffer[-500:]
        self.ringbuffer = []
        # set the new 500 points of channel 0
        self.line.set_ydata(self.plotbuffer)
        return self.line,

    # appends data to the ringbuffer
    def addData(self, v):
        self.ringbuffer.append(v)

# Create an instance of an animated scrolling window with text label parameters
realtimePlotWindowData = RealtimePlotWindow('Realtime LDR Data','Samples','ADC sensor data',[0,.5])
realtimePlotWindowFilter = RealtimePlotWindow('Filtered LDR Data','Samples','Filtered ADC sensor data',[-0.1,.3])

# called for every new sample which has arrived from the Arduino
def callBack(data):
    # send the sample to the plotwindow
    output=yn.doFilter(data)
    realtimePlotWindowFilter.addData(output)
    realtimePlotWindowData.addData(data)
    jump.check(output) #checks if a jump is needed
    
class Jump:
    def __init__(self,fs):
        self.samplingRate = fs
        self.timestamp = 0
        self.i=0
        self.jump=0
        self.oldt=0
        self.capture=np.zeros(1000)
        
    def check(self,output):
        self.timestamp += (1 / self.samplingRate)
        self.capture[self.i]=output #stores data for any future analysis
        if (output>0.01 and self.timestamp-self.oldt>0.25 and self.timestamp>5): #peak detection
            self.jump+=1
            wsh.SendKeys(" ") 
            #we could write to a stepper motor here!
            self.oldt=self.timestamp
        self.i+=1
    
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
    
    #calculates coeffs
    coeffs[3]=1.0
    coeffs[4]=(2*D-2)/(1+C+D)
    coeffs[5]=(1-C+D)/(1+C+D)
    coeffs[0]=1/(1+C+D)
    coeffs[1]=-2/(1+C+D)
    coeffs[2]=coeffs[0]
    return coeffs

fs=20 #20Hz sampling rate
f1=0.1/fs
coeffs=coeffHP(f1,fs) #calculate coeffs
yn=IIR.IIR2Filter(coeffs) #initiate IIR class with coeffs
jump=Jump(fs)

# Get the Ardunio board.
board = Arduino(PORT)
# Set the sampling rate in the Arduino
board.samplingOn(1000 / fs)
# Register the callback which adds the data to the animated plot
board.analog[0].register_callback(callBack)
# Enable the callback
board.analog[0].enable_reporting()
board.analog[1].enable_reporting()
# show the plot and start the animation
plt.show()


