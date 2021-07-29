from .instrumentmanager import InstrumentManager
from .instrumenttypes import Instrument, VisaInstrument, TelnetInstrument, SocketInstrument, SerialInstrument, \
    WebInstrument
from .localinstruments import LocalInstruments

try: from .InstrumentManagerWindow import InstrumentManagerWindow
except: print("Could not load InstrumentManagerWindow")

from .spectrumanalyzer import E4440
from .nwa import E5071
from .PNAX import N5242A
from .rfgenerators import N5183B,E8257D,BNC845
from .cryostat import Triton
from .awg import *
from .spec_analyzer.spectrum_analyzer import *
from .ipsmagnet import *
from .TestInstruments import EchoInstrument,RandomInstrument
from .TDS7104 import TekTDS7104
from .RCA18 import MCRCA18
from .multimeter import Keithley199, HP34401A

try: from .AD5780DAC.AD5780 import AD5780
except: print("Could not load AD5780 dac")
try: from .labbrick.labbrick import LMS_get_device_info,LMS103,LPS802,LDA602
except: print("Could not load labbrick")
try: from .relaybox.relaybox import RelayBox
except: print("Could not load relaybox")
try: from .relaybox.heliummanifold import HeliumManifold
except: print("Could not load heliummanifold")
try: from .relaybox.RFSwitch import RFSwitch
except: print("Could not load heliummanifold")
try: from .bkpowersupply import BK9130A
except: print("Could not load BKPowerSupply")
try: from .bkpowersupply import BK9130B
except: print("Could not load BKPowerSupplynew")
try: from .KEPCOPowerSupply import KEPCOPowerSupply
except: print("Could not load KEPCOPowerSupply")
try: from .voltsource import SRS900
except: print("Could not load SRS900")
try: from .voltsource import YokogawaGS200
except: print("Could not load YokogawaGS200")
from .Alazar import Alazar, AlazarConfig, AlazarConstants
try: from .Alazar import Alazar, AlazarConfig, AlazarConstants
except: print("Could not load Alazar card")
try: from .function_generator import BiasDriver,FilamentDriver,BNCAWG
except: print("Could not load BNC AWG classes")
try: from .multimeter import Keithley199, HP34401A
except: print("Could not load Keithley199/HP34401A multimeter classes")
try: from .spectrumanalyzer import E4440
except: print("Could not load E4440 Spectrum Analyzer")
try: from .cryocon import Cryocon
except: print("Could not load Cryocon instrument driver")
try: from .DigitalAttenuator import DigitalAttenuator
except: print("Could not load Digital Attenuator driver")
try: from .HeaterSwitch import HeaterSwitch
except: print("Could not load Heater Switch Driver")
try: from .Omega16i import Omega16i
except: print("Could not load Omega 16i driver")
try: from .lockin import SR844
except: print("Could not load SR844 driver")
try: from .PressureGauge import PressureGauge
except: print("Could not load PressureGauge driver")
try: from .Oerlikon import Center_Three
except: print('Could not load oerlikon pressure readout driver')
try: from .Setra225 import SetraHP34401A
except: print('Could not load SetraHP34401A pressure readout driver')
try: from .compressor import CP2800
except: print('Could not load CP2800 compressor')
try: from .Keithley2182 import Keithley2182
except: print('Could not load Keithley2182 nanovoltmeter')
try: from .Keithley6221 import Keithley6221
except: print('Could not load Keithley6221 current source')