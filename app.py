import streamlit as st
import pandas as pd

# ----------------------------
# Custom Streamlit Styling
# ----------------------------
st.markdown("""
<style>
h1 {
    color: #2E8B57;
    font-family: 'Trebuchet MS', sans-serif;
    text-align: center;
}
.stButton>button {
    background-color: #2E8B57;
    color: white;
    border-radius: 10px;
    height: 40px;
    width: 200px;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Title and description
# ----------------------------
st.title("🚀 Intelligent AI Data Analysis Agent")
st.markdown("Upload your dataset (CSV or Excel) to preview and analyze data easily.")

# ----------------------------
# Sidebar for upload & options
# ----------------------------
with st.sidebar:
    st.header("📂 Upload Data")
    file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx'])
    analysis_option = st.selectbox(
        "Select Analysis Type",
        ["Preview Data", "Summary Statistics", "Show Columns"]
    )

# ----------------------------
# Phase 1: Data Loading Logic
# ----------------------------
def load_file(uploaded_file):
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("❌ Unsupported file format.")
            return None
        return df
    except Exception as e:
        st.error(f"⚠️ Error reading file: {e}")
        return None

# ----------------------------
# Display Results
# ----------------------------
df = load_file(file)

if df is not None:
    st.success("✅ File loaded successfully!")

    if analysis_option == "Preview Data":
        st.dataframe(df.head(10))
    elif analysis_option == "Summary Statistics":
        st.write(df.describe())
    elif analysis_option == "Show Columns":
        st.write(df.columns.tolist())
else:
    st.info("Please upload a dataset to begin.")



