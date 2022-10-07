"""
Install script for BRC pipeline
"""
import glob
import logging
import os
import shutil
import stat
import sys

LOG = logging.getLogger(__name__)
SRCDIR = os.path.abspath(os.path.dirname(sys.argv[0]))

def srcfile(name):
    """:return: Path to file in source tree"""
    return os.path.join(SRCDIR, name)

def srcfile_read(name):
    """:return: Contents of text file in source tree"""
    with open(srcfile(name), encoding="utf-8") as f:
        return f.read()

def parent_is_writable(d):
    """:return: True if parent directory is writable, False otherwise"""
    parent_dir = os.path.dirname(d)
    return os.access(parent_dir, os.W_OK)

def creatable_dir(prompt, defaults):
    """:return: Path to directory chosen by user which they have permission to create"""
    default = ""
    for d in defaults:
        if parent_is_writable(d):
            default = d

    response = input(f"{prompt} [{default}]: ").strip()
    if not response:
        response = default
    if os.path.exists(response):
        raise ValueError(f"Specified directory {response} already exists")
    elif not parent_is_writable(response):
        raise ValueError(f"You do not have permission to create the directory {response}")
    return response

def have_files(d, check_files):
    """:return: True if all relative paths in check_files exist in d, False otherwise"""
    for f in check_files:
        if not os.path.exists(os.path.join(d, f)):
            return False
    return True

def find_package(package_name, *check_files, search=(), optional=False):
    """
    Find the directory containing a package
    
    :param check_files: Relative paths to files to check if directory looks right (e.g. bin/fslmaths
    :param search: Sequence of paths to check to find default (may contain globs)
    :param optional: If True, give error if no suitable directory is given
    """
    default = ""
    for g in search:
        for d in glob.glob(g):
            LOG.debug(f"Looking for {package_name} in {d}")
            if have_files(d, check_files):
                LOG.debug("FOUND")
                default = d
                break

    prompt = f"Location of {package_name} installation"
    if default:
        prompt += f" [{default}]"
    response = input(prompt + ": ").strip()
    if not response:
        response = default

    if not response:
        if optional:
            return None
        else:
            raise ValueError(f"{package_name} is required")
    elif not os.path.isdir(response):
        raise ValueError(f"Specified directory {response} does not exist or is not a directory")
    if not have_files(response, check_files):
        raise ValueError(f"Expected file {f} not found in directory {response}")
    return response

def yesno(prompt, default):
    """:return: True if response looks like a yes, False otherwise"""
    response = input(f"{prompt} [{default}]").strip().lower()
    return response in ("y", "yes")

def copyall(src, dst, exclude=()):
    """Copy all files and directories in src to dest, excluding those with basenames in exclude"""
    os.makedirs(dst, exist_ok=True)
    for item in os.listdir(src):
        if os.path.basename(item) in exclude:
            continue
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copyall(s, d, exclude=exclude)
        else:
            shutil.copy2(s, d)
            if s.endswith(".sh"):
                os.chmod(s, os.stat(s).st_mode | stat.S_IEXEC)

brc_files = ["version.txt", "product.txt"]
for f in brc_files:
    if not os.path.exists(srcfile(f)):
        raise ValueError(f"Couldn't find expected BRC pipeline file: {f} - it should be in the same folder as this script")

product = srcfile_read("product.txt")
version = srcfile_read("version.txt")
if product.lower().strip() != "brc pipeline":
    raise ValueError(f"Contents of product.txt file did not contain 'BRC pipeline'")

LOG.info(f"BRC Pipeline installer {version}\n")

home = os.path.expanduser("~")
destdir_defaults = ["/usr/local/BRC_Pipeline", f"{home}/BRC_Pipeline"]
destdir = creatable_dir("Installation directory for BRC pipeline", destdir_defaults)

clustermode = yesno("Are you installing the BRC pipeline on a cluster with queueing system (e.g. Slurm)?", "No")
#lmodmode = yesno("Do you want to use the LMOD/MODULE system for dependency resolution?", "No")

