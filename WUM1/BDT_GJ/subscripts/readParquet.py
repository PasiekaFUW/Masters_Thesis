import pandas as pd
import os
import glob

def read_parquet(path: str):
    """
    Reads all parquet files found directly within the specified directory.
    Does NOT enter subdirectories.
    """
    # 1. Check if the path is a directory
    if os.path.isdir(path):
        # Find all .parquet files strictly inside this folder
        search_pattern = os.path.join(path, "*.parquet")
        files = glob.glob(search_pattern)
        
        if not files:
            raise FileNotFoundError(f"No .parquet files found directly in: {path}")
        
        print(f"Found {len(files)} files in {path}. Loading...")
        
        # Load each file into a list and combine
        df_list = [pd.read_parquet(f) for f in files]
        df = pd.concat(df_list, ignore_index=True)
        
    # 2. If the user provided a direct path to a single file
    elif os.path.isfile(path) and path.endswith(".parquet"):
        df = pd.read_parquet(path)
    
    else:
        raise ValueError(f"The path '{path}' is not a valid directory or parquet file.")

    print(f"✅ Successfully loaded {len(df)} rows.")
    return df