from configuration_IQ import config, qubit_freq, qubit_LO, rr_LO, ge_IF
from qm.qua import *
from qm import SimulationConfig
from qm.QuantumMachinesManager import QuantumMachinesManager
import numpy as np
import matplotlib.pyplot as plt
from slab import*
from slab.instruments import instrumentmanager
from slab.dsfit import*
from tqdm import tqdm

im = InstrumentManager()
LO_q = im['RF5']
LO_r = im['RF8']
##################
# ramsey_prog:
##################
LO_q.set_frequency(qubit_LO)
LO_q.set_ext_pulse(mod=False)
LO_q.set_power(16)
LO_r.set_frequency(rr_LO)
LO_r.set_ext_pulse(mod=True)
LO_r.set_power(18)

ramsey_freq = 50e3
detune_freq = ge_IF + ramsey_freq

dt = 250
T_max = 30000
times = np.arange(0, T_max + dt/2, dt)

wait_times = np.arange(0, 2500 + dt/2, dt)#wait between readout pulse and the ramsey experiment

avgs = 10
reset_time = 500000
simulation = 0
with program() as ramsey:

    ##############################
    # declare real-time variables:
    ##############################

    n = declare(int)      # Averaging
    i = declare(int)      # Amplitudes
    t = declare(int) #array of time delays
    I = declare(fixed)
    Q = declare(fixed)
    I1 = declare(fixed)
    Q1 = declare(fixed)
    I2 = declare(fixed)
    Q2 = declare(fixed)

    I_st = declare_stream()
    Q_st = declare_stream()

    ###############
    # the sequence:
    ###############
    update_frequency("qubit", detune_freq)
    # update_frequency("rr", rr_IF)

    with for_(n, 0, n < avgs, n + 1):

        with for_(i, 0, i < 2500 + dt/2, dt):

                with for_(t, 0, t < T_max + dt/2, t + dt):

                    wait(reset_time//4, "rr")
                    play("clear", "rr")
                    wait(i, "rr")
                    align("rr", "qubit")
                    play("pi2", "qubit")
                    wait(t, "qubit")
                    play("pi2", "qubit")
                    align("qubit", "rr")
                    measure("clear", "rr", None, demod.full("clear_integW1", I1, 'out1'),
                            demod.full("clear_integW2", Q1, 'out1'),
                            demod.full("clear_integW1", I2, 'out2'), demod.full("clear_integW2", Q2, 'out2'))

                    assign(I, I1+Q2)
                    assign(Q, I2-Q1)

                    save(I, I_st)
                    save(Q, Q_st)

    with stream_processing():
        # I_st.save("I_s")
        # I_st.save_all("I_s_all")
        # Q_st.save("Q_s")
        # Q_st.save_all("Q_s_all")

        I_st.buffer(len(wait_times), len(times)).average().save('I')
        Q_st.buffer(len(wait_times), len(times)).average().save('Q')

qmm = QuantumMachinesManager()
qm = qmm.open_qm(config)

if simulation:
    """To simulate the pulse sequence"""
    job = qm.simulate(ramsey, SimulationConfig(150000))
    samples = job.get_simulated_samples()
    samples.con1.plot()
else:
    """To run the actual experiment"""
    print("Experiment execution Done")
    job = qm.execute(ramsey, duration_limit=0, data_limit=0)

    res_handles = job.result_handles
    res_handles.wait_for_all_values()
    I_handle = res_handles.get("I")
    Q_handle = res_handles.get("Q")

    I = I_handle.fetch_all()
    Q = Q_handle.fetch_all()
    print("Data collection done")

    times = 4*times/1e3
    z = 2

    p = fitdecaysin(times[z:len(I)], I[z:], showfit=False)
    T2 = p[3]