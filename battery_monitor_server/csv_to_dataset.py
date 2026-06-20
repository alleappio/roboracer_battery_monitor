import pandas as pd
import numpy as np

def create_battery_ml_dataset_flexible(csv_filename, target_v_drop=0.05, output_filename='battery_ml_dataset.csv'):
    # 1. Load your raw CSV
    df = pd.read_csv(csv_filename)
    
    # Calculate net amp-hours
    df['net_ah'] = df['charge_drawn'] - df['charge_regen']
    
    # Filter out any hardware fault codes first
    df = df[df['fault_code'] == 0].reset_index(drop=True)
    
    dataset_rows = []
    
    # 2. Use a pointer to step through the rows sequentially
    i = 0
    while i < len(df) - 1:
        start_row = df.iloc[i]
        v_start = start_row['voltage_input']
        ah_start = start_row['net_ah']
        
        found_next_point = False
        
        # Look forward until the voltage drops by our target amount (e.g., 0.05V)
        for j in range(i + 1, len(df)):
            end_row = df.iloc[j]
            v_end = end_row['voltage_input']
            ah_end = end_row['net_ah']
            
            delta_v = v_start - v_end
            delta_ah = ah_end - ah_start
            
            # If we hit the target voltage drop window
            if delta_v >= target_v_drop:
                # Ensure capacity was actually consumed
                if delta_ah > 0:
                    dataset_rows.append({
                        'v_start': round(v_start, 2),
                        'delta_v': round(delta_v, 3),
                        'delta_ah': round(delta_ah, 4)
                    })
                    # Move our starting pointer to this new index to start the next window
                    i = j
                    found_next_point = True
                    break
        
        # If we couldn't find any further voltage drop in the rest of the file, stop
        if not found_next_point:
            break

    # 3. Save to clean DataFrame
    ml_df = pd.DataFrame(dataset_rows)
    
    if not ml_df.empty:
        ml_df = ml_df.drop_duplicates().reset_index(drop=True)
        ml_df.to_csv(output_filename, index=False)
        print(f"Success! Created {len(ml_df)} training samples using a {target_v_drop}V window.")
    else:
        print("DataFrame is still empty. Your total voltage drop across the entire file might be lower than the target threshold.")
        
    return ml_df

# --- Run the Flexible Script ---
# We use a tiny 0.05V window to guarantee it catches data on short test runs
ml_ready_data = create_battery_ml_dataset_flexible('your_raw_mqtt_logs.csv', target_v_drop=0.05)
print(ml_ready_data)
