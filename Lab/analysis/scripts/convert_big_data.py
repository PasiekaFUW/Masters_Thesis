import os
import uproot
import pandas as pd
import awkward as ak
import time
import re
start_time = time.time()

# import analysis.scripts.preprocess_functions as prf

#neutral_particles = [-12, 12, -14, 14, -16, 16, -2112, 2112, -111, 111, -3122, 3122, -3212, 3212,
#                        -421, 421, -311, 311, -130, 130, 2000000101, 1000180400, 130, 310, 3322, -3322,# 221, 331, 443]

# cząstki neutralne, które uznajemy, że są niewidoczne w detektorze: neutrina i neutrony
# neutrony w zasadzie można rejestrować, ale niska efektywność - obejrzeć pracę MicroBooNE

neutral_particles = [-12, 12, -14, 14, -16, 16, 2112]

def sort_columns_by_suffix(df):
    def sort_key(col):
        match = re.match(r"(\D+)_(\d+)", col)
        
        if match:
            prefix, num = match.groups()
            if (prefix[0]=='P'):
                return int(num), 'A'
            elif(prefix[0]=='E'):
                return int(num), 'z'
            return int(num), prefix
        else:
            
            return float(0), col  
    
    return df[sorted(df.columns, key=sort_key)]

def extract_field(text, field):
    match = re.search(rf"{field}:([^;]+)", text)
    return match.group(1) if match else None

def extract_data(filename, exportname, chunk_size="100 MB"):
    
    # ADDED: Track temporary files and a master list of all unique columns
    temp_files = []
    all_columns = set()
    base_dir = os.path.dirname(exportname) or '.'
    
    print(f"Starting chunked processing of {filename}...")
    
    for i, batch in enumerate(uproot.iterate(f"{filename}:gRooTracker", step_size=chunk_size)):
        print(f"Processing chunk {i+1}...")
        
        evt_num_map = dict(enumerate(batch["EvtNum"]))

        stdhep_status=batch["StdHepStatus"]
        stdhep_status_df=ak.to_dataframe(stdhep_status)
        del stdhep_status

        stdhep_status_df =stdhep_status_df.reset_index()
        stdhep_status_df.rename(columns={"values": "Status"}, inplace=True)

        # Children                 
        stdhep_fchild=batch["StdHepFd"]
        stdhep_fchild_df=ak.to_dataframe(stdhep_fchild)
        del stdhep_fchild

        stdhep_fchild_df =stdhep_fchild_df.reset_index()
        stdhep_fchild_df.rename(columns={"values": "Fchild"}, inplace=True)

        stdhep_lchild=batch["StdHepLd"]
        stdhep_lchild_df=ak.to_dataframe(stdhep_lchild)
        del stdhep_lchild
        
        stdhep_lchild_df =stdhep_lchild_df.reset_index()
        stdhep_lchild_df.rename(columns={"values": "Lchild"}, inplace=True)

        stdhep_Pdg=batch["StdHepPdg"]
        stdhep_Pdg_df=ak.to_dataframe(stdhep_Pdg)
        del stdhep_Pdg

        stdhep_Pdg_df =stdhep_Pdg_df.reset_index()
        stdhep_Pdg_df.rename(columns={"values": "Pdg"}, inplace=True)

        stdhep_Pdg_Status_df=stdhep_Pdg_df[["Pdg"]].join(stdhep_status_df[["Status"]])
        stdhep_Pdg_Status_Fc_df=stdhep_Pdg_Status_df.join(stdhep_fchild_df[["Fchild"]])
        stdhep_Pdg_Status_Fc_Lc_df=stdhep_Pdg_Status_Fc_df.join(stdhep_lchild_df[["Lchild"]])     
        
        del stdhep_Pdg_df
        del stdhep_status_df
        del stdhep_Pdg_Status_df
        del stdhep_Pdg_Status_Fc_df
        
        stdhep_p4 = batch["StdHepP4"]
        
        stdhep_p4_rec = ak.zip({
            "px": stdhep_p4[..., 0],
            "py": stdhep_p4[..., 1],
            "pz": stdhep_p4[..., 2],
            "E":  stdhep_p4[..., 3],
        })

        del stdhep_p4
        stdhep_df = ak.to_dataframe(stdhep_p4_rec)
        del stdhep_p4_rec

        stdhep_df = stdhep_df.reset_index()

        stdhep_df['entry'] = stdhep_df['entry'].map(evt_num_map)
        stdhep_df.rename(columns={"entry": "EvtNum", "subentry": "particle"}, inplace=True)
        
        df = pd.DataFrame({"EvtNum": batch["EvtNum"]})

        proc_split=ak.to_dataframe(batch['fString'])  

        proc_split=proc_split.reset_index() 
        proc_split['entry'] = proc_split['entry'].map(evt_num_map)
        proc_split.rename(columns={"entry": "EvtNum","values": "EvtCode"}, inplace=True)

        nu_df = proc_split['EvtCode'].apply(lambda x: extract_field(x, "nu"))
        proc_df = proc_split['EvtCode'].apply(lambda x: extract_field(x, "proc"))
        
        general_df = proc_df.str.extract(r"Weak\[(.*?)\]")
        general_df.rename(columns={0: "CCNC"}, inplace=True)
        
        inttype_df = proc_df.str.extract(r"\](.*?)(?:;|$)").iloc[:, 0].str.lstrip(",")  

        nu_df=nu_df.to_frame(name="Nu")
        inttype_df=inttype_df.to_frame(name="IntType")

        all_df = pd.concat([nu_df,general_df,inttype_df],axis=1)
        
        stdhep_df=stdhep_df.drop('particle',axis=1)

        merged_from_EvtCode = pd.concat([df,all_df],axis=1)
        del df

        merged_P4 = pd.merge(merged_from_EvtCode,stdhep_df, on="EvtNum")
        del stdhep_df

        total_merged=merged_P4.join(stdhep_Pdg_Status_Fc_Lc_df)    
        total_merged=total_merged[total_merged["Status"] == 1]
        total_merged=total_merged[~total_merged["Pdg"].isin(neutral_particles)]
        total_merged=total_merged.drop(['Status','CCNC','IntType','Nu'],axis=1)
        
        total_merged['row_number'] = total_merged.groupby('EvtNum').cumcount() + 1
        
        df_wide = total_merged.pivot(index='EvtNum', columns='row_number')

        df_wide.columns = [f'{col}_{num}' for col, num in df_wide.columns]
        df_wide = df_wide.reset_index()

        df_total = pd.merge(merged_from_EvtCode,df_wide, on="EvtNum")
        del merged_from_EvtCode, df_wide
        
        # CHANGED: Instead of holding in RAM, save chunk to a temporary pickle file
        temp_file = os.path.join(base_dir, f"temp_chunk_{i}.pkl")
        df_total.to_pickle(temp_file)
        temp_files.append(temp_file)
        
        # Track all unique columns encountered across chunks
        all_columns.update(df_total.columns)
        
        # Force garbage collection to free RAM
        del df_total, total_merged, merged_P4
        import gc
        gc.collect()

    print("\nAll chunks processed. Assembling final CSV...")

    # ADDED: Determine the final master column layout
    dummy_df = pd.DataFrame(columns=list(all_columns))
    dummy_df = sort_columns_by_suffix(dummy_df)
    final_cols = dummy_df.columns.tolist()

    # ADDED: Write just the header to the final CSV
    pd.DataFrame(columns=final_cols).to_csv(exportname, index=False)

    # ADDED: Stream temp files to the final CSV one by one
    for temp_file in temp_files:
        df_chunk = pd.read_pickle(temp_file)
        
        # reindex automatically aligns the columns and fills missing particle columns with 0
        df_chunk = df_chunk.reindex(columns=final_cols, fill_value=0)
        df_chunk.fillna(0, inplace=True)
        
        # Append to final CSV
        df_chunk.to_csv(exportname, mode='a', index=False, header=False)
        
        # Delete temp file to save disk space
        os.remove(temp_file)

    print(f"Data successfully exported to {exportname}!")

