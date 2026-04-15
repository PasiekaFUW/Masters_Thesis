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




def plot_tau_energy(df, QES=False):

    if QES:
        if 'IntType' in df.columns:
            df_to_process = df[df['IntType'] == 'QES'].copy()
        else:
            print("Warning: 'IntType' column missing. Proceeding with all events.")
            df_to_process = df.copy()
    else:
        df_to_process = df.copy()
        
    # Lista na zebrane energie
    tau_energies = []
    
    # ID cząstek dla taonu (15) i antytaonu (-15)
    tau_pdg_ids = [15, -15]
    # tau_pdg_ids = [15]
    
    # Przeszukujemy wszystkie 28 slotów cząstek zdefiniowanych w Twoim nagłówku
    for i in range(1, 29):
        pdg_col = f'Pdg_{i}'
        energy_col = f'E_{i}'
        if pdg_col in df_to_process.columns and energy_col in df_to_process.columns:
            # Wybieramy tylko te wiersze, gdzie w danym slocie jest Taon
            mask = df_to_process[pdg_col].isin(tau_pdg_ids)
            # Wyciągamy wartości energii dla tych wierszy i dodajemy do listy
            found_energies = df_to_process.loc[mask, energy_col].dropna().tolist()
            tau_energies.extend(found_energies)

    if not tau_energies:
        suffix = " (QES only)" if QES else ""
        print(f"No taons found in the data frame{suffix}.")
        return


    # Tworzenie wykresu
    plt.figure(figsize=(10, 6))
    plt.hist(tau_energies, bins=120, color='darkorange', edgecolor='black', alpha=0.7)
    # plt.xticks(np.arange(0, 30, step=5))
    plt.xticks(np.arange(0, max(tau_energies) + 5, step=5))
    plt.minorticks_on()
    
    title_suffix = " (QES Events)" if QES else ""
    plt.title(f'$\\tau^\\pm$ energy distribution{title_suffix}')
    plt.xlabel('Energy [GeV]')
    plt.ylabel('Particle count')
    plt.grid(axis='both', linestyle=':', alpha=0.6)
    
    plt.show()




