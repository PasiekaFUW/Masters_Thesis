import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# ==============================================================================
# 1. LOGGERS AND BASIC VISUALIZATIONS (Unchanged)
# ==============================================================================

def visualize_data(df):
    fig, axes = plt.subplots(2,2, figsize=(12, 12))

    axes[0,0].hist(df['CurrentType'], bins=3, alpha=0.7, color='blue')
    axes[0,0].set_title("Distribution of Current Types")
    axes[0,0].set_xlabel("Current Type")
    axes[0,0].set_ylabel("Number of Events")
    axes[0,0].grid(alpha=0.3)

    axes[0,1].hist(df['InteractionType'], bins=4, alpha=0.7, color='orange')
    axes[0,1].set_title("Distribution of Interaction Types")
    axes[0,1].set_xlabel("Interaction Type")
    axes[0,1].set_ylabel("Number of Events")
    axes[0,1].grid(alpha=0.3)

    pdg_map = {2212: "p", 2112: "n", 211: "pi+", -211: "pi-", 111: "pi0", 11: "e-", 13: "mu-", 15: "tau-", 22: "gamma", 321: "K+", -321: "K-", 3112: "Lambda", 3222: "Sigma+"}
    counts = df['P1_id'].dropna().value_counts().sort_index()
    labels = [pdg_map.get(int(i), str(int(i))) for i in counts.index]
    axes[1, 0].clear() 
    axes[1, 0].bar(range(len(counts)), counts.values, color='purple', alpha=0.7)
    axes[1, 0].set_xticks(range(len(counts)))
    axes[1, 0].set_xticklabels(labels, rotation=45, fontsize=9)
    axes[1, 0].set_title("Primary Particle (P1) Identity")
    axes[1, 0].set_ylabel("Events")
    axes[1, 0].grid(axis='y', alpha=0.3)
    plt.tight_layout()

    axes[1, 1].hist(df['P1_E'], bins=50, alpha=0.7, color='green')
    axes[1,1].set_title("Distribution of P1 Energy")
    axes[1,1].set_xlabel("P1 Energy")
    axes[1,1].set_ylabel("Number of Events")
    axes[1,1].grid(alpha=0.3)

    plt.show()

def logger(df):
    print("CC percentage:", (df['CurrentType'] == 'CC').mean() * 100)
    print("Expected CC percentage: ~3.8%")
    print("NC percentage:", (df['CurrentType'] == 'NC').mean() * 100)
    print("Expected NC percentage: ~96.2%")

    print("CC QES percentage:", ((df['CurrentType'] == 'CC') & (df['InteractionType'] == 'QES')).sum() / df['CurrentType'].eq('CC').sum() * 100)
    print("Expected CC QES percentage: ~51%")

def logger_kg(df):
    print("CC percentage:", (df['CCNC'] == 'CC').mean() * 100)
    print("Expected CC percentage: ~3.8%")
    print("NC percentage:", (df['CCNC'] == 'NC').mean() * 100)
    print("Expected NC percentage: ~96.2%")

    print("CC QES percentage:", ((df['CCNC'] == 'CC') & (df['IntType'] == 'QES')).sum() / df['CCNC'].eq('CC').sum() * 100)
    print("Expected CC QES percentage: ~51%")

def visualize_kg(df):
    fig, axes = plt.subplots(2,2, figsize=(12, 12))

    axes[0,0].hist(df['CCNC'], bins=3, alpha=0.7, color='blue')
    axes[0,0].set_title("Distribution of Current Types")
    axes[0,0].set_xlabel("Current Type")
    axes[0,0].set_ylabel("Number of Events")
    axes[0,0].grid(alpha=0.3)

    axes[0,1].hist(df['IntType'], bins=4, alpha=0.7, color='orange')
    axes[0,1].set_title("Distribution of Interaction Types")
    axes[0,1].set_xlabel("Interaction Type")
    axes[0,1].set_ylabel("Number of Events")
    axes[0,1].grid(alpha=0.3)

    pdg_map = {2212: "p", 2112: "n", 211: "pi+", -211: "pi-", 111: "pi0", 11: "e-", 13: "mu-", 15: "tau-", 22: "gamma", 321: "K+", -321: "K-", 3112: "Lambda", 3222: "Sigma+"}
    counts = df['Pdg_1'].dropna().value_counts().sort_index()
    labels = [pdg_map.get(int(i), str(int(i))) for i in counts.index]
    axes[1, 0].clear()
    axes[1, 0].bar(range(len(counts)), counts.values, color='purple', alpha=0.7)
    axes[1, 0].set_xticks(range(len(counts)))
    axes[1, 0].set_xticklabels(labels, rotation=45, fontsize=9)
    axes[1, 0].set_title("Primary Particle (P1) Identity")
    axes[1, 0].set_ylabel("Events")
    axes[1, 0].grid(axis='y', alpha=0.3)
    plt.tight_layout()

    axes[1, 1].hist(df['E_1'], bins=50, alpha=0.7, color='green')
    axes[1,1].set_title("Distribution of P1 Energy")
    axes[1,1].set_xlabel("P1 Energy")
    axes[1,1].set_ylabel("Number of Events")
    axes[1,1].grid(alpha=0.3)

    plt.show()

