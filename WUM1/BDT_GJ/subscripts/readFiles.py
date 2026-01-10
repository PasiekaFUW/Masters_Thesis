import pandas as pd
import matplotlib.pyplot as plt
import sys
import numpy as np
import os
import glob

try:
    import uproot
except ImportError:
    uproot = None
    print("Warning: uproot not installed, .root files will not be supported.")

def read_parquet(path: str):
    """Read data from a parquet file or all parquet files in a folder"""
    if os.path.isdir(path):
        files = glob.glob(os.path.join(path, "*.parquet"))
        if not files:
            raise FileNotFoundError(f"No .parquet files found in directory: {path}")
        df_list = [pd.read_parquet(f) for f in files]
        df = pd.concat(df_list, ignore_index=True)
    else:
        df = pd.read_parquet(path)
    
    print("\n--- Data Preview (parquet) ---")
    print(df.head())
    print("\n--- Columns ---")
    print(df.columns.tolist())

    return df


def read_root(path: str, tree_name: str = None):
    """Read data from ROOT file"""
    if uproot is None:
        raise ImportError("uproot is required to read ROOT files.")

    with uproot.open(path) as f:
        if tree_name is None:
            # pick first tree-like object
            keys = [k for k in f.keys() if f[k].classname.startswith("TTree")]
            if not keys:
                raise ValueError("No TTree found in the ROOT file.")
            tree_name = keys[0]

        tree = f[tree_name]
        df = tree.arrays(library="pd")

    print("\n--- Data Preview (root) ---")
    print(df.head())
    print("\n--- Columns ---")
    print(df.columns.tolist())

    return df


def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <file.parquet|file.root>")
        sys.exit(1)

    path = sys.argv[1]
    ext = os.path.splitext(path)[-1].lower()

    if ext == ".parquet" or os.path.isdir(path):
        df = read_parquet(path)
    elif ext == ".root":
        df = read_root(path)
    else:
        print(f"Unsupported file extension: {ext}")
        sys.exit(1)

    ### <<< SELECTION >>> ###

    selection = (
        (df['pt_1'] > 20)
        & (df['pt_2'] > 20)
        & (abs(df['eta_1']) < 2.4)
        & (abs(df['eta_2']) < 2.4)
        & (df["idDeepTau2018v2p5VSjet_2"] >= 5)  # np. 'tight' WP
        & (df["idDeepTau2018v2p5VSe_2"] >= 2)   # odrzuca fake'i z elektronów
        & (df["idDeepTau2018v2p5VSmu_2"] >= 4)    # odrzuca fake'i z mionów
    )

    df = df[selection].copy()
    print(f"\n✅ After selection: {len(df)} events remain.\n")

    ### <<< DALSZY KOD >>> ###

if __name__ == "__main__":
    main()