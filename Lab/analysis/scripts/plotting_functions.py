def plot_physics_single_canva(dfs, mode, feature='multiplicity', titles=["All (CC+NC)", "Signal CC", "Background NC"], ax=None, density=True):
    import numpy as np
    import matplotlib.pyplot as plt
    import pandas as pd

    plot_data = []
    active_titles = []
    
    column_name = f"{feature}_{mode}"
    
    label_map = {
        'multiplicity': 'Multiplicity',
        'p_leading': 'Leading Momentum [GeV/c]',
        'pt_leading': 'Leading Transverse Momentum [GeV/c]',
        'theta_leading': 'Leading Theta [rad]',
        'cos_theta_leading': 'cos(Theta)'
    }
    x_label = label_map.get(feature, feature)

    # --- Data Extraction with Skip Logic ---
    for i, df in enumerate(dfs):
        # Skip if the item is None or not a DataFrame
        if df is None or not isinstance(df, pd.DataFrame):
            continue
            
        if column_name in df.columns:
            series = df[column_name].dropna()
            if not series.empty:
                plot_data.append(series)
                # Keep track of which title belongs to which valid DF
                active_titles.append(titles[i] if i < len(titles) else f"Dataset {i+1}")
        else:
            print(f"Warning: Column {column_name} not found in dataset {i}")

    if not plot_data:
        print(f"No data found for {column_name} in any provided dataframes.")
        return ax

    # --- Binning Logic ---
    if feature == 'multiplicity':
        all_max = [d.max() for d in plot_data]
        max_val = int(max(all_max)) if all_max else 5
        common_bins = np.arange(0, max_val + 2) - 0.5
    else:
        min_val = min([d.min() for d in plot_data])
        max_val = max([d.max() for d in plot_data])
        common_bins = np.linspace(min_val, max_val, 80)

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    # Colors mapped to your original list: 0:Gray, 1:Blue, 2:Green
    full_color_list = ['gray', 'blue', 'green', 'darkorange', 'purple', 'cyan']
    
    # We need to pick the color based on the original index in 'dfs'
    # so that CC is always blue and NC is always green
    color_indices = [i for i, df in enumerate(dfs) if df is not None and isinstance(df, pd.DataFrame)]

    for idx, (data, title) in enumerate(zip(plot_data, active_titles)):
        # Use the original index to pick the color
        original_idx = color_indices[idx]
        c = full_color_list[original_idx % len(full_color_list)]
            
        if feature == 'multiplicity':
            ax.hist(data, bins=common_bins, color=c, edgecolor='black', 
                     alpha=0.5, density=density, rwidth=0.8, label=title)
            ax.set_xticks(range(int(max_val) + 1))
        else:
            ax.hist(data, bins=common_bins, color=c, edgecolor=c, 
                     alpha=0.5, density=density, label=title, histtype='stepfilled')
            ax.hist(data, bins=common_bins, color=c, 
                     density=density, histtype='step', linewidth=1.5)

    # Formatting 
    ax.set_title(f"{mode.upper()} - {feature.replace('_', ' ').capitalize()}")
    ax.set_xlabel(x_label)
    ax.set_ylabel("Prob. Density" if density else "Count")
    ax.grid(axis='both', linestyle=':', alpha=0.6)
    ax.legend()
    
    return ax

def plot_physics_results(df, column='CCNC', ccnc_filter=None, int_filter=None, ax=None, density=False, color='skyblue', bins=None):
    import matplotlib.pyplot as plt
    import numpy as np
    """
    column: 'CCNC', 'IntType', 'Prob_is_CC', or 'NN_Decision_CC'
    ccnc_filter: 1 or 0 (after transformation)
    int_filter: 'DIS', 'RES', 'QES', 'MEC' (Strings)
    """
    # 1. Apply Filters
    subset = df.copy()
    
    # Check for None specifically so that '0' (NC) doesn't get skipped
    if ccnc_filter is not None:
        subset = subset[subset['CCNC'] == ccnc_filter]
        
    if int_filter is not None:
        subset = subset[subset['IntType'] == int_filter]

    # 2. Setup Axes
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 4))

    if subset.empty:
        ax.text(0.5, 0.5, f"No Data Found for\n{int_filter if int_filter else ''}", 
                ha='center', va='center', fontsize=12, color='gray')
        return ax

    # 3. Categorical Plots (CCNC, IntType, NN_Decision_CC)
    if column in ['CCNC', 'IntType', 'NN_Decision_CC']:
        labels, counts = np.unique(subset[column], return_counts=True)
        
        display_counts = counts.astype(float)
        if density:
            display_counts /= counts.sum()
            y_label = "Density"
        else:
            y_label = "Events"

        # Sort labels to keep DIS/RES/QES/MEC order consistent if possible
        ax.bar([str(l) for l in labels], display_counts, alpha=0.7, edgecolor='black', color=color)
        ax.set_ylabel(y_label)
        ax.set_title(f"Distribution of {column}")

    # 4. Probability Plots (Separation Power)
    elif column == 'Prob_is_CC':
        if bins is None:
            bins = np.linspace(0, 1, 41)
        
        # Using 1 and 0 for labels
        cc_vals = subset[subset['CCNC'] == 1][column]
        nc_vals = subset[subset['CCNC'] == 0][column]

        # Use your Green/Blue theme
        if not nc_vals.empty:
            ax.hist(nc_vals, bins=bins, density=density, alpha=0.3, 
                    label='True NC (0)', color='green', histtype='stepfilled')
            ax.hist(nc_vals, bins=bins, density=density, histtype='step', 
                    color='green', lw=1.5)
            
        if not cc_vals.empty:
            ax.hist(cc_vals, bins=bins, density=density, alpha=0.3, 
                    label='True CC (1)', color='blue', histtype='stepfilled')
            ax.hist(cc_vals, bins=bins, density=density, histtype='step', 
                    color='blue', lw=1.5)
        
        ax.set_xlabel("NN Prediction (CC Probability)")
        ax.set_ylabel("Density" if density else "Events")
        ax.legend(frameon=True, loc='upper center')
        
        filter_text = f"Mode: {int_filter}" if int_filter else "Full Dataset"
        ax.set_title(f"Separation: {filter_text}")

    ax.grid(axis='y', alpha=0.3, ls='--')
    return ax

