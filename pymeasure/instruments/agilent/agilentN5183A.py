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

# from .buffer import KeithleyBuffer


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class AgilentN5183A(Instrument):
    """ Represents the Adcmt 6240a SourceMeter and provides a
    high-level interface for interacting with the instrument.

    .. code-block:: python

        Agilent = AgilentN5183A("GPIB::1")

        Agilent.apply_current()                # Sets up to source current
        Agilent.source_current_range = 10e-3   # Sets the source current range to 10 mA
        Agilent.compliance_voltage = 10        # Sets the compliance voltage to 10 V
        Agilent.source_current = 0             # Sets the source current to 0 mA
        Agilent.enable_source()                # Enables the source output

        Agilent.measure_voltage()              # Sets up to measure voltage

        Agilent.ramp_to_current(5e-3)          # Ramps the current to 5 mA
        print(Agilent.voltage)                 # Prints the voltage in Volts

        Agilent.shutdown()                     # Ramps the current to 0 mA and disables output

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
            adapter, "Agilent N5138A signal generator", **kwargs
        )
    
    def initialize(self):
        self.write("*RST")
    
    def set_frequency(self,frequency=1):
        self.write(f":FREQ {frequency} GHz")

    def set_power(self,DBM):
        self.write(f':POW {DBM} DBM')
    
    def set_config(self):
        self.write(':FREQ:MODE CW')
        self.write(':POW:MODE FIX')
    
    def source_enabled(self,enable=True):
        if enable==True:
            self.write('OUTP ON')
        else:
            self.write('OUTP OFF')
    
    def shutdown(self):
        self.source_enabled(enable=False)
        self.write("*RST")


    
  