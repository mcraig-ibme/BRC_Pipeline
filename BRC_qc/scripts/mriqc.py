"""
mriqc.py: BRC script to run MRIQC
"""
import argparse
import sys
import os
import subprocess
import tempfile
import shutil
import json

from idps_to_json import get_idp_names, subject_to_json

def run_mriqc(subjid, subjdir, outpath):
    print(f" - Processing MRIQC in {subjdir}")

    # MRIQC runs on a BIDS dataset so make a 'fake bids' folder
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "dataset_description.json"), "w") as f:
            f.write('{"Name": "brc", "BIDSVersion": "1.4.0", "DatasetType": "raw"}\n')
        with open(os.path.join(d, "participants.tsv"), "w") as f:
            f.write(f'participant_id\{subjid}')
        anatdir = os.path.join(d, f'sub-{subjid}', 'ses-1', 'anat')
        os.makedirs(anatdir)
        t1 = os.path.join(subjdir, "raw", "anatMRI", "T1", "T1_orig.nii.gz")
        t2 = os.path.join(subjdir, "raw", "anatMRI", "T2", "T2_orig.nii.gz")
        if os.path.isfile(t1):
            shutil.copy(t1, os.path.join(anatdir, f'sub-{subjid}_ses-1_T1w.nii.gz'))
        if os.path.isfile(t2):
            shutil.copy(t2, os.path.join(anatdir, f'sub-{subjid}_ses-1_T2w.nii.gz'))

        SINGULARITY_IMAGE = '/software/imaging/singularity_images/poldracklab_mriqc-2021-01-30-767af1135fae.simg'
        cmd = [
            'singularity', 'run', '--cleanenv', SINGULARITY_IMAGE,
            d, f'{d}/mriqc', 'participant', '--no-sub'
            ]
        print(" ".join(cmd))
        stdout = subprocess.check_output(cmd)
        print(stdout.decode("utf-8"))

        # Copy out the JSON files into the QC output tree, with slight reformatting
        # to fit with SQUAT requirements
        anatdir_out = os.path.join(f'{d}/mriqc', f'sub-{subjid}', 'ses-1', 'anat')
        qcdir_out = os.path.join(subjdir, outpath)
        if os.path.isfile(t1):
            json_in = os.path.join(anatdir_out, f'sub-{subjid}_ses-1_T1w.json')
            json_out = os.path.join(qcdir_out, "t1.json")
            _mriqc_to_squat(json_in, json_out)
        if os.path.isfile(t2):
            json_in = os.path.join(anatdir_out, f'sub-{subjid}_ses-1_T2w.json')
            json_out = os.path.join(qcdir_out, "t2.json")
            _mriqc_to_squat(json_in, json_out)

def _mriqc_to_squat(json_in, json_out):
    squat_data = {}
    with open(json_in, 'r') as f:
        mriqc_data = json.load(f)
        for k, v in mriqc_data.items():
            if isinstance(v, (float, int)):
                squat_data[f"qc_mriqc_{k}"] = v
    print(squat_data)
    with open(json_out, 'w') as f:
        json.dump(squat_data, f, sort_keys=True, indent=4, separators=(',', ': '))