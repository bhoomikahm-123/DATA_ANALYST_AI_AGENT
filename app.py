import time
import os
import streamlit as st
from streamlit_lottie import st_lottie
from util import load_lottie, stream_data, welcome_message, introduction_message
from regression_model import regression_model_pipeline
from visualization import render_and_save_charts, render_chart
from src.util import read_file_from_streamlit
from data_cleaning_agent import clean_data
from data_analysis_agent import analyze_data_with_charts
# <-- updated import: use the premium PDF exporter
from report_export_agent import create_premium_pdf
from Dashboard_export_agent import render_dashboard_image
from dotenv import load_dotenv

# Load .env for GOOGLE_API_KEY
load_dotenv()
GOOGLE_API_KEY = st.secrets["google"]["api_key"] if "google" in st.secrets else os.getenv("GOOGLE_API_KEY")
def _ensure_api_key_ui():
    if not GOOGLE_API_KEY:
        with st.sidebar:
            st.error("GOOGLE_API_KEY not found. Add it to Streamlit Secrets or .env.")
        return False
    return True
# ========================================
# Helper: Normalize saved charts output
# ========================================
def _normalize_saved_charts(saved_charts):
    """Accepts either list of paths or list of dicts with 'saved_path'.
    Returns list of file paths (strings).
    """
    out = []
    if not saved_charts:
        return out
    for item in saved_charts:
        if isinstance(item, dict):
            # common keys: saved_path, path, filename
            path = item.get("saved_path") or item.get("path") or item.get("filename")
            if path:
                out.append(path)
        elif isinstance(item, str):
            out.append(item)
    return out


# ========================================
# PAGE CONFIG
# ========================================
st.set_page_config(page_title="InsightPilot", page_icon=":rocket:", layout="wide")

# Small utility to show a persistent API-key banner if missing
def _ensure_api_key_ui():
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        with st.sidebar:
            st.error("GOOGLE_API_KEY not found. Add it to your .env or environment variables.")
            st.markdown("Follow the instructions to create/renew a Google Generative AI API key in AI Studio.")
        return False
    return True

# ========================================
# TITLE SECTION
# ========================================
with st.container():
    st.subheader("Hello there 👋")
    st.title("Welcome to InsightPilot!")

    if 'initialized' not in st.session_state:
        st.session_state.initialized = True

    if st.session_state.initialized:
        st.session_state.welcome_message = welcome_message()
        st.write(stream_data(st.session_state.welcome_message))
        time.sleep(0.5)
        st.write("[GitHub > ](https://github.com/Wilson-ZheLin/Streamline-Analyst)")
        st.session_state.initialized = False
    else:
        st.write(st.session_state.welcome_message)
        st.write("[GitHub > ](https://github.com/Wilson-ZheLin/Streamline-Analyst)")

# ========================================
# INTRO SECTION
# ========================================
with st.container():
    st.divider()
    if 'lottie' not in st.session_state:
        st.session_state.lottie_url1, st.session_state.lottie_url2 = load_lottie()
        st.session_state.lottie = True

    # What can InsightPilot do?
    left_column_r1, right_column_r1 = st.columns([6, 4])
    with left_column_r1:
        st.header("What can InsightPilot do?")
        st.write(introduction_message()[0])
    with right_column_r1:
        if st.session_state.lottie:
            st_lottie(st.session_state.lottie_url1, height=280, key="animation1")

    # Simple to Use
    left_column_r2, _, right_column_r2 = st.columns([6, 1, 5])
    with left_column_r2:
        if st.session_state.lottie:
            st_lottie(st.session_state.lottie_url2, height=200, key="animation2")
    with right_column_r2:
        st.header("Simple to Use")
        st.write(introduction_message()[1])

    st.divider()
    st.subheader("🧩 Understanding the Models")
    st.caption("Learn what each model type means in simple terms")

    left_column_r3, right_column_r3 = st.columns([6, 4])
    with left_column_r3:
        st.header("What is a Regression Model?")
        st.write("""
            This model helps to **predict continuous numerical values**, such as prices or sales.
            It shows relationships between different factors.
            📘 **Example:** Predicting house prices based on size and location.
        """)
    with right_column_r3:
        st.header("What is Data Visualization?")
        st.write("""
            Data visualization helps you **see your data clearly using charts and graphs.**
            It makes trends, patterns, and insights easier to understand for everyone.
            📘 **Example:** A bar chart showing monthly sales performance.
        """)

# ========================================
# FILE UPLOAD SECTION (Main Page)
# ========================================
st.divider()
st.subheader("📂 Upload Your Dataset")

uploaded_file = st.file_uploader("Upload a CSV or Excel file to begin:", type=["csv", "xlsx"])

