import pandas as pd
import os
import glob

raw_path = 'data/raw/'
processed_path = 'data/processed/processed_data.csv'

# List CSVs in raw folder
all_files = [f for f in glob.glob(os.path.join(raw_path, "*.csv")) if os.path.getsize(f) > 0]
print("Files to load:", all_files)

df_list = []

for f in all_files:
    df = pd.read_csv(f, encoding='utf-8', skip_blank_lines=True)
    
    if 'Date' not in df.columns or 'Close' not in df.columns:
        print(f"Skipping {f} - missing required columns")
        continue
    
    df_list.append(df)
    print(f"Loaded {f} -> rows: {len(df)} columns: {len(df.columns)}")

if not df_list:
    print("No valid CSV files to process!")
    exit()

# Merge all
data = pd.concat(df_list, ignore_index=True)

# Clean & transform
data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
data.sort_values(['Symbol', 'Date'], inplace=True)
data.reset_index(drop=True, inplace=True)

# Optional: Daily return
data['Daily_Return'] = data['Close'].pct_change()

# Save
os.makedirs(os.path.dirname(processed_path), exist_ok=True)
data.to_csv(processed_path, index=False)
print(f"Processed data saved at {processed_path}")
print(data.head())
