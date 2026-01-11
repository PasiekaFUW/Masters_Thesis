#GJ 
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

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