#!/usr/bin/env python3

import argparse
import os, os.path

# NEEDS TO BE UPDATE PER-SYSTEM
from program_profile import ProgramProfile

def parse_arguments():
    """ Parses program arguments """
    parser = argparse.ArgumentParser()
    parser.add_argument('prog_folder',
                        help='Location of programs to run')
    parser.add_argument('log_folder',
                        help='Location of log files')
    args = parser.parse_args()
    return args

def main(args):

    # For every program in folder (assuming folder ONLY contains programs)
    for program in sorted(os.listdir(args.prog_folder)):

        # Create ProgramProfile (NEEDS TO BE UPDATED PER-SYSTEM)
        profile = ProgramProfile(os.path.join(args.prog_folder, program))

        # Run profiling
        outfile = os.path.join(args.log_folder, '{}.output'.format(program))
        print('Sending program output to {}'.format(outfile))
        profile.run(outfile)

        # Dump results
        dumpfile = os.path.join(args.log_folder, '{}.csv'.format(program))
        print('Dumping gathered data to {}'.format(dumpfile))
        profile.dump_to_file(dumpfile)

        print(profile)
        print()

if __name__ == '__main__':
    args = parse_arguments()
    main(args)