# The master list (the order the CNN sees)
# The master feature map for the 1D CNN
FEATURE_INDEX_MAP = {
    0:  'p_leading_ch_pions',
    1:  'pt_leading_ch_pions',
    2:  'cos_theta_leading_ch_pions',
    3:  'multiplicity_ch_pions',
    4:  'multiplicity_charged',
    5:  'p_leading_charged',
    6:  'pt_leading_charged',
    7:  'cos_theta_leading_charged',
    8:  'multiplicity_n_pions',
    9:  'p_leading_n_pions',
    10: 'pt_leading_n_pions',
    11: 'cos_theta_leading_n_pions'
}
# Set of indices that should use integer-aligned bins in plots
DISCRETE_FEATURE_INDICES = {3, 4, 8}


def plot_feature_from_dataset(dataset, feature_idx, feature_list=FEATURE_INDEX_MAP, ax=None, density=False):
    """
    Plots distributions directly from a tf.data.Dataset to verify preprocessing.
    feature_list: The list of 12 column names used in preProcess_data.
    """
    import numpy as np
    import matplotlib.pyplot as plt

    feature_name = feature_list[feature_idx]
    cc_data = []
    nc_data = []

    # 1. Collect data from the TF Dataset batches
    for features, labels in dataset:
        feat_np = features.numpy()
        lab_np = labels.numpy()
        
        # In case features are (Batch, 12, 1), flatten or index properly
        if len(feat_np.shape) == 3:
            val = feat_np[:, feature_idx, 0]
        else:
            val = feat_np[:, feature_idx]
        
        cc_data.extend(val[lab_np == 1.0])
        nc_data.extend(val[lab_np == 0.0])

    cc_data = np.array(cc_data)
    nc_data = np.array(nc_data)

    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 5))

    # --- Smart Physics Binning Logic ---
    # Automatically detect discrete variables by name
    is_discrete = "multiplicity" in feature_name.lower()
    
    all_vals = np.concatenate([cc_data, nc_data])
    if len(all_vals) == 0: 
        ax.text(0.5, 0.5, "Empty Dataset", ha='center')
        return ax
    
    min_val, max_val = all_vals.min(), all_vals.max()

    if is_discrete:
        common_bins = np.arange(0, int(max_val) + 2) - 0.5
        rwidth = 0.8
        ax.set_xticks(range(int(max_val) + 1))
    else:
        common_bins = np.linspace(min_val, max_val, 60)
        rwidth = 1.0

    # 2. Plotting using the Green/Blue theme
    ax.hist(nc_data, bins=common_bins, label='NC (0)', 
            color='green', alpha=0.4, edgecolor='green', 
            density=density, rwidth=rwidth, histtype='stepfilled')
    
    ax.hist(cc_data, bins=common_bins, label='CC (1)', 
            color='blue', alpha=0.4, edgecolor='blue', 
            density=density, rwidth=rwidth, histtype='stepfilled')

    # Formatting
    ax.set_title(f"TF Dataset Audit: {feature_name}")
    ax.set_xlabel(feature_name.replace('_', ' ').capitalize())
    ax.set_ylabel("Probability Density" if density else "Counts")
    ax.grid(axis='both', linestyle=':', alpha=0.6)
    ax.legend()
    
    return ax

def plotTrainHistory(history):
  import matplotlib.pyplot as plt
  fig, axes = plt.subplots(1, 2, figsize=(10, 5))
  axes[0].plot(history.history['loss'], 'blue', label = 'train')
  axes[0].plot(history.history['val_loss'], 'orange', label = 'validation')
  axes[0].set_title('Loss function')
  axes[0].set_xlabel('Epoch')
  axes[0].legend(loc='upper right')

  axes[1].plot(history.history['loss'], 'blue', label = 'train')
  axes[1].plot(history.history['val_loss'], 'orange', label = 'validation')
  axes[1].set_title('Loss Function Log')
  axes[1].set_xlabel('Epoch')
  axes[1].set_yscale('log')
  axes[1].legend(loc='upper right')

  plt.subplots_adjust(bottom = 0.02, left = 0.02, right = 0.98, wspace = 0.4)
  plt.show()


