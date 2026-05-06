import numpy as np


PDG_MAP = {
    'proton': [2212, -2212], 'neutron': [2112, -2112],
    'Sigma+-': [3222, 3112], 'Sigma0': [3212],
    'SigmaC+': [4212], 'SigmaC++': [4222],
    'Lambda': [3122, -3122], 'LambdaC+': [4122],
    'muons': [13, -13], 'electrons': [11, -11], 'taus': [15, -15], 'gamma': [22],
    'pi+-': [211, -211], 'pi_0': [111],
    'K+-': [321, -321], 'K0L': [130], 'K0': [311, -311],
    'D+-': [411, -411], 'D0': [421], 'Ds+': [431]
}
ALL_KNOWN_PDGS = {0}.union(*(codes for codes in PDG_MAP.values()))

def get_target_pdgs(mode):
    targets = {
        'protons': PDG_MAP['proton'],
        'neutrons': PDG_MAP['neutron'],
        'ch_pions': PDG_MAP['pi+-'],
        'n_pions': PDG_MAP['pi_0'],
        'charged': (PDG_MAP['proton'] + PDG_MAP['Sigma+-'] + PDG_MAP['SigmaC+'] +
                    PDG_MAP['SigmaC++'] + PDG_MAP['LambdaC+'] + PDG_MAP['pi+-'] +
                    PDG_MAP['K+-'] + PDG_MAP['D+-'] + PDG_MAP['Ds+'] +
                    PDG_MAP['muons'] + PDG_MAP['electrons'] + PDG_MAP['taus'])
    }
    return targets.get(mode, [])

def get_particle_mask(df, mode):
    selected_pdgs = get_target_pdgs(mode)
    pdg_cols = [c for c in df.columns if c.startswith('Pdg_')]
    return df[pdg_cols].isin(selected_pdgs).values

def calc_multiplicity(df, mode, warn_unknown=True):
    pdg_cols = [c for c in df.columns if c.startswith('Pdg_')]
    if warn_unknown:
        unknown = set(np.unique(df[pdg_cols].values)) - ALL_KNOWN_PDGS
        if unknown:
            print(f"--- [INFO] Nieznane kody PDG w trybie {mode}: {unknown} ---")
    mask = get_particle_mask(df, mode)
    return mask.sum(axis=1)

def calc_max_momentum(df, mode):
    mask = get_particle_mask(df, mode)
    p_matrix = np.zeros(mask.shape)
    max_particles = max([int(c.split('_')[-1]) for c in df.columns if c.startswith('px_')], default=0)
    for i in range(1, max_particles + 1):
    # for i in range(1, 29):
        if f'px_{i}' in df.columns:
            p_matrix[:, i-1] = np.sqrt(df[f'px_{i}']**2 + df[f'py_{i}']**2 + df[f'pz_{i}']**2)
    return np.max(np.where(mask, p_matrix, 0), axis=1)

def calc_pt_of_leading_p(df, mode):
    mask = get_particle_mask(df, mode)
    p_matrix, pt_matrix = np.zeros(mask.shape), np.zeros(mask.shape)
    for i in range(1, 29):
        if f'px_{i}' in df.columns:
            px, py, pz = df[f'px_{i}'], df[f'py_{i}'], df[f'pz_{i}']
            p_matrix[:, i-1] = np.sqrt(px**2 + py**2 + pz**2)
            pt_matrix[:, i-1] = np.sqrt(px**2 + py**2)
            
    p_filtered = np.where(mask, p_matrix, 0)
    leading_indices = np.argmax(p_filtered, axis=1)
    leading_pt = pt_matrix[np.arange(len(df)), leading_indices]
    return np.where(np.max(p_filtered, axis=1) > 0, leading_pt, np.nan)

def calc_theta_of_leading_p(df, mode):
    mask = get_particle_mask(df, mode)
    p_matrix, theta_matrix = np.zeros(mask.shape), np.zeros(mask.shape)
    for i in range(1, 29):
        if f'px_{i}' in df.columns:
            px, py, pz = df[f'px_{i}'], df[f'py_{i}'], df[f'pz_{i}']
            theta_matrix[:, i-1] = np.arctan2(np.sqrt(px**2 + py**2), pz)
            p_matrix[:, i-1] = np.sqrt(px**2 + py**2 + pz**2)
            
    p_filtered = np.where(mask, p_matrix, 0)
    leading_indices = np.argmax(p_filtered, axis=1)
    leading_theta = theta_matrix[np.arange(len(df)), leading_indices]
    return np.where(np.max(p_filtered, axis=1) > 0, np.degrees(leading_theta), np.nan)

