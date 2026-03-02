import uproot
import numpy as np
import awkward as ak
import pandas as pd

# --- Configuration ---
ROOT_FILE_PATH = 'omtfTree.root'
TREE_NAME = 'tOmtf'
MAX_EVENTS_TO_FIND = 10
MIN_PT_TRACKER_MUON = 10.0

# Muon types
SA_MUON_TYPE = 16
TK_MUON_TYPE = 15

def analyze_l1_muon_events_final(file_path, tree_name):
    print(f"--- Starting analysis of {file_path} ---")
    
    try:
        with uproot.open(file_path) as file:
            # ---------------------------------------------------------
            # PART 1: Fetch Event IDs directly from the 'event' branch
            # ---------------------------------------------------------
            # We construct the full path: Tree -> Branch -> Leaf
            print("1. Fetching Event IDs...")
            
            # Using the paths confirmed by your first diagnostic
            runs = file[f'{tree_name}/event/run'].array(library="np")
            lumis = file[f'{tree_name}/event/lumi'].array(library="np")
            ids = file[f'{tree_name}/event/id'].array(library="np")
            
            print(f"   Fetched {len(ids)} event headers.")

            # ---------------------------------------------------------
            # PART 2: Fetch Muon Data using the EXACT keys found
            # ---------------------------------------------------------
            print("2. Fetching Muon Data...")
            
            # We access the l1ObjColl branch first
            l1_branch = file[f'{tree_name}/l1ObjColl']
            
            # Use the literal keys from your diagnostic output
            # Path: l1ObjColl -> theL1Obj -> theL1Obj.pt
            pt_array = l1_branch['theL1Obj/theL1Obj.pt'].array(library="ak")
            type_array = l1_branch['theL1Obj/theL1Obj.type'].array(library="ak")
            
            print(f"   Fetched {len(pt_array)} muon entries.")

    except Exception as e:
        print(f"\n--- FATAL ERROR during data loading ---")
        print(f"Details: {e}")
        return

    # ---------------------------------------------------------
    # PART 3: Analysis
    # ---------------------------------------------------------

    # Separate Tracker Muons and SA Muons
    is_tk_muon = (type_array == TK_MUON_TYPE)
    is_sa_muon = (type_array == SA_MUON_TYPE)
    
    tk_muon_pt = pt_array[is_tk_muon]
    sa_muon_pt = pt_array[is_sa_muon]

    # --- Apply Filtering Logic ---
    
    # Filter 1: Zero Standalone Muons
    filter_no_sa = (ak.num(sa_muon_pt) == 0)

    # Filter 2: At least one Tracker Muon with pT > MIN_PT
    tk_muon_high_pt = (tk_muon_pt >= MIN_PT_TRACKER_MUON)
    filter_high_pt_tk = ak.any(tk_muon_high_pt, axis=1)    
    # Combine filters
    final_filter = filter_no_sa & filter_high_pt_tk
    
    # Count matches
    total_found = np.sum(final_filter)
    
    print("\n------------------------------------------------------------------")
    print(f"Found {total_found} events satisfying the criteria:")
    print(f"   (Tracker Muon pT > {MIN_PT_TRACKER_MUON} GeV) AND (No SA Muon)")
    print("------------------------------------------------------------------")
    
    if total_found > 0:
        # Apply the boolean mask to the numpy arrays of IDs
        selected_runs = runs[final_filter]
        selected_lumis = lumis[final_filter]
        selected_ids = ids[final_filter]
        
        # Create a DataFrame for nice printing
        output_data = pd.DataFrame({
            'Run': selected_runs,
            'Lumi': selected_lumis,
            'Event': selected_ids,
        }).head(MAX_EVENTS_TO_FIND)

        print(output_data.to_string(index=False))
        
        print(f"\nStopped after printing the first {min(total_found, MAX_EVENTS_TO_FIND)} event structures.")
            
    else:
        print("No events found that match the criteria.")

def inspect_event_by_run_lumi_event(file_path, tree_name, target_run, target_lumi, target_event):
    """Print detailed muon info for a specific Run:Lumi:Event"""
    print(f"\n--- Inspecting Run:{target_run} Lumi:{target_lumi} Event:{target_event} ---\n")
    
    try:
        with uproot.open(file_path) as file:
            # Fetch all data
            l1_branch = file[f'{tree_name}/l1ObjColl']
            pt_array = l1_branch['theL1Obj/theL1Obj.pt'].array(library="ak")
            type_array = l1_branch['theL1Obj/theL1Obj.type'].array(library="ak")
            
            runs = file[f'{tree_name}/event/run'].array(library="np")
            lumis = file[f'{tree_name}/event/lumi'].array(library="np")
            ids = file[f'{tree_name}/event/id'].array(library="np")
            
            # Find the event
            mask = (runs == target_run) & (lumis == target_lumi) & (ids == target_event)
            indices = np.where(mask)[0]
            
            if len(indices) == 0:
                print(f"Event not found!")
                return
            
            event_idx = indices[0]
            print(f"Found at index: {event_idx}")
            print(f"\nMuons in this event:")
            print("-" * 70)
            
            # Get muons for this event
            pts = pt_array[event_idx]
            types = type_array[event_idx]
            
            muon_data = []
            for i, (pt, mtype) in enumerate(zip(pts, types)):
                muon_type_name = "Tracker" if mtype == TK_MUON_TYPE else ("Standalone" if mtype == SA_MUON_TYPE else "Unknown")
                muon_data.append({
                    'Index': i,
                    'Type': muon_type_name,
                    'Type_Code': int(mtype),
                    'pT (GeV)': float(pt)
                })
            
            if muon_data:
                df = pd.DataFrame(muon_data)
                print(df.to_string(index=False))
            else:
                print("No muons found in this event!")
                
    except Exception as e:
        print(f"Error inspecting event: {e}")

if __name__ == "__main__":
    analyze_l1_muon_events_final(ROOT_FILE_PATH, TREE_NAME)
    
    # Inspect the specific event: Run 1, Lumi 1, Event 4
    inspect_event_by_run_lumi_event(ROOT_FILE_PATH, TREE_NAME, 1, 1, 4)
    inspect_event_by_run_lumi_event(ROOT_FILE_PATH, TREE_NAME, 1, 2, 139)
    inspect_event_by_run_lumi_event(ROOT_FILE_PATH, TREE_NAME, 1, 2, 169)