def get_experiment_folder(base_name="training_run"):
    from datetime import datetime
    import os
    
    # Since we are already IN /Lab, the target is just 'checkpoints'
    target_root = "checkpoints"
    
    # 1. Get the current date
    date_str = datetime.now().strftime("%Y-%m-%d")
    folder_name = f"{date_str}_{base_name}"
    
    # 2. Create the initial full path relative to /Lab
    final_path = os.path.join(target_root, folder_name)
    
    # 3. Check for existence and increment
    counter = 1
    while os.path.exists(final_path):
        new_folder_name = f"{folder_name}({counter})"
        final_path = os.path.join(target_root, new_folder_name)
        counter += 1
    
    # 4. Create the folder (and its parent 'checkpoints' if it doesn't exist)
    os.makedirs(final_path, exist_ok=True)
    
    print(f"--- Experiment directory created: {final_path} ---")
    return final_path