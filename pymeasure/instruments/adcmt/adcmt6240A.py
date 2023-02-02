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


class Adcmt6240A(Instrument):
    """ Represents the Adcmt 6240a SourceMeter and provides a
    high-level interface for interacting with the instrument.

    .. code-block:: python

        adcmt = Adcmt6240a("GPIB::1")

        adcmt.apply_current()                # Sets up to source current
        adcmt.source_current_range = 10e-3   # Sets the source current range to 10 mA
        adcmt.compliance_voltage = 10        # Sets the compliance voltage to 10 V
        adcmt.source_current = 0             # Sets the source current to 0 mA
        adcmt.enable_source()                # Enables the source output

        adcmt.measure_voltage()              # Sets up to measure voltage

        adcmt.ramp_to_current(5e-3)          # Ramps the current to 5 mA
        print(adcmt.voltage)                 # Prints the voltage in Volts

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


    ###############
    # Voltage (V) #
    ###############

    voltage = Instrument.measurement(
        "SOV?","SOV%g",
        """ Reads the voltage in Volts, if configured for this reading.
        """
    )
  
    ####################
    # Methods        #
    ####################

    def __init__(self, adapter, **kwargs):
        super().__init__(
            adapter, "Adcmt 6240a SourceMeter", **kwargs
        )
    
    def initialize(self):
        self.write("*RST")

    def source_enabled(self,enable=True):
        if enable==True:
            self.write("OPR")
        else:
            self.write("SBY")


    def apply_voltage(self, volatege_range=None,source_voltage=0,compliance_current=0.1):
        log.info("%s is sourcing voltage." % self.name)
        self.write(f'SOV{source_voltage},LMI{compliance_current}')


    def shutdown(self):
        """ Ensures that the current or voltage is turned to zero
        and disables the output. """
        log.info("Shutting down %s." % self.name)
        self.apply_voltage(source_voltage=0)
        self.write('*RST')
        super().shutdown()
