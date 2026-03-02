import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import uproot as upr
from termcolor import colored
from matplotlib.colors import LogNorm
import shutil
import os
import warnings
#there is a future warning that is not important for now. 
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.copy_on_write = True 

###############################################################################################################
###############################################################################################################
def load_data(filename, path, tree):

    file = upr.open(path + filename)
    tree = file[tree]
    
    #print("Available branches:", tree.keys())
    columns_to_drop = ['theL1Obj.fUniqueID', 'theL1Obj.fBits','theL1Obj.hits']

    df_reco = tree.arrays(filter_name=["l1ObjColl/theL1Obj/theL1Obj.*"], library="pd")
    df_gen = tree.arrays(filter_name=["genColl/theColl/theColl._*"], library="pd")
    df = pd.merge(df_gen, df_reco,  how='outer', left_index=True, right_index=True)
    columns = df.columns.tolist()
    columns_to_explode = [col for col in columns if col.startswith('theL1Obj.')]
    ##workaround to convert awkward arrays to lists to get correct explode behavior
    df = pd.DataFrame(df.to_numpy(), columns=df.columns) 
    df = df.convert_dtypes()  
    ###
    df = df.explode(columns_to_explode)
    index_level_0 = df.index
    index_level_1 = df.groupby(index_level_0).cumcount()
    multi_index = pd.MultiIndex.from_arrays([index_level_0, index_level_1],names=['entry','subentry'])
    df.index = multi_index
    df = df.drop(columns=columns_to_drop)
    
    df = calculate_dxy_Lxy_Lz_for_gen(df)
    df['theColl._phi'] = df['theColl._phi'] + np.pi

    #Apply HW-> physics scale for objects with Phase1 GMT scales
    df_omtfTree = df[df['theL1Obj.type'] < 15].copy()
    df_omtfTree.loc[:, 'theL1Obj.eta'] = df_omtfTree['theL1Obj.eta'] / 240 * 2.61
    df_omtfTree.loc[:, 'theL1Obj.phi'] = ((15 + df_omtfTree['theL1Obj.iProcessor'] * 60) / 360 + df_omtfTree['theL1Obj.phi'] / 576) * 2 * np.pi
    df_omtfTree.loc[:, 'theL1Obj.pt'] = (df_omtfTree['theL1Obj.pt'] - 1) / 2
    df.update(df_omtfTree)

    df_SA = df[df['theL1Obj.type'] == 16].copy()
    df_SA['theL1Obj.phi'] = df_SA['theL1Obj.phi'] + np.pi
    df.update(df_SA)
        
    print(colored('Loading data from',"blue"), filename,f'tree: {tree.name}', end=' ')
    print(colored('Number of events:', "blue"),df.index.get_level_values(0).max()+1)
    return df

###############################################################################################################
###############################################################################################################
def calculate_dxy_Lxy_Lz_for_gen(data):
    data['theColl._dxy'] = -(data['theColl._vx'] * np.sin(data['theColl._phi']) - data['theColl._vy'] * np.cos(data['theColl._phi']))
    data['theColl._Lxy'] = np.sqrt(data['theColl._vx']**2 + data['theColl._vy']**2)
    data['theColl._Lz'] = np.abs(data['theColl._vz'])
    data['theColl._abs_dxy'] = np.abs(data['theColl._dxy'])

    return data
###############################################################################################################
###############################################################################################################
def match_gen_muons(df):
    df.sort_values(['theL1Obj.q','theL1Obj.pt'], ascending=False, inplace=True)
    df_grouped = df.groupby(level="entry").head(1)
    df = df_grouped.sort_values(by='entry',ascending=True)
    return df
###############################################################################################################
###############################################################################################################
def sanitize_filename(filename):
    return re.sub(r'\W+', '_', filename)
###############################################################################################################
###############################################################################################################
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
###############################################################################################################
###############################################################################################################
def calculate_dxy_Lxy_Lz_for_gen(data):
    data['theColl._dxy'] = -(data['theColl._vx'] * np.sin(data['theColl._phi']) - data['theColl._vy'] * np.cos(data['theColl._phi']))
    data['theColl._Lxy'] = np.sqrt(data['theColl._vx']**2 + data['theColl._vy']**2)
    data['theColl._Lz'] = np.abs(data['theColl._vz'])
    data['theColl._abs_dxy'] = np.abs(data['theColl._dxy'])

    return data
###############################################################################################################
###############################################################################################################










