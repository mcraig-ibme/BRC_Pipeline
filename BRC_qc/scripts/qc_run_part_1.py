"""
qc_run.py: BRC script to run QC

This is the script that is actually submitted to the queue on a cluster system
"""
import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(f'QC data generation', add_help=True)
    parser.add_argument('--subjids', required=True, help='A list of subject IDs that are pre-processed and have had IDP extraction run')
    parser.add_argument('--indir', required=True, help='The full path of the input directory. All of the IDs that are in the input list MUST have a pre-processed folder in this directory')
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()