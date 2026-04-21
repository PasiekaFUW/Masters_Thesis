import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

#Visualize
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
    axes[1, 0].clear() # Clear the old histogram if re-running
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
    axes[1, 0].clear() # Clear the old histogram if re-running
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




def plot_tau_energy(df, DIS=False, RES=False, QES=False, COH=False, MEC=False, NuEEL=False, ALL=False, ax=None):
    # Mapping of flag names to their column values and colors
    types_map = {
        'DIS': (DIS, 'blue'),
        'RES': (RES, 'green'),
        'QES': (QES, 'darkorange'),
        'COH': (COH, 'red'),
        'MEC': (MEC, 'purple'),
        'NuEEL': (NuEEL, 'cyan')
    }
    
    # Determine which types to plot
    selected_types = [name for name, (val, color) in types_map.items() if val]
    
    # If nothing is selected, default to plotting all events as a single category
    if not selected_types and not ALL:
        to_plot = [('All Events', df, 'gray')]
    else:
        to_plot = []
        if ALL:
            to_plot.append(('All Events', df, 'gray'))
        for name in selected_types:
            subset = df[df['IntType'] == name] if 'IntType' in df.columns else df
            to_plot.append((name, subset, types_map[name][1]))

    # Setup the Axis
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    tau_pdg_ids = [15, -15]
    
    for label, subset, color in to_plot:
        energies = []
        # Vectorized energy collection across all slots
        for i in range(1, 29):
            pdg_col = f'Pdg_{i}'
            energy_col = f'E_{i}'
            if pdg_col in subset.columns and energy_col in subset.columns:
                mask = subset[pdg_col].isin(tau_pdg_ids)
                energies.extend(subset.loc[mask, energy_col].dropna().tolist())

        if energies:
            ax.hist(energies, bins=120, color=color, edgecolor='black', 
                    alpha=0.5, label=label, histtype='stepfilled')

    # Formatting
    ax.set_title(r'$\tau^\pm$ Energy Distribution by Interaction Type')
    ax.set_xlabel('Energy [GeV]')
    ax.set_ylabel('Particle count')
    ax.grid(axis='both', linestyle=':', alpha=0.6)
    ax.minorticks_on()
    ax.legend()
    
    return ax



