from configuration_IQ import config
from qm.qua import *
from qm import SimulationConfig
from qm.QuantumMachinesManager import QuantumMachinesManager
import numpy as np
import matplotlib.pyplot as plt
from slab import*
from slab.instruments import instrumentmanager
im = InstrumentManager()
LO_q = im['RF5']
LO_r = im['RF8']

from slab.dsfit import*

##################
# power_rabi_prog:
##################
qubit_freq = 4.748488058227563e9
ge_IF = 100e6
qubit_LO = qubit_freq + ge_IF
rr_IF = 0e6
rr_LO = 8.0517e9 - rr_IF

LO_q.set_frequency(qubit_LO)
LO_q.set_ext_pulse(mod = False)
LO_q.set_power(18)
LO_r.set_frequency(rr_LO)
LO_r.set_ext_pulse(mod = False)
LO_r.set_power(18)

a_min = 0.0
a_max = 1.0
da = 0.01
amps = np.arange(a_min, a_max + da/2, da)
avgs = 500
reset_time = 500000
simulation = 0
with program() as ge_rabi:

    ##############################
    # declare real-time variables:
    ##############################

    n = declare(int)        # Averaging
    a = declare(fixed)      # Amplitudes
    I = declare(fixed)
    Q = declare(fixed)
    I_st = declare_stream()
    Q_st = declare_stream()

    ###############
    # the sequence:
    ###############
    update_frequency("qubit", ge_IF)
    update_frequency("rr", rr_IF)

    with for_(n, 0, n < avgs, n + 1):

        with for_(a, a_min, a < a_max + da/2, a + da):

            wait(reset_time//4, "qubit")
            play("gaussian"*amp(a), "qubit")
            align("qubit", "rr")
            measure("long_readout", "rr", None, demod.full("long_integW1", I, 'out1'),demod.full("long_integW1", Q, 'out2'))
            save(I, I_st)
            save(Q, Q_st)

    with stream_processing():
        I_st.buffer(len(amps)).average().save('I')
        Q_st.buffer(len(amps)).average().save('Q')

qmm = QuantumMachinesManager()
qm = qmm.open_qm(config)

if simulation:
    job = qm.simulate(ge_rabi, SimulationConfig(15000))
    samples = job.get_simulated_samples()
    samples.con1.plot()
else:
    job = qm.execute(ge_rabi, duration_limit=0, data_limit=0)
    print ("Done")
    start_time=time.time()

    res_handles = job.result_handles
    res_handles.wait_for_all_values()
    I_handle = res_handles.get("I")
    Q_handle = res_handles.get("Q")
    I = I_handle.fetch_all()
    Q = Q_handle.fetch_all()
    print ("Done 2")
    stop_time=time.time()
    print (f"Time taken: {stop_time-start_time}")

    z = 3
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))
    axs[0].plot(amps[z:len(I)], I[z:],'bo')
    p = fitdecaysin(amps[z:len(I)], I[z:], showfit=False)
    print ("fits :", p)
    print ("a_pi", 1/2/p[1])
    axs[0].axvline(1/2/p[1])
    axs[0].plot(amps[z:len(I)], decaysin(np.append(p,0), amps[z:len(I)]), 'b-')
    axs[0].set_xlabel('Amps')
    axs[0].set_ylabel('I')

    z = 1
    axs[1].plot(amps[z:len(I)], Q[z:],'ro')
    p = fitdecaysin(amps[z:len(I)], Q[z:], showfit=False)
    axs[1].plot(amps[z:len(I)], decaysin(np.append(p,0), amps[z:len(I)]), 'r-')
    print ("fits :", p)
    print ("a_pi", 1/2/p[1])
    axs[1].axvline(1/2/p[1])
    axs[1].set_xlabel('Amps')
    axs[1].set_ylabel('Q')
    plt.tight_layout()
    fig.show()