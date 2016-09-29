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
    parser.add_argument('--config',
                        help='Configuration file containing files to run')
    args = parser.parse_args()
    return args

def profile_program(args, program):
    """ Runs profiler for a single program """
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

def run_config(args, program_set):
    """ Runs a subset of all programs in a folder, as specified by user """
    for program in sorted(os.listdir(args.prog_folder)):
        if program in program_set:
            profile_program(args, program)

def run_all(args):
    """ Runs all programs in a folder """
    for program in sorted(os.listdir(args.prog_folder)):
        profile_program(args, program)

def main(args):

    # For every program in folder (assuming folder ONLY contains programs)
    if args.config:
        try:
            program_subset = []
            with open(args.config, 'r') as _:
                program_subset = [line for line in _.readlines()]
        except OSError as err:
            print('Problem reading config file: {}'.format(err))
        else:
            run_config(args, program_subset)
    else:
        run_all(args)

if __name__ == '__main__':
    args = parse_arguments()
    main(args)
