from configuration_IQ import config, qubit_LO, rr_LO, ge_IF, qubit_freq
from qm.qua import *
from qm import SimulationConfig
from qm.QuantumMachinesManager import QuantumMachinesManager
import numpy as np
import matplotlib.pyplot as plt
from slab import*
from slab.instruments import instrumentmanager
from slab.dsfit import*
from tqdm import tqdm
from h5py import File
import os
from slab.dataanalysis import get_next_filename

im = InstrumentManager()
LO_q = im['RF5']
LO_r = im['RF8']
##################
# ramsey_prog:
##################
LO_q.set_frequency(qubit_LO)
LO_q.set_ext_pulse(mod=False)
LO_q.set_power(18)
LO_r.set_frequency(rr_LO)
LO_r.set_ext_pulse(mod=False)
LO_r.set_power(13)

ramsey_freq = 1000e3
detune_freq = ge_IF + ramsey_freq

dt = 25
T_max = 750
times = np.arange(4, T_max + dt/2, dt)

wait_tmin = 25
wait_tmax = 400
wait_dt = 10
wait_tvec = np.arange(wait_tmin, wait_tmax + wait_dt/2, wait_dt)
t_buffer = 250

avgs = 2000
reset_time = 500000
simulation = 0
with program() as ramsey:

    ##############################
    # declare real-time variables:
    ##############################

    n = declare(int)      # Averaging
    i = declare(int)      # wait_times after CLEAR
    t = declare(int)        #array of time delays
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

    with for_(n, 0, n < avgs, n + 1):

        with for_(i, wait_tmin, i < wait_tmax + wait_dt/2, i + wait_dt):

            with for_(t, 4, t < T_max + dt/2, t + dt):

                wait(reset_time//4, "rr")
                play('clear', 'rr')
                align("rr", "qubit")
                wait(i, "qubit")
                play("pi2", "qubit")
                wait(t, "qubit")
                play("pi2", "qubit")
                align("qubit", "rr")
                wait(t_buffer, "rr")
                measure("long_readout", "rr", None,
                        demod.full("long_integW1", I1, 'out1'),
                        demod.full("long_integW2", Q1, 'out1'),
                        demod.full("long_integW1", I2, 'out2'),
                        demod.full("long_integW2", Q2, 'out2'))

                assign(I, I1+Q2)
                assign(Q, I2-Q1)

                save(I, I_st)
                save(Q, Q_st)

    with stream_processing():
        I_st.buffer(len(wait_tvec), len(times)).average().save('I')
        Q_st.buffer(len(wait_tvec), len(times)).average().save('Q')

qmm = QuantumMachinesManager()
qm = qmm.open_qm(config)

if simulation:
    """To simulate the pulse sequence"""
    job = qm.simulate(ramsey, SimulationConfig(150000))
    samples = job.get_simulated_samples()
    samples.con1.plot()
else:
    start_time = time.time()
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

    stop_time = time.time()
    """Stop the output from OPX,heats up the fridge"""
    with program() as stop_playing:
        pass
    job = qm.execute(stop_playing, duration_limit=0, data_limit=0)
    print(f"Time taken: {stop_time - start_time}")

    path = os.getcwd()
    data_path = os.path.join(path, "data/")
    seq_data_file = os.path.join(data_path,
                                 get_next_filename(data_path, 'ramsey_clear', suffix='.h5'))
    print(seq_data_file)

    wait_tvec = 4*wait_tvec
    times = 4*times
    with File(seq_data_file, 'w') as f:
        dset = f.create_dataset("I", data=I)
        dset = f.create_dataset("Q", data=Q)
        dset = f.create_dataset("wait_time", data=wait_tvec)
        dset = f.create_dataset("ramsey_times", data=times)