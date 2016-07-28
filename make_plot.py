#! /usr/bin/env python2.7

import csv
import getopt
import matplotlib.pyplot as plt
import numpy as np
#import pandas
import sys

from matplotlib.offsetbox import AnchoredOffsetbox, TextArea

plot_params, data_files = getopt.getopt(sys.argv[1:], "f:x:y:ph:sxykm:", ["figtitle=", "xlabel=", "ylabel=", "showplot", "hline=", "scatter", "logx", "logy", "skiprows=", "ymax="])

showplot = False
hline = False
scatter = False
logx = False
logy = False
ymax = False

skiprows = 1

for param, value in plot_params:
    if (param == "--figtitle"):
        title_list = ([' ' if (a == '_') else a for a in value])
        title = ''.join(title_list)
    elif (param == "--xlabel"):
        xlabel = value
    elif (param == "--ylabel"):
        ylabel = value
    elif (param == "--showplot"):
        showplot = True
    elif (param == "--hline"):
        hline = True
        hlineval = value
    elif (param == "--scatter"):
        scatter = True
    elif (param == "--logx"):
        logx = True
    elif (param == "--logy"):
        logy = True
    elif (param == "--skiprows"):
        skiprows = int(value)
    elif (param == "--ymax"):
        ymax = True
        ymax_val = float(value)

ax = plt.gca()
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width*0.7, box.height])

max_x_value = 0
colors = ['b', 'g', 'r', 'm']

for data_file in data_files:
    if (data_file.find("config") == -1):
        f = open(data_file, 'r')
        opt_str = f.readline()[0:-1].split(', ')
        opts, _ = getopt.getopt(opt_str, "l:h:", ["legend=", "hline="])
        data_hline = False
        for opt, value in opts:
            if opt == "--legend":
                legend = "".join([x if x != "'" else '' for x in value])
            elif opt == "--hline":
                data_hline = True
                data_hlineval = float("".join([x if x != "'" else '' for x in value]))
        f.close()

        line = np.loadtxt(data_file, skiprows=2)
        #line = pandas.read_csv(data_file, skiprows=1)
        X = line[:,0]
        Y = line[:,1]
        X = X[::skiprows]
        Y = Y[::skiprows]

        c = colors.pop()
        if data_hline:
            plt.plot([0, max(X)], [data_hlineval, data_hlineval], color=c, linestyle="dashed")

        if (not scatter):
            plt.plot(X, Y, label=legend, color=c)
        else:
            plt.scatter(X,Y, label=legend, color=c, s=1)

        if max(X) > max_x_value:
            max_x_value = max(X)
    else:
        f = open(data_file, 'r')
        config_txt = f.read()
        box = TextArea(config_txt, textprops=dict(size=10))
        anchored_box = AnchoredOffsetbox(loc=2, child=box, bbox_to_anchor=(1,1),
                                         bbox_transform=ax.transAxes, frameon=False)

if hline:
    plt.plot([0, max_x_value], [hlineval, hlineval], color='k', linestyle="dashed")

plt.title(title)
plt.xlabel(xlabel)
plt.ylabel(ylabel)

plt.legend(fontsize="small", loc="lower left", framealpha=0.0, bbox_to_anchor=(1, 0))
ax.add_artist(anchored_box)

plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))

if ymax:
    ylims = plt.ylim()
    if (ylims[1] > ymax_val):
        plt.ylim([0, ymax_val])

if logx:
    ax.set_xscale('log')

if logy:
    ax.set_yscale('log')

if showplot:
    plt.show()
else:
    plt.savefig("plots/" + title.replace(" ", "_") + ".pdf", format="pdf")