if uploaded_file:
    df = read_file_from_streamlit(uploaded_file)
    st.session_state['df'] = df
    st.success("✅ File uploaded successfully! You can now explore the tabs below.")
    st.write("### Preview of Uploaded Data")
    st.dataframe(df.head())
else:
    st.info("Please upload a dataset to start your analysis.")


# Helper function
def get_df():
    return st.session_state.get('df', None)

# ========================================
# MAIN TABS
# ========================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🧹 Clean Data",
    "🧠 AI Data Analysis",
    "📊 Visualize",
    "📈 Regression Model",
    "PDF Export",
    "Dashboard Export"
])

# DATA CLEANING
with tab1:
    st.header("🧹 AI Data Cleaning")

    df = get_df()
    if df is None:
        st.warning("Please upload a CSV or Excel file from the sidebar.")
    else:
        st.write("### Uploaded Raw Data")
        st.dataframe(df)

        if st.button("Clean Data with AI"):
            with st.spinner("Cleaning data..."):
                cleaned_df = clean_data(df)
                if cleaned_df is None:
                    st.error("Cleaning failed — check logs or input file.")
                else:
                    st.dataframe(cleaned_df)
                    st.session_state['df'] = cleaned_df

#DATA ANALYSIS
with tab2:
    st.header("🧠 AI-powered Data Insights")

    df = get_df()  # Use your cleaned dataset
    if df is None or getattr(df, "empty", True):
        st.warning("Upload a dataset to begin.")
    else:
        if st.button("Run AI Analysis"):
            with st.spinner("Analyzing data using AI..."):
                try:
                    # Ensure API key present
                    if not _ensure_api_key_ui():
                        st.error("AI analysis cannot run without GOOGLE_API_KEY set.")
                    else:
                        # Run analysis
                        analysis_result = analyze_data_with_charts(df, GOOGLE_API_KEY)

                        if not analysis_result:
                            st.error("AI analysis returned no results.")
                        else:
                            # --- Store in session_state for later use ---
                            st.session_state['DF_uploaded'] = df
                            st.session_state['analysis_results'] = analysis_result

                            # --- Show AI Explanation ---
                            st.subheader("💡 AI Explanation")
                            st.write(analysis_result.get("ai_response", ""))

                            # --- Show Chart Recommendations with explanation ---
                            st.subheader("📊 Suggested Charts")
                            chart_rec = analysis_result.get("chart_recommendations", [])
                            for chart in chart_rec:
                                x = chart.get("x")
                                y = chart.get("y")
                                ctype = chart.get("chart_type")
                                expl = chart.get("explanation")
                                st.markdown(f"**Chart:** {ctype}, X: {x}, Y: {y}  \n*Explanation:* {expl}")

                            # --- Show Data Summary ---
                            st.subheader("🗂 Processed Data Summary")
                            st.dataframe(analysis_result.get("summary"))

                            # --- Cluster & Anomaly summaries ---
                            st.subheader("🧮 Cluster Summary")
                            st.json(analysis_result.get("cluster_summary", {}))
                            st.subheader("⚠️ Anomaly Summary")
                            st.json(analysis_result.get("anomaly_summary", {}))

                            st.success("✅ AI Analysis Completed and Saved!")

                except Exception as e:
                    st.error(f"AI analysis failed: {e}")

# VISUALIZATION
with tab3:
    st.header("📊 Data Visualization (AI Recommendations)")

    df = get_df()
    if df is None or getattr(df, "empty", True):
        st.warning("Please upload a CSV or Excel file to visualize.")
    else:
        st.info("Charts are generated based on AI recommendations (x, y, chart type). Save all charts at the bottom.")

        # Render charts (silent save; visualization module saves charts but does not display)
        chart_figs = render_and_save_charts(df, json_file="chart_recommendations.json", output_folder="charts_output")

        if chart_figs:
            st.success(f"{len(chart_figs)} chart(s) rendered and saved successfully.")

            # Button to save charts for PDF/dashboard (they are already saved; this just confirms)
            if st.button("Save All Charts for PDF/Dashboard"):
                saved_charts = render_and_save_charts(df, json_file="chart_recommendations.json", output_folder="charts_output",display=False)

                norm = _normalize_saved_charts(saved_charts)

                st.success(f"Charts saved: {len(norm)} files.")
                for path in norm:
                    st.write(path)
        else:
            st.info("No charts to display.")

# REGRESSION MODEL
with tab4:
    st.header("📈 Build Regression Model")

    df = get_df()
    if df is None or getattr(df, "empty", True):
        st.warning("Upload a dataset to train the model.")
    else:
        cols = list(df.columns)
        target_col = st.selectbox("Select Target Column (y):", cols)

        if st.button("Train Regression Model"):
            with st.spinner("Training model..."):
                try:
                    metrics = regression_model_pipeline(
                        df,
                        target_col,
                        GOOGLE_API_KEY
                    )
                    st.success("🎯 Model Training Completed!")
                    st.json(metrics if metrics is not None else {})
                except Exception as e:
                    st.error(f"Model training failed: {e}")


