"""
fit_brain_age_part_1.py: BRC script to fit brain age using IDPs

This is the script that is actually submitted to the queue on a cluster system. There's some
overlap with fit_brain_age.py because of the need to run as an independent batch job.
"""
import argparse
import sys
import os
import subprocess

import numpy as np
import pandas as pd

GLOBAL_IDPLIST_PATH = "config/IDP_list.txt"
SUBJECT_IDPS_PATH = "analysis/IDP_files/IDPs.txt"

def get_idp_names():
    idp_names_file = os.path.join(os.environ["BRC_GLOBAL_DIR"], GLOBAL_IDPLIST_PATH)
    idp_names = pd.read_csv(idp_names_file, sep="\s+", header=None)
    idp_names = list(idp_names[1])
    print(" - IDP names from %s" % idp_names_file)
    #print(" - IDP names: %s" % ",".join(idp_names))
    print(" - Found %i IDPs" % len(idp_names))
    return idp_names

def get_subject_idps(subjdir):
    subj_idps_file = os.path.join(subjdir, SUBJECT_IDPS_PATH)
    with open(subj_idps_file, "r") as f:
        idps = f.read().split()[1:]
    print(f" - Found IDPs for subject {subjdir}")
    return [float(idp) for idp in idps]

def main():
    parser = argparse.ArgumentParser(f'Brain age fitting', add_help=True)
    parser.add_argument('--subjids', required=True, help='A list of subject IDs that are pre-processed and have had IDP extraction run')
    parser.add_argument('--indir', required=True, help='The full path of the input directory. All of the IDs that are in the input list MUST have a pre-processed folder in this directory')
    parser.add_argument('--outdir', required=True, help='The full path of the output directory. Brain age output for all subjects will be put in this directory')
    parser.add_argument('--ages', required=True, help='The full path to a list of true ages for the subjects')
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if not os.path.isdir(args.indir):
        parser.error(f"Input directory {args.indir} does not exist or is not a directory")
    if not os.path.isfile(args.subjids):
        parser.error(f"Subject list {args.subjids} does not exist or is not a file")
    
    os.makedirs(args.outdir, exist_ok=True)
    with open(args.subjids) as f:
        subjids = [s.strip() for s in f if s.strip()]
    print("Found %i subjects: %s" % (len(subjids), ",".join(subjids)))

    with open(args.ages) as f:
        ages = [float(s) for s in f if s.strip()]
    print("Found %i subject ages" % len(ages))

    if len(ages) != len(subjids):
        raise RuntimeError("Number of ages doesn't match number of subjects")

    idp_names = get_idp_names()
    idps = np.zeros((len(subjids), len(idp_names)), dtype=np.float)
    for idx, subjid in enumerate(subjids):
        subjdir = os.path.join(args.indir, subjid)
        if not os.path.isdir(subjdir):
            print(f" - WARNING: Subject directory {subjdir} not found or not a directory - skipping")
            continue

        print(f" - Processing subject output in {subjdir}")
        subj_idps = get_subject_idps(subjdir)
        print(f" - Found {len(subj_idps)} IDPs")
        idps[idx, :] = subj_idps[:len(idp_names)]
    
    # Remove any IDPs which have nans for any subject
    remove_cols = []
    for idx, name in enumerate(idp_names):
        if np.any(np.isnan(idps[:, idx])):
            print(f" - Removing IDP data for {name} as some subject are NaN")
            remove_cols.append(idx)

    offset = 0
    for idx in remove_cols:
        idps = np.delete(idps, idx - offset, axis=1)
        offset += 1

    idps_fname = os.path.join(args.outdir, "idps.csv")
    np.savetxt(idps_fname, idps)

    print("Running brain age fitting")
    deltab_outfile = os.path.join(args.outdir, "deltab.txt")
    model_outfile = os.path.join(args.outdir, "deltab_model.pkl")
    cmd = [
        "/software/imaging/deltab/default/bin/deltab",
        "--train-ages", args.ages, 
        "--train-features", idps_fname, 
        "--predict", "delta", 
        "--predict-output", deltab_outfile, 
        "--predict-model", "unbiased_quadratic",
        "--overwrite",
        "--save", model_outfile, 
    ]
    print(" ".join(cmd))
    stdout = subprocess.check_output(cmd)
    print(stdout.decode("utf-8"))

    print("DONE")

if __name__ == "__main__":
    main()