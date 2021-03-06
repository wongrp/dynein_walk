import numpy as np
import matplotlib.pyplot as plt
import scipy.constants
import sys
sys.path.append("../data")
import importlib
import argparse
import subprocess
import bb_energy_distribution

params = importlib.import_module("params")

prob = []

angles = [[] for i in range(2)]

C =  params.for_simulation['exp-unbinding-constant']         # exponential binding constant from paper_params.py April 12


L = 24         # Length
b = 1

eqb_angle = params.for_simulation['eqb']
if bb_energy_distribution.eq_in_degrees:
        eqb_angle = eqb_angle*np.pi/180

max_P = 0.1
x = 0
while x < 9:
        # Making random motor angles
        nma = np.random.uniform(0, 2*np.pi)
        fma = np.random.uniform(0, 2*np.pi)

        dynein = bb_energy_distribution.DyneinBothBound(nma, fma, params, L)

        # Checking if energy is nan
        if np.isnan(dynein.E_total) == True:
                continue
        else:
                # Calculating partition function
                P = np.exp(-b*dynein.E_total)
                if P > max_P:
                        max_P = P
                        x = 0
                        angles[0] = []
                        angles[1] = []
                P = P/max_P

                rate_trailing = np.exp(C*(dynein.nba - eqb_angle))
                rate_leading = np.exp(C*(dynein.fba - eqb_angle))

                prob_trailing = P*rate_trailing
                prob_leading = P*rate_leading

                if np.random.random() < P:
                        angles[0].append(nma)
                        angles[1].append(fma)
                        x = x + 1

                if prob_trailing > prob_leading:
                    prob.append(prob_trailing)
                else:
                    prob.append(prob_leading)

def rad_to_deg(angle):
    return angle*180/np.pi

def plot_bb_energy_distribution(self, d1, d2, d3, d4, d5, d6, d7, d8, d9):
    """Plot the energy distribution for the both bound configuration given an
    array of motor angles and an initial displacement.
    """

    fig = plt.figure(figsize=(10,15))

    # make contourf graph
    ax1 = fig.add_subplot(1, 1, 1)
    ProbabilityPlot = ax1.contourf(rad_to_deg(self.nma), rad_to_deg(self.fma), self.prob_trailing/np.nanmax(self.prob_trailing), 100)
    contour = ax1.contour(rad_to_deg(self.nma), rad_to_deg(self.fma), self.prob_trailing/np.nanmax(self.prob_trailing), np.linspace(0, 1, 5), colors='w', linewidth=10)
    ax1.set_xlabel(r'$\theta_{nm}$', fontsize=60)
    ax1.set_ylabel(r'$\theta_{fm}$', fontsize=60)
    ax1.set_xticks(np.linspace(0, 360, 13))
    ax1.set_yticks(np.linspace(0, 360, 13))
    cb = plt.colorbar(ProbabilityPlot)
    cb.set_label(r"Probability", fontsize=40)
    cb.set_ticks(np.linspace(0, 1, 5))
    cb.add_lines(contour)

    # find the extrema
    j_max, i_max, j_min, i_min = self.find_energy_extrema()
    marker_size = 300
    # ax1.scatter(rad_to_deg(self.nma)[i_min, j_min], rad_to_deg(self.fma)[i_min, j_min], s = marker_size, color='black')
    ax1.scatter(rad_to_deg(d1.nma), rad_to_deg(d1.fma), s=marker_size, color='red')
    ax1.scatter(rad_to_deg(d2.nma), rad_to_deg(d2.fma), s=marker_size, color='orange')
    ax1.scatter(rad_to_deg(d3.nma), rad_to_deg(d3.fma), s=marker_size, color='lime')
    ax1.scatter(rad_to_deg(d4.nma), rad_to_deg(d4.fma), s=marker_size, color='blue')
    ax1.scatter(rad_to_deg(d5.nma), rad_to_deg(d5.fma), s=marker_size, color='gray')
    ax1.scatter(rad_to_deg(d6.nma), rad_to_deg(d6.fma), s=marker_size, color='magenta')
    ax1.scatter(rad_to_deg(d7.nma), rad_to_deg(d7.fma), s=marker_size, color='green')
    ax1.scatter(rad_to_deg(d8.nma), rad_to_deg(d8.fma), s=marker_size, color='purple')
    ax1.scatter(rad_to_deg(d9.nma), rad_to_deg(d9.fma), s=marker_size, color='sienna')

    ax1.set_aspect('equal')
    # ax2 = fig.add_subplot(1, 2, 2)
    # x_coords_min = [self.r_nb[0,i_min, j_min],
    #                 self.r_nm[0,i_min, j_min],
    #                 self.r_t[0,i_min, j_min],
    #                 self.r_fm[0,i_min, j_min],
    #                 self.r_fb[0,i_min, j_min]]
    # y_coords_min = [self.r_nb[1,i_min, j_min],
    #                 self.r_nm[1,i_min, j_min],
    #                 self.r_t[1,i_min, j_min],
    #                 self.r_fm[1,i_min, j_min],
    #                 self.r_fb[1,i_min, j_min]]


    # ax2.plot(x_coords_min, y_coords_min, color='black', label='Minimum Energy', linewidth=3)
    # ax2.plot([-6, 30], [0, 0], color = 'black', linestyle='-', linewidth=3)
    # ax2.axis('off')
    # ax2.axis('equal')
    # ax2.legend()
    plt.savefig('../papers/jin-poster/poster-probability-plot.svg', transparent=True)
    plt.savefig('../papers/jin-poster/poster-probability-plot.png', transparent=True)


