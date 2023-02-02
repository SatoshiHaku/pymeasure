#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import logging
import time

import numpy as np

from pymeasure.instruments import Instrument, RangeException
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

import cmath

# from .buffer import KeithleyBuffer


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class AgilentN5222A(Instrument):
    """ Represents the Agilent N5222A Network Analyzer and provides a
    high-level interface for interacting with the instrument.

    .. code-block:: python

        keithley = Keithley2182A("GPIB::1")

        keithley.apply_current()                # Sets up to source current
        keithley.source_current_range = 10e-3   # Sets the source current range to 10 mA
        keithley.compliance_voltage = 10        # Sets the compliance voltage to 10 V
        keithley.source_current = 0             # Sets the source current to 0 mA
        keithley.enable_source()                # Enables the source output

        keithley.measure_voltage()              # Sets up to measure voltage

        keithley.ramp_to_current(5e-3)          # Ramps the current to 5 mA
        print(keithley.voltage)                 # Prints the voltage in Volts

        adcmt.shutdown()                     # Ramps the current to 0 mA and disables output

    """

    # source_mode = Instrument.control(
    #     ":SOUR:FUNC?", ":SOUR:FUNC %s",
    #     """ A string property that controls the source mode, which can
    #     take the values 'current' or 'voltage'. The convenience methods
    #     :meth:`~.Keithley2400.apply_current` and :meth:`~.Keithley2400.apply_voltage`
    #     can also be used. """,
    #     validator=strict_discrete_set,
    #     values={'current': 'CURR', 'voltage': 'VOLT'},
    #     map_values=True
    # )
    def __init__(self, adapter, **kwargs):
        super().__init__(
            adapter, "Agilent N5222A network analyzer", **kwargs
        )
  
    ####################
    # Methods        #
    ####################

    def set_preset(self):
        self.write("SYST:FPReset")

    def setup_SPARM(self,n=1,SPAR="S21"):
        self.write(f"DISPlay:WINDow{n}:STATE ON") #turn on display
        self.write(f"CALCulate{n}:PARameter:DEFine:EXT 'MyMeas{n}',{SPAR}") #Define masurement name and parameters
        self.write(f"DISPlay:WINDow{n}:TRACe{n}:FEED 'MyMeas{n}'") #shows graph result in window
        # SendAna("CALC:PAR:SEL 'MyMeas1'")

    def set_sweep(self,n=1,startFreq=5e8,endFreq=1e9,fCW=1e9,time=1,num=101,type="LIN",BW=1):
        self.write(f"SENS{n}:SWE:TYPE {type}")#sweep type
        if type =="LIN":
            self.write(f"SENS{n}:FREQ:STAR {startFreq}")#Start of frequency
            self.write(f"SENS{n}:FREQ:STOP {endFreq}")#End of frequency
            self.write(f"SENS{n}:SWE:TIME {time}")#seconds

        
        elif type =="CW":
            self.write(f"SENS{n}:FREQ:CW {fCW}")#CW
            # self.write(f"SENS{n}:FREQ:CW 1e9")#CW

        self.write(f"SENS{n}:SWE:POIN {num}")#Numebr of sweep points
        self.write(f"SENS{n}:BWID {BW}kHZ")#band width kHZ

    
    def set_power(self,n=1,P=0):
        self.write(f"SOUR:POW{n} {P}") #power DB

    def set_autoYscale(self,n=1):
        self.write(f"DISP:WIND{n}:TRAC:Y:SCAL:AUTO")# Auto y scale of display 
        
    
    def set_average(self,n=1,counts=1):
        self.write(f"SENS{n}:AVER:CLE")#Clear average
        self.write(f"SENS{n}:AVER:COUN {counts}")#1-2^16
        self.write(f"SENS{n}:AVER ON")#ON

    def parse_data(self,n=1):
        self.write(f"SENS{n}:X?") #get X values(ex:frequency)
        self.write(f"CALC{n}:PAR:CAT?") #->'"MyMeas1,S21"\n'
        self.write(f"CALC{n}:PAR:SEL 'MyMeas{n}'") #set data name
        self.write(f"FORM:DATA 'ASCII'")# set data format
        self.write(f"FORM:BORD")#
        time.sleep(1)

    def get_data(self,n=1):
        self.write(f"SENS{n}:X?")
        X = self.read() # get x data
        self.write(f"CALC{n}:DATA? SDATA")
        Y = self.read()# get complex data

        x = list(map(float, X.split(",")))#x data
        y0 = list(map(float, Y.split(",")))[0::2] #real part
        y1 = list(map(float, Y.split(",")))[1::2] #imaginary part

        y = [x+y*1j for x, y in  zip(y0,y1)] # make complex value from Re and Im
        r = np.array(list(map(abs,y)))#get absolute values
        theta = np.array(list(map(cmath.phase,y)))#get phases

        return x,theta,r
    def set_power_off(self):
        self.write("OUTP OFF")






# SendAna("CALC1:DATA?")


# import matplotlib.pyplot as plt


# # print(theta)
# R = 10*np.log10(r**2)# R mW -> dbm
# plt.plot(x, R)
# #plt.yscale("log")