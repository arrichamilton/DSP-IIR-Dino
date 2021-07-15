# -*- coding: utf-8 -*-
"""
Created on Thurs Nov 5 10:35:22 2020

@author: Arric Hamilton & Ishan Patel
"""
   
class IIR2Filter:
    def __init__(self,_coeffs):
        """
        Sets coeffs for the 2nd order filter
    
        Parameters
        ----------
        coeffs : [0:3] must be FIR coeffs and [3:6] IIR coeffs    
        """
        #sets coeffs
        self.a0,self.a1,self.a2=_coeffs[3:6]
        self.b0,self.b1,self.b2=_coeffs[0:3]
    
        self.in_acc = 0
        self.out_acc = 0
        self.buf1 = 0
        self.buf2= 0
        self.output = 0

    def doFilter(self, data):
        #IIR part
        self.in_acc = data
        self.in_acc = self.in_acc - (self.a1*self.buf1)
        self.in_acc = self.in_acc - (self.a2*self.buf2)
            
        #FIR part
        self.out_acc = self.in_acc * self.b0
        self.out_acc = self.out_acc + (self.b1*self.buf1)
        self.out_acc = self.out_acc + (self.b2*self.buf2)
            
        self.buf2=self.buf1 #shifts buffers along
        self.buf1=self.in_acc
            
        self.output=self.out_acc
        return self.output 

class IIRFilter:
    def __init__(self,_coeffs):
        #sets no. of filters required
        self.chain=[]
        #sets the sos array coeffs to correct filter
        for i in range(len(_coeffs)):
            self.chain.append(IIR2Filter(_coeffs[i]))

    def doFilter(self, data):
        for i in range(len(self.chain)):
            data=self.chain[i].doFilter(data) #return data output for next input
        return data 
