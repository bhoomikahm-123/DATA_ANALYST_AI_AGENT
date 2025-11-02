import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def analyze_data(df):
    """Perform data analysis and clustering."""
    if df is None or df.empty:
        print("⚠️ No data provided for analysis.")
        return None, None

    print("\n📊 Starting Data Analysis...")

    summary = df.describe(include='all')

    num_data = df.select_dtypes(include='number')
    if not num_data.empty:
        scaler = StandardScaler()
        scaled = scaler.fit_transform(num_data)
        kmeans = KMeans(n_clusters=3, n_init='auto', random_state=42)
        df['Cluster'] = kmeans.fit_predict(scaled)

    print("✅ Analysis completed successfully.")
    return df, summary