def calc_COS_theta_of_leading_p(df, mode):
    mask = get_particle_mask(df, mode)
    p_matrix, theta_matrix = np.zeros(mask.shape), np.zeros(mask.shape)
    for i in range(1, 29):
        if f'px_{i}' in df.columns:
            px, py, pz = df[f'px_{i}'], df[f'py_{i}'], df[f'pz_{i}']
            theta_matrix[:, i-1] = np.arctan2(np.sqrt(px**2 + py**2), pz)
            p_matrix[:, i-1] = np.sqrt(px**2 + py**2 + pz**2)
            
    p_filtered = np.where(mask, p_matrix, 0)
    leading_indices = np.argmax(p_filtered, axis=1)
    leading_theta = theta_matrix[np.arange(len(df)), leading_indices]
    return np.where(np.max(p_filtered, axis=1) > 0, np.cos(leading_theta), np.nan)

def calc_all_momentum(df, mode):
    mask = get_particle_mask(df, mode)
    px, py, pz = np.zeros(len(df)), np.zeros(len(df)), np.zeros(len(df))
    for i in range(1, 29):
        if f'px_{i}' in df.columns:
            px += df[f'px_{i}'].values * mask[:, i-1]
            py += df[f'py_{i}'].values * mask[:, i-1]
            pz += df[f'pz_{i}'].values * mask[:, i-1]
    return np.sqrt(px**2 + py**2 + pz**2)

def calc_all_pt(df, mode):
    mask = get_particle_mask(df, mode)
    px, py = np.zeros(len(df)), np.zeros(len(df))
    for i in range(1, 29):
        if f'px_{i}' in df.columns:
            px += df[f'px_{i}'].values * mask[:, i-1]
            py += df[f'py_{i}'].values * mask[:, i-1]
    return np.sqrt(px**2 + py**2)

def calc_all_theta(df, mode):
    mask = get_particle_mask(df, mode)
    px, py, pz = np.zeros(len(df)), np.zeros(len(df)), np.zeros(len(df))
    for i in range(1, 29):
        if f'px_{i}' in df.columns:
            px += df[f'px_{i}'].values * mask[:, i-1]
            py += df[f'py_{i}'].values * mask[:, i-1]
            pz += df[f'pz_{i}'].values * mask[:, i-1]
    return np.degrees(np.arctan2(np.sqrt(px**2 + py**2), pz))

def get_feature_data(df, mode, feature, warn_unknown=False):
    """
    Adds calculated feature columns to the DataFrame.
    Supports single strings or lists for 'mode' and 'feature'.
    """
    # Ensure mode and feature are lists for iteration
    modes = [mode] if isinstance(mode, str) else mode
    features = [feature] if isinstance(feature, str) else feature

    # Mapping of feature keys to their calculation functions
    func_map = {
        'multiplicity': calc_multiplicity,
        'p_leading': calc_max_momentum,
        'pt_leading': calc_pt_of_leading_p,
        'theta_leading': calc_theta_of_leading_p,
        'cos_theta_leading': calc_COS_theta_of_leading_p,
        'all_momentum': calc_all_momentum,
        'all_pt': calc_all_pt,
        'all_theta': calc_all_theta
    }

    for m in modes:
        for f in features:
            if f not in func_map:
                raise ValueError(f"Unknown feature: {f}")
            
            # Generate column name, e.g., 'p_leading_ch_pions'
            col_name = f"{f}_{m}"
            
            # Calculate data
            # Note: We pass warn_unknown only to multiplicity as per your original code
            if f == 'multiplicity':
                df[col_name] = func_map[f](df, m, warn_unknown=warn_unknown)
            else:
                df[col_name] = func_map[f](df, m)
                
    return df

import pandas as pd

