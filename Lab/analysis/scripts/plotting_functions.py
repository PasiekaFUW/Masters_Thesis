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




def plot_tau_energy(df):
    # Lista na zebrane energie
    tau_energies = []
    
    # ID cząstek dla taonu (15) i antytaonu (-15)
    tau_pdg_ids = [15, -15]
    
    # Przeszukujemy wszystkie 28 slotów cząstek zdefiniowanych w Twoim nagłówku
    for i in range(1, 29):
        pdg_col = f'Pdg_{i}'
        energy_col = f'E_{i}'
        
        # Sprawdzamy, czy kolumny istnieją w df (bezpiecznik)
        if pdg_col in df.columns and energy_col in df.columns:
            # Wybieramy tylko te wiersze, gdzie w danym slocie jest Taon
            mask = df[pdg_col].isin(tau_pdg_ids)
            
            # Wyciągamy wartości energii dla tych wierszy i dodajemy do listy
            found_energies = df.loc[mask, energy_col].tolist()
            tau_energies.extend(found_energies)

    if not tau_energies:
        print("No taons in the data frame).")
        return

    # Tworzenie wykresu
    plt.figure(figsize=(10, 6))
    plt.hist(tau_energies, bins=80, color='darkorange', edgecolor='black', alpha=0.7)
    plt.xticks(np.arange(0, 85, step=5))
    plt.minorticks_on()
    
    plt.title('$ \\pm \\tau$ energy distribution')
    plt.xlabel('Energy [GeV]')
    plt.ylabel('Particle count')
    plt.grid(axis='both', linestyle=':', alpha=0.6)
    
    plt.show()

