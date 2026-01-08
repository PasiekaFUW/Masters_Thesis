import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import uproot as upr
import awkward as ak
from matplotlib.colors import LogNorm
import shutil
import os
import mplhep as hep
import matplotlib.pyplot as plt
import numba as nb
import re
from numba import jit

# Set the style for matplotlib and mplhep

#hep.style.use("CMS")
params = {'legend.fontsize': 'xx-large',
          'figure.figsize': (5, 5),
          'axes.labelsize': 'xx-large',
          'axes.titlesize':'xx-large',
          'xtick.labelsize':'xx-large',
          'ytick.labelsize':'xx-large',
          'patch.linewidth': 3}
plt.rcParams.update(params)

colors = ['red', 'blue', 'green', 'darkorange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']


# Make a filename with only alphanumeric characters
def sanitize_filename(filename):
    return re.sub(r'\W+', '_', filename)

# Make the labels shorter example: SAMuon:prompt -> p SAMuon:displaced -> d
def shorten_labels(labels):
    shortened = []
    for label in labels:
        if ':' in label:
            parts = label.split(':')
            shortened.append(parts[1][0])
        else:
            shortened.append(''.join(word[0] for word in label.split()))
    return shortened


# Plot 1D histogram with comparison of multiple datasets
def histogram_1D_comparison(datasets, dataset_labels, column, bins, xlabel, ylabel, title, fig_path, save=False, range=None):
    plt.figure()
    
    for i, data in enumerate(datasets):
        plt.hist(data[column], bins=bins, histtype='step', color=colors[i % len(colors)], linewidth=params['patch.linewidth'], range=range, label=dataset_labels[i])
    
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(f"{title}")
    plt.legend()
    plt.grid(True)
    
    hep.cms.text("Private")

    if save:
        short_labels = shorten_labels(dataset_labels)
        sanitized_title = sanitize_filename(f"{title}_{xlabel}_{'_'.join(short_labels)}")
        plt.savefig(os.path.join(fig_path, sanitized_title + '.png'))
        print(f"Saved figure to {os.path.join(fig_path, sanitized_title + '.png')}")
    else:
        # plt.show()
        print('')


# Plot 2D histogram 
def histogram_2D(data, column1, column2, bins, xlabel, ylabel, title, fig_path, save=False, log_scale=False, range=None):
    plt.figure()
    if log_scale:
        h = plt.hist2d(data[column1], data[column2], bins=bins, norm=LogNorm(), range=range)
        plt.colorbar(h[3], ax=plt.gca())
    else:
        plt.hist2d(data[column1], data[column2], bins=bins, range=range)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(f"{title}")
    
    hep.cms.text("Private")

    if save:
        sanitized_title = sanitize_filename(f"{title}_{ylabel}")
        plt.savefig(os.path.join(fig_path, sanitized_title + '.png'))
    else:   
        # plt.show()
        print('')


# Calculate mean values for histogram bins
def calculate_mean(data, column1, column2, bins):
    data['bin'] = pd.cut(data[column1], bins=bins)
    mean_values = data.groupby('bin', observed=False)[column2].mean()
    min_values = data.groupby('bin', observed=False)[column2].min()
    max_values = data.groupby('bin', observed=False)[column2].max()
    std_errors = data.groupby('bin', observed=False)[column2].sem()
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    return bin_centers, mean_values, (-min_values+mean_values, max_values-mean_values)


# Plot mean values with error bars for comparison of multiple datasets
def plot_mean_comparison(datasets, dataset_labels, column1, column2, bins, xlabel, ylabel, title, fig_path, save=False,density=False):
    plt.figure()
    
    for i, data in enumerate(datasets):
        bin_centers, mean_values, std_errors = calculate_mean(data, column1, column2, bins)
        plt.errorbar(bin_centers, mean_values, yerr=std_errors, fmt='o', markersize=10, color=colors[i % len(colors)], ecolor=colors[i % len(colors)], capsize=5, linestyle='None', linewidth=2, label=dataset_labels[i])
    
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(f"{title}")
    if density:
        plt.ylim(-0.02, 1.05)
    plt.legend()
    plt.grid(True)
    
    hep.cms.text("Private")

    if save:
        short_labels = shorten_labels(dataset_labels)
        sanitized_title = sanitize_filename(f"{title}_{ylabel}_{'_'.join(short_labels)}")
        print(f"Saved figure to {os.path.join(fig_path, sanitized_title + '.png')}")
        plt.savefig(os.path.join(fig_path, sanitized_title + '.png'))
    else:
        # plt.show()
        print('')