import pandas as pd

def process_massive_csv_in_chunks(input_csv, output_csv, chunk_size=100000):
    import preprocess_functions as pf
    import os

    print(f"Starting chunked preprocessing of {input_csv}...")
    
    # Read the first chunk just to get the final cleaned columns for the header
    first_chunk = next(pd.read_csv(input_csv, chunksize=10))
    first_chunk = pf.get_feature_data(first_chunk, ['ch_pions', 'charged', 'n_pions'], 
                                  ['multiplicity', 'p_leading', 'pt_leading', 'cos_theta_leading'])
    first_chunk = pf.clean_particle_data(first_chunk)
    
    # Write the header to the new file (only once)
    if not os.path.exists(output_csv):
        first_chunk.iloc[0:0].to_csv(output_csv, index=False)
    # first_chunk.iloc[0:0].to_csv(output_csv, index=False)
    
    # Now process the real data in chunks
    for i, chunk in enumerate(pd.read_csv(input_csv, chunksize=chunk_size)):
        print(f"  Calculating features for chunk {i+1}...")
        
        # 1. Fill NaNs first! (Crucial for your math functions)
        chunk = pf.fill_nans(chunk, 0)
        
        # 2. Calculate features
        chunk = pf.get_feature_data(chunk, ['ch_pions', 'charged', 'n_pions'], 
                                 ['multiplicity', 'p_leading', 'pt_leading', 'cos_theta_leading'])
        
        # 3. Clean away the heavy raw columns
        chunk = pf.clean_particle_data(chunk)
        
        # 4. Append to the lightweight CSV
        chunk.to_csv(output_csv, mode='a', index=False, header=False)

    print(f"Finished! Cleaned data saved to {output_csv}")



# def build_offline_combined_set(path_cc, path_nc, output_path):
#     print("Loading CC dataset...")
#     df_cc = pd.read_csv(path_cc)
    
#     print("Loading NC dataset...")
#     df_nc = pd.read_csv(path_nc)
    
#     print("Merging datasets...")
#     # Using your existing function to combine them
#     df_combined = prf.prepare_combined_pool(df_cc, df_nc)
    
#     print("Filling NaNs...")
#     # Filling NaNs offline so the training script doesn't have to
#     df_combined = prf.fill_nans(df_combined)
    
    
#     print(f"Saving merged dataset to {output_path}...")
#     df_combined.to_csv(output_path, index=False)
#     print("Offline preparation complete!")