def plot_bb_figures(self, dynein_color):
    """Plot just the figure of dynein for the both bound configuration given an
    array of motor angles and an initial displacement.
    """
    fig = plt.figure()

    ax = fig.add_subplot(1, 1, 1)
    x_coords = [self.r_nb[0],
                    self.r_nm[0],
                    self.r_t[0],
                    self.r_fm[0],
                    self.r_fb[0]]
    y_coords = [self.r_nb[1],
                    self.r_nm[1],
                    self.r_t[1],
                    self.r_fm[1],
                    self.r_fb[1]]

    ax.plot(x_coords, y_coords, color= dynein_color, linewidth=3)
    ax.plot([-6, 30], [0, 0], color = 'black', linestyle='-', linewidth=3)
    ax.axis('off')
    ax.axis('equal')
    ax.legend()
    plt.savefig('../papers/jin-poster/poster-stick-figure-{}.svg'.format(dynein_color), transparent=True)
    plt.savefig('../papers/jin-poster/poster-stick-figure-{}.png'.format(dynein_color), transparent=True)

dynein1 = bb_energy_distribution.DyneinBothBound(angles[0][0], angles[1][0], params, L)
dynein2 = bb_energy_distribution.DyneinBothBound(angles[0][1], angles[1][1], params, L)
dynein3 = bb_energy_distribution.DyneinBothBound(angles[0][2], angles[1][2], params, L)
dynein4 = bb_energy_distribution.DyneinBothBound(angles[0][3], angles[1][3], params, L)
dynein5 = bb_energy_distribution.DyneinBothBound(angles[0][4], angles[1][4], params, L)
dynein6 = bb_energy_distribution.DyneinBothBound(angles[0][5], angles[1][5], params, L)
dynein7 = bb_energy_distribution.DyneinBothBound(angles[0][6], angles[1][6], params, L)
dynein8 = bb_energy_distribution.DyneinBothBound(angles[0][7], angles[1][7], params, L)
dynein9 = bb_energy_distribution.DyneinBothBound(angles[0][8], angles[1][8], params, L)

plot_bb_figures(dynein1, 'red')
plot_bb_figures(dynein2, 'orange')
plot_bb_figures(dynein3, 'lime')
plot_bb_figures(dynein4, 'blue')
plot_bb_figures(dynein5, 'gray')
plot_bb_figures(dynein6, 'magenta')
plot_bb_figures(dynein7, 'green')
plot_bb_figures(dynein8, 'purple')
plot_bb_figures(dynein9, 'sienna')

print("dynein1 nma: {0} fma: {1}".format(dynein1.nma, dynein1.fma))
print("dynein2 nma: {0} fma: {1}".format(dynein2.nma, dynein2.fma))
print("dynein3 nma: {0} fma: {1}".format(dynein3.nma, dynein3.fma))
print("dynein4 nma: {0} fma: {1}".format(dynein4.nma, dynein4.fma))
print("dynein5 nma: {0} fma: {1}".format(dynein5.nma, dynein5.fma))
print("dynein6 nma: {0} fma: {1}".format(dynein6.nma, dynein6.fma))
print("dynein7 nma: {0} fma: {1}".format(dynein7.nma, dynein7.fma))
print("dynein8 nma: {0} fma: {1}".format(dynein8.nma, dynein8.fma))
print("dynein9 nma: {0} fma: {1}".format(dynein9.nma, dynein9.fma))

num_points = 500
nma1 = np.linspace(0, 2*np.pi, num_points)
fma1 = np.linspace(0, 2*np.pi, num_points)
NMA, FMA = np.meshgrid(nma1, fma1)
dynein_24 = bb_energy_distribution.DyneinBothBound(NMA, FMA, params, L=24)
plot_bb_energy_distribution(dynein_24, dynein1, dynein2, dynein3, dynein4, dynein5, dynein6, dynein7, dynein8, dynein9)

plt.show()
