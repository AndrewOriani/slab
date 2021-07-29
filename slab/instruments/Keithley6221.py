# -*- coding: utf-8 -*-
"""
Keithley6221 Current Source (Keithley199.py)
===========================================
:Author: Kan-Heng Lee
"""
from slab.instruments import VisaInstrument
from slab.datamanagement import SlabFile
import re
import time
import numpy as np
import datetime
import os
from slab.dsfit import fitlinear

class Keithley6221(VisaInstrument):

    def __init__(self,name="keithley6221",address='GPIB0::12::INSTR',enabled=True,timeout=1):
        #if ':' not in address: address+=':22518'
        # VisaInstrument.__init__(self,name,address,enabled, term_chars='\r')
        VisaInstrument.__init__(self, name, address, enabled)
        self.query_sleep=0.001
        self.recv_length=65536
        self.term_char='\r'

    def get_id(self):
        return self.queryb('*IDN?')

    def initiate(self, curr_range=2E-2, volt_comp=10):
        """
        1. Abort any previous operation and reset memory
        2. Set current range (amp).
        3. Set voltage_compliance. Defalut is the tool maximum = 12 V.
        """
        self.write('ABOR')
        time.sleep(1)
        self.write('*rst')
        time.sleep(1)
        self.write(':sour:curr:rang ' + str(curr_range))
        self.write(':sour:curr:compliance ' + str(volt_comp))
    
    def abort(self):
        """
        Abort any operation.
        """
        self.write('ABOR')

    def set_output(self, state=False):
        """Turn on/off currents"""
        if state == True:
            self.write('OUTP ON')
        elif state == False:
            self.write('OUTP OFF')
        else:
            raise TypeError('State must be type bool')

    def set_curr(self, value):
        """Set current output in Amp."""
        self.write(':sour:curr:lev ' + str(value))

