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


# from slab.experiments.PulseExperiments.get_data import get_singleshot_data_two_qubits_4_calibration_v2,\
#     get_singleshot_data_two_qubits, data_to_correlators, two_qubit_quantum_state_tomography,\
#     density_matrix_maximum_likelihood

import pickle

class SequentialExperiment:
    def __init__(self, quantum_device_cfg, experiment_cfg, hardware_cfg,experiment_name, path,analyze = False,show=True,P = 'Q'):

        self.seq_data = []
        
        eval('self.' + experiment_name)(quantum_device_cfg, experiment_cfg, hardware_cfg,path)
        if analyze:
            try:
                #haven't fixed post-experiment analysis
                self.analyze(quantum_device_cfg, experiment_cfg, hardware_cfg, experiment_name,show,self.data,P = 'I')
            except: print ("No post expt analysis")
        else:pass

    def t1rho_sweep(self,quantum_device_cfg, experiment_cfg, hardware_cfg, path):
        expt_cfg = experiment_cfg['t1rho_sweep']
        data_path = os.path.join(path, 'data/')


        amparray = np.arange(expt_cfg['ampstart'],expt_cfg['ampstop'],expt_cfg['ampstep'])
        print(amparray)

        experiment_name = 't1rho_sweep'
        print("Sequences generated")
        seq_data_file = os.path.join(data_path, get_next_filename(data_path, 't1rho_sweep', suffix='.h5'))
        for ampval in amparray:
            experiment_name = 't1rho'
            ps = PulseSequences(quantum_device_cfg, experiment_cfg, hardware_cfg, plot_visdom=False)
            sequences = ps.get_experiment_sequences(experiment_name)
            experiment_cfg['t1rho']['amp']=ampval
            exp = Experiment(quantum_device_cfg, experiment_cfg, hardware_cfg, sequences, experiment_name)
            data = exp.run_experiment_pxi(sequences, path, experiment_name, expt_num=0, check_sync=False)
            self.seq_data.append(data)

        self.seq_data = np.array(self.data)

    def histogram_sweep(self,quantum_device_cfg, experiment_cfg, hardware_cfg, path):

        expt_cfg = experiment_cfg['histogram_sweep']
        sweep_amp = expt_cfg['sweep_amp']
        attens = np.arange(expt_cfg['atten_start'],expt_cfg['atten_stop'],expt_cfg['atten_step'])
        freqs = np.arange(expt_cfg['freq_start'],expt_cfg['freq_stop'],expt_cfg['freq_step'])

        experiment_name = 'histogram'

        expt_cfg = experiment_cfg[experiment_name]
        data_path = os.path.join(path, 'data/')

        seq_data_file = os.path.join(data_path, get_next_filename(data_path, 'histogram_sweep', suffix='.h5'))

        for qb in experiment_cfg[experiment_name]['on_qubits']:
            if sweep_amp:
                for att in attens:
                    quantum_device_cfg['powers'][qb]['readout_drive_digital_attenuation'] = att
                    ps = PulseSequences(quantum_device_cfg, experiment_cfg, hardware_cfg)
                    sequences = ps.get_experiment_sequences(experiment_name)
                    exp = Experiment(quantum_device_cfg, experiment_cfg, hardware_cfg, sequences, experiment_name)
                    data = exp.run_experiment_pxi(sequences, path, experiment_name, seq_data_file=seq_data_file)
                    self.seq_data.append(data)
            else:
                for freq in freqs:
                    quantum_device_cfg['readout'][qb]['freq'] = freq
                    ps = PulseSequences(quantum_device_cfg, experiment_cfg, hardware_cfg)
                    sequences = ps.get_experiment_sequences(experiment_name)
                    exp = Experiment(quantum_device_cfg, experiment_cfg, hardware_cfg, sequences, experiment_name)
                    data = exp.run_experiment_pxi(sequences, path, experiment_name, seq_data_file=seq_data_file)
                    self.seq_data.append(data)

        self.seq_data = np.array(self.seq_data)

    def qp_pumping_t1_sweep(self, quantum_device_cfg, experiment_cfg, hardware_cfg, path):

        expt_cfg = experiment_cfg['qp_pumping_t1_sweep']
        sweep_N_pump = np.arange(expt_cfg['N_pump_start'], expt_cfg['N_pump_stop'], expt_cfg['N_pump_step'])
        sweep_pump_wait = np.arange(expt_cfg['pump_wait_start'], expt_cfg['pump_wait_stop'], expt_cfg['pump_wait_step'])

        experiment_name = 'qp_pumping_t1'

        expt_cfg = experiment_cfg[experiment_name]
        data_path = os.path.join(path, 'data/')

        seq_data_file = os.path.join(data_path, get_next_filename(data_path, 'qp_pumping_t1_sweep', suffix='.h5'))

        for N_pump in sweep_N_pump:
            experiment_cfg['qp_pumping_t1']['N_pump'] = int(N_pump)
            print ("Number of pi pulses: " + str(N_pump) )
            for pump_wait in sweep_pump_wait:
                experiment_cfg['qp_pumping_t1']['pump_wait'] = int(pump_wait)
                print("pi pulse delay: " + str(pump_wait))
                ps = PulseSequences(quantum_device_cfg, experiment_cfg, hardware_cfg)
                sequences = ps.get_experiment_sequences(experiment_name)
                exp = Experiment(quantum_device_cfg, experiment_cfg, hardware_cfg, sequences, experiment_name)
                data = exp.run_experiment_pxi(sequences, path, experiment_name, seq_data_file=seq_data_file)
                self.seq_data.append(data)


        self.seq_data = np.array(self.seq_data)

    def resonator_spectroscopy(self,quantum_device_cfg, experiment_cfg, hardware_cfg, path):
        experiment_name = 'resonator_spectroscopy'
        expt_cfg = experiment_cfg[experiment_name]
        data_path = os.path.join(path, 'data/')
        seq_data_file = os.path.join(data_path, get_next_filename(data_path, 'resonator_spectroscopy', suffix='.h5'))
        ps = PulseSequences(quantum_device_cfg, experiment_cfg, hardware_cfg)

        for qb in experiment_cfg[experiment_name]['on_qubits']:
            for freq in np.arange(expt_cfg['start'], expt_cfg['stop'], expt_cfg['step']):
                quantum_device_cfg['readout'][qb]['freq'] = freq
                sequences = ps.get_experiment_sequences(experiment_name)
                exp = Experiment(quantum_device_cfg, experiment_cfg, hardware_cfg, sequences, experiment_name)
                data = exp.run_experiment_pxi(sequences, path, experiment_name, seq_data_file=seq_data_file)
                self.seq_data.append(data)

        self.seq_data = np.array(self.seq_data)

    def resonator_spectroscopy_pi(self,quantum_device_cfg, experiment_cfg, hardware_cfg, path):
        """Runs res spec with pi pulse before resonator pulse, so you can measure chi by comparing to normal res_spec"""
        experiment_name = 'resonator_spectroscopy_pi'
        expt_cfg = experiment_cfg[experiment_name]
        data_path = os.path.join(path, 'data/')
        seq_data_file = os.path.join(data_path, get_next_filename(data_path, 'resonator_spectroscopy_pi', suffix='.h5'))
        ps = PulseSequences(quantum_device_cfg, experiment_cfg, hardware_cfg)

        for qb in experiment_cfg[experiment_name]['on_qubits']:
            for freq in np.arange(expt_cfg['start'], expt_cfg['stop'], expt_cfg['step']):
                quantum_device_cfg['readout'][qb]['freq'] = freq
                sequences = ps.get_experiment_sequences(experiment_name)
                exp = Experiment(quantum_device_cfg, experiment_cfg, hardware_cfg, sequences, experiment_name)
                data = exp.run_experiment_pxi(sequences, path, experiment_name, seq_data_file=seq_data_file)
                self.seq_data.append(data)

        self.seq_data = np.array(self.seq_data)

    def resonator_spectroscopy_ef_pi(self,quantum_device_cfg, experiment_cfg, hardware_cfg, path):
        """Runs res spec with pi pulse on e/f before resonator pulse, so you can measure chi/contrast by comparing to normal res_spec"""
        experiment_name = 'resonator_spectroscopy_ef_pi'
        expt_cfg = experiment_cfg[experiment_name]
        data_path = os.path.join(path, 'data/')
        seq_data_file = os.path.join(data_path, get_next_filename(data_path, 'resonator_spectroscopy_ef_pi', suffix='.h5'))
        ps = PulseSequences(quantum_device_cfg, experiment_cfg, hardware_cfg)

        for qb in experiment_cfg[experiment_name]['on_qubits']:
            for freq in np.arange(expt_cfg['start'], expt_cfg['stop'], expt_cfg['step']):
                quantum_device_cfg['readout'][qb]['freq'] = freq
                sequences = ps.get_experiment_sequences(experiment_name)
                exp = Experiment(quantum_device_cfg, experiment_cfg, hardware_cfg, sequences, experiment_name)
                data = exp.run_experiment_pxi(sequences, path, experiment_name, seq_data_file=seq_data_file)
                self.seq_data.append(data)

        self.seq_data = np.array(self.seq_data)

    def rabisweep(self,quantum_device_cfg, experiment_cfg, hardware_cfg, path):
        experiment_name = 'rabisweep'
        expt_cfg = experiment_cfg[experiment_name]
        data_path = os.path.join(path, 'data/')
        seq_data_file = os.path.join(data_path, get_next_filename(data_path, 'resonator_spectroscopy', suffix='.h5'))
        ps = PulseSequences(quantum_device_cfg, experiment_cfg, hardware_cfg)

        for qb in experiment_cfg[experiment_name]['on_qubits']:
            for freq in np.arange(expt_cfg['start'], expt_cfg['stop'], expt_cfg['step']):
                quantum_device_cfg['readout'][qb]['freq'] = freq
                sequences = ps.get_experiment_sequences(experiment_name)
                exp = Experiment(quantum_device_cfg, experiment_cfg, hardware_cfg, sequences, experiment_name)
                data = exp.run_experiment_pxi(sequences, path, experiment_name, seq_data_file=seq_data_file)
                self.seq_data.append(data)

        self.seq_data = np.array(self.seq_data)

    def resonator_spectroscopy_power_sweep(self, quantum_device_cfg, experiment_cfg, hardware_cfg, path):
        sweep_expt_name = 'resonator_spectroscopy_power_sweep'
        swp_cfg = experiment_cfg[sweep_expt_name]

        experiment_name = 'resonator_spectroscopy'
        expt_cfg = experiment_cfg[experiment_name]
        data_path = os.path.join(path, 'data/')
        seq_data_file = os.path.join(data_path, get_next_filename(data_path, sweep_expt_name, suffix='.h5'))
        ps = PulseSequences(quantum_device_cfg, experiment_cfg, hardware_cfg)

        for qb in experiment_cfg[experiment_name]['on_qubits']:
            for atten in np.arange(swp_cfg['start'], swp_cfg['stop'], swp_cfg['step']):
                print("Attenuation set to ", atten, 'dB')
                quantum_device_cfg['powers'][qb]['readout_drive_digital_attenuation']= atten
                data_t = []
                for freq in np.arange(expt_cfg['start'], expt_cfg['stop'], expt_cfg['step']):
                    quantum_device_cfg['readout'][qb]['freq'] = freq
                    sequences = ps.get_experiment_sequences(experiment_name)
                    exp = Experiment(quantum_device_cfg, experiment_cfg, hardware_cfg, sequences, experiment_name)
                    data = exp.run_experiment_pxi(sequences, path, experiment_name, seq_data_file=seq_data_file)
                    data_t.append(data)

            self.seq_data.append(np.array(data_t))

        self.seq_data = np.array(self.seq_data)


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
            data = exp.run_experiment_pxi(sequences, path, experiment_name, seq_data_file=seq_data_file)
            self.seq_data.append(data)

        self.seq_data = np.array(self.seq_data)

    def pulse_probe_delay_sweep(self, quantum_device_cfg, experiment_cfg, hardware_cfg, path):
        swp_cfg = experiment_cfg['pulse_probe_delay_sweep']
        delays = np.arange(swp_cfg['start'], swp_cfg['stop'], swp_cfg['step'])

        experiment_name = 'pulse_probe_iq'

        expt_cfg = experiment_cfg[experiment_name]
        data_path = os.path.join(path, 'data/')

        seq_data_file = os.path.join(data_path, get_next_filename(data_path, 'pulse_probe_delay_sweep', suffix='.h5'))

        for delay in delays:

            experiment_cfg["pulse_probe_iq"]["delay"] = delay
            print("delay set to", delay)
            ps = PulseSequences(quantum_device_cfg, experiment_cfg, hardware_cfg)
            sequences = ps.get_experiment_sequences(experiment_name)
            exp = Experiment(quantum_device_cfg, experiment_cfg, hardware_cfg, sequences, experiment_name)
            data = exp.run_experiment_pxi(sequences, path, experiment_name, seq_data_file=seq_data_file)
            self.seq_data.append(data)

        self.seq_data = np.array(self.seq_data)

    def pulse_probe_atten_sweep(self, quantum_device_cfg, experiment_cfg, hardware_cfg, path):
        swp_cfg = experiment_cfg['pulse_probe_atten_sweep']
        attens = np.arange(swp_cfg['start'], swp_cfg['stop'], swp_cfg['step'])

        experiment_name = 'pulse_probe_iq'

        expt_cfg = experiment_cfg[experiment_name]
        data_path = os.path.join(path, 'data/')

        seq_data_file = os.path.join(data_path, get_next_filename(data_path, 'pulse_probe_atten_sweep', suffix='.h5'))

        for qb in experiment_cfg[experiment_name]['on_qubits']:
            for atten in attens:

                quantum_device_cfg['powers'][qb]["qubit_drive_digital_attenuation"] = atten
                print("atten set to", atten)
                ps = PulseSequences(quantum_device_cfg, experiment_cfg, hardware_cfg)
                sequences = ps.get_experiment_sequences(experiment_name)
                exp = Experiment(quantum_device_cfg, experiment_cfg, hardware_cfg, sequences, experiment_name)
                data = exp.run_experiment_pxi(sequences, path, experiment_name, seq_data_file=seq_data_file)
                self.seq_data.append(data)

        self.seq_data = np.array(self.seq_data)


    #TODO: haven't fixed post-analysis
    def analyze(self,quantum_device_cfg, experiment_cfg, hardware_cfg, experiment_name,show,Is,Qs,P='Q'):
        PA = PostExperiment(quantum_device_cfg, experiment_cfg, hardware_cfg, experiment_name, Is,Qs,P,show)