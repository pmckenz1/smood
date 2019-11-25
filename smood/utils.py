#!/usr/bin/env python

import seaborn as sns
import numpy as np


def plot_density(density_mat):
    dens_mat = density_mat.copy()
    # set the dimensions
    sns.set(rc={'figure.figsize': (17, 12.016239316239318)})

    # look at the plot
    sns.heatmap(dens_mat,
                xticklabels=False,
                yticklabels=False,
                cbar=False,
                vmin=0,
                vmax=1)


def plot_threshold(density_mat,
                   threshold):
    # copy the table so that we don't directly edit it...
    thresh_mat = density_mat.copy()
    # set the dimensions
    sns.set(rc={'figure.figsize': (17, 12.016239316239318)})
    # for each cell...
    for row in range(thresh_mat.shape[0]):
        for col in range(thresh_mat.shape[1]):

            # take the value
            val = thresh_mat[row, col]

            # don't do anything to it if it's nan
            if val == np.nan:
                pass

            # set to one if it's over threshold
            elif val >= threshold:
                thresh_mat[row, col] = 1

            # set to zero if it's under threshold
            elif val < threshold:
                thresh_mat[row, col] = 0

    # look at the plot
    sns.heatmap(thresh_mat,
                xticklabels=False,
                yticklabels=False,
                cbar=False,
                vmin=0,
                vmax=2)
