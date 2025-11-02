# data_cleaning_agent.py

import pandas as pd
import numpy as np

def clean_data(df):
    """Clean and preprocess the dataset."""
    print("\n🔧 Starting Data Cleaning Phase...")

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Fill missing numeric values with column means
    df = df.fillna(df.mean(numeric_only=True))

    # Standardize column names (lowercase, replace spaces with underscores)
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    # ✅ Standardize date columns (this is the new addition)
    for col in df.columns:
        if 'date' in col:  # If column name contains 'date'
            df[col] = pd.to_datetime(df[col], errors='coerce')

    print("✅ Data cleaned successfully!")
    print(f"Cleaned Data Shape: {df.shape}")

    return df


# ✅ Optional: test this file individually
if __name__ == "__main__":
    from data_import_agent import import_data
    df = import_data("dataset.csv")
    cleaned_df = clean_data(df)
    print(cleaned_df.head())
