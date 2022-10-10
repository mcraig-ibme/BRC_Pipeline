"""
qc_run.py: BRC script to run QC

This is the script that is actually submitted to the queue on a cluster system. There's some
overlap with qc_run.py because of the need to run as an independent batch job.
"""
import argparse
import sys
import os
import subprocess
import tempfile
import shutil

from utils import runcmd
from idpqc import run_idpqc
from mriqc import run_mriqc
from eddyqc import run_eddyqc

SUBJECT_IDPQC_PATH = "analysis/QC_files/idpqc.json"
SUBJECT_EDDYQC_PATH = "analysis/QC_files/eddyqc"
SUBJECT_MRIQC_PATH = "analysis/QC_files/mriqc"
SUBJECT_REPORT_PATH = "analysis/QC_files/qc_report.pdf"

EDDY_OUTPUT_PATH = "analysis/dMRI/preproc/eddy/"

def main():
    parser = argparse.ArgumentParser(f'QC data generation', add_help=True)
    parser.add_argument('--subjids', required=True, help='A list of subject IDs that are pre-processed and have had IDP extraction run')
    parser.add_argument('--indir', required=True, help='The full path of the input directory. All of the IDs that are in the input list MUST have a pre-processed folder in this directory')
    parser.add_argument('--outdir', required=True, help='The full path of the output directory. QC output for all subjects will be put in this directory')
    parser.add_argument('--mriqc', help='Run MRIQC', action="store_true", default=False)
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

    qcfiles = set()
    for subjid in subjids:
        subjdir = os.path.join(args.indir, subjid)
        print(f" - Processing subject {subjdir}")
        if not os.path.isdir(subjdir):
            print(f" - WARNING: Subject directory {subjdir} not found or not a directory - skipping")
            continue

        # Generate QC data from IDP values
        run_idpqc(subjid, subjdir, SUBJECT_IDPQC_PATH)
        qcfiles.add(SUBJECT_IDPQC_PATH)

        # Run squat_eddy if we have Eddy output
        if os.path.isdir(os.path.join(subjdir, EDDY_OUTPUT_PATH)):
            run_eddyqc(subjid, subjdir, EDDY_OUTPUT_PATH, SUBJECT_EDDYQC_PATH)
            qcfiles.add(os.path.join(SUBJECT_EDDYQC_PATH, "qc.json"))

        # Run MRIQC if requested
        if args.mriqc:
            run_mriqc(subjid, subjdir, SUBJECT_MRIQC_PATH)
            qcfiles.add(os.path.join(SUBJECT_MRIQC_PATH, "t1.json"))
            qcfiles.add(os.path.join(SUBJECT_MRIQC_PATH, "t2.json"))

    # Collect individual subjects into a group JSON file and generate reports
    print("Collecting subject QC dir into group JSON file")
    squatdir = os.environ.get("SQUATDIR", "")
    cmd = [
        f"{squatdir}/squat",
        "--subjdir", args.indir, 
        "--subjects", args.subjids, 
        "--extract",
        "--output", args.outdir,
        "--report-def", args.report_def, "--group-report", "--subject-reports",
        "--subject-report-path", SUBJECT_REPORT_PATH,
        "--overwrite",
        "--qcpaths",
    ] + list(qcfiles)
    runcmd(cmd)

if __name__ == "__main__":
    main()