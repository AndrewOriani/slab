# -*- coding: utf-8 -*-
'''
Keithley2182 nanovoltmeter (Keithley199.py)
===========================================
:Author: Kan-Heng Lee
'''

import time
from slab.instruments import VisaInstrument


class Keithley2182(VisaInstrument):
    '''
    Important note:
    If 2182 is directly connect to the pc through gpib, it is set to 'GPIB0::7::INSTR'
    by defalut. If 2182 is connected to the 6221 through RS232, the address should be
    set to the address of 6221, which by default is .'GPIB0::12::INSTR'.
    '''
    def __init__(self,name="keithley2182",address='GPIB0::7::INSTR',enabled=True,timeout=1, passthru=False):
        #if ':' not in address: address+=':22518'
        # VisaInstrument.__init__(self,name,address,enabled, term_chars='\r')
        VisaInstrument.__init__(self, name, address, enabled)
        self.query_sleep=0.001
        self.recv_length=65536
        self.term_char='\r'
        if passthru==True:
            self.comm = 'RS232' ###Change this when you switch connection.
        else:
            self.comm = 'GPIB'
        
    def write_thru(self,command, comm=None):
        '''
        "GPIB" when 2182a is connected to gpib, pass the command as it is.
        "RS232" when 2182a is connected to RS232 "through" 6221. Note it is not
        connected to PC at all in this config.
        '''
        if comm==None:
            comm=self.comm
            
        if comm == 'GPIB':
            self.write(command)
        elif comm == 'RS232':
            self.write(f''':SYST:COMM:SER:SEND "{command}"''')
    
    def queryb_thru(self,command, comm=None):
        if comm==None:
            comm=self.comm

        if comm == 'GPIB':
            return self.queryb(command)
        elif comm == 'RS232':
            self.write(f''':SYST:COMM:SER:SEND "{command}"''')
            return self.queryb(':SYST:COMM:SER:ENT?')

    def get_id(self):
        return self.queryb_thru('*IDN?')

    def init(self):
        self.write_thru('ABOR')
        time.sleep(1)
        self.write_thru('*rst')
        time.sleep(1)

    def buffer_reset(self, n=1024):
        """
        n is number of measurement points that will be stored in buffer.
        1. Clear whatever in the buffer
        2. Set buffer type to 'Sense[1]'
        3. Set buffer size to max (1024) as defalt.
        4. Select buffer control mode 'Next'
        """
        self.write_thru(':trac:cle')
        self.write_thru(':trac:feed sens1')
        self.write_thru(':trac:poin ' + str(n))
        self.write_thru('trac:feed:control NEXT')

    def reset(self):
        self.write_thru(':syst:pres')

    def set_para(self, channel, v_range = None, rate=0.1, digit = 6):
        """
        Basic setting of the meters:
        Set measurement channel (1 or 2)
        v_range=expected voltage range to measure. Default is auto. Range can be 0 to 120V.
        rate = measuring speed (in secs), best SNR between 0.01667 to 0.1 seconds.
        digit = displayed digit on the meter screen
        """
        if v_range == None:
            self.write_thru(':sens:volt:rang:auto on')
        else:
            self.write_thru(':sens:volt:rang ' + str(v_range))
        self.write_thru(':sens:CHAN ' + str(channel))
        self.write_thru(':sens:volt:aper ' + str(rate))
        self.write_thru(':sens:volt:dig ' + str(digit))

    def get_volt(self):
        """Returns the last measured voltage in the buffer"""
        return float(self.queryb_thru('SENS:DATA:FRES?'))

    def done(self):
        """Returns 1 if all pending operations is done."""
        return int(self.queryb_thru('*OPC?'))

    def set_trigger_delay(self, delay):
        self.write_thru(':trig:del %.2f'%delay)


#    def integrate_voltage(self, dt):
#        """
#        :param time: time in seconds to integrate the signal
#        :return: mean and standard deviation of the voltage
#        """
#        t0 = time.time()
#        v = []
#        while time.time() < t0+dt:
#            V = self.get_volt()
#            time.sleep(0.017)
#            v.append(V)
#
#        return np.mean(np.array(v)), np.std(np.array(v))



    # def set_mode(self, mode):
    #     """
    #     :param mode: may be one of the following: "VDC", "VAC", "Ohms", "IDC", "IAC"
    #     :return:
    #     """
    #     conversion_table = {'VDC' : 'F0', 'VAC' : 'F1', 'Ohms' : 'F2', 'IDC' : 'F3', 'IAC' : 'F4'}
    #     self.write(conversion_table[mode]+'X')

#if __name__ == '__main__':
#    print("HERE")
#    # #magnet=IPSMagnet(address='COM1')
#    # V=Keithley199(address='GPIB0::26::INSTR')
#    # print V.get_id()
#    # V.set_range_auto()
#    # print V.get_volt()
#    dmm=HP34401A()