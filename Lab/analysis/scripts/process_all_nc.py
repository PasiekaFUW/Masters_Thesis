import os
import convert_big_data as conv

# 1. Configuration
output_dir = '/scratch1/gjedrzej/Lab/analysis/processedData'
final_output_path = os.path.join(output_dir, 'data_NC_train_cleaned_ALL.csv')

# Base path with {} where the number will go
base_input_path = "/scratch1/gjedrzej/Lab/Generators/data/NC_samples/nu_tau_NC_{}_interactions.gtrac.root"

# Delete the final output file if it exists from a previous failed run 
# so we don't accidentally append to old data
if os.path.exists(final_output_path):
    os.remove(final_output_path)
    print(f"Removed old final output file: {final_output_path}")

# 2. Main Processing Loop
for i in range(1, 13):  # Loops from 1 up to 12
    input_root = base_input_path.format(i)
    
    # Create a unique temporary heavy CSV for this specific root file
    temp_heavy_csv = os.path.join(output_dir, f'temp_heavy_NC_{i}.csv')
    
    print(f"\n" + "="*40)
    print(f"Processing File {i} of 12")
    print(f"Input: {input_root}")
    print("="*40)
    
    # Safety check
    if not os.path.exists(input_root):
        print(f"WARNING: File {input_root} not found! Skipping...")
        continue
        
    # --- STEP A: Extract to Temporary Heavy CSV ---
    conv.extract_data(input_root, temp_heavy_csv)
    
    # --- STEP B: Process and append to Final Cleaned CSV ---
    # Because of our tweak, this will write the header on file 1, and just append for files 2-12
    conv.process_massive_csv_in_chunks(temp_heavy_csv, final_output_path)
    
    # --- STEP C: Cleanup ---
    if os.path.exists(temp_heavy_csv):
        os.remove(temp_heavy_csv)
        print(f"Deleted temporary heavy file: {temp_heavy_csv}")

print(f"\nAll 12 files successfully processed and merged into:")
print(final_output_path)