#!/usr/bin/env python3

import argparse
import inspect
import os, os.path

import program_profile

def get_profiles():
    profiles = []
    for name, obj in inspect.getmembers(program_profile):
        if inspect.isclass(obj) and obj.__module__ == program_profile.__name__:
            if name != 'ProgramProfile':
                profiles.append(name)
    return profiles

def parse_arguments():
    """ Parses program arguments """
    parser = argparse.ArgumentParser()
    parser.add_argument('profile',
                        help='Name of profile (specific to system)',
                        choices=get_profiles())
    parser.add_argument('prog_folder',
                        help='Location of programs to run')
    parser.add_argument('log_folder',
                        help='Location of log files')
    args = parser.parse_args()
    return args

def main(args):

    # For every program in folder (assuming folder ONLY contains programs)
    for program in sorted(os.listdir(args.prog_folder)):

        # Create ProgramProfile
        path = os.path.join(args.prog_folder, program)
        profile = getattr(program_profile, args.profile)(path)

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
