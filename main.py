#!/usr/bin/env python3

import argparse
import os, os.path

from program_profile import ProgramProfile

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('prog_folder',
                        help='Location of programs to run')
    parser.add_argument('log_folder',
                        help='Location of log files')
    args = parser.parse_args()
    return args

def main(args):

    for program in os.listdir(args.prog_folder):
        profile = ProgramProfile(os.path.join(args.prog_folder, program))
        profile.run()
        dumpfile = '{}.txt'.format(program)
        profile.dump_to_file(os.path.join(args.log_folder, dumpfile))
        print(profile)

if __name__ == '__main__':
    args = parse_arguments()
    main(args)