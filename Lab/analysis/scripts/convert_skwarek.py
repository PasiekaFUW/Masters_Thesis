import ROOT, uproot
import numpy as np
import pandas as pd


#Kod J. Skwarek
#Lista kodów PDG cząstek neutralnych, które chcemy usunąć ze zbioru danych
neutral_particles = [
    -12, 12, -14, 14, -16, 16,
    -3122, 3122, -3212, 3212, -421, 421, -311, 311,
    -130, 130, 2000000101, 1000180400, 130, 310,
    3322, -3322, 221, 331, 443, 2112, -2112
]



#Kod J. Skwarek 
def parse_interaction_code(code_str):
    current = "CC" if "CC" in code_str else "NC" if "NC" in code_str else "UNK"
    if "DIS" in code_str: interaction = "DIS"
    elif "RES" in code_str: interaction = "RES"
    elif "QES" in code_str: interaction = "QES"
    else: interaction = "OTHER"
    return current, interaction


#Kod J. Skwarek - zmodyfikowany 
def extract_data_hybrid(input_path, output_csv, neutral_particles=neutral_particles):
    # --- 1. Get EvtCode using PyROOT (Safe for Strings) ---
    print("Extracting metadata with PyROOT...")
    rf = ROOT.TFile.Open(input_path)
    r_tree = rf.Get("gRooTracker")
    
    evt_codes = []
    for entry in r_tree:
        # PyROOT handles the TObjString/TObject conversion automatically
        evt_codes.append(entry.EvtCode.GetString().Data())
    rf.Close()

    # --- 2. Get Physics Data using Uproot (Fast & Stable) ---
    print("Extracting physics data with Uproot...")
    with uproot.open(input_path + ":gRooTracker") as tree:
        # Exclude EvtCode here to avoid the UnknownInterpretation error
        branches = ["EvtNum", "StdHepN", "StdHepPdg", "StdHepStatus", "StdHepP4"]
        data = tree.arrays(branches)

        pdg = data["StdHepPdg"]
        status = data["StdHepStatus"]
        p4 = data["StdHepP4"]

        # --- 3. Filtering Logic ---
        # Final state mask
        mask = (status == 1)
        for code in neutral_particles:
            mask = mask & (pdg != code)

        # Momentum cut for protons (PDG 2212)
        px, py, pz = p4[:, :, 0], p4[:, :, 1], p4[:, :, 2]
        momentum = np.sqrt(px**2 + py**2 + pz**2)
        mask = mask & ~((pdg == 2212) & (momentum < 0.4))

        final_pdgs = pdg[mask]
        final_p4s = p4[mask]

        # --- 4. Building Rows ---
        rows = []
        for i in range(len(data["EvtNum"])):
            current_type, interaction_type = parse_interaction_code(evt_codes[i])
            row = [data["EvtNum"][i], current_type, interaction_type]
            
            p_info = []
            for p_idx in range(min(len(final_pdgs[i]), 4)):
                p_info.append(final_pdgs[i][p_idx])
                p_info.extend(final_p4s[i][p_idx].tolist())
            
            while len(p_info) < 20: p_info.append(None)
            rows.append(row + p_info[:20])

        # --- 5. Save ---
        df = pd.DataFrame(rows)
        header = ["EvtNum", "CurrentType", "InteractionType"]
        for i in range(1, 5):
            header.extend([f"P{i}_id", f"P{i}_px", f"P{i}_py", f"P{i}_pz", f"P{i}_E"])
        
        df.to_csv(output_csv, header=header, index=False)
        print(f"Done! Saved to {output_csv}")