def plotConfusionMatrix(df, label_col='CCNC', pred_col='NN_Decision_CC', title="Confusion Matrix", ax=None, cmap='Blues'):
    from sklearn.metrics import ConfusionMatrixDisplay
    import matplotlib.pyplot as plt
    
    # 1. Map labels to integers (NC=0, CC=1)
    mapping = {"NC": 0, "CC": 1}
    y_true = df[label_col].map(mapping).fillna(df[label_col]).astype(int)
    y_pred = df[pred_col].astype(int)

    # 2. Handle axis creation
    if ax is None:
        fig, ax = plt.subplots(figsize=(5, 5))

    # 3. Plot
    cmd = ConfusionMatrixDisplay.from_predictions(
        y_true, 
        y_pred, 
        display_labels=["NC", "CC"], 
        normalize="true", 
        values_format=".2f", 
        ax=ax,
        cmap=cmap
    )
    
    ax.set_title(title)
    
    return ax

def plotROC(df, label_col='CCNC', prob_col='Prob_is_CC', model_name="1DCNN", ax=None, color='darkorange', thresholds_to_plot=None):
    from sklearn.metrics import RocCurveDisplay, roc_auc_score, roc_curve
    import matplotlib.pyplot as plt
    import numpy as np
    
    # Set default thresholds to plot if none are provided
    if thresholds_to_plot is None:
        thresholds_to_plot = [0.3, 0.5, 0.7]
        
    # 1. Map labels to integers
    mapping = {"NC": 0, "CC": 1}
    y_true = df[label_col].map(mapping).fillna(df[label_col]).astype(int)
    y_score = df[prob_col]

    # 2. Create axis if not provided (allows for subplots)
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))

    # 3. Plotting the main ROC curve
    RocCurveDisplay.from_predictions(
        y_true, 
        y_score, 
        name=model_name,
        color=color,
        ax=ax
    )

    # 4. Extract arrays to plot threshold points
    fpr, tpr, thresholds = roc_curve(y_true, y_score)

    # 5. Find and plot specific decision thresholds
    if thresholds_to_plot:
        # Define a few colors/markers if you want them distinct, or keep them uniform
        for thresh in thresholds_to_plot:
            # Find the index of the threshold closest to our target
            idx = np.argmin(np.abs(thresholds - thresh))
            
            # Scatter plot the point on the axis
            ax.scatter(fpr[idx], tpr[idx], marker='o', s=60, edgecolors='black', zorder=5, label=f'Thr ≈ {thresh}')
            
            # Annotate the point on the graph
            ax.annotate(f"{thresh}", 
                        (fpr[idx], tpr[idx]), 
                        textcoords="offset points", 
                        xytext=(10, -10), # Offset x and y to prevent covering the line
                        ha='center',
                        fontsize=9)

    # Add the "Chance" line
    ax.plot([0, 1], [0, 1], "k--")

    ax.set_title(f"ROC Curve - {model_name}")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.legend()
    ax.grid(alpha=0.3)

    # 6. Print score and return the axis
    auc_value = roc_auc_score(y_true, y_score)
    print(f"{model_name} ROC AUC: {auc_value:.4f}")
    
    return ax


def plotFeatureImportance(model, data_batch, feature_map=FEATURE_INDEX_MAP, title="Feature Dependency (Saliency Map)", ax=None):
    import tensorflow as tf
    import numpy as np
    import matplotlib.pyplot as plt

    # 1. Calculate Importance via Backprop
    # Extract one batch from the tf.data.Dataset
    for images, labels in data_batch.take(1):
        input_tensor = tf.convert_to_tensor(images)
        break
    
    with tf.GradientTape() as tape:
        tape.watch(input_tensor)
        predictions = model(input_tensor)
        
    # Get gradients of output w.r.t input
    grads = tape.gradient(predictions, input_tensor)
    
    # Average the absolute gradient magnitude across the batch
    importance = tf.reduce_mean(tf.abs(grads), axis=0).numpy().flatten()
    
    # 2. Map indices to names
    feature_names = [feature_map.get(i, f"feat_{i}") for i in range(len(importance))]

    # 3. Plotting
    # If no ax is provided, create a new figure and ax
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 5))
    
    # Using a horizontal bar chart often makes long physics labels easier to read
    bars = ax.barh(feature_names, importance, color='teal', edgecolor='black', alpha=0.8)
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel("Sensitivity (Mean |Gradient|)")
    ax.set_ylabel("Physics Feature")
    ax.grid(axis='x', linestyle='--', alpha=0.6)
    
    # Invert y-axis so the first feature (index 0) is at the top
    ax.invert_yaxis() 
    
    # Note: Removed plt.show() so the ax remains active and modifiable
    plt.tight_layout()
    
    return ax