def plot_physics_analysis(dfs, mode, feature='multiplicity', titles=["Signal CC", "Signal CC QE", "Background NC"]):
    """
    dfs: lista [df1, df2, df3]
    mode: 'protons', 'neutrons', 'ch_pions', 'n_pions', 'charged'
    feature: 'multiplicity' (krotność) lub 'p_leading', 'pt_leading', 'theta_leading' (dla leading particle, all_momentum, all_pt, all_theta dla wszystkich cząstek)
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

    # Wybór kodów PDG dla wybranego modu (np. 'charged')
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

    def get_counts(df):
        pdg_cols = [c for c in df.columns if c.startswith('Pdg_')]
        pdg_data = df[pdg_cols]
        
        # Sprawdzanie nieznanych kodów
        unique_in_df = set(np.unique(pdg_data.values))
        unknown = unique_in_df - all_known_pdgs
        if unknown:
            print(f"--- [INFO] Nieznane kody PDG w {mode}: {unknown} ---")
            
        return pdg_data.isin(selected_pdgs).sum(axis=1)
    

    def get_max_momentum(df):
        pdg_cols = [c for c in df.columns if c.startswith('Pdg_')]
        mask = df[pdg_cols].isin(selected_pdgs).values
        
        # Inicjalizacja macierzy pędów (wiersze x 28 slotów)
        p_matrix = np.zeros(mask.shape)
        
        for i in range(1, 29):
            if f'px_{i}' in df.columns:
                # p = sqrt(px^2 + py^2 + pz^2)
                p_val = np.sqrt(df[f'px_{i}']**2 + df[f'py_{i}']**2 + df[f'pz_{i}']**2)
                p_matrix[:, i-1] = p_val
        
        # Filtrujemy tylko interesujące nas cząstki (reszta na 0)
        p_filtered = np.where(mask, p_matrix, 0)
        
        # Zwracamy max pęd w każdym evencie
        return np.max(p_filtered, axis=1)

    def get_pt_of_leading_p(df):
        pdg_cols = [c for c in df.columns if c.startswith('Pdg_')]
        mask = df[pdg_cols].isin(selected_pdgs).values
        
        # Macierze na pęd całkowity (p) i pęd poprzeczny (pt)
        p_matrix = np.zeros(mask.shape)
        pt_matrix = np.zeros(mask.shape)
        
        for i in range(1, 29):
            if f'px_{i}' in df.columns:
                px = df[f'px_{i}']
                py = df[f'py_{i}']
                pz = df[f'pz_{i}']
                
                # Obliczamy oba parametry dla każdego slotu
                p_matrix[:, i-1] = np.sqrt(px**2 + py**2 + pz**2)
                pt_matrix[:, i-1] = np.sqrt(px**2 + py**2)
        
        # Zerujemy pędy cząstek, których NIE szukamy
        p_filtered = np.where(mask, p_matrix, 0)
        
        # Znajdujemy indeksy cząstek o maksymalnym pędzie całkowitym w każdym evencie
        # argmax zwróci numer kolumny (0-27) dla każdego wiersza
        leading_indices = np.argmax(p_filtered, axis=1)
        
        # Wyciągamy pT odpowiadające tym indeksom
        # Używamy np.take_along_axis lub prostego indeksowania:
        rows = np.arange(len(df))
        leading_pt = pt_matrix[rows, leading_indices]
        
        # Jeśli w evencie nie było żadnej szukanej cząstki (max p = 0), 
        # ustawiamy wynik na NaN lub 0, żeby nie zaburzać statystyki
        has_particles = np.max(p_filtered, axis=1) > 0
        return np.where(has_particles, leading_pt, np.nan)
    
    def get_theta_of_leading_p(df):
        pdg_cols = [c for c in df.columns if c.startswith('Pdg_')]
        mask = df[pdg_cols].isin(selected_pdgs).values
        
        # Macierze na pęd całkowity (p) i kąt theta
        p_matrix = np.zeros(mask.shape)
        theta_matrix = np.zeros(mask.shape)
        
        for i in range(1, 29):
            if f'px_{i}' in df.columns:
                px = df[f'px_{i}']
                py = df[f'py_{i}']
                pz = df[f'pz_{i}']
                
                p_total = np.sqrt(px**2 + py**2 + pz**2)
                pt = np.sqrt(px**2 + py**2)
                
                # Obliczamy kąt theta w radianach
                # arctan2(y, x) -> tutaj arctan2(pt, pz) daje kąt od osi Z
                theta_val = np.arctan2(pt, pz)
                
                p_matrix[:, i-1] = p_total
                theta_matrix[:, i-1] = theta_val
        
        # Zerujemy pędy cząstek, których NIE szukamy
        p_filtered = np.where(mask, p_matrix, 0)
        
        # Znajdujemy indeks leading particle (tej o największym p całkowitym)
        leading_indices = np.argmax(p_filtered, axis=1)
        
        # Wyciągamy theta dla tych indeksów
        rows = np.arange(len(df))
        leading_theta = theta_matrix[rows, leading_indices]
        
        # Konwersja na stopnie (opcjonalnie, fizycy często wolą stopnie do wizualizacji)
        leading_theta_deg = np.degrees(leading_theta)
        
        # Zabezpieczenie: jeśli brak szukanej cząstki w evencie -> NaN
        has_particles = np.max(p_filtered, axis=1) > 0
        return np.where(has_particles, leading_theta_deg, np.nan)
    
    def get_all_momentum(df):
        pdg_cols = [c for c in df.columns if c.startswith('Pdg_')]
        mask = df[pdg_cols].isin(selected_pdgs).values
        
        p_matrix = np.zeros(mask.shape)
        for i in range(1, 29):
            if f'px_{i}' in df.columns:
                p_val = np.sqrt(df[f'px_{i}']**2 + df[f'py_{i}']**2 + df[f'pz_{i}']**2)
                p_matrix[:, i-1] = p_val
        
        # Wybieramy tylko te komórki, gdzie maska jest True
        return p_matrix[mask]
    

    
    def get_all_pt(df):
        pdg_cols = [c for c in df.columns if c.startswith('Pdg_')]
        mask = df[pdg_cols].isin(selected_pdgs).values
        
        pt_matrix = np.zeros(mask.shape)
        for i in range(1, 29):
            if f'px_{i}' in df.columns:
                pt_val = np.sqrt(df[f'px_{i}']**2 + df[f'py_{i}']**2)
                pt_matrix[:, i-1] = pt_val
        
        return pt_matrix[mask]

    def get_all_theta(df):
        pdg_cols = [c for c in df.columns if c.startswith('Pdg_')]
        mask = df[pdg_cols].isin(selected_pdgs).values
        
        theta_matrix = np.zeros(mask.shape)
        for i in range(1, 29):
            if f'px_{i}' in df.columns:
                px, py, pz = df[f'px_{i}'], df[f'py_{i}'], df[f'pz_{i}']
                pt = np.sqrt(px**2 + py**2)
                theta_matrix[:, i-1] = np.degrees(np.arctan2(pt, pz))
        
        return theta_matrix[mask]

    # Inicjalizacja wykresu
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=(feature=='multiplicity'))
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

    for i, df in enumerate(dfs):
        ax = axes[i]

        if feature == 'multiplicity':
            data = get_counts(df)
            max_val = int(data.max()) if data.max() > 0 else 5
            bins = np.arange(0, max_val + 2) - 0.5
            ax.hist(data, bins=bins, color=colors[i], alpha=0.7, edgecolor='black', density=True, rwidth=0.8)
            ax.set_xticks(range(max_val + 1))
            ax.set_xlabel("Krotność (Multiplicity)")
        
        elif feature == 'p_leading':
            data = get_max_momentum(df)
            data_to_plot = data[data > 0]
            ax.hist(data_to_plot, bins=50, color=colors[i], alpha=0.7, edgecolor='black', density=True)
            ax.set_xlabel("Max Momentum $p_{max}$ [GeV/c]")

        elif feature == 'pt_leading':
            data = get_pt_of_leading_p(df)
            data_to_plot = data[data > 0]
            ax.hist(data_to_plot, bins=50, color=colors[i], alpha=0.7, edgecolor='black', density=True)
            ax.set_xlabel("Max Transverse Momentum $p_{T,max}$ [GeV/c]")

        elif feature == 'theta_leading':
            data = get_theta_of_leading_p(df)
            data_to_plot = data[~np.isnan(data)]
            ax.hist(data_to_plot, bins=50, color=colors[i], alpha=0.7, edgecolor='black', density=True)
            ax.set_xlabel("Theta of Leading Particle [degrees]")
        
        elif feature == 'all_momentum':
            data = get_all_momentum(df)
            ax.hist(data, bins=50, color=colors[i], alpha=0.7, edgecolor='black', density=True)
            ax.set_xlabel("Momentum $p$ [GeV/c]")
        
        elif feature == 'all_pt':
            data = get_all_pt(df)
            ax.hist(data, bins=50, color=colors[i], alpha=0.7, edgecolor='black', density=True)
            ax.set_xlabel("Transverse Momentum $p_T$ [GeV/c]")

        elif feature == 'all_theta':
            data = get_all_theta(df)
            ax.hist(data, bins=50, color=colors[i], alpha=0.7, edgecolor='black', density=True)
            ax.set_xlabel("Theta [degrees]")

        ax.set_title(f"{titles[i]}\n{mode.upper()} ({feature})", fontsize=12)
        ax.grid(axis='y', alpha=0.3)
        if i == 0: ax.set_ylabel("Probability Density")

    plt.tight_layout()
    plt.show()