# Plot efficiency comparison of multiple datasets
def plot_efficiency_comparison(datasets_numerator, datasets_denominator, dataset_labels, column, bins, 
                               xlabel, ylabel, title, fig_path, save=False, ptCut=0):
    plt.figure()
    
    for i, (data_num, data_den) in enumerate(zip(datasets_numerator, datasets_denominator)):
        filtered_data_num = data_num[data_num['theL1Obj.pt'] >= ptCut]
        hist1 = np.histogram(filtered_data_num[column], bins=bins)
        hist2 = np.histogram(data_den[column], bins=bins)
        with np.errstate(divide='ignore', invalid='ignore'):  
            eff = np.nan_to_num(hist1[0] / hist2[0], nan=0.0)
            eff_err = np.sqrt(eff * (1 - eff) / np.where(hist2[0] > 0, hist2[0], 1))
        bin_centers = 0.5 * (bins[1:] + bins[:-1])

        plt.errorbar(bin_centers, eff, yerr=eff_err, fmt='o', markersize=10, color=colors[i % len(colors)], ecolor=colors[i % len(colors)], capsize=5, linestyle='None', linewidth=2, label=dataset_labels[i])
    
    # Add vertical line for ptCut
    plt.axvline(ptCut, color='black', linestyle='--', linewidth=2, label=f'$p_T$ cut: {ptCut} GeV')

    #plt.xscale('log')  # Set x-axis to log scale
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.ylim(-0.02, 1.05)
    plt.title(f"{title}")
    plt.legend()
    plt.grid(True, which="both", linestyle='--', linewidth=0.5)
    
    hep.cms.text("Private")

    if save:
        short_labels = shorten_labels(dataset_labels)
        sanitized_title = sanitize_filename(f"{title}_{ylabel}_{'_'.join(short_labels)}")
        plt.savefig(os.path.join(fig_path, sanitized_title + '.png'))
    else:
        # plt.show()
        print('')



# Plot efficiency for one dataset, different ptCuts

def plot_efficiency_ptCuts_single_dataset(data_numerator, data_denominator, dataset_label, column, bins, xlabel, ylabel, title, fig_path, save=False, ptCuts=[0]):
    if save==True:
        plt.figure()
    
    for i, ptCut in enumerate(ptCuts):
        hist1 = np.histogram(data_numerator[data_numerator['theL1Obj.pt'] >= ptCut][column], bins=bins)
        hist2 = np.histogram(data_denominator[column], bins=bins)

        with np.errstate(divide='ignore', invalid='ignore'):  
            eff = np.nan_to_num(hist1[0] / hist2[0], nan=0.0)
            eff_err = np.sqrt(eff * (1 - eff) / np.where(hist2[0] > 0, hist2[0], 1))
        bin_centers = 0.5 * (bins[1:] + bins[:-1])

        label_text = f'$p_T$ cut: {ptCut} GeV' if ptCut != 0 else 'No $p_T$ cut'
        plt.errorbar(bin_centers, eff, yerr=eff_err, fmt='o', markersize=10, color=colors[i % len(colors)], ecolor=colors[i % len(colors)], capsize=5, linestyle='None', linewidth=2, label=label_text)

    if save:
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(f"{title}  {dataset_label}")
        plt.ylim(-0.02, 1.05)
        plt.legend()
        plt.grid(True) 
        hep.cms.text("Private")
        short_label = shorten_labels([dataset_label])
        sanitized_title = sanitize_filename(f"{title}_{ylabel}_ptCuts_{short_label}")
        plt.savefig(os.path.join(fig_path, sanitized_title + '.png'))
    else:
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(f"{title}  {dataset_label}")
        hep.cms.text("Private")
        plt.ylim(-0.02, 1.05)
        plt.legend()
        plt.grid(True) 



# Plot efficiency for three eta ranges (EMTF, OMTF, BMTF) in one figure
def plot_3_eta_ranges(data_numerator, data_denominator, dataset_label, column, bins, xlabel, ylabel, title, fig_path, save=False, ptCuts=[0]):
    fig, axs = plt.subplots(1, 3)  

    filtered_numerator_BMTF = data_numerator[abs(data_numerator['theColl._eta']) < 0.83]
    filtered_denominator_BMTF = data_denominator[abs(data_denominator['theColl._eta']) < 0.83]

    filtered_numerator_OMTF = data_numerator[(abs(data_numerator['theColl._eta']) >= 0.83) & (abs(data_numerator['theColl._eta']) <= 1.24)]
    filtered_denominator_OMTF = data_denominator[(abs(data_denominator['theColl._eta']) >= 0.83) & (abs(data_denominator['theColl._eta']) <= 1.24)]

    filtered_numerator_EMTF = data_numerator[(abs(data_numerator['theColl._eta']) > 1.24) & (abs(data_numerator['theColl._eta']) <= 2.4)]
    filtered_denominator_EMTF = data_denominator[(abs(data_denominator['theColl._eta']) > 1.24) & (abs(data_denominator['theColl._eta']) <= 2.4)]

    plt.sca(axs[0])
    plot_efficiency_ptCuts_single_dataset(filtered_numerator_BMTF, filtered_denominator_BMTF, 'BMTF', column, bins, xlabel, ylabel, '', fig_path, save=False, ptCuts=ptCuts)

    plt.sca(axs[1])
    plot_efficiency_ptCuts_single_dataset(filtered_numerator_OMTF, filtered_denominator_OMTF, 'OMTF', column, bins, xlabel, ylabel, '', fig_path, save=False, ptCuts=ptCuts)

    plt.sca(axs[2])
    plot_efficiency_ptCuts_single_dataset(filtered_numerator_EMTF, filtered_denominator_EMTF, 'EMTF', column, bins, xlabel, ylabel, '', fig_path, save=False, ptCuts=ptCuts)

    plt.suptitle(f"{title} - {dataset_label}") 

    for ax in axs:
        ax.set_xlabel(xlabel)  
        ax.set_ylabel(ylabel) 
        ax.tick_params(axis='both', which='major')  

    plt.tight_layout()

    if save:
        short_label = shorten_labels([dataset_label])
        sanitized_title = sanitize_filename(f"{title}_{ylabel}_{short_label}_3plots")
        plt.savefig(os.path.join(fig_path, sanitized_title + '.png'))
    else:
        # plt.show() 
        print('')