def prepare_combined_pool(df_cc, df_nc):
    """
    Combines CC and NC dataframes and ensures the CCNC flag is correctly set.
    """
    # Explicitly set CCNC flags to ensure the split function works correctly
    df_cc = df_cc.copy()
    df_nc = df_nc.copy()
    
    df_cc['CCNC'] = 1
    df_nc['CCNC'] = 0
    
    # Combine
    df_combined = pd.concat([df_cc, df_nc], axis=0).sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"Pool Prepared:")
    print(f"  - Total Events: {len(df_combined)}")
    print(f"  - CC Count: {len(df_cc)}")
    print(f"  - NC Count: {len(df_nc)}")
    
    return df_combined

def clean_particle_data(df):
    """
    Removes raw particle data and metadata, leaving only 
    CCNC, IntType, and (optionally) calculated features.
    """
    # 1. Define the specific columns to drop
    to_drop = ['Nu']
    
    # 2. Define the prefixes of columns to drop (Pdg_1, px_2, etc.)
    prefixes_to_drop = ['Pdg_', 'Fchild_', 'Lchild_', 'px_', 'py_', 'pz_', 'E_']
    
    # Identify all columns in the DF that start with those prefixes
    dynamic_drops = [
        col for col in df.columns 
        if any(col.startswith(p) for p in prefixes_to_drop)
    ]
    
    # Combine the lists
    all_to_drop = to_drop + dynamic_drops
    
    # Drop columns that actually exist in the dataframe
    existing_drops = [c for c in all_to_drop if c in df.columns]
    
    df_cleaned = df.drop(columns=existing_drops)
    
    return df_cleaned

def transform_ccnc(df):
    """
    Transforms 'CC' to 1 and 'NC' to 0 in the CCNC column.
    """
    if 'CCNC' in df.columns:
        # map() converts CC -> 1 and NC -> 0. 
        # Existing numbers or NaNs remain if not specified, 
        # unless you want them to become NaN (use .replace instead if preferred)
        df['CCNC'] = df['CCNC'].map({'CC': 1, 'NC': 0, 0:0, 1:1})
    return df

def fill_nans(df, value=0):
    """
    Replaces all NaN values in the DataFrame with a specified value (default 0).
    """
    return df.fillna(value)

def filter_int_types(df, types_to_remove):
    """
    Removes rows where 'IntType' is in the types_to_remove list.
    
    Parameters:
    df: The input DataFrame
    types_to_remove: A single integer or a list of integers (e.g., [1, 2, 3])
    """
    if 'IntType' not in df.columns:
        print("Warning: 'IntType' column not found.")
        return df

    # Ensure types_to_remove is a list for consistency
    if not isinstance(types_to_remove, list):
        types_to_remove = [types_to_remove]

    # Keep rows where IntType is NOT in the list
    df_filtered = df[~df['IntType'].isin(types_to_remove)].copy()
    
    # Optional: Print how many rows were removed
    removed_count = len(df) - len(df_filtered)
    print(f"Removed {removed_count} rows with IntTypes: {types_to_remove}")
    
    return df_filtered



