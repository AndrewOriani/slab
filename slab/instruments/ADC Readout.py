

from slab.instruments import SerialInstrument

class ADCReadout(SerialInstrument):
    def __init__(self, name="ADCReadout", address='COM7',enabled=True,timeout=1):
        SerialInstrument.__init__(self, name, address, enabled, timeout)

    def VoltRead(self):
        return self.query('0')