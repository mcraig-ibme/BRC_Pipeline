"""
qc_run.py: BRC script to run QC

This is the script that is actually submitted to the queue on a cluster system. There's some
overlap with qc_run.py because of the need to run as an independent batch job.
"""
import argparse
import sys
import os

from idps_to_json import get_idp_names, subject_to_json

def main():
    parser = argparse.ArgumentParser(f'QC data generation', add_help=True)
    parser.add_argument('--subjids', required=True, help='A list of subject IDs that are pre-processed and have had IDP extraction run')
    parser.add_argument('--indir', required=True, help='The full path of the input directory. All of the IDs that are in the input list MUST have a pre-processed folder in this directory')
    parser.add_argument('--outdir', required=True, help='The full path of the output directory. QC output for all subjects will be put in this directory')
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if not os.path.isdir(args.indir):
        parser.error("Input directory does not exist or is not a directory")
    if not os.path.isfile(args.subjids):
        parser.error("Subject list does not exist or is not a file")
    
    os.makedirs(args.outdir, exist_ok=True)
    with open(args.subjids) as f:
        subjids = [s.strip() for s in f if s.strip()]
    print("Found %i subjects: %s" % (len(subjids), ",".join(subjids)))

    idp_names = get_idp_names()
    for subjid in subjids:
        subjdir = os.path.join(args.indir, subjid)
        if not os.path.isdir(subjdir):
            print(f" - WARNING: Subject directory {subjdir} not found or not a directory - skipping")
            continue
        
        print(f" - Processing subject output in {subjdir}")
        subject_to_json(subjdir, idp_names)

if __name__ == "__main__":
    main()