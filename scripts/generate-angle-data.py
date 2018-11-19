#!/usr/bin/python3

import os
import dynein.run as run
import glob
import numpy as np
import argparse
import subprocess
import sys

sys.path.insert(0, os.getcwd() + "/data/")
import paper_params as params

runtime = 5e-2
framerate = 1e-10

basename = "paper_stroke_angles"

os.system("python3 scripts/generate-stepping-data.py" \
          + " --ls " + str(params.ls)\
          + " --lt " + str(params.lt)\
          + " --kub " + str(params.stroke_angle_k_ub)\
          + " --kb  " + str(params.stroke_angle_k_b)\
          + " --cb " + str(params.cb)\
          + " --cm " + str(params.cm)\
          + " --ct " + str(params.ct)\
          + " --eqb " + str(params.eqb)\
          + " --eqt " + str(params.eqt)\
          + " --eqmpre " + str(params.eqmpre)\
          + " --eqmpost " + str(params.eqmpost)\
          + " --unbindingconst " + str(params.cexp)\
          + " --runtime " + str(runtime)\
          + " --framerate " + str(framerate)\
          + " --seed " + str(params.stroke_angle_seed)\
          + " --label paper_stroke_angles"\
          + " --renameangles"\
          + " --anglemode")
