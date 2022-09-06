"""
idps_to_json.py: Convert IDP values for each subject into a Numpy array suitable for deltab
"""
import os
import sys
import pandas as pd

GLOBAL_IDPLIST_PATH = "config/IDP_list.txt"
SUBJECT_IDPS_PATH = "analysis/IDP_files/IDPs.txt"

def get_idp_names():
    idp_names_file = os.path.join(os.environ["BRC_GLOBAL_DIR"], GLOBAL_IDPLIST_PATH)
    idp_names = pd.read_csv(idp_names_file, sep="\s+", header=None)
    idp_names = list(idp_names[1])
    print(" - IDP names: %s" % ",".join(idp_names))
    return idp_names

def get_subject_idps(subjdir):
    subj_idps_file = os.path.join(subjdir, SUBJECT_IDPS_PATH)
    with open(subj_idps_file, "r") as f:
        idps = f.read().split()
    print(f" - Found IDPs for subject {subjdir}")
    return [float(idp) for idp in idps]
