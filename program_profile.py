import codecs
from multiprocessing import Pipe, Process
import os
import subprocess
import time

class ProgramProfile(object):
    """ Extensible class that encapsulates all of the profiling activities """

    # Class Constants
    #   warmup_time         time before a program runs to wait (while still
    #                           gathering data)
    #   cooldown_time       time after a program ends to wait (while still
    #                           gathering data)
    #   frequency           number of samples to gather per second
    warmup_time = 5.0
    cooldown_time = 5.0
    frequency = 4  

    def __init__(self, program):
        """ Class initialization

            Inputs:
                program     name of program to execute (should include path)
        """
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

    def run(self, outfile):
        """ Runs profiling

            Inputs:
                outfile     file to dump output of program (if any) to
        """
        
        # Start logging power
        parent_conn, child_conn = Pipe()
        logging_proc = self.begin_logging_power(child_conn)

        # Wait for warmup time
        print('Warming up...')
        time.sleep(self.warmup_time)

        # Run program
        print('Running {}...'.format(self.program))
        self.start_time = time.monotonic()
        with open(outfile, 'w') as f:
            subprocess.call(self.program, stdout=f, stderr=subprocess.STDOUT)
        self.end_time = time.monotonic()
        print('{} complete.'.format(self.program))

        # Wait for cooldown time
        print('Cooling down...')
        time.sleep(self.cooldown_time)

        # Stop logging power
        self.end_logging_power(logging_proc, parent_conn)

    def dump_to_file(self, dumpfile):
        """ Dump all gathered data to a CSV file 

            Inputs:
                dumpfile    file to dump data to
        """
        with open(dumpfile, 'w') as f:
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
        """ Starts logging power, using a separate process

            Inputs:
                conn        one end of a Pipe()

            Returns:
                logging_proc    Pythonic-process object (for joining later)
        """
        logging_proc = Process(target=self.log_power, args=(conn, ))
        logging_proc.start()
        return logging_proc

    def end_logging_power(self, logging_proc, conn):
        """ Stops logging power and receives power data from process

            Inputs:
                logging_proc    Pythonic-process object (started earlier)
                conn            one end of a Pipe()
        """
        conn.send('1')  #Doesn't matter what is sent, just that something is
        self.power_measurements = conn.recv()
        logging_proc.join()

    def log_power(self, conn):
        """ Records instantaneous power consumption until signaled

            Inputs:
                conn            one end of a Pipe()
        """
        power_measurements = []

        # Measures until something shows up on receiving end of conn
        while not conn.poll():
            t = time.monotonic()
            p = self.read_power()
            power_measurements.append([t] + p)
            time.sleep(1.0 / self.frequency)

        # Sends all gathered data back through conn
        conn.send(power_measurements)

    def read_power(self):
        """ Read instantaneous power

            TO BE IMPLEMENTED PER-SYSTEM
        """
        return [0.0]

class x86ProgramProfile(ProgramProfile):
    """ Subclass of ProgramProfile for reading power on x86 system """

    def read_power(self):
        power_reading = None

        # Read /proc/power
        with codecs.open('/proc/power','r','utf-8') as f:
            power_reading = f.readlines()

        # Parse file contents
        temp = power_reading[1].split('\t')
        temp = [int(x) for x in temp[1:]]
        return temp