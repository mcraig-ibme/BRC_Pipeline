#!/bin/bash
#
# Simple wrapper to run Python implementation
#
# Copyright 2022 University of Nottingham

set -e

${FSLDIR}/bin/fslpython ${BRC_DELTAB_SCR}/fit_brain_age.py $@
