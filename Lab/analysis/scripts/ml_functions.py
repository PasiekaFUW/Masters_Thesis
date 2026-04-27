import importlib
import analysis.scripts.plotting_functions as pf
importlib.reload(pf)

def get_balanced_subset(df, cc_per_type=25, nc_per_type=100):
    import pandas as pd
    """
    Filters the dataframe to get a specific number of CC and NC events 
    across the 4 main interaction types.
    """
    interaction_types = ['DIS', 'RES', 'QES', 'MEC'] 
    cc_samples = []
    nc_samples = []

    for itype in interaction_types:
        # Pull subsets based on CCNC and Interaction Type
        cc_subset = df[(df['CCNC'] == 'CC') & (df['IntType'] == itype)].head(cc_per_type)
        nc_subset = df[(df['CCNC'] == 'NC') & (df['IntType'] == itype)].head(nc_per_type)
        
        cc_samples.append(cc_subset)
        nc_samples.append(nc_subset)

    # Combine and shuffle to mix types before they hit the tensor stage
    balanced = pd.concat(cc_samples + nc_samples).sample(frac=1).reset_index(drop=True)
    
    print(f"--- Subset Created: {len(balanced)} events ---")
    return balanced

def preProcess_data(balanced, batch_size=32):
    #warning, its hardcoded for 200 events
    import pandas as pd
    import numpy as np
    import tensorflow as tf


    # We call our external functions once on the entire 'balanced' dataframe.

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
    # When a particle type doesn't exist in an event, leading features return NaN.
    # We replace these with 0.0 for the neural network.
    feature_matrix = np.column_stack([
        ch_pion_mult,
        np.nan_to_num(ch_lead_p),
        np.nan_to_num(ch_lead_theta),
        np.nan_to_num(ch_lead_pt),
        n_pion_mult,
        np.nan_to_num(n_lead_p),
        np.nan_to_num(n_lead_theta)
    ]).astype(np.float32)

    # Label: CC = 1, NC = 0
    labels = (balanced['CCNC'] == 'CC').astype(np.float32).values

    # --- STEP 4: Create the final TF Dataset ---
    # X and y are already in the correct shape/type from the column_stack above
    X = feature_matrix
    y = labels

    test_data = tf.data.Dataset.from_tensor_slices((X, y))
    test_data = test_data.shuffle(buffer_size=200).batch(batch_size)

    # Returning 'balanced' as processed_data to keep your return signature consistent
    return test_data