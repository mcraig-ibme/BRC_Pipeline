"""
mriqc.py: BRC script to run QC on Eddy output
"""
from utils import runcmd

def run_eddyqc(subjid, subjdir, eddypath, outpath):
    print(f" - Running Eddy QC in {subjdir}/{eddypath}")
    cmd = [
        'squat_eddy',
        '--eddydir', os.path.join(subjdir, eddypath),
        '--eddybase', 'eddy_unwarped_images',
        '--idx', 'index.txt',
        '--bvals', 'Pos.bval',
        '--bvecs', 'Pos.bvec',
        '--eddy-params', 'acqparams.txt',
        '--mask', 'nodif_brain_mask.nii.gz',
        '--overwrite', '-o', outpath,
    ]
    runcmd(cmd)