fsldir = find_package("FSL", "bin/fslmaths", search=["/usr/local/fsl*", "/opt/fsl*"])
fsdir = find_package("Freesurfer", search=["/usr/local/freesurfer*"], optional=True)
matlabdir = find_package("Matlab", search=["/usr/local/matlab*"], optional=True)
spmdir = find_package("SPM", search=["/usr/local/SPM/*"], optional=True)
dvarsdir = find_package("DVARS", ["/usr/local/DVARS*"], optional=True)
antsdir = find_package("ANTS", ["/usr/local/ANTs*"], optional=True)
c3ddir = find_package("C3D", ["/usr/local/c3d*"], optional=True)
cudadir = find_package("Cuda", ["/usr/local/cuda*"], optional=True)
cudimotdir = find_package("CUDIMOT", ["/usr/local/cudimot*"], optional=True)

pipelines = {
    "BRC_structural_pipeline" : "SCTRUC", # FIXME is this a typo?
    "BRC_diffusion_pipeline" : "DMRI",
    "BRC_functional_pipeline" : "fMRI",
    "BRC_perfusion_pipeline" : "PMRI",
    "BRC_func_group_analysis" : "FMRI_GP",
    "BRC_IDP_extraction" : "IDPEXTRACT",
    "global" : "GLOBAL",
}

os.makedirs(destdir)
copyall(SRCDIR, destdir, exclude=["install.py"])

setup_script = os.path.join(destdir, "SetUpBRCPipeline.sh")
with open(setup_script, "w") as setup:

    setup.write('#!/usr/bin/env bash\n')
    setup.write('# Setup script for BRC pipeline\n\n')
    setup.write('# Autogenerated by brc_install.py\n') # FIXME timestamp
    setup.write('# Copyright 2018 University of Nottingham\n\n')

    cluster = "YES" if clustermode else "NO"
    setup.write(f'export CLUSTER_MODE="{clustermode}"\n\n')

    if not clustermode:
        # Setup FSL (if not already done so in the running environment)
        setup.write(f'export FSLDIR="{fsldir}"\n')
        setup.write(f'. $FSLDIR/etc/fslconf/fsl.sh\n')
        setup.write(f'export FSLCONFDIR=${{FSLDIR}}/config\n')
        setup.write(f'export FSLOUTPUTTYPE="NIFTI_GZ"\n\n')

        # Setup FreeSurfer (if not already done so in the running environment)
        setup.write(f'export FREESURFER_HOME="{fsdir}"\n')
        setup.write(f'source $FREESURFER_HOME/SetUpFreeSurfer.sh\n\n')

        setup.write(f'export MATLABpath="{matlabdir}"\n\n')

        # Set libraries for Eddy FIXME seems to want FSL 5.0.11
        #setup.write('export FSLDIR_5_0_11="/usr/local/fsl-5.0.11"
        setup.write(f'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:{cudadir}/lib64')

    setup.write(f'export BRCDIR="{destdir}"\n')
    for name, env in pipelines.items():
        subdir = f"BRC_{name}"
        LOG.info(f'Setting up variables for pipeline: {subdir}')
        setup.write(f'export BRC_{env}_DIR="${{BRCDIR}}/{subdir}"\n')
        setup.write(f'export BRC_{env}_SCR="${{BRC_{env}_DIR}}/scripts"\n')

    # SETUP MATLAB and LIBRARIES
    setup.write(f'\nexport SPMpath="{spmdir}"\n') # Functional pipeline - slice timing correction
    setup.write(f'export DVARSpath="{dvarsdir}"\n') # Functional pipeline - QC
    setup.write(f'export ANTSPATH="{antsdir}"\n') # Structural pipeline
    setup.write(f'export C3DPATH="{c3ddir}"\n') # Structural pipeline
    setup.write(f'export CUDIMOT="{cudimotdir}"\n\n') # FIXME not used???

    setup.write(f'PATH=$PATH:$BRC_SCTRUC_DIR:$BRC_DMRI_DIR:$BRC_FMRI_DIR:$BRC_PMRI_DIR:$BRC_FMRI_GP_DIR:$BRC_IDPEXTRACT_DIR\n')
    setup.write(f'export PATH\n')
