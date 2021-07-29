import slab
from slab import *
import numpy as np
import time
import warnings
from slab.instruments import HP34401A

class SetraHP34401A(HP34401A):
    def __init__(self, name="", address='COM6', enabled=True, timeout=.5):
        HP34401A.__init__(self, name=name, address=address, enabled=enabled, timeout=timeout)

    def configure(self, cfg):
        self.serial = cfg['serial']
        self.calibration = np.array(cfg['calibration']).T
        self.m, self.b = np.polyfit(self.calibration[0], self.calibration[1], 1)
        self.units = 'bar'

    def get_pressure(self, chan=None, units=None):
        return self.volt_to_pressure(self.get_value(), units)

    def volt_to_pressure(self, volts, units=None):
        if units is None:
            units = self.units

        if units == 'bar':
            corr = 0.0689476
        elif units == 'psi':
            corr = 1
        else:
            raise Exception('ERROR: Units invalid, must be psi or bar')

        pres = corr * ((self.m * volts + self.b) + 14.6959)
        if pres < 0:
            pres = 0
        else:
            pass
        return pres
