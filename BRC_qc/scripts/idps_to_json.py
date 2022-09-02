"""
idps_to_json.py: Convert IDP values for each subject into a JSON file
"""
import os
import sys
import json
import pandas as pd

def get_idp_names():
    idp_names_file = os.path.join(os.environ["BRC_GLOBAL_DIR"], "config", "IDP_list.txt")
    idp_names = pd.read_csv(idp_names_file, sep="\s+", header=None)
    idp_names = list(idp_names[1])
    print(" - IDP names: %s" % ",".join(idp_names))
    return idp_names

def subject_to_json(subjdir, idp_names):
    subj_idps_dir = os.path.join(subjdir, "analysis/IDP_files")
    subj_idps_file = os.path.join(subj_idps_dir, "IDPs.txt")
    with open(subj_idps_file, "r") as f:
        idps = f.read().split()
    print(" - Found IDPs for subject")

    qc_data = {}
    for idp, name in zip(idps[1:], idp_names):
        if not idp.strip().lower() == "nan":
            qc_data[f"qc_{name}"] = float(idp)

    qc_output = os.path.join(subj_idps_dir, 'qc.json')
    with open(qc_output, 'w') as f:
        json.dump(qc_data, f, indent=4)
    print(f" - Wrote subject QC output to {qc_output}")

def main():
    idp_names = get_idp_names()
    for subjdir in sys.argv[1:]:
        do_subject(subjdir, idp_names)