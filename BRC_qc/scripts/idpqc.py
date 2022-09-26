"""
idps_to_json.py: Convert IDP values for each subject into a JSON file
"""
import os
import sys
import json
import pandas as pd

GLOBAL_IDPLIST_PATH = "config/IDP_list.txt"
SUBJECT_IDPS_PATH = "analysis/IDP_files/IDPs.txt"
IDP_NAMES = None

def _get_idp_names():
    idp_names_file = os.path.join(os.environ["BRC_GLOBAL_DIR"], GLOBAL_IDPLIST_PATH)
    idp_names = pd.read_csv(idp_names_file, sep="\s+", header=None)
    idp_names = list(idp_names[1])
    print(" - IDP names from %s" % idp_names_file)
    print(" - IDP names: %s" % ",".join(idp_names))
    print(" - Found %i IDP names" % len(idp_names))
    return idp_names

def run_idpqc(subjid, subjdir, out_fpath):
    print(f" - Running IDP QC in {subjdir}")
    global IDP_NAMES
    if IDP_NAMES is None:
        IDP_NAMES = _get_idp_names()
    subj_idps_file = os.path.join(subjdir, SUBJECT_IDPS_PATH)
    with open(subj_idps_file, "r") as f:
        idps = f.read().split()[1:]
    print(f" - Found {len(idps)} IDPs for subject")

    qc_data = {}
    for idp, name in zip(idps, IDP_NAMES):
        if not idp.strip().lower() == "nan":
            qc_data[f"qc_{name}"] = float(idp)

    out_fpath = os.path.join(subjdir, out_fpath)
    os.makedirs(os.path.dirname(out_fpath), exist_ok=True)
    with open(out_fpath, 'w') as f:
        json.dump(qc_data, f, indent=4)
    print(f" - Wrote subject QC output to {out_fpath}")
