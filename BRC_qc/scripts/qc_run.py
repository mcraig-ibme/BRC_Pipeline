"""
qc_run.py: Python implementation of BRC script to submit QC run job

This script does what would normally be done by the main wrapper script
qc_run.sh but it's just way easier to write it in Python.
"""
import argparse
import sys
import os

from utils import runcmd

def count_lines(fname):
    with open(fname) as f:
        return len([l for l in f.readlines() if l.strip()])

def submit(cmd, **kwargs):
    submit_cmd = [
        "{JOBSUBpath}/jobsub",
        "-q", "cpu", "-p", "1", "-s", "BRC_QC", "-t", "{time_limit}",
        "-m", "10", "-c", " ".join(cmd)
    ]
    submit_cmd = [s.format(**kwargs) for s in submit_cmd]
    stdout = runcmd(submit_cmd)
    return int(stdout.split()[-1])

def envvar(var):
    val = os.environ.get(var, "")
    if not val:
        raise RuntimeError(f"{var} not set")
    return val

def main():
    parser = argparse.ArgumentParser(f'QC data generation', add_help=True)
    parser.add_argument('--in', dest="subjids", required=True, help='A list of subject IDs that are pre-processed and have had IDP extraction run')
    parser.add_argument('--indir', required=True, help='The full path of the input directory. All of the IDs that are in the input list MUST have a pre-processed folder in this directory')
    parser.add_argument('--outdir', required=True, help='The full path of the output directory. QC output for all subjects will be put in this directory')
    parser.add_argument('--mriqc', help='Run MRIQC', action="store_true", default=False)
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if not os.path.isdir(args.indir):
        parser.error("Input directory does not exist or is not a directory")
    if not os.path.isfile(args.subjids):
        parser.error(f"Subject list {args.subjids} does not exist or is not a file")

    fsldir = envvar("FSLDIR")
    brc_qc_scr = envvar("BRC_QC_SCR")
    brc_global_dir = envvar("BRC_GLOBAL_DIR")
    report_def = f"{brc_global_dir}/config/qc_report.json"
    
    cmd = [
        f"{fsldir}/bin/fslpython",
        f"{brc_qc_scr}/qc_run_part_1.py",
        f"--subjids={args.subjids}",
        f"--indir={args.indir}",
        f"--outdir={args.outdir}",
        f"--report-def={report_def}",
    ]
    if args.mriqc:
        cmd.append("--mriqc")

    if os.environ.get("CLUSTER_MODE", "NO") == "YES":
        if args.mriqc:
            mins_per_subj = 30
        else:
            mins_per_subj = 4
        num_subjs = count_lines(args.subjids)
        minutes = num_subjs * mins_per_subj
        hours = minutes // 60
        minutes = minutes % 60
        time_limit = f"{hours}:{minutes}:00"

        job_id = submit(cmd, time_limit=time_limit, **os.environ)
        print(f"jobID_1: {job_id}")
    else:
        runcmd(cmd)

if __name__ == "__main__":
    main()
