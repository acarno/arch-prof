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
    parser.add_argument('--thread_counts',
                        help='Thread counts to run (separated by commas)')
    parser.add_argument('--config',
                        help='Configuration file containing files to run')
    args = parser.parse_args()
    return args

def profile_program(args, program, num_threads=1):
    """ Runs profiler for a single program """
    # Create ProgramProfile
    path = os.path.join(args.prog_folder, program)
    profile = getattr(program_profile, args.profile)(path, num_threads)

    program_name = '.'.join(program.split('.')[:-1] + [str(num_threads)])
    # Run profiling
    outfile = os.path.join(args.log_folder, '{}.output'.format(program_name))
    print('Sending program output to {}'.format(outfile))
    profile.run(outfile)

    # Dump results
    dumpfile = os.path.join(args.log_folder, '{}.csv'.format(program_name))
    print('Dumping gathered data to {}'.format(dumpfile))
    profile.dump_to_file(dumpfile)

    print(profile)
    print()

def run_config(args, program_set, thread_counts):
    """ Runs a subset of all programs in a folder, as specified by user """
    
    # Run all specified programs
    for program in sorted(os.listdir(args.prog_folder)):
        if program in program_set:
            for tc in thread_counts:
                profile_program(args, program, tc)

def run_all(args, thread_counts):
    """ Runs all programs in a folder """
    for program in sorted(os.listdir(args.prog_folder)):
        for tc in thread_counts:
            profile_program(args, program, tc)

def main(args):
    # Default number of threads is 1
    thread_counts = [1]
    
    # If user specified number of threads to run, parse here
    if args.thread_counts:
        try:
            thread_counts = [int(x) for x in args.thread_counts.split(',')]
        except ValueError as err:
            print('Could not parse thread_counts: {}'.format(err))

    # For every program in folder (assuming folder ONLY contains programs)
    if args.config:
        try:
            program_subset = []
            with open(args.config, 'r') as _:
                program_subset = [line.strip() for line in _.readlines()]
        except OSError as err:
            print('Problem reading config file: {}'.format(err))
        else:
            run_config(args, program_subset, thread_counts)
    else:
        run_all(args, thread_counts)

if __name__ == '__main__':
    args = parse_arguments()
    main(args)
