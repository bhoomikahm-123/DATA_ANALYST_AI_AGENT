import os
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import json
import streamlit as st
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env for local testing
load_dotenv()

# -----------------------------
# Read API key safely
# -----------------------------
GOOGLE_API_KEY = st.secrets["google"]["api_key"] if "google" in st.secrets else os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("❌ GOOGLE_API_KEY not found. Add it to .env locally or Streamlit Secrets in Cloud.")

# Configure the Google GenAI client
genai.configure(api_key=GOOGLE_API_KEY)

# Optional: preferred model (override via .env)
PREFERRED_MODEL = os.getenv("GENAI_MODEL", "models/gemini-2.5-flash")

def list_models(api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        return r.json().get("models", [])
    except Exception:
        return []

def pick_supported_model(api_key, want_method="generateContent"):
    # prefer configured model, else pick first that supports generateContent
    models = list_models(api_key)
    # first try common favorites
    for preferred_prefix in ("gemini-3", "gemini-2.5", "gemini-1.5"):
        for m in models:
            if m.get("name","").startswith(preferred_prefix):
                supported = m.get("supportedMethods") or m.get("supportedMethods", [])
                # some returned metadata names vary — accept if any mention generateContent
                if not supported or want_method in supported:
                    return m["name"]
    # fallback: search list for explicit supportedMethods
    for m in models:
        supported = m.get("supportedMethods") or []
        if want_method in supported:
            return m["name"]
    # last resort: return None
    return None

def _configure_model():
    if not API_KEY:
        raise RuntimeError("Missing GOOGLE_API_KEY in environment.")
    genai.configure(api_key=API_KEY)
    # try preferred first
    try:
        model = genai.GenerativeModel(PREFERRED_MODEL)
        return PREFERRED_MODEL, model
    except Exception:
        # pick one that supports generateContent
        safe = pick_supported_model(API_KEY, "generateContent")
        if not safe:
            raise RuntimeError("No supported model found for generateContent. Check your API/project.")
        model = genai.GenerativeModel(safe)
        return safe, model

def analyze_data_with_charts(df, json_file="chart_recommendations.json"):
    if df is None or df.empty:
        return {
            "summary": None,
            "ai_response": "No data provided.",
            "chart_recommendations": [],
            "cluster_summary": {},
            "anomaly_summary": {},
            "correlations": pd.DataFrame(),
            "processed_df": df
        }

    # --- Stats ---
    summary = df.describe(include="all")
    num_df = df.select_dtypes(include="number")

    # --- Clustering ---
    cluster_summary = {}
    try:
        if not num_df.empty:
            scaled = StandardScaler().fit_transform(num_df)
            kmeans = KMeans(n_clusters=min(3, max(1, len(num_df.columns))), n_init="auto", random_state=42)
            df["Cluster"] = kmeans.fit_predict(scaled)
            cluster_summary = df["Cluster"].value_counts().to_dict()
    except Exception:
        cluster_summary = {}

    # --- Anomalies ---
    anomaly_summary = {}
    try:
        if not num_df.empty:
            iso = IsolationForest(contamination=0.05, random_state=42)
            df["Anomaly"] = iso.fit_predict(num_df)
            count = int((df["Anomaly"] == -1).sum())
            anomaly_summary = {
                "Total Anomalies": count,
                "Percentage": round((count / len(df)) * 100, 2)
            }
    except Exception:
        df["Anomaly"] = None
        anomaly_summary = {}

    # --- Correlation ---
    correlations = num_df.corr() if not num_df.empty else pd.DataFrame()

    prompt = f"""
You are a senior data analyst.

DATASET SUMMARY:
Shape: {df.shape}
Columns: {list(df.columns)}
Missing Values: {df.isnull().sum().to_dict()}

Statistical Summary:
{summary.to_string()}

Cluster Summary:
{cluster_summary}

Anomaly Summary:
{anomaly_summary}

Correlations:
{correlations.to_string()}

TASK:
Recommend meaningful charts for this dataset.
Return a JSON array with items: x, y (or null), chart_type (scatter,histogram,box,bar,line,pie), explanation (short).
Keep explanations short and precise.
"""

    ai_response = ""
    chart_recommendations = []
    try:
        model_name, model = _configure_model()
        # small safety: limit prompt length; this is still a text request
        response = model.generate_content(prompt)
        ai_response = getattr(response, "text", "") or ""
        try:
            chart_recommendations = json.loads(ai_response)
        except Exception:
            chart_recommendations = []
    except Exception as e:
        ai_response = f"⚠️ Error getting AI insights: {e}"
        chart_recommendations = []

    # fallback generate diversified chart suggestions
    if not chart_recommendations:
        numeric_cols = num_df.columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

        # 1️⃣ Scatter (numeric vs numeric)
        for i in range(min(3, len(numeric_cols))):
            for j in range(i + 1, min(4, len(numeric_cols))):
                chart_recommendations.append({
                    "x": numeric_cols[i],
                    "y": numeric_cols[j],
                    "chart_type": "scatter",
                    "explanation": f"Relationship between {numeric_cols[i]} and {numeric_cols[j]}"
                })

        # 2️⃣ Histogram (numeric distribution)
        for col in numeric_cols[:3]:
            chart_recommendations.append({
                "x": col,
                "y": None,
                "chart_type": "histogram",
                "explanation": f"Distribution of {col}"
            })

        # 3️⃣ Box plot (binary or low-cardinality numeric)
        for col in numeric_cols:
            if df[col].nunique() <= 5:
                chart_recommendations.append({
                    "x": col,
                    "y": None,
                    "chart_type": "box",
                    "explanation": f"Value spread and outliers for {col}"
                })

        # 4️⃣ Bar chart (categorical)
        for col in categorical_cols[:2]:
            chart_recommendations.append({
                "x": col,
                "y": None,
                "chart_type": "bar",
                "explanation": f"Category frequency for {col}"
            })

        # 5️⃣ Line chart (time series detection)
        for col in df.columns:
            if "date" in col or "time" in col:
                num_target = numeric_cols[0] if numeric_cols else None
                if num_target:
                    chart_recommendations.append({
                        "x": col,
                        "y": num_target,
                        "chart_type": "line",
                        "explanation": f"Trend of {num_target} over time"
                    })
        # 6️⃣ Pie chart (low-cardinality categorical or binary)
        for col in df.columns:
            unique_vals = df[col].nunique()
            if unique_vals > 1 and unique_vals <= 6:
                chart_recommendations.append({
                "x": col,
                "y": None,
                "chart_type": "pie",
                "explanation": f"Proportion of categories in {col}"
            })
            break  # avoid too many pie charts



    # Save to json
    try:
        with open(json_file, "w") as f:
            json.dump(chart_recommendations, f, indent=4)
    except Exception:
        pass

    return {
        "summary": summary,
        "ai_response": ai_response,
        "chart_recommendations": chart_recommendations,
        "cluster_summary": cluster_summary,
        "anomaly_summary": anomaly_summary,
        "correlations": correlations,
        "processed_df": df
    }


