"""
qc_run.py: BRC script to run QC

This is the script that is actually submitted to the queue on a cluster system. There's some
overlap with qc_run.py because of the need to run as an independent batch job.
"""
import argparse
import sys
import os
import subprocess

from idps_to_json import get_idp_names, subject_to_json

SUBJECT_QC_PATH = "analysis/QC_files/qc.json"
SUBJECT_REPORT_PATH = "analysis/QC_files/qc_report.pdf"

def main():
    parser = argparse.ArgumentParser(f'QC data generation', add_help=True)
    parser.add_argument('--subjids', required=True, help='A list of subject IDs that are pre-processed and have had IDP extraction run')
    parser.add_argument('--indir', required=True, help='The full path of the input directory. All of the IDs that are in the input list MUST have a pre-processed folder in this directory')
    parser.add_argument('--outdir', required=True, help='The full path of the output directory. QC output for all subjects will be put in this directory')
    parser.add_argument('--report-def', required=True, help='The full path to the JSON QC report definition')
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if not os.path.isdir(args.indir):
        parser.error(f"Input directory {args.indir} does not exist or is not a directory")
    if not os.path.isfile(args.subjids):
        parser.error(f"Subject list {args.subjids} does not exist or is not a file")
    if not os.path.isfile(args.report_def):
        parser.error(f"Report definition {args.report_def}  does not exist or is not a file")
    
    os.makedirs(args.outdir, exist_ok=True)
    with open(args.subjids) as f:
        subjids = [s.strip() for s in f if s.strip()]
    print("Found %i subjects: %s" % (len(subjids), ",".join(subjids)))

    # Generate individual subject JSON QC data from IDP values
    idp_names = get_idp_names()
    for subjid in subjids:
        subjdir = os.path.join(args.indir, subjid)
        if not os.path.isdir(subjdir):
            print(f" - WARNING: Subject directory {subjdir} not found or not a directory - skipping")
            continue
        
        print(f" - Processing subject output in {subjdir}")
        subject_to_json(subjdir, idp_names, os.path.join(subjdir, SUBJECT_QC_PATH))

    # Collect individual subjects into a group JSON file and generate reports
    print("Collecting subject QC dir into group JSON file")
    cmd = [
        "/software/imaging/miniconda3/envs/hcp/bin/squat",
        "--subjdir", args.indir, 
        "--subjects", args.subjids, 
        "--qcpaths", SUBJECT_QC_PATH, 
        "--extract", 
        "--output", args.outdir,
        "--report-def", args.report_def, "--group-report", "--subject-reports",
        "--subject-report-path", SUBJECT_REPORT_PATH,
        "--overwrite",
    ]
    print(" ".join(cmd))
    stdout = subprocess.check_output(cmd)
    print(stdout.decode("utf-8"))

if __name__ == "__main__":
    main()