def plot_tau_energy(df, DIS=False, RES=False, QES=False, COH=False, MEC=False, NuEEL=False, ALL=False, ax=None, density=False):
    types_map = {
        'DIS': (DIS, 'blue'), 'RES': (RES, 'green'), 'QES': (QES, 'darkorange'),
        'COH': (COH, 'red'), 'MEC': (MEC, 'purple'), 'NuEEL': (NuEEL, 'cyan')
    }
    selected_types = [name for name, (val, color) in types_map.items() if val]
    
    if not selected_types and not ALL:
        to_plot = [('All Events', df, 'gray')]
    else:
        to_plot = []
        if ALL:
            to_plot.append(('All Events', df, 'gray'))
        for name in selected_types:
            subset = df[df['IntType'] == name] if 'IntType' in df.columns else df
            to_plot.append((name, subset, types_map[name][1]))

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    tau_pdg_ids = [15, -15]
    
    for label, subset, color in to_plot:
        energies = []
        for i in range(1, 29):
            pdg_col = f'Pdg_{i}'
            energy_col = f'E_{i}'
            if pdg_col in subset.columns and energy_col in subset.columns:
                mask = subset[pdg_col].isin(tau_pdg_ids)
                energies.extend(subset.loc[mask, energy_col].dropna().tolist())

        if energies:
            ax.hist(energies, bins=120, color=color, edgecolor='black', 
                    alpha=0.5, label=label, histtype='stepfilled', density=density)

    ax.set_title(r'$\tau^\pm$ Energy Distribution by Interaction Type')
    ax.set_xlabel('Energy [GeV]')
    y_label = "Probability Density" if density else "Particle count"
    ax.set_ylabel(y_label)
    ax.grid(axis='both', linestyle=':', alpha=0.6)
    ax.minorticks_on()
    ax.legend()
    
    return ax

# ==============================================================================
# 2. EXTRACTED FEATURE CALCULATORS (Reusable functions)
# ==============================================================================

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
    for i in range(1, 29):
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

# Helper to act as a unified data router for the plotting functions
def get_feature_data(df, mode, feature, warn_unknown=False):
    """Returns the calculated numpy array and the string label for the x-axis."""
    if feature == 'multiplicity':
        return calc_multiplicity(df, mode, warn_unknown), "Krotność (Multiplicity)"
    elif feature == 'p_leading':
        data = calc_max_momentum(df, mode)
        return data[data > 0], "Max Momentum $p_{max}$ [GeV/c]"
    elif feature == 'pt_leading':
        data = calc_pt_of_leading_p(df, mode)
        return data[~np.isnan(data)], "Max Transverse Momentum $p_{T,max}$ [GeV/c]"
    elif feature == 'theta_leading':
        data = calc_theta_of_leading_p(df, mode)
        return data[~np.isnan(data)], "Theta of Leading Particle [degrees]"
    elif feature == 'all_momentum':
        return calc_all_momentum(df, mode), "Momentum $p$ [GeV/c]"
    elif feature == 'all_pt':
        return calc_all_pt(df, mode), "Transverse Momentum $p_T$ [GeV/c]"
    elif feature == 'all_theta':
        return calc_all_theta(df, mode), "Theta [degrees]"
    else:
        raise ValueError(f"Unknown feature: {feature}")

# ==============================================================================
# 3. REFACTORED PLOTTING FUNCTIONS
# ==============================================================================