#PDF EXPORT
with tab5:
    st.header("📄 Generate PDF Report")

    if 'DF_uploaded' not in st.session_state or 'analysis_results' not in st.session_state:
        st.warning("Please upload dataset, clean it, and run AI analysis first.")
    else:
        df_raw = st.session_state['DF_uploaded']
        analysis_result = st.session_state['analysis_results']

        st.subheader("✅ Ready to Export")
        st.write("Your PDF will include:")
        st.write("- Dataset summary (statistical, cluster, anomaly, correlations)")
        st.write("- AI insights and recommendations")
        st.write("- Charts with X/Y axis info and explanations")

        if st.button("Generate PDF Report"):
            with st.spinner("Creating PDF..."):

                # Generate PDF using premium exporter (this function will save charts itself)
                try:
                    pdf_path = create_premium_pdf(
                        df_raw,
                        analysis_result,
                        GOOGLE_API_KEY,
                        json_file="chart_recommendations.json",
                        output_path="AI_Data_Insights_Report.pdf"
                    )

                    # Provide download button
                    with open(pdf_path, 'rb') as f:
                        st.download_button(
                            label="📥 Download PDF Report",
                            data=f,
                            file_name=os.path.basename(pdf_path),
                            mime="application/pdf"
                        )

                    st.success("🎉 PDF Report Generated Successfully!")
                except Exception as e:
                    st.error(f"PDF generation failed: {e}")

# ========================================
# DASHBOARD EXPORT (Tab 6)
# ========================================
with tab6:
    st.header("📊 Generate Dashboard Image")

    if 'DF_uploaded' not in st.session_state or 'analysis_results' not in st.session_state:
        st.warning("Please upload dataset, clean it, and run AI analysis first.")
    else:
        df = st.session_state['DF_uploaded']
        analysis_result = st.session_state['analysis_results']

        # ============================
        # 🔹 FIX 1: KPI CARDS (TOP)
        # ============================
        st.subheader("Dataset Overview")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Rows", df.shape[0])
        col2.metric("Columns", df.shape[1])
        col3.metric("Missing Values", int(df.isnull().sum().sum()))
        col4.metric("Numeric Features", len(df.select_dtypes(include="number").columns))

        # ============================
        # 🔹 FIX 4: STORY GUIDANCE
        # ============================
        st.info(
            "Start with distribution charts to understand data spread. "
            "Then explore relationship and proportion charts to uncover insights."
        )

        st.subheader("✅ Ready to Export")
        st.write("Your dashboard will include:")
        st.write("- Up to 4 insight-driven charts")
        st.write("- KPI overview for quick context")
        st.write("- Clean 2x2 professional layout")

        if st.button("Render Dashboard Image"):
            with st.spinner("Generating dashboard image..."):

                # 1️⃣ Generate saved charts ONCE
                saved_charts = render_and_save_charts(
                    df,
                    json_file="chart_recommendations.json",
                    output_folder="charts_output"
                ) or []

                # 2️⃣ Normalize chart objects
                charts = []
                for c in saved_charts:
                    path = c.get("saved_path") or c.get("path") or c.get("filename")
                    if path and os.path.exists(path):
                        charts.append({
                            "path": path,
                            "chart_type": c.get("chart_type", "unknown"),
                            "explanation": c.get("explanation", "")
                        })

                if not charts:
                    st.error("No charts found to build the dashboard. Run analysis again.")
                else:
                    # ============================
                    # 🔹 FIX 3: CHART FILTER
                    # ============================
                    chart_types = list(set(c["chart_type"] for c in charts))
                    selected_types = st.multiselect(
                        "Filter chart types",
                        chart_types,
                        default=chart_types
                    )

                    # ============================
                    # 🔹 FIX 2: INSIGHT → CHART FLOW
                    # ============================
                    for chart in charts:
                        if chart["chart_type"] in selected_types:
                            st.markdown(f"**Insight:** {chart['explanation']}")
                            st.image(chart["path"], use_column_width=True)

                    # ============================
                    # DASHBOARD IMAGE EXPORT
                    # ============================
                    img_path = render_dashboard_image(charts)

                    with open(img_path, "rb") as f:
                        st.download_button(
                            "📥 Download Dashboard Image",
                            f,
                            file_name="Auto_Dashboard.png",
                            mime="image/png"
                        )

                    st.success("🎉 Dashboard Image Generated Successfully!")






