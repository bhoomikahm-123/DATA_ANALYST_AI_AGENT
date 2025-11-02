import matplotlib.pyplot as plt
import seaborn as sns

def visualize_data(df):
    """Create and save visualizations for analysis results."""
    print("\n📊 Creating Visualizations...")
    num_cols = df.select_dtypes(include='number').columns

    # Example: correlation heatmap
    plt.figure(figsize=(8,6))
    sns.heatmap(df[num_cols].corr(), annot=True, cmap='coolwarm')
    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.savefig("correlation_heatmap.png")
    plt.close()

    # Example: Cluster count visualization (if cluster exists)
    if 'Cluster' in df.columns:
        sns.countplot(x='Cluster', data=df)
        plt.title("Cluster Distribution")
        plt.savefig("cluster_distribution.png")
        plt.close()

    print("✅ Visualizations saved as images.")
    return ["correlation_heatmap.png", "cluster_distribution.png"]

# Test your phase
if __name__ == "__main__":
    from analysis_agent import analyze_data
    from data_cleaning_agent import clean_data
    from data_import_agent import import_data

    df = import_data("dataset.csv")
    clean_df = clean_data(df)
    analyzed_df, _ = analyze_data(clean_df)
    visualize_data(analyzed_df)
