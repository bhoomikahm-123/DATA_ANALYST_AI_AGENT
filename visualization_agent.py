# visualization.py  (replace existing)
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import json
import os

def render_chart(df, chart):
    """Render a single chart based on a recommendation dict (for UI)."""
    x = chart.get("x")
    y = chart.get("y")
    ctype = chart.get("chart_type", "").lower()
    expl = chart.get("explanation", "")

    st.markdown(f"**Chart:** {ctype.capitalize()}, X: {x}, Y: {y}  \n*Explanation:* {expl}")

    fig, ax = plt.subplots(figsize=(6,4))
    try:
        if ctype == "histogram" and x in df.columns:
            ax.hist(df[x].dropna(), bins=20)
            ax.set_title(f"Histogram of {x}")
        elif ctype == "scatter" and x in df.columns and y in df.columns:
            ax.scatter(df[x], df[y], alpha=0.6)
            ax.set_title(f"Scatter Plot: {x} vs {y}")
            ax.set_xlabel(x); ax.set_ylabel(y)
        elif ctype == "box" and x in df.columns:
            sns.boxplot(x=df[x].dropna(), ax=ax)
            ax.set_title(f"Boxplot of {x}")
        elif ctype == "line" and x in df.columns and y in df.columns:
            ax.plot(df[x], df[y], marker='o')
            ax.set_title(f"Line Chart: {y} over {x}")
        elif ctype == "bar" and x in df.columns:
            counts = df[x].astype(str).value_counts()
            counts.plot(kind='bar', ax=ax)
            ax.set_title(f"Bar Chart of {x}")
        else:
            st.info(f"Skipping unsupported/invalid chart: {ctype} ({x},{y})")
            plt.close(fig)
            return None
        st.pyplot(fig)
        return fig
    except Exception as e:
        st.warning(f"Failed to render chart ({ctype}): {e}")
        plt.close(fig)
        return None

def render_and_save_charts(df, json_file="chart_recommendations.json", output_folder="charts_output",display=True):
    """
    Render charts listed in json_file (if present) to the app UI and save PNGs.
    Returns list of dicts with chart info + saved_path.
    """
    charts = []
    if os.path.exists(json_file):
        try:
            with open(json_file, "r") as f:
                charts = json.load(f)
        except Exception:
            charts = []

    if not charts:
        st.info("No chart recommendations found.")
        return []

    os.makedirs(output_folder, exist_ok=True)
    saved_charts = []

    for idx, chart in enumerate(charts, start=1):
        # Show chart in UI (use render_chart)
        fig = render_chart(df, chart) if display else _render_chart_silent(df, chart)
        # Save figure if rendered
        if fig is not None:
            filename = f"{idx}_{chart.get('chart_type')}_{chart.get('x')}_{chart.get('y')}.png".replace(" ", "_")
            path = os.path.join(output_folder, filename)
            try:
                fig.savefig(path, bbox_inches='tight')
                saved = chart.copy()
                saved["saved_path"] = path
                saved_charts.append(saved)
            except Exception as e:
                st.warning(f"Could not save chart image: {e}")
    return saved_charts
def _render_chart_silent(df, chart):
    x = chart.get("x")
    y = chart.get("y")
    ctype = chart.get("chart_type", "").lower()

    fig, ax = plt.subplots(figsize=(6, 4))

    if ctype == "histogram" and x in df.columns:
        ax.hist(df[x].dropna(), bins=30)
        ax.set_title(f"Distribution of {x}")

        # Log scale for skewed data
        if df[x].skew() > 1:
            ax.set_xscale("log")

    elif ctype == "scatter" and x in df.columns and y in df.columns:
        ax.scatter(df[x], df[y], alpha=0.5, s=30)
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        ax.set_title(f"{y} vs {x}")

        # Trendline
        sns.regplot(x=df[x], y=df[y], scatter=False, ax=ax)

        # Log scale for CRIM-like features
        if df[x].skew() > 1:
            ax.set_xscale("log")

    elif ctype == "box" and x in df.columns:
        sns.boxplot(x=df[x], ax=ax)
        ax.set_title(f"{x} distribution")

    else:
        plt.close(fig)
        return None

    return fig
