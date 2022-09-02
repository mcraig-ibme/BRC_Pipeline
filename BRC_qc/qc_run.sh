#!/bin/bash
#
# Simple wrapper to run Python implementation
#
# Copyright 2022 University of Nottingham

set -e

${FSLDIR}/bin/fslpython ${BRC_QC_SCR}/qc_run.py $@
