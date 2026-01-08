import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import uproot as upr
import awkward as ak
from termcolor import colored
from matplotlib.colors import LogNorm
import shutil
import os
from numba import jit
import warnings
#there is a future warning that is not important for now. 
warnings.simplefilter(action='ignore', category=FutureWarning)

# list of available functions:
# - load_data
# - refresh_fig_dir
# - calculate_dxy_Lxy_Lz_for_gen
# - match_gen_muons

unused_columns_gen = ['theColl._mass', 'theColl._id', 'theColl._mid','theColl._beta']
unused_columns_reco= ['theL1Obj.fUniqueID', 'theL1Obj.fBits', 'theL1Obj.z0', 'theL1Obj.d0', 'theL1Obj.disc','theL1Obj.hits']


# Loading data and extracting specific branches from ROOT files

def load_data(filename, path, tree, branch):
    # Open the ROOT file
    file = upr.open(path + filename)
    # Access the specified tree
    tree = file[tree]
    
    # Display available branches (commented out)
    # print("Available branches:", tree.keys())
    
    # Extract the specified branch as an awkward array
    arrays = tree.arrays(filter_name=branch)
    # Convert the awkward array to a pandas DataFrame
    data = ak.to_dataframe(arrays)
    # Add 'entry' and 'subentry' columns based on the index levels - useful when .root file contains nested lists
    data['entry'] = data.index.get_level_values(0)   
    data['subentry'] = data.index.get_level_values(1) 
    # Reset the index of the DataFrame
    data = data.reset_index(drop=True)
    # Explode the DataFrame to flatten nested lists
    data = data.explode(list(data.columns))  

    #remove unused columns

    if branch == 'genColl/theColl/theColl._*':
        data = data.drop(columns=unused_columns_gen)
        # Filter data to include only rows where 'subentry' (if in subentry 0 and 1 are duplicates) equals 0
        data = data[data['subentry'] == 0]
        # Calculate additional variables (dxy, Lxy, Lz) for gen-level data
        data = calculate_dxy_Lxy_Lz_for_gen(data)

        # Adjust the 'phi' value by adding \pi to shift the range to (0,2\pi)
        data.loc[:, 'theColl._phi'] = data['theColl._phi'] + np.pi
        data=data[abs(data['theColl._eta'])<2.4]

    elif branch == 'l1ObjColl/theL1Obj/theL1Obj.*' in branch:
        
        data = data.drop(columns=unused_columns_reco)

        # Apply transformations to normal eta and phi for theL1Obj.type == 10
        data_omtf = data[data['theL1Obj.type'] == 10].copy()

        data_omtf.loc[:, 'theL1Obj.eta'] = data_omtf['theL1Obj.eta'] / 240 * 2.61
        data_omtf.loc[:, 'theL1Obj.phi'] = ((15 + data_omtf['theL1Obj.iProcessor'] * 60) / 360 + data_omtf['theL1Obj.phi'] / 576) * 2 * np.pi
        data_omtf.loc[:, 'theL1Obj.pt'] = (data_omtf['theL1Obj.pt'] - 1) / 2
        data.update(data_omtf)

        data_SA = data[data['theL1Obj.type'] == 16].copy()
        data_SA['theL1Obj.phi'] = data_SA['theL1Obj.phi'] + np.pi
        data.update(data_SA)
        

    # Print information about the loaded data
    print(colored('Loading data from',"blue"), filename,f'tree: {tree.name}, branch: {branch}', end=' ')
    print(colored('Data shape:', "blue"),data.shape)

    return data





def refresh_fig_dir(fig_path, refresh=False):
    if refresh:
        try:
            # Remove the directory if it exists
            shutil.rmtree(fig_path)
        except FileNotFoundError:
            pass
        # Create the directory
        os.makedirs(fig_path, exist_ok=True)
        print('Directory refreshed')
    else: 
        print('Directory not refreshed')




def calculate_dxy_Lxy_Lz_for_gen(data):
    data['theColl._dxy'] = -(data['theColl._vx'] * np.sin(data['theColl._phi']) - data['theColl._vy'] * np.cos(data['theColl._phi']))
    data['theColl._Lxy'] = np.sqrt(data['theColl._vx']**2 + data['theColl._vy']**2)
    data['theColl._Lz'] = np.abs(data['theColl._vz'])
    data['theColl._abs_dxy'] = np.abs(data['theColl._dxy'])

    return data



def match_gen_muons(data_reco, data_gen):
    data_reco = data_reco.copy()
    data_gen = data_gen.copy()

    # Merge reco and gen data on 'entry' column
    merged_df = pd.merge(data_gen, data_reco, on='entry', how='left')

    # Calculate deltaEta between gen and reco muons
    # deltaEta calculated according to the formula from RooTAnalysis (my code provides the same matching result):
    # deltaEta =   -myGenObj.eta()*aCand.etaValue();
    merged_df['deltaEta'] = (-1)*merged_df['theColl._eta']*merged_df['theL1Obj.eta']
    # merged_df['deltaEta'] = abs(merged_df['theColl._eta'] - merged_df['theL1Obj.eta'])
    # print(merged_df)

    # Find the closest match for each entry based on minimum deltaEta
    merged_df = merged_df.loc[
        merged_df.groupby('entry')['deltaEta'].idxmin().dropna().astype(int)
    ].combine_first(merged_df[merged_df['deltaEta'].isna()])
    

    return merged_df














