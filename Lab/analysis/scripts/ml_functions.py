import importlib
import analysis.scripts.plotting_functions as pf
importlib.reload(pf)

def get_train_val_subsets(df, cc_per_type=25, nc_per_type=25, val_size=0.2, shuffle=True):
    """
    Creates two distinct, balanced dataframes for training and validation.
    Checks if enough events exist before proceeding.
    """
    import pandas as pd
    import numpy as np

    interaction_types = ['DIS', 'RES', 'QES', 'MEC'] 
    
    # Calculate how many events we need in total per type
    total_cc_needed = cc_per_type
    total_nc_needed = nc_per_type
    
    # Validation counts per type
    val_cc_count = int(cc_per_type * val_size)
    val_nc_count = int(nc_per_type * val_size)
    
    # Training counts (the remainder)
    train_cc_count = cc_per_type - val_cc_count
    train_nc_count = nc_per_type - val_nc_count

    train_samples = []
    val_samples = []

    for itype in interaction_types:
        # Filter pools
        cc_pool = df[(df['CCNC'] == 'CC') & (df['IntType'] == itype)]
        nc_pool = df[(df['CCNC'] == 'NC') & (df['IntType'] == itype)]
        
        # --- Safety Check ---
        if len(cc_pool) < total_cc_needed or len(nc_pool) < total_nc_needed:
            print(f"--- [ERROR] Dataset too small for {itype} ---")
            print(f"Needed: {total_cc_needed} CC, {total_nc_needed} NC")
            print(f"Found:  {len(cc_pool)} CC, {len(nc_pool)} NC")
            return None, None

        # Split using iloc
        # Training gets the first chunk
        train_samples.append(cc_pool.iloc[:train_cc_count])
        train_samples.append(nc_pool.iloc[:train_nc_count])
        
        # Validation gets the chunk immediately following training
        val_samples.append(cc_pool.iloc[train_cc_count : total_cc_needed])
        val_samples.append(nc_pool.iloc[train_nc_count : total_nc_needed])

    # Combine and shuffle
    if shuffle == True:
        train_df = pd.concat(train_samples).sample(frac=1, random_state=42).reset_index(drop=True)
        val_df = pd.concat(val_samples).sample(frac=1, random_state=42).reset_index(drop=True)
    else:
        # If no shuffle, they stay ordered by Interaction Type (DIS, then RES, etc.)
        train_df = pd.concat(train_samples).reset_index(drop=True)
        val_df = pd.concat(val_samples).reset_index(drop=True)
    
    print(f"--- Success! Train: {len(train_df)} events, Val: {len(val_df)} events ---")
    return train_df, val_df

def preProcess_data(balanced, batch_size=32, shuffle=False):
    #the default is shuffle false so DF NEED to be shuffled before passing

    import pandas as pd
    import numpy as np
    import tensorflow as tf


    # We call our external functions once on the entire 'balanced' dataframe.

    #charged
    ch_charged_mult  = pf.calc_multiplicity(balanced, 'charged')

    # Charged Pion Features
    ch_pion_mult  = pf.calc_multiplicity(balanced, 'ch_pions')
    ch_lead_p     = pf.calc_max_momentum(balanced, 'ch_pions')
    ch_lead_theta = pf.calc_theta_of_leading_p(balanced, 'ch_pions')
    ch_lead_pt    = pf.calc_pt_of_leading_p(balanced, 'ch_pions')

    # Neutral Pion Features
    n_pion_mult   = pf.calc_multiplicity(balanced, 'n_pions')
    n_lead_p      = pf.calc_max_momentum(balanced, 'n_pions')
    n_lead_theta  = pf.calc_theta_of_leading_p(balanced, 'n_pions')

    # --- STEP 3: Handle NaNs and Packaging ---
    #
    #the order is important - one type grouped, p next to pt and thetas next to each others
    #changing this order influences some plotting functions!
    #
    # When a particle type doesn't exist in an event, leading features return NaN.
    # We replace these with 0.0 for the neural network.

    feature_matrix = np.column_stack([
        np.nan_to_num(ch_lead_pt),
        np.nan_to_num(ch_lead_p),
        np.nan_to_num(ch_lead_theta),
        ch_pion_mult,
        ch_charged_mult,
        n_pion_mult,
        np.nan_to_num(n_lead_theta),
        np.nan_to_num(n_lead_p)
        
    ]).astype(np.float32)

    # Label: CC = 1, NC = 0
    labels = (balanced['CCNC'] == 'CC').astype(np.float32).values

    # --- STEP 4: Create the final TF Dataset ---
    # X and y are already in the correct shape/type from the column_stack above
    X = feature_matrix
    y = labels

    test_data = tf.data.Dataset.from_tensor_slices((X, y))
    if(shuffle==True):
        test_data = test_data.shuffle(buffer_size=len(balanced))

    test_data = test_data.batch(batch_size)

    # Returning 'balanced' as processed_data to keep your return signature consistent
    return test_data