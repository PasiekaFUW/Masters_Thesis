#GJ based on https://github.com/WiktorMat/ML_tau_pt/blob/master/inputs.py
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import os

# Define the dictionary mapping
channel_map = {0: 'et', 1: 'mt', 2: 'tt'}

def plot_clean_tree(model, tree_idx=0):
    # Get the channel name from our dictionary
    channel_name = channel_map.get(tree_idx, "Unknown")
    
    # 1. Get the tree data
    df = model.get_booster().trees_to_dataframe()
    df_tree = df[df['Tree'] == tree_idx]
    
    if df_tree.empty:
        print(f"Tree {tree_idx} not found in model.")
        return

    G = nx.DiGraph()
    labels = {}
    pos = {}
    
    def assign_pos(node_id, x, y, width):
        # Filter for the specific node in this tree
        node_row = df_tree[df_tree['ID'] == node_id]
        if node_row.empty: return
        row = node_row.iloc[0]
        
        pos[node_id] = (x, y)
        
        if row['Feature'] != 'Leaf':
            labels[node_id] = f"{row['Feature']}\n<{row['Split']:.1f}"
            assign_pos(row['Yes'], x - width/2, y - 1, width/2)
            assign_pos(row['No'], x + width/2, y - 1, width/2)
            G.add_edge(node_id, row['Yes'])
            G.add_edge(node_id, row['No'])
        else:
            labels[node_id] = f"Value:\n{row['Gain']:.2f}"

    # Start recursion
    root_id = df_tree['ID'].iloc[0]
    assign_pos(root_id, 0, 0, 10)

    # 2. Draw
    plt.figure(figsize=(20, 12))
    nx.draw(G, pos, with_labels=True, labels=labels, 
            node_size=5000, node_color="#e1f5fe", 
            font_size=8, edge_color="gray", arrows=True)
    
    # Updated title using the dictionary mapping
    plt.title(f"Channel: {channel_name} | Visualization of Tree {tree_idx}", fontsize=18, fontweight='bold')
    plt.show()



def plot_physics_res(y_true, y_pred, label):
    res = (y_pred - y_true) / y_true
    
    # Calculate Mean (Bias) and Width (Resolution)
    mean_res = np.mean(res)
    std_res = np.std(res)
    
    plt.hist(res, bins=60, range=(-1.8, 1.8), histtype='step', 
             label=f'{label} (μ={mean_res:.3f}, σ={std_res:.3f})')


def plot_histogram_comparison(y_arr, preds_arr, dim_idx, bins=60, range_vals=(0, 120), output_path=None):
    """Histogram comparing true vs predicted distributions for one dimension"""
    base_dir = '/scratch/gjedrzej/WUM1/BDT_GJ'
    plots_dir = os.path.join(base_dir, 'plots')
    
    # Create the 'plots' folder if it doesn't exist
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)


    if output_path is None:
        filename = f"hist_true_vs_pred_dim{dim_idx+1}.png"
        output_path = os.path.join(plots_dir, filename)
    
    plt.figure(figsize=(10, 6))
    plt.hist(y_arr[:, dim_idx], bins=bins, range=range_vals, alpha=0.5, label="True")
    plt.hist(preds_arr[:, dim_idx], bins=bins, range=range_vals, alpha=0.5, label="Predicted (denorm)")
    plt.xlabel(f"Output dim {dim_idx+1}")
    plt.ylabel("Count")
    plt.legend()
    plt.tight_layout()
    print(f"Saving plot to: {output_path}")
    plt.savefig(output_path)

    # plt.close()



def plot_resolution(
        y_arr, preds_arr, dim_idx, title, bins=60, range_vals=(-1.0, 1.0),
        output_path=None, reco_df=None
    ):
    
    if output_path is None:
        output_path = f"plots/resolution_dim{dim_idx}.png"

    denom = y_arr[:, dim_idx]
    mask = denom != 0
    if not np.any(mask):
        return

    res_pred = (denom[mask] - preds_arr[:, dim_idx][mask]) / denom[mask]
    res_pred = res_pred[(res_pred > range_vals[0]) & (res_pred < range_vals[1])]

    mean = np.mean(res_pred)
    median = np.median(res_pred)
    std = np.std(res_pred)

    p16, p84 = np.percentile(res_pred, [32, 68])
    sigma68 = 0.5 * (p84 - p16)

    p2p5, p97p5 = np.percentile(res_pred, [2.5, 97.5])
    sigma95 = 0.5 * (p97p5 - p2p5)

    plt.hist(
        res_pred, bins=bins, range=range_vals,
        alpha=0.8, color="C0", label="Prediction"
    )

    plt.text(
        0.02, 0.95,
        "Prediction:\n"
        f"mean   = {mean:.4f}\n"
        f"median = {median:.4f}\n"
        f"std    = {std:.4f}\n"
        f"σ68    = {sigma68:.4f}\n"
        f"σ95    = {sigma95:.4f}",
        transform=plt.gca().transAxes,
        verticalalignment="top",
        fontsize=10,
        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
    )

    method_colors = ["C1", "C2", "C3"]

    if reco_df is not None:
        for i, col in enumerate(reco_df.columns):
            reco = reco_df[col]
            label = col
            color = method_colors[i % len(method_colors)]

            res = (denom[mask] - reco[mask]) / denom[mask] - 0.02
            res = res[(res > range_vals[0]) & (res < range_vals[1])]

            mean_r = np.mean(res)
            median_r = np.median(res)
            std_r = np.std(res)

            p16_r, p84_r = np.percentile(res, [32, 68])
            sigma68_r = 0.5 * (p84_r - p16_r)

            p2p5_r, p97p5_r = np.percentile(res, [2.5, 97.5])
            sigma95_r = 0.5 * (p97p5_r - p2p5_r)

            plt.hist(
                res, bins=bins, range=range_vals,
                alpha=0.6, label=label, color=color
            )

            plt.text(
                0.02, 0.70 - 0.22 * i,
                f"{label}:\n"
                f"mean   = {mean_r:.4f}\n"
                f"median = {median_r:.4f}\n"
                f"std    = {std_r:.4f}\n"
                f"σ68    = {sigma68_r:.4f}\n"
                f"σ95    = {sigma95_r:.4f}",
                transform=plt.gca().transAxes,
                verticalalignment="top",
                fontsize=10,
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
            )

    plt.legend()
    plt.xlabel("(pt_true - pt_reco) / pt_true")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(output_path)
    # plt.close()
    plt.title(title)
    plt.show()
