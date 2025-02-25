"""
fit_brain_age.py: Python implementation of BRC script to submit brain age run job

This script does what would normally be done by the main wrapper script
fit_brain_age.sh but it's just way easier to write it in Python.
"""
import argparse
import sys
import os
import subprocess

def count_lines(fname):
    with open(fname) as f:
        return len([l for l in f.readlines() if l.strip()])

def submit(cmd, **kwargs):
    submit_cmd = [
        "{JOBSUBpath}/jobsub",
        "-q", "cpu", "-p", "1", "-s", "BRC_DELTAB", "-t", "{time_limit}",
        "-m", "10", "-c", cmd
    ]
    submit_cmd = [s.format(**kwargs) for s in submit_cmd]
    print(" ".join(submit_cmd))
    stdout = subprocess.check_output(submit_cmd)
    print(stdout)
    return int(stdout.split()[-1])

def envvar(var):
    val = os.environ.get(var, "")
    if not val:
        raise RuntimeError(f"{var} not set")
    return val

def main():
    parser = argparse.ArgumentParser(f'Fit brain age from BRC IDPs', add_help=True)
    parser.add_argument('--in', dest="subjids", required=True, help='A list of subject IDs that are pre-processed and have had IDP extraction run')
    parser.add_argument('--indir', required=True, help='The full path of the input directory. All of the IDs that are in the input list MUST have a pre-processed folder in this directory with IDPs')
    parser.add_argument('--outdir', required=True, help='The full path of the output directory. Brain age output for all subjects will be put in this directory')
    parser.add_argument('--ages', required=True, help='The full path to a list of true ages for the subjects')
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if not os.path.isdir(args.indir):
        parser.error("Input directory does not exist or is not a directory")
    if not os.path.isfile(args.subjids):
        parser.error(f"Subject list {args.subjids} does not exist or is not a file")

    fsldir = envvar("FSLDIR")
    brc_deltab_scr = envvar("BRC_DELTAB_SCR")
    brc_global_dir = envvar("BRC_GLOBAL_DIR")

    cmd = f"{fsldir}/bin/fslpython {brc_deltab_scr}/fit_brain_age_part_1.py --subjids={args.subjids} --indir={args.indir} --outdir={args.outdir} --ages={args.ages}"

    if os.environ.get("CLUSTER_MODE", "NO") == "YES":
        num_subjs = count_lines(args.subjids)
        minutes = num_subjs * 4
        hours = minutes // 60
        minutes = minutes % 60
        time_limit = f"{hours}:{minutes}:00"
        
        job_id = submit(cmd, time_limit=time_limit, **os.environ)
        print(f"jobID_1: {job_id}")
    else:
        subprocess.check_output(cmd)

if __name__ == "__main__":
    main()