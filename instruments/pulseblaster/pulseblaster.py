__author__ = 'Nelson'

from spinapi import *


def start_pulseblaster(exp_period_ns,awg_trig_len,card_trig_time,readout_trig_time,card_trig_len,readout_trig_len):
    # Enable the log file
    pb_set_debug(1)

    print("Using SpinAPI Library version %s" % pb_get_version())
    print("Found %d boards in the system.\n" % pb_count_boards())

    pb_select_board(0)

    if pb_init() != 0:
        print("Error initializing board: %s" % pb_get_error())
        # exit()
        # TODO: pulseblaster intialization fails for sequential experiment
        pass

    # time settings
    unit_inst_time = 10 # ns
    idle_unit_inst_time = 10000  # ns
    exp_period = exp_period_ns
    #exp_period = 200*1000 # 100us

    awg_trig_time = 0
    #awg_trig_len = 100

    #card_trig_time = 2000
    #card_trig_len = 100

    # readout_trig_time = card_trig_time
    #readout_trig_len = 1000 # has to be longer than card_trig_len


    # calculated time value
    awg_trig_delay_loop = awg_trig_len/unit_inst_time
    card_trig_delay_loop = card_trig_len/unit_inst_time
    readout_trig_delay_loop = (readout_trig_len)/unit_inst_time

    awg_card_idle_time = card_trig_time - (awg_trig_time + awg_trig_len)
    awg_card_idle_delay_loop = awg_card_idle_time/unit_inst_time

    card_readout_idle_time = readout_trig_time - (card_trig_time+card_trig_len)
    card_readout_idle_delay_loop = card_readout_idle_time/unit_inst_time

    total_time = readout_trig_time + readout_trig_len
    period_idle_time = exp_period - total_time
    period_idle_delay_loop = int(period_idle_time / idle_unit_inst_time - 1)



    # delay loop
    delay_loop = 20

    # ports hex value
    idle = 0x0
    awg_trig = 0x1
    card_trig = 0x2
    readout_trig = 0x4
    drive_trig = 0x8

    # Configure the core clock
    pb_core_clock(500.0)

    # Program the pulse program
    pb_start_programming(PULSE_PROGRAM)

    # idle till next experiment - alex, moved idle to beginning of cycle
    start = pb_inst_pbonly64(drive_trig, Inst.LONG_DELAY, period_idle_delay_loop, idle_unit_inst_time)

    # awg trigger
    pb_inst_pbonly64(awg_trig + drive_trig, Inst.LONG_DELAY,awg_trig_delay_loop,unit_inst_time)

    # idle between end of awg trig and card trig
    pb_inst_pbonly64(drive_trig, Inst.LONG_DELAY, awg_card_idle_delay_loop, unit_inst_time)

    # card trig starts first at the same time
    pb_inst_pbonly64(card_trig+drive_trig, Inst.LONG_DELAY,card_trig_delay_loop,unit_inst_time)

    # idle between card trig and readout trig
    pb_inst_pbonly64(idle, Inst.LONG_DELAY, card_readout_idle_delay_loop, unit_inst_time)

    # readout trig after card trig finished
    pb_inst_pbonly64(readout_trig, Inst.LONG_DELAY,readout_trig_delay_loop,unit_inst_time)

    # idle for next experiment
    # pb_inst_pbonly64(drive_trig, Inst.LONG_DELAY, period_idle_delay_loop, idle_unit_inst_time)

    # branch to start; Outputs are off
    pb_inst_pbonly64(idle, Inst.BRANCH, start, idle_unit_inst_time)

    pb_stop_programming()

    # Trigger the board
    pb_reset()
    # run_pulseblaster()

    #pb_close()

def run_pulseblaster():
    pb_start()

def stop_pulseblaster():
    pb_stop()