from slab.experiments.PulseExperiments_PXI.sequences_pxi import PulseSequences
from slab.experiments.PulseExperiments_PXI.pulse_experiment import Experiment
from slab.instruments.keysight import keysight_pxi_load as ks_pxi
import numpy as np
import os
import json
from slab.dataanalysis import get_next_filename
from slab.datamanagement import SlabFile
from slab.dsfit import fitdecaysin
try:from skopt import Optimizer
except:print("No optimizer")
from slab.experiments.PulseExperiments_PXI.PostExperimentAnalysis import PostExperiment


from slab.experiments.PulseExperiments.get_data import get_singleshot_data_two_qubits_4_calibration_v2,\
    get_singleshot_data_two_qubits, data_to_correlators, two_qubit_quantum_state_tomography,\
    density_matrix_maximum_likelihood

import pickle

class SequentialExperiment:
    def __init__(self, quantum_device_cfg, experiment_cfg, hardware_cfg,experiment_name, path,analyze = False,show=True,P = 'Q'):

        self.Is = []
        self.Qs = []

        eval('self.' + experiment_name)(quantum_device_cfg, experiment_cfg, hardware_cfg,path)
        if analyze:
            try:
                self.analyze(quantum_device_cfg, experiment_cfg, hardware_cfg, experiment_name,show,self.Is,self.Qs,P = 'I')
            except: print ("No post expt analysis")
        else:pass

    def histogram_sweep(self,quantum_device_cfg, experiment_cfg, hardware_cfg, path):

        expt_cfg = experiment_cfg['histogram_sweep']
        sweep_amp = expt_cfg['sweep_amp']
        attens = np.arange(expt_cfg['atten_start'],expt_cfg['atten_stop'],expt_cfg['atten_step'])
        freqs = np.arange(expt_cfg['freq_start'],expt_cfg['freq_stop'],expt_cfg['freq_step'])

        experiment_name = 'histogram'

        expt_cfg = experiment_cfg[experiment_name]
        data_path = os.path.join(path, 'data/')

        seq_data_file = os.path.join(data_path, get_next_filename(data_path, 'histogram_sweep', suffix='.h5'))

        if sweep_amp:
            for att in attens:
                quantum_device_cfg['readout']['dig_atten'] = att
                ps = PulseSequences(quantum_device_cfg, experiment_cfg, hardware_cfg)
                sequences = ps.get_experiment_sequences(experiment_name)
                exp = Experiment(quantum_device_cfg, experiment_cfg, hardware_cfg, sequences, experiment_name)
                I,Q = exp.run_experiment_pxi(sequences, path, experiment_name, seq_data_file=seq_data_file)
                self.Is.append(I)
                self.Qs.append(Q)
        else:
            for freq in freqs:
                quantum_device_cfg['readout']['freq'] = freq
                ps = PulseSequences(quantum_device_cfg, experiment_cfg, hardware_cfg)
                sequences = ps.get_experiment_sequences(experiment_name)
                exp = Experiment(quantum_device_cfg, experiment_cfg, hardware_cfg, sequences, experiment_name)
                I, Q = exp.run_experiment_pxi(sequences, path, experiment_name, seq_data_file=seq_data_file)
                self.Is.append(I)
                self.Qs.append(Q)


        self.Is = np.array(self.Is)
        self.Qs = np.array(self.Qs)



    def resonator_spectroscopy(self,quantum_device_cfg, experiment_cfg, hardware_cfg, path):
        experiment_name = 'resonator_spectroscopy'
        expt_cfg = experiment_cfg[experiment_name]
        data_path = os.path.join(path, 'data/')
        seq_data_file = os.path.join(data_path, get_next_filename(data_path, 'resonator_spectroscopy', suffix='.h5'))
        ps = PulseSequences(quantum_device_cfg, experiment_cfg, hardware_cfg)

        for freq in np.arange(expt_cfg['start'], expt_cfg['stop'], expt_cfg['step']):
            quantum_device_cfg['readout']['freq'] = freq
            sequences = ps.get_experiment_sequences(experiment_name)
            exp = Experiment(quantum_device_cfg, experiment_cfg, hardware_cfg, sequences, experiment_name)
            I,Q = exp.run_experiment_pxi(sequences, path, experiment_name, seq_data_file=seq_data_file)
            self.Is.append(I)
            self.Qs.append(Q)

        self.Is = np.array(self.Is)
        self.Qs = np.array(self.Qs)

    def qubit_temperature(self,quantum_device_cfg, experiment_cfg, hardware_cfg, path):
        experiment_name = 'ef_rabi'
        expt_cfg = experiment_cfg[experiment_name]
        data_path = os.path.join(path, 'data/')
        seq_data_file = os.path.join(data_path, get_next_filename(data_path, 'qubit_temperature', suffix='.h5'))

        for ge_pi in [True,False]:

            experiment_cfg['ef_rabi']['ge_pi'] = ge_pi
            if ge_pi:pass
            else:experiment_cfg['ef_rabi']['acquisition_num'] = 5000
            ps = PulseSequences(quantum_device_cfg, experiment_cfg, hardware_cfg)
            sequences = ps.get_experiment_sequences(experiment_name)
            exp = Experiment(quantum_device_cfg, experiment_cfg, hardware_cfg, sequences, experiment_name)
            I,Q = exp.run_experiment_pxi(sequences, path, experiment_name, seq_data_file=seq_data_file)
            self.Is.append(I)
            self.Qs.append(Q)

        self.Is = np.array(self.Is)
        self.Qs = np.array(self.Qs)


    def sideband_rabi_freq_scan_length_sweep(self,quantum_device_cfg, experiment_cfg, hardware_cfg, path):
        expt_cfg = experiment_cfg['sideband_rabi_freq_scan_length_sweep']
        lengths = np.arange(expt_cfg['start'],expt_cfg['stop'],expt_cfg['step'])

        experiment_name = 'sideband_rabi_freq_scan'

        expt_cfg = experiment_cfg[experiment_name]
        data_path = os.path.join(path, 'data/')

        seq_data_file = os.path.join(data_path, get_next_filename(data_path, 'sideband_rabi_freq_scan_length_sweep', suffix='.h5'))

        for length in lengths:

            experiment_cfg[experiment_name]['length'] = length
            ps = PulseSequences(quantum_device_cfg, experiment_cfg, hardware_cfg)
            sequences = ps.get_experiment_sequences(experiment_name)
            exp = Experiment(quantum_device_cfg, experiment_cfg, hardware_cfg, sequences, experiment_name)
            I,Q = exp.run_experiment_pxi(sequences, path, experiment_name, seq_data_file=seq_data_file)
            self.Is.append(I)
            self.Qs.append(Q)

        self.Is = np.array(self.Is)
        self.Qs = np.array(self.Qs)

    def sideband_rabi_sweep(self, quantum_device_cfg, experiment_cfg, hardware_cfg, path):
        swp_cfg = experiment_cfg['sideband_rabi_sweep']
        freqs = np.arange(swp_cfg['start'], swp_cfg['stop'], swp_cfg['step'])

        experiment_name = 'sideband_rabi'

        expt_cfg = experiment_cfg[experiment_name]
        data_path = os.path.join(path, 'data/')

        seq_data_file = os.path.join(data_path, get_next_filename(data_path, 'sideband_rabi_sweep', suffix='.h5'))

        for freq in freqs:
            print("Sideband frequency set to", freq, "GHz")

            experiment_cfg[experiment_name]['freq'] = freq
            ps = PulseSequences(quantum_device_cfg, experiment_cfg, hardware_cfg)
            sequences = ps.get_experiment_sequences(experiment_name)
            exp = Experiment(quantum_device_cfg, experiment_cfg, hardware_cfg, sequences, experiment_name)
            I, Q = exp.run_experiment_pxi(sequences, path, experiment_name, seq_data_file=seq_data_file)
            self.Is.append(I)
            self.Qs.append(Q)

        self.Is = np.array(self.Is)
        self.Qs = np.array(self.Qs)

    def sequential_sideband_ramsey(self,quantum_device_cfg, experiment_cfg, hardware_cfg, path):
        swp_cfg = experiment_cfg['sequential_sideband_ramsey']
        stops = np.arange(swp_cfg['start'], swp_cfg['stop'], swp_cfg['step'])[1:]

        experiment_name = 'sideband_ramsey'

        expt_cfg = experiment_cfg[experiment_name]
        data_path = os.path.join(path, 'data/')

        seq_data_file = os.path.join(data_path, get_next_filename(data_path, 'sequential_sideband_ramsey', suffix='.h5'))

        for ii in range(len(stops)):
            experiment_cfg[experiment_name]['stop'] = stops[ii]
            if ii is 0:experiment_cfg[experiment_name]['start'] = swp_cfg['start']
            else:experiment_cfg[experiment_name]['start'] = stops[ii-1]

            print ("Sideband Ramsey start,stop,step = ",experiment_cfg[experiment_name]['start'],experiment_cfg[experiment_name]['stop'],experiment_cfg[experiment_name]['step'])
            ps = PulseSequences(quantum_device_cfg, experiment_cfg, hardware_cfg)
            sequences = ps.get_experiment_sequences(experiment_name)
            exp = Experiment(quantum_device_cfg, experiment_cfg, hardware_cfg, sequences, experiment_name)
            I,Q = exp.run_experiment_pxi(sequences, path, experiment_name, seq_data_file=seq_data_file)
            self.Is.append(I)
            self.Qs.append(Q)

        self.Is = np.array(self.Is)
        self.Qs = np.array(self.Qs)


    def analyze(self,quantum_device_cfg, experiment_cfg, hardware_cfg, experiment_name,show,Is,Qs,P='Q'):
        PA = PostExperiment(quantum_device_cfg, experiment_cfg, hardware_cfg, experiment_name, Is,Qs,P,show)
