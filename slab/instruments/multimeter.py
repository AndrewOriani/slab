# -*- coding: utf-8 -*-
"""
Keithley199 Voltage Source (Keithley199.py)
===========================================
:Author: Gerwin Koolstra
"""
from slab.instruments import SerialInstrument,VisaInstrument
import re
import time
import numpy as np

class HP34401A(SerialInstrument):
    def __init__(self, name="", address='COM6', enabled=True, timeout=.5):
        self.query_sleep=0.01
        self.timeout=timeout
        self.recv_length=1024
        self.term_char='\r\n'
        SerialInstrument.__init__(self, name, address, enabled, timeout, baudrate=9600, query_sleep=self.query_sleep)
        self.write("SYST:REM")
        self.def_digits=3
        self.def_v_range=10
        self.set_DCvoltage(v_range=self.def_v_range, digits=self.def_digits)
    
    def c_query(self, cmd, bit_len=1024):
        self.ser.write(str(cmd+self.term_char).encode())
        time.sleep(self.query_sleep)
        mes=self.ser.read(bit_len)
        return mes.decode().split('\r\n')[0]

    def get_id(self):
        return self.c_query('*IDN?')

    def get_value(self):
        val=self.c_query("READ?", bit_len=17)
        return float(val)

    def set_DCvoltage(self, v_range=10, digits=4):
        self.write('CONF:VOLT:DC {},{}'.format(v_range, np.format_float_positional(1*10**-digits, trim='-')))


    def set_ACvoltage(self):
        self.write("CONF:VOLT:AC")


    def set_DCcurrent(self):
        self.write("CONF:CURR:DC")
        self.write("READ?")
        self.c_query_sleep = 3

    def set_ACcurrent(self):
        self.write("CONF:CURR:AC")
        self.write("READ?")
        self.c_query_sleep = 3
        #self.write("MEAS:CURR:AC?")

    def set_2wireresistance(self):
        self.write("CONF:RES")
        self.c_query("MEAS:RES?")
        self.c_query_sleep = 1

    def set_4wireresistance(self):
        self.write("CONF:FRES")
        self.c_query("MEAS:FRES?")
        self.c_query_sleep = 1

    def get_errors(self):
        return self.c_query("SYST:ERR?")

    def get_commands(self):
        return "Commands: get_id, get_value, set_DCvoltage, set_DCcurrent, set_2wireDCresistance, set_4wireDCresistance"

    #def get_derivative(self):

class Keithley199(VisaInstrument):

    def __init__(self,name="keithley199",address='GPIB0::26::INSTR',enabled=True,timeout=1):
        #if ':' not in address: address+=':22518'        
        
        VisaInstrument.__init__(self,name,address,enabled, term_chars='\r')
        self.query_sleep=0.05
        self.recv_length=65536
        self.term_char='\r' 
    
    def get_id(self):
        return self.query('*IDN?')

    def get_volt(self):
        """Returns power supply voltage"""
        return float(self.query('S1')[4:])

    def set_range_auto(self):
        self.write('R0X')

    def set_mode(self, mode):
        """
        :param mode: may be one of the following: "VDC", "VAC", "Ohms", "IDC", "IAC"
        :return:
        """
        conversion_table = {'VDC' : 'F0', 'VAC' : 'F1', 'Ohms' : 'F2', 'IDC' : 'F3', 'IAC' : 'F4'}
        self.write(conversion_table[mode]+'X')

    def set_volt_range(self, range):
        """
        :param range: may be one of the following: 0.3V, 3V, 30V or 300V.
        :return:
        """
        allowed = [0.3, 3, 30, 300]

        if range in allowed:
            conversion_table = {'0.3' : 'R1', '3' : 'R2', '30' : 'R3', '300' : 'R4'}
            self.write(conversion_table[str(range)]+'X')

    def integrate_voltage(self, dt):
        """
        :param time: time in seconds to integrate the signal
        :return: mean and standard deviation of the voltage
        """
        t0 = time.time()
        v = []
        while time.time() < t0+dt:
            V = self.get_volt()
            time.sleep(0.017)
            v.append(V)

        return np.mean(np.array(v)), np.std(np.array(v))

if __name__ == '__main__':
    print("HERE")
    # #magnet=IPSMagnet(address='COM1')
    # V=Keithley199(address='GPIB0::26::INSTR')
    # print V.get_id()
    # V.set_range_auto()
    # print V.get_volt()
    dmm=HP34401A()