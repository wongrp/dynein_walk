#!/usr/bin/python3

import os
import dynein.run as run
import glob
import numpy as np
import argparse

parser = argparse.ArgumentParser(description="script to generate stepping "
                                 "data for specified parameters and record stepping statistics")

parser.add_argument('-k_b', '--binding', dest='k_b', action='store', type=float,
                    default=1e8, help="pre-exponential binding constant", metavar='')
parser.add_argument('-k_ub', '--unbinding', dest='k_ub', action='store', type=float,
                    default=100, help="pre-exponential unbinding constant", metavar='')
parser.add_argument('-t', '--runtime', dest='runtime', action='store', type=float,
                    default=1.0, help='total runtime for simulation in seconds', metavar='')
parser.add_argument('-exp', '--exp-unbinding-constant', dest='exp_unbinding_constant',
                    action='store', type=float, default=0.0, help="exponential unbinding constant", metavar='')
parser.add_argument('-s', '--seed', dest ='seed', action='store', type=float,
                    default=1.0, help ="random number seed", metavar='')
parser.add_argument('-f', '--logfile', dest='logfile', action='store', type=str,
                    default='data/parameterSearch/testedParameters.csv', help=".txt file for logging stepping statistics", metavar='')

args = parser.parse_args()


if os.path.exists('parameter_search.py'):
    os.chdir('../')
os.system("make generate_stepping_data")


basename = run.sim(**{"k_b": args.k_b,
                      "k_ub": args.k_ub,
                      "cb": 0.1,
                      "cm": 0.4,
                      "ct": 0.2,
                      "ls": 10.49,
                      "lt": 23.8,
                      "eqb": 120,
                      "eqmpre": 200,
                      "eqmpost": 224,
                      "eqt": 0,
                      "dt": 1e-10,
                      "label": "paramSearch",
                      "seed": args.seed,
                      "runtime": args.runtime,
                      "framerate": 1e-10,
                      "crash-movie": False,
                      "nomovie": True,
                      "exp-unbinding-constant": args.exp_unbinding_constant})

# print(os.getcwd())
# dataFile = glob.glob("data/stepping_data_paramSearch*.txt")
# if len(dataFile) is not 1:
#     print(len(dataFile))
#     print("Something went wrong. Make sure data was generated and that old paramSearch files have been deleted or renamed")
dataFile = "data/stepping_data_"+basename+".txt"

step_times = []
onebound_times = []
bothbound_times = []
step_lengths = []

data = np.loadtxt(dataFile)
print("Data loaded...")
bind_times = np.array(data[:, 1])
unbind_times = np.array(data[:, 0])
near_positions = np.around(np.array(data[:, 2]), decimals=7)
far_positions = np.around(np.array(data[:, 3]), decimals=7)
near_step_lens = near_positions[1:] - near_positions[:-1]
far_step_lens = far_positions[1:] - far_positions[:-1]

# add code to count "drunk" and "sober" steps for went front foot
# takes successive steps vs when the back foot steps like a normal
# person

onebound_times = bind_times[1:]-unbind_times[1:]
bothbound_times = unbind_times[1:]-bind_times[:-1]
step_lengths = near_step_lens + far_step_lens
step_times = onebound_times + bothbound_times

print("Calculating...")
max_ob_t = np.amax(onebound_times)
min_ob_t = np.amin(onebound_times)
max_bb_t = np.amax(bothbound_times)
min_bb_t = np.amin(bothbound_times)
max_nb_step = np.amax(near_step_lens)
min_nb_step = np.amin(near_step_lens)
max_fb_step = np.amax(far_step_lens)
min_fb_step = np.amin(far_step_lens)
total_steps = len(bind_times)
nb_disp = near_positions[-1]-near_positions[0]
fb_disp = far_positions[-1]-far_positions[0]

print("logging stepping statistics")

if not os.path.exists(args.logfile):
    os.system("touch {0}".format(args.logfile))
    with open(args.logfile, 'a') as file:
        s = "--ls 10.49, --lt 23.8, --cb 0.1, --cm 0.4, --ct 0.2, --dt 1e-10,  --seed 1, --framerate 1e-10, --eqb 120, --eqmpre 200, --eqmpost 224, --eqt 0, --nomovie"\
            "\n\nk_b,\tk_ub,\truntime,\texp_binding_constant,\tmax ob time,\tmin ob time,\tmax bb time,\tmin bb time,\tmax nb step,\tmin nb step,\tmax fb step,\t"\
            "min fb step,\ttotal steps,\tnbx disp,\tfbx disp"
        file.write(s)


with open("data/parameterSearch/testedParameters.csv", "a") as file:
    file.write("{0},\t{1},\t{2},\t{3},\t{4},\t{5},\t{6},\t{7},\t{8},\t{9},\t{10}, \t{11}, \t{12}, \t{13}, \t{14}\n".format(args.k_b, args.k_ub, args.runtime, args.exp_unbinding_constant, max_ob_t, min_ob_t, max_bb_t, min_bb_t, max_nb_step, min_nb_step, max_fb_step, min_fb_step, total_steps, nb_disp, fb_disp))

print(os.getcwd())
os.system("mv ./{3} data/parameterSearch/kb{0}_kub{1}_expbc{2}_t{4}_seed{5}.txt".format(args.k_b, args.k_ub, args.exp_unbinding_constant, dataFile, args.runtime, args.seed))

print("All done.")