def plot_physics_analysis(dfs, mode, feature='multiplicity', titles=["Signal CC", "Signal CC QE", "Background NC"], density=False):
    """
    dfs: lista [df1, df2, df3]
    mode: 'protons', 'neutrons', 'ch_pions', 'n_pions', 'charged'
    feature: 'multiplicity', 'p_leading', 'pt_leading', 'theta_leading', 'all_momentum', 'all_pt', 'all_theta'
    density: bool, if True plots probability density, else plots raw counts
    """
    
    PDG = {
        'proton': [2212, -2212],
        'neutron': [2112, -2112],
        'Sigma+-': [3222, 3112],
        'Sigma0': [3212],
        'SigmaC+': [4212],
        'SigmaC++': [4222],
        'Lambda': [3122, -3122],
        'LambdaC+': [4122],
        'muons': [13, -13],
        'electrons': [11, -11],
        'taus': [15, -15],
        'gamma': [22],
        'pi+-': [211, -211],
        'pi_0': [111],
        'K+-': [321, -321], 
        'K0L': [130],
        'K0': [311, -311],
        'D+-': [411, -411],
        'D0': [421],
        'Ds+': [431]
    }

    targets = {
        'protons': PDG['proton'],
        'neutrons': PDG['neutron'],
        'ch_pions': PDG['pi+-'],
        'n_pions': PDG['pi_0'],
        'charged': PDG['proton'] + PDG['Sigma+-'] + PDG['SigmaC+'] + PDG['SigmaC++'] + PDG['LambdaC+'] +
                   PDG['pi+-'] + PDG['K+-'] + PDG['D+-'] + PDG['Ds+'] +
                   PDG['muons'] + PDG['electrons'] + PDG['taus']
    }
    selected_pdgs = targets.get(mode, [])

    all_known_pdgs = {0}
    for codes in PDG.values(): all_known_pdgs.update(codes)

    # --- Helper Data Extraction Functions ---
    def get_counts(df):
        pdg_cols = [c for c in df.columns if c.startswith('Pdg_')]
        return df[pdg_cols].isin(selected_pdgs).sum(axis=1)
    
    def get_max_momentum(df):
        pdg_cols = [c for c in df.columns if c.startswith('Pdg_')]
        mask = df[pdg_cols].isin(selected_pdgs).values
        p_matrix = np.zeros(mask.shape)
        for i in range(1, 29):
            if f'px_{i}' in df.columns:
                p_val = np.sqrt(df[f'px_{i}']**2 + df[f'py_{i}']**2 + df[f'pz_{i}']**2)
                p_matrix[:, i-1] = p_val
        p_filtered = np.where(mask, p_matrix, 0)
        return np.max(p_filtered, axis=1)

    def get_pt_of_leading_p(df):
        pdg_cols = [c for c in df.columns if c.startswith('Pdg_')]
        mask = df[pdg_cols].isin(selected_pdgs).values
        p_matrix = np.zeros(mask.shape)
        pt_matrix = np.zeros(mask.shape)
        for i in range(1, 29):
            if f'px_{i}' in df.columns:
                px, py, pz = df[f'px_{i}'], df[f'py_{i}'], df[f'pz_{i}']
                p_matrix[:, i-1] = np.sqrt(px**2 + py**2 + pz**2)
                pt_matrix[:, i-1] = np.sqrt(px**2 + py**2)
        p_filtered = np.where(mask, p_matrix, 0)
        leading_indices = np.argmax(p_filtered, axis=1)
        rows = np.arange(len(df))
        leading_pt = pt_matrix[rows, leading_indices]
        has_particles = np.max(p_filtered, axis=1) > 0
        return np.where(has_particles, leading_pt, np.nan)
    
    def get_theta_of_leading_p(df):
        pdg_cols = [c for c in df.columns if c.startswith('Pdg_')]
        mask = df[pdg_cols].isin(selected_pdgs).values
        p_matrix = np.zeros(mask.shape)
        theta_matrix = np.zeros(mask.shape)
        for i in range(1, 29):
            if f'px_{i}' in df.columns:
                px, py, pz = df[f'px_{i}'], df[f'py_{i}'], df[f'pz_{i}']
                p_total = np.sqrt(px**2 + py**2 + pz**2)
                pt = np.sqrt(px**2 + py**2)
                p_matrix[:, i-1] = p_total
                theta_matrix[:, i-1] = np.degrees(np.arctan2(pt, pz))
        p_filtered = np.where(mask, p_matrix, 0)
        leading_indices = np.argmax(p_filtered, axis=1)
        rows = np.arange(len(df))
        leading_theta = theta_matrix[rows, leading_indices]
        has_particles = np.max(p_filtered, axis=1) > 0
        return np.where(has_particles, leading_theta, np.nan)
    
    def get_all_momentum(df):
        pdg_cols = [c for c in df.columns if c.startswith('Pdg_')]
        mask = df[pdg_cols].isin(selected_pdgs).values
        sum_px, sum_py, sum_pz = np.zeros(len(df)), np.zeros(len(df)), np.zeros(len(df))
        for i in range(1, 29):
            if f'px_{i}' in df.columns:
                sum_px += df[f'px_{i}'].values * mask[:, i-1]
                sum_py += df[f'py_{i}'].values * mask[:, i-1]
                sum_pz += df[f'pz_{i}'].values * mask[:, i-1]
        return np.sqrt(sum_px**2 + sum_py**2 + sum_pz**2)
    
    def get_all_pt(df):
        pdg_cols = [c for c in df.columns if c.startswith('Pdg_')]
        mask = df[pdg_cols].isin(selected_pdgs).values
        sum_px, sum_py = np.zeros(len(df)), np.zeros(len(df))
        for i in range(1, 29):
            if f'px_{i}' in df.columns:
                sum_px += df[f'px_{i}'].values * mask[:, i-1]
                sum_py += df[f'py_{i}'].values * mask[:, i-1]
        return np.sqrt(sum_px**2 + sum_py**2)

    def get_all_theta(df):
        pdg_cols = [c for c in df.columns if c.startswith('Pdg_')]
        mask = df[pdg_cols].isin(selected_pdgs).values
        sum_px, sum_py, sum_pz = np.zeros(len(df)), np.zeros(len(df)), np.zeros(len(df))
        for i in range(1, 29):
            if f'px_{i}' in df.columns:
                sum_px += df[f'px_{i}'].values * mask[:, i-1]
                sum_py += df[f'py_{i}'].values * mask[:, i-1]
                sum_pz += df[f'pz_{i}'].values * mask[:, i-1]
        return np.degrees(np.arctan2(np.sqrt(sum_px**2 + sum_py**2), sum_pz))

    # --- Plotting ---
    # Sharey is usually True for density (comparison) and False for counts (absolute scale)
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=density)
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    y_label = "Probability Density" if density else "Counts"

    for i, df in enumerate(dfs):
        ax = axes[i]
        data_to_plot = None
        x_label = ""
        is_discrete = False

        if feature == 'multiplicity':
            data_to_plot = get_counts(df)
            max_val = int(data_to_plot.max()) if data_to_plot.max() > 0 else 5
            bins = np.arange(0, max_val + 2) - 0.5
            is_discrete = True
            x_label = "Krotność (Multiplicity)"
        
        elif feature == 'p_leading':
            data = get_max_momentum(df)
            data_to_plot = data[data > 0]
            x_label = "Max Momentum $p_{max}$ [GeV/c]"

        elif feature == 'pt_leading':
            data = get_pt_of_leading_p(df)
            data_to_plot = data[~np.isnan(data)]
            x_label = "Max Transverse Momentum $p_{T,max}$ [GeV/c]"

        elif feature == 'theta_leading':
            data = get_theta_of_leading_p(df)
            data_to_plot = data[~np.isnan(data)]
            x_label = "Theta of Leading Particle [degrees]"
        
        elif feature == 'all_momentum':
            data_to_plot = get_all_momentum(df)
            x_label = "Momentum $p$ [GeV/c]"
        
        elif feature == 'all_pt':
            data_to_plot = get_all_pt(df)
            x_label = "Transverse Momentum $p_T$ [GeV/c]"

        elif feature == 'all_theta':
            data_to_plot = get_all_theta(df)
            x_label = "Theta [degrees]"

        # Unified Histogram Call
        if is_discrete:
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
    Zwraca: obiekt ax z narysowanym wykresem.
    """
    
    PDG = {
        'proton': [2212, -2212], 'neutron': [2112, -2112],
        'Sigma+-': [3222, 3112], 'Sigma0': [3212],
        'SigmaC+': [4212], 'SigmaC++': [4222],
        'Lambda': [3122, -3122], 'LambdaC+': [4122],
        'muons': [13, -13], 'electrons': [11, -11], 'taus': [15, -15], 'gamma': [22],
        'pi+-': [211, -211], 'pi_0': [111],
        'K+-': [321, -321], 'K0L': [130], 'K0': [311, -311],
        'D+-': [411, -411], 'D0': [421], 'Ds+': [431]
    }

    targets = {
        'protons': PDG['proton'],
        'neutrons': PDG['neutron'],
        'ch_pions': PDG['pi+-'],
        'n_pions': PDG['pi_0'],
        'charged': PDG['proton'] + PDG['Sigma+-'] + PDG['SigmaC+'] + PDG['SigmaC++'] + PDG['LambdaC+'] +
                   PDG['pi+-'] + PDG['K+-'] + PDG['D+-'] + PDG['Ds+'] +
                   PDG['muons'] + PDG['electrons'] + PDG['taus']
    }
    
    selected_pdgs = targets.get(mode, [])
    all_known_pdgs = {0}.union(*(codes for codes in PDG.values()))

    def _get_mask(df):
        pdg_cols = [c for c in df.columns if c.startswith('Pdg_')]
        return df[pdg_cols].isin(selected_pdgs).values

    def get_counts(df):
        pdg_cols = [c for c in df.columns if c.startswith('Pdg_')]
        unknown = set(np.unique(df[pdg_cols].values)) - all_known_pdgs
        if unknown:
            print(f"--- [INFO] Nieznane kody PDG w {mode}: {unknown} ---")
        return _get_mask(df).sum(axis=1)

    def get_max_momentum(df):
        mask = _get_mask(df)
        p_matrix = np.zeros(mask.shape)
        for i in range(1, 29):
            if f'px_{i}' in df.columns:
                p_matrix[:, i-1] = np.sqrt(df[f'px_{i}']**2 + df[f'py_{i}']**2 + df[f'pz_{i}']**2)
        return np.max(np.where(mask, p_matrix, 0), axis=1)

    def get_pt_of_leading_p(df):
        mask = _get_mask(df)
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
    
    def get_theta_of_leading_p(df):
        mask = _get_mask(df)
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
    
    def get_all_momentum(df):
        mask = _get_mask(df)
        px, py, pz = np.zeros(len(df)), np.zeros(len(df)), np.zeros(len(df))
        for i in range(1, 29):
            if f'px_{i}' in df.columns:
                px += df[f'px_{i}'].values * mask[:, i-1]
                py += df[f'py_{i}'].values * mask[:, i-1]
                pz += df[f'pz_{i}'].values * mask[:, i-1]
        return np.sqrt(px**2 + py**2 + pz**2)
    
    def get_all_pt(df):
        mask = _get_mask(df)
        px, py = np.zeros(len(df)), np.zeros(len(df))
        for i in range(1, 29):
            if f'px_{i}' in df.columns:
                px += df[f'px_{i}'].values * mask[:, i-1]
                py += df[f'py_{i}'].values * mask[:, i-1]
        return np.sqrt(px**2 + py**2)

    def get_all_theta(df):
        mask = _get_mask(df)
        px, py, pz = np.zeros(len(df)), np.zeros(len(df)), np.zeros(len(df))
        for i in range(1, 29):
            if f'px_{i}' in df.columns:
                px += df[f'px_{i}'].values * mask[:, i-1]
                py += df[f'py_{i}'].values * mask[:, i-1]
                pz += df[f'pz_{i}'].values * mask[:, i-1]
        return np.degrees(np.arctan2(np.sqrt(px**2 + py**2), pz))

    # --- Pobieranie i czyszczenie danych ---
    plot_data = []
    
    for df in dfs:
        if feature == 'multiplicity':
            data, x_label = get_counts(df), "Krotność (Multiplicity)"
        elif feature == 'p_leading':
            data, x_label = get_max_momentum(df), "Max Momentum $p_{max}$ [GeV/c]"
            data = data[data > 0]
        elif feature == 'pt_leading':
            data, x_label = get_pt_of_leading_p(df), "Max Transverse Momentum $p_{T,max}$ [GeV/c]"
            data = data[~np.isnan(data)]
        elif feature == 'theta_leading':
            data, x_label = get_theta_of_leading_p(df), "Theta of Leading Particle [degrees]"
            data = data[~np.isnan(data)]
        elif feature == 'all_momentum':
            data, x_label = get_all_momentum(df), "Momentum $p$ [GeV/c]"
        elif feature == 'all_pt':
            data, x_label = get_all_pt(df), "Transverse Momentum $p_T$ [GeV/c]"
        elif feature == 'all_theta':
            data, x_label = get_all_theta(df), "Theta [degrees]"
        else:
            raise ValueError(f"Unknown feature: {feature}")
            
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