import convert_big_data as conv
import os

output_dir = '/scratch1/gjedrzej/Lab/analysis/processedData'
FilePath = "/scratch1/gjedrzej/Lab/Generators/data/nu_tau_CC_NC_train_interactions.gtrac.root"
output_path = os.path.join(output_dir, 'data_all_tau_train_raw.csv')

# conv.extract_data(FilePath, output_path)
conv.process_massive_csv_in_chunks(output_path, os.path.join(output_dir, 'data_all_tau_train.csv'))