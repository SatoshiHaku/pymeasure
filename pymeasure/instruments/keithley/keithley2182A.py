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


class Keithley2182A(Instrument):
    """ Represents the Adcmt 6240a SourceMeter and provides a
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
            adapter, "Keithley 2182a nanovoltmeter", **kwargs
        )
  
    ####################
    # Methods        #
    ####################
    def reset(self):
        self.write('*RST')

    def set_filter(self,WIND=0):
        #Specify filter window (in %)
        self.write(f":SENSe:VOLTage:DFILter {WIND}")

    def set_rate(self,PLC=1):
        #PLC=0.1:fast, PLC=1:medium,PLC=5:slow
        self.write(f":SENSe:VOLTage:NPLCycles {PLC}")

    def measure_voltage(self):
        self.write(":READ?")
        return float(self.read())
