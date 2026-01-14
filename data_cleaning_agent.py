#data_cleaning_agent
import pandas as pd
import numpy as np
import streamlit as st

def clean_data(df):
    """Automatically clean and preprocess any dataset for Streamline Analyst."""
    st.write("🔧 Starting Data Cleaning Phase...")

    df = df.copy()

    # 1️⃣ Remove duplicates
    df.drop_duplicates(inplace=True)

    # 2️⃣ Standardize column names
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    # 3️⃣ Handle missing values
    for col in df.columns:
        if df[col].dtype in [np.float64, np.int64]:
            df[col].fillna(df[col].mean(), inplace=True)
        elif df[col].dtype == "object":
            if not df[col].mode().empty:
                df[col].fillna(df[col].mode()[0], inplace=True)
            else:
                df[col].fillna("unknown", inplace=True)
        else:
            df[col].fillna(method="ffill", inplace=True)  # forward fill for other types

    # 4️⃣ Clean text columns
    text_cols = df.select_dtypes(include=["object"]).columns
    for col in text_cols:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.lower()
            .replace(r"[^a-z0-9\s]", "", regex=True)
        )

    # 5️⃣ Convert date/time columns
    for col in df.columns:
        if "date" in col or "time" in col:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    st.success(f"✅ Data cleaned successfully! Final shape: {df.shape}")
    return df

# Optional local test
if __name__ == "__main__":
    df = pd.read_csv("dataset.csv")
    cleaned_df = clean_data(df)
    print("\nPreview of Cleaned Data:")
    print(cleaned_df.head())
