#!/usr/bin/python3
import argparse
import os, sys
import numpy as np
import dynein.run as run

runtime = 5
seeds = [1, 2, 3, 4]

sims = []
sims.append({"cb" : "0.1", "cm" : "1.5", "ct" : "0.6", "kb" : "100000000", "kub" : "100"})

for sim in sims:
    for s in seeds:
        os.system("rq run --job-name paperexponentialhisto-" + str(s) \
                  + " python3 scripts/generate-stepping-data.py" \
                  + " --kub " + sim["kub"] \
                  + " --kb " + sim["kb"] \
                  + " --cb " + sim["cb"] \
                  + " --cm " + sim["cm"] \
                  + " --ct " + sim["ct"] \
                  + " --seed " + str(s) \
                  + " --unbindingconst 5.0" \
                  + " --label paperexponentialhisto-" + str(s)\
                  + " --renameexponential"\
                  + " --runtime " + str(runtime))