def get_physics_informed_split(df, total_train_size=1000, total_val_size=400, total_test_size=400):
    import pandas as pd
    import numpy as np

    interaction_types = ['DIS', 'RES', 'QES', 'MEC']
    
    # 1. Calculate the "Natural" Ratios from the source data
    total_counts = len(df)
    global_cc_prop = len(df[df['CCNC'] == 1]) / total_counts
    global_nc_prop = len(df[df['CCNC'] == 0]) / total_counts

    # 2. Setup storage
    train_samples = []
    val_samples = []
    test_samples = []

    # Training needs to be balanced (50/50 CC/NC and equal IntTypes)
    # total_train_size / (2 classes * 4 types)
    train_per_type = total_train_size // 8 

    for itype in interaction_types:
        for ccnc in [1, 0]: # Using 1 for CC and 0 for NC after transformation
            # Create a localized pool for this specific slice
            pool = df[(df['CCNC'] == ccnc) & (df['IntType'] == itype)].sample(frac=1, random_state=42)
            
            # --- TRAINING SELECTION (Balanced) ---
            # We take the training slice first
            train_slice = pool.iloc[:train_per_type]
            train_samples.append(train_slice)
            
            # --- VALIDATION SELECTION (Physical) ---
            val_target_count = 0
            if total_val_size > 0:
                class_prop = global_cc_prop if ccnc == 1 else global_nc_prop
                internal_itype_prop = len(df[(df['CCNC'] == ccnc) & (df['IntType'] == itype)]) / len(df[df['CCNC'] == ccnc])
                
                val_target_count = int(total_val_size * class_prop * internal_itype_prop)
                
                # START validation from where training ended to ensure 0% overlap
                val_slice = pool.iloc[train_per_type : train_per_type + val_target_count]
                val_samples.append(val_slice)

            # --- TESTING SELECTION (Physical) ---
            if total_test_size > 0:
                # Use the exact same physical proportions for the test set
                class_prop = global_cc_prop if ccnc == 1 else global_nc_prop
                internal_itype_prop = len(df[(df['CCNC'] == ccnc) & (df['IntType'] == itype)]) / len(df[df['CCNC'] == ccnc])
                
                test_target_count = int(total_test_size * class_prop * internal_itype_prop)
                
                # START testing from where validation ended to ensure 0% overlap with BOTH train and val
                start_test_idx = train_per_type + val_target_count
                end_test_idx = start_test_idx + test_target_count
                
                test_slice = pool.iloc[start_test_idx : end_test_idx]
                test_samples.append(test_slice)

                # Safety Check
                if len(pool) < end_test_idx:
                    print(f"Warning: Insufficient data for {ccnc}-{itype}. Requested {end_test_idx}, have {len(pool)}")

    # 3. Finalize and Shuffle (Return None if val/test are empty)
    train_df = pd.concat(train_samples).sample(frac=1, random_state=42).reset_index(drop=True)
    
    val_df = pd.concat(val_samples).sample(frac=1, random_state=42).reset_index(drop=True) if total_val_size > 0 else None
    test_df = pd.concat(test_samples).sample(frac=1, random_state=42).reset_index(drop=True) if total_test_size > 0 else None
    
    # --- Final Audit ---
    print("Split Complete. Overlap Checks:")
    if val_df is not None:
        print(f"  - Train/Val shared events:  {len(pd.merge(train_df, val_df, how='inner'))}")
    if test_df is not None:
        print(f"  - Train/Test shared events: {len(pd.merge(train_df, test_df, how='inner'))}")
    if val_df is not None and test_df is not None:
        print(f"  - Val/Test shared events:   {len(pd.merge(val_df, test_df, how='inner'))}")
    
    if val_df is not None:
        print("\n[Validation Set Physics Profile]")
        print(f"CC/NC Ratio: {val_df['CCNC'].value_counts(normalize=True).to_dict()}")
        print(f"Interaction Type Ratios:\n{val_df['IntType'].value_counts(normalize=True)}")

    if test_df is not None:
        print("\n[Testing Set Physics Profile]")
        print(f"CC/NC Ratio: {test_df['CCNC'].value_counts(normalize=True).to_dict()}")
        print(f"Interaction Type Ratios:\n{test_df['IntType'].value_counts(normalize=True)}")
    
    return train_df, val_df, test_df


def tensorize_data(df, batch_size=32, shuffle=False):
    """
    Converts a pre-processed DataFrame into a TensorFlow Dataset.
    Assumes features are already calculated and NaNs are already 0.
    """
    import tensorflow as tf

    # 1. Final 12-feature list in logical grouping
    feature_cols = [
        # Charged Pions
        'p_leading_ch_pions', 'pt_leading_ch_pions', 'cos_theta_leading_ch_pions', 'multiplicity_ch_pions',
        # Charged (Total)
        'multiplicity_charged', 'p_leading_charged', 'pt_leading_charged', 'cos_theta_leading_charged',
        # Neutral Pions
        'multiplicity_n_pions', 'p_leading_n_pions', 'pt_leading_n_pions', 'cos_theta_leading_n_pions'
    ]

    # 2. Directly extract values (NaNs already handled in the DataFrame)
    X = df[feature_cols].values.astype('float32')
    y = df['CCNC'].values.astype('float32')

    # 3. Build the pipeline
    dataset = tf.data.Dataset.from_tensor_slices((X, y))
    
    if shuffle:
        # Using a buffer size equal to the data length for a perfect shuffle
        dataset = dataset.shuffle(buffer_size=len(df))

    # Batching and prefetching for performance
    dataset = dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE)

    return dataset


