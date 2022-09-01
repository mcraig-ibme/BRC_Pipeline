"""
idps_to_json.py: Convert IDP values for each subject into a JSON file
"""
import os
import sys
import argparse
import json
import pandas as pd

def get_tree(names):
    print("get_tree: ", names)
    prefixes = []
    for l in range(len(names)):
        prefixes = set(["_".join(n.split("_")[:l]) for n in names])
        if len(prefixes) > 1:
            break
            
    print("prefixes: ", prefixes)
    if len(prefixes) == 1:
        return names
    else:
        ret = {}
        for prefix in prefixes:
            #print(prefix, l)
            #for n in names:
                #print(tuple(n[:l]), prefix)
                #if tuple(n[:l]) == prefix:
                #    print(n[l:])
            names_with_prefix = [n[len(prefix)+1:] for n in names if n.startswith(prefix)]
            #print(names_with_prefix)
            ret[prefix] = get_tree(names_with_prefix)
            
        return ret

def main():
    idp_names_file = os.path.join(os.environ["BRC_GLOBAL_DIR"], "config", "IDP_list.txt")
    idp_names = pd.read_csv(idp_names_file, sep="\s+", header=None)
    idp_names = list(idp_names[1])

    for subjdir in sys.argv[1:]:
        subj_idps_dir = os.path.join(subjdir, "analysis/IDP_files")
        subj_idps_file = os.path.join(subj_idps_dir, "IDPs.txt")
        with open(subj_idps_file, "r") as f:
            idps = f.read().split()

        #idp_names = [n.split("_") for n in idp_names]
        #for name in idp_names:
        #    print(name)
        #tree = get_tree(idp_names)
        #print(tree)

        qc_data = {}
        for idp, name in zip(idps[1:], idp_names):
            qc_data[f"qc_{name}"] = float(idp)

        with open(os.path.join(subj_idps_dir, 'qc.json'), 'w') as f:
            json.dump(qc_data, f, indent=4)
