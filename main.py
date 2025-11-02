from data_import_agent import import_data
from data_cleaning_agent import clean_data
from analysis_agent import analyze_data
from visualization_agent import visualize_data
from report_export_agent import export_report

def main():
    print("\n🚀 Starting Intelligent Cross-Domain Data Analysis AI Agent...\n")

    # Phase 1: Import
    df = import_data(r"C:\Users\User\Downloads\DATA_ANALYST_AI_AGENT-main\DATA_ANALYST_AI_AGENT-main\Dataset.xlsx")
    print("✅ Phase 1: Data Import Completed\n")

    # Phase 2: Clean
    cleaned_df = clean_data(df)
    print("✅ Phase 2: Data Cleaning Completed\n")

    # Phase 3: Analyze
    analyzed_df, summary = analyze_data(cleaned_df)
    print("✅ Phase 3: Data Analysis Completed\n")

    # Phase 4: Visualize
    charts = visualize_data(analyzed_df)
    print("✅ Phase 4: Visualization Completed\n")

    # Phase 5: Export Report
    export_report(summary, charts)
    print("✅ Phase 5: Report Generated Successfully!\n")

    print("🎉 All phases completed successfully!")

if __name__ == "__main__":
    main()