def plot_physics_analysis(dfs, mode, feature='multiplicity', titles=["Signal CC", "Signal CC QE", "Background NC"], density=False):
    """
    dfs: lista [df1, df2, df3]
    mode: 'protons', 'neutrons', 'ch_pions', 'n_pions', 'charged'
    feature: 'multiplicity', 'p_leading', 'pt_leading', 'theta_leading', 'all_momentum', 'all_pt', 'all_theta'
    density: bool, if True plots probability density, else plots raw counts
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=density)
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    y_label = "Probability Density" if density else "Counts"

    for i, df in enumerate(dfs):
        ax = axes[i]
        data_to_plot, x_label = get_feature_data(df, mode, feature)
        is_discrete = (feature == 'multiplicity')

        if is_discrete:
            max_val = int(data_to_plot.max()) if len(data_to_plot) > 0 and data_to_plot.max() > 0 else 5
            bins = np.arange(0, max_val + 2) - 0.5
            ax.hist(data_to_plot, bins=bins, color=colors[i], alpha=0.7, 
                    edgecolor='black', density=density, rwidth=0.8)
            ax.set_xticks(range(int(data_to_plot.max()) + 1))
        else:
            ax.hist(data_to_plot, bins=50, color=colors[i], alpha=0.7, 
                    edgecolor='black', density=density)

        ax.set_xlabel(x_label)
        ax.set_title(f"{titles[i]}\n{mode.upper()} ({feature})", fontsize=12)
        ax.grid(axis='y', alpha=0.3)
        
        if i == 0: 
            ax.set_ylabel(y_label)

    plt.tight_layout()
    plt.show()

def plot_physics_single_canva(dfs, mode, feature='multiplicity', titles=["All (CC+NC)", "Signal CC", "Background NC"], ax=None, density=True):
    """
    dfs: lista [df_all, df_cc, df_nc]
    mode: 'protons', 'neutrons', 'ch_pions', 'n_pions', 'charged'
    feature: 'multiplicity', 'p_leading', 'pt_leading', 'theta_leading', 'all_momentum', 'all_pt', 'all_theta'
    ax: opcjonalny obiekt matplotlib.axes.Axes. Jeśli None, tworzy nowy.
    """
    plot_data = []
    x_label = ""
    
    for df in dfs:
        data, x_label = get_feature_data(df, mode, feature, warn_unknown=True)
        plot_data.append(data)

    # --- Wyrównanie koszyków (binning) ---
    if feature == 'multiplicity':
        max_val = max([int(d.max()) if len(d) > 0 and d.max() > 0 else 5 for d in plot_data])
        common_bins = np.arange(0, max_val + 2) - 0.5
    else:
        min_val = min([d.min() for d in plot_data if len(d) > 0])
        max_val = max([d.max() for d in plot_data if len(d) > 0])
        common_bins = np.linspace(min_val, max_val, 120)

    # --- Rysowanie na wskazanym 'ax' ---
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    colors = ['gray', 'blue', 'green', 'darkorange', 'purple', 'cyan']
    
    for i, data in enumerate(plot_data):
        c = colors[i % len(colors)]
        label_title = titles[i] if i < len(titles) else f"Dataset {i+1}"
            
        if feature == 'multiplicity':
            ax.hist(data, bins=common_bins, color=c, edgecolor='black', 
                     alpha=0.5, density=density, rwidth=0.8, label=label_title)
            ax.set_xticks(range(int(max_val) + 1))
        else:
            ax.hist(data, bins=common_bins, color=c, edgecolor='black', 
                     alpha=0.5, density=density, label=label_title, histtype='stepfilled')

    # Formatting 
    ax.set_title(f"{mode.upper()} ({feature})")
    ax.set_xlabel(x_label)
    
    y_label = "Probability Density" if density else "Particle count"
    ax.set_ylabel(y_label)

    ax.grid(axis='both', linestyle=':', alpha=0.6)
    ax.minorticks_on()
    ax.legend()
    
    return ax


# feature_matrix = np.column_stack([
#     np.nan_to_num(ch_lead_pt),
#     np.nan_to_num(ch_lead_p),
#     np.nan_to_num(ch_lead_theta),
#     ch_pion_mult,
#     ch_charged_mult,
#     n_pion_mult,
#     np.nan_to_num(n_lead_theta),
#     np.nan_to_num(n_lead_p)
    
# ]).astype(np.float32)

# The "Cheat Sheet" - update this if you change your preProcess_data logic
FEATURE_INDEX_MAP = {

    0: "Ch Leading pt [GeV/c]",
    1: "Ch Leading p [GeV/c]",
    2: "Ch Leading Theta [deg]",
    3: "Ch Pion Multiplicity",
    4: "Charged Particles Multiplicity",
    5: "Neutral Pion Multiplicity",
    6: "Neutral Leading Theta [deg]",
    7: "Neutral Leading p [GeV/c]"
   
}

def plot_feature_from_dataset(dataset, feature_idx, feature_name=None, ax=None, density=False):
    if feature_name is None:
        feature_name = FEATURE_INDEX_MAP.get(feature_idx, f"Feature {feature_idx}")

    cc_data = []
    nc_data = []

    # 1. Collect data from the generator
    for features, labels in dataset:
        feat_np = features.numpy()
        lab_np = labels.numpy()
        # Flattening to ensure we have 1D arrays for the histogram
        val = feat_np[:, feature_idx].flatten()
        
        cc_data.extend(val[lab_np == 1.0])
        nc_data.extend(val[lab_np == 0.0])

    cc_data = np.array(cc_data)
    nc_data = np.array(nc_data)

    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 5))

    # --- Physics Binning Logic ---
    is_discrete = feature_idx in [3, 4, 5] # Multiplicities
    
    # Calculate common limits
    all_vals = np.concatenate([cc_data, nc_data])
    if len(all_vals) == 0: return ax
    
    min_val, max_val = all_vals.min(), all_vals.max()

    if is_discrete:
        # Align bins to integer centers
        common_bins = np.arange(0, int(max_val) + 2) - 0.5
        rwidth = 0.8
        if max_val <= 20:
            ax.set_xticks(range(int(max_val) + 1))
    else:
        # Use a higher resolution for continuous physics variables
        common_bins = np.linspace(min_val, max_val, 100)
        rwidth = 1.0

    # 2. Plotting with shared bins
    ax.hist(cc_data, bins=common_bins, label='CC (Signal)', 
            color='blue', alpha=0.5, edgecolor='black', 
            density=density, rwidth=rwidth)
    
    ax.hist(nc_data, bins=common_bins, label='NC (Background)', 
            color='green', alpha=0.5, edgecolor='black', 
            density=density, rwidth=rwidth)

    # Formatting
    ax.set_title(f"Dataset Check: {feature_name}")
    ax.set_xlabel(feature_name)
    ax.set_ylabel("Probability Density" if density else "Counts")
    ax.grid(axis='both', linestyle=':', alpha=0.6)
    ax.legend()
    
    return ax

def plotTrainHistory(history):
  fig, axes = plt.subplots(1, 2, figsize=(10, 5))
  axes[0].plot(history.history['loss'], 'blue', label = 'train')
  axes[0].plot(history.history['val_loss'], 'orange', label = 'validation')
  axes[0].set_title('Loss function')
  axes[0].set_xlabel('Epoch')
  axes[0].legend(loc='upper right')

  axes[1].plot(history.history['loss'], 'blue', label = 'train')
  axes[1].plot(history.history['val_loss'], 'orange', label = 'validation')
  axes[1].set_title('Loss Function Log')
  axes[1].set_xlabel('Epoch')
  axes[1].set_yscale('log')
  axes[1].legend(loc='upper right')

  plt.subplots_adjust(bottom = 0.02, left = 0.02, right = 0.98, wspace = 0.4)
  plt.show()






def plot_physics_results(df, column='CCNC', ccnc_filter=None, int_filter=None, ax=None, density=False, color='skyblue', bins=None):
    import matplotlib.pyplot as plt
    import numpy as np
    """
    column: 'CCNC', 'IntType', 'Prob_is_CC', or 'NN_Decision_CC'
    ccnc_filter: 'CC' or 'NC' (Optional)
    int_filter: 'QES', 'MEC', 'RES', or 'DIS' (Optional)
    """
    # 1. Apply Filters
    subset = df.copy()
    if ccnc_filter:
        subset = subset[subset['CCNC'] == ccnc_filter]
    if int_filter:
        subset = subset[subset['IntType'] == int_filter]

    # 2. Setup Axes
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 4))

    if subset.empty:
        ax.text(0.5, 0.5, "No Data Found", ha='center', va='center')
        return ax

    # 3. Categorical Plots (CCNC, IntType, NN_Decision_CC)
    if column in ['CCNC', 'IntType', 'NN_Decision_CC']:
        labels, counts = np.unique(subset[column], return_counts=True)
        
        # Manual Density Calculation for Bars
        display_counts = counts.astype(float)
        if density:
            display_counts /= counts.sum()
            y_label = "Density"
        else:
            y_label = "Events"

        # Use the 'color' argument passed to the function
        ax.bar([str(l) for l in labels], display_counts, alpha=0.7, edgecolor='black', color=color)
        ax.set_ylabel(y_label)
        ax.set_title(f"Distribution of {column}")

    # 4. Probability Plots (Prob_is_CC)
    elif column == 'Prob_is_CC':
        if bins is None:
            bins = np.linspace(0, 1, 21)
        cc_vals = subset[subset['CCNC'] == 'CC'][column]
        nc_vals = subset[subset['CCNC'] == 'NC'][column]


        if not nc_vals.empty:
            w_nc = np.ones_like(nc_vals) / len(nc_vals) if density else None
            ax.hist(nc_vals, bins=bins, weights=w_nc, density=density, edgecolor='black', alpha=0.5, histtype='stepfilled', label='NC_meta', color='green', lw=2)
        if not cc_vals.empty:
            w_cc = np.ones_like(cc_vals) / len(cc_vals) if density else None
            ax.hist(cc_vals, bins=bins, weights=w_cc, density=density, edgecolor='black', alpha=0.5, histtype='stepfilled', label='CC_meta', color='blue', lw=2)
        
        ax.set_xlabel("CC Probability")
        ax.set_ylabel("Density" if density else "Events")
        ax.legend()
        ax.set_title(f"Separation: {int_filter if int_filter else 'All'}")

    ax.grid(axis='y', alpha=0.3, ls='--')
    return ax


def plotConfusionMatrix(df, label_col='CCNC', pred_col='NN_Decision_CC', title="Confusion Matrix", ax=None, cmap='Blues'):
    from sklearn.metrics import ConfusionMatrixDisplay
    import matplotlib.pyplot as plt
    
    # 1. Map labels to integers (NC=0, CC=1)
    mapping = {"NC": 0, "CC": 1}
    y_true = df[label_col].map(mapping).fillna(df[label_col]).astype(int)
    y_pred = df[pred_col].astype(int)

    # 2. Handle axis creation
    if ax is None:
        fig, ax = plt.subplots(figsize=(5, 5))

    # 3. Plot
    cmd = ConfusionMatrixDisplay.from_predictions(
        y_true, 
        y_pred, 
        display_labels=["NC", "CC"], 
        normalize="true", 
        values_format=".2f", 
        ax=ax,
        cmap=cmap
    )
    
    ax.set_title(title)
    
    return ax

def plotROC(df, label_col='CCNC', prob_col='Prob_is_CC', model_name="1DCNN", ax=None):
    from sklearn.metrics import RocCurveDisplay, roc_auc_score
    import matplotlib.pyplot as plt
    
    # 1. Map labels to integers
    mapping = {"NC": 0, "CC": 1}
    y_true = df[label_col].map(mapping).fillna(df[label_col]).astype(int)
    y_score = df[prob_col]

    # 2. Create axis if not provided (allows for subplots)
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))

    # 3. Plotting
    RocCurveDisplay.from_predictions(
        y_true, 
        y_score, 
        name=model_name,
        color="darkorange",
        ax=ax
    )

    # Add the "Chance" line
    ax.plot([0, 1], [0, 1], "k--", label="Chance (AUC = 0.50)")

    ax.set_title(f"ROC Curve - {model_name}")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.legend()
    ax.grid(alpha=0.3)

    # 4. Print score and return the axis
    auc_value = roc_auc_score(y_true, y_score)
    print(f"{model_name} ROC AUC: {auc_value:.4f}")
    
    return ax


def plotFeatureImportance(model, data_batch, feature_map=FEATURE_INDEX_MAP, title="Feature Dependency (Saliency Map)", ax=None):
    import tensorflow as tf
    import numpy as np
    import matplotlib.pyplot as plt

    # 1. Calculate Importance via Backprop
    # Extract one batch from the tf.data.Dataset
    for images, labels in data_batch.take(1):
        input_tensor = tf.convert_to_tensor(images)
        break
    
    with tf.GradientTape() as tape:
        tape.watch(input_tensor)
        predictions = model(input_tensor)
        
    # Get gradients of output w.r.t input
    grads = tape.gradient(predictions, input_tensor)
    
    # Average the absolute gradient magnitude across the batch
    importance = tf.reduce_mean(tf.abs(grads), axis=0).numpy().flatten()
    
    # 2. Map indices to names
    feature_names = [feature_map.get(i, f"feat_{i}") for i in range(len(importance))]

    # 3. Plotting
    # If no ax is provided, create a new figure and ax
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 5))
    
    # Using a horizontal bar chart often makes long physics labels easier to read
    bars = ax.barh(feature_names, importance, color='teal', edgecolor='black', alpha=0.8)
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel("Sensitivity (Mean |Gradient|)")
    ax.set_ylabel("Physics Feature")
    ax.grid(axis='x', linestyle='--', alpha=0.6)
    
    # Invert y-axis so the first feature (index 0) is at the top
    ax.invert_yaxis() 
    
    # Note: Removed plt.show() so the ax remains active and modifiable
    plt.tight_layout()
    
    return ax