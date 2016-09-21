import codecs
from multiprocessing import Pipe, Process
import os
import subprocess
import time

class ProgramProfile(object):

    warmup_time = 5.0
    cooldown_time = 5.0
    quantum = 0.25

    def __init__(self, program):
        self.program = program

        self.start_time = 0.0
        self.end_time = 0.0
        self.power_measurements = []


    def __repr__(self):
        return 'ProgramProfile({})'.format(self.program)

    def __str__(self):
        name_str = 'Program Name:      {}'.format(self.program)
        time_str = 'Execution Time:    {}'.format(self.end_time-self.start_time)
        powr_str = '# of Pwr Readings: {}'.format(len(self.power_measurements))
        return '\n'.join([name_str, time_str, powr_str])

    def run(self):
        print('Running {}'.format(self.program))

        parent_conn, child_conn = Pipe()
        logging_proc = self.begin_logging_power(child_conn)

        time.sleep(self.warmup_time)

        self.start_time = time.monotonic()
        with open(os.devnull, 'w') as FNULL:
            subprocess.call(self.program, stdout=FNULL, 
                            stderr=subprocess.STDOUT)
        self.end_time = time.monotonic()

        time.sleep(self.cooldown_time)

        self.end_logging_power(logging_proc, parent_conn)

    def dump_to_file(self, filename):
        with open(filename, 'w') as f:
            f.write(self.program)
            f.write('\n')

            f.write('{}'.format(self.start_time))
            f.write('\n')

            f.write('{}'.format(self.end_time))
            f.write('\n')

            for measurement in self.power_measurements:
                f.write(','.join([str(x) for x in measurement]))
                f.write('\n')

    def begin_logging_power(self, conn):
        logging_proc = Process(target=self.log_power, args=(conn, ))
        logging_proc.start()
        return logging_proc

    def end_logging_power(self, logging_proc, conn):
        conn.send('1')
        self.power_measurements = conn.recv()
        logging_proc.join()

    def log_power(self, conn):
        power_measurements = []

        while not conn.poll():
            t = time.monotonic()
            p = self.read_power()
            power_measurements.append([t] + p)
            time.sleep(self.quantum)

        conn.send(power_measurements)

    def read_power(self):
        return [0.0]

class x86ProgramProfile(ProgramProfile):

    def read_power(self):
        power_reading = None

        # Read /proc/power
        with codecs.open('/proc/power','r','utf-8') as f:
            power_reading = f.readlines()

        # Parse file contents
        temp = power_reading[1].split('\t')
        temp = [int(x) for x in temp[1:]]
        return temp