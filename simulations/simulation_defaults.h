#ifndef SIMULATION_DEFAULTS_H
#define SIMULATION_DEFAULTS_H

const long long iterations = 1e11;
const long long data_generation_skip_iterations = 1e6;

const int num_corr_datapoints = 1000;
const double tau_runtime_fraction = 1e-5;
const int movie_num_frames = 1e2;

const int num_generate_pe_datapoints = 70;
const int num_generate_angle_datapoints = num_generate_pe_datapoints;
const int num_generate_force_datapoints = num_generate_pe_datapoints;

const int custom_generate_averaging_width = 1;

#include "custom_simulation_parameters.h"

#endif
