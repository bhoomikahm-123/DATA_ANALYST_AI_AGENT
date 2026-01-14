import os
import datetime
from fpdf import FPDF
import google.generativeai as genai
from visualization import render_and_save_charts

# ---------------- Configuration ---------------- #

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

genai.configure(api_key=GOOGLE_API_KEY)


# ---------------- PDF Class ---------------- #

class PremiumPDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        try:
            self.set_font(self._pdf_font_family, "", 9)
        except Exception:
            self.set_font("Helvetica", "", 9)

        self.cell(0, 10, f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", align="L")
        self.cell(0, 10, f"Page {self.page_no()}", align="R")


# ---------------- Utility Helpers ---------------- #

def _sanitize_text(text):
    if text is None:
        return ""
    s = str(text)
    replacements = {
        "\u2014": " - ",
        "\u2013": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2026": "..."
    }
    for k, v in replacements.items():
        s = s.replace(k, v)
    return "".join(ch for ch in s if ord(ch) >= 32 or ch == "\n")


def _register_unicode_font(pdf):
    font_path = os.path.join("fonts", "DejaVuSans.ttf")
    if os.path.exists(font_path):
        pdf.add_font("DejaVu", "", font_path, uni=True)
        pdf.add_font("DejaVu", "B", font_path, uni=True)
        pdf._pdf_font_family = "DejaVu"
    else:
        pdf._pdf_font_family = "Helvetica"


def _card(pdf, title, value):
    w = (pdf.w - pdf.l_margin - pdf.r_margin) * 0.22
    pdf.set_fill_color(245, 245, 247)

    pdf.set_font(pdf._pdf_font_family, "B", 11)
    pdf.cell(w, 10, _sanitize_text(title), ln=2, fill=True)

    pdf.set_font(pdf._pdf_font_family, "", 10)
    pdf.cell(w, 10, _sanitize_text(value), border=1)
    pdf.ln(14)


def _fallback_chart_title(chart):
    ctype = chart.get("chart_type", "").capitalize()
    x = chart.get("x", "")
    y = chart.get("y", "")

    if y:
        return f"{ctype} Analysis of {y} vs {x}"
    return f"{ctype} Analysis of {x}"


# ---------------- AI Chart Title Generator ---------------- #

def generate_ai_chart_title(chart: dict) -> str:
    """
    Generates a concise, professional chart title using AI.
    Falls back safely if AI fails.
    """
    try:
        model = genai.GenerativeModel("gemini-pro")

        prompt = f"""
        Generate a concise, professional chart title (max 12 words).
        Do NOT include words like chart, graph, or visualization.

        Chart type: {chart.get("chart_type")}
        X column: {chart.get("x")}
        Y column: {chart.get("y")}
        Insight: {chart.get("explanation")}
        """

        response = model.generate_content(prompt)
        title = response.text.strip().replace("\n", " ")
        return _sanitize_text(title)

    except Exception:
        return _fallback_chart_title(chart)


# ---------------- Main PDF Generator ---------------- #

def create_premium_pdf(df_raw, analysis_result, json_file="chart_recommendations.json", output_path=None):
    pdf = PremiumPDF()
    pdf.set_auto_page_break(True, 15)
    _register_unicode_font(pdf)

    # ---------- Cover Page ---------- #
    pdf.add_page()
    pdf.set_fill_color(20, 40, 75)
    pdf.rect(0, 0, pdf.w, 80, "F")

    pdf.set_xy(15, 22)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font(pdf._pdf_font_family, "B", 26)
    pdf.cell(0, 12, "InsightPilot – AI Data Insights", ln=True)

    pdf.set_font(pdf._pdf_font_family, "", 12)
    pdf.cell(0, 8, "Executive-ready analytics report", ln=True)

    pdf.ln(10)
    pdf.set_font(pdf._pdf_font_family, "", 10)
    pdf.multi_cell(0, 6, f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    pdf.set_text_color(0, 0, 0)

    # ---------- Executive Summary ---------- #
    pdf.add_page()
    pdf.set_font(pdf._pdf_font_family, "B", 16)
    pdf.cell(0, 10, "Executive Summary", ln=True)

    pdf.set_font(pdf._pdf_font_family, "", 11)
    summary = analysis_result.get("ai_response", "Automated exploratory data analysis was performed.")
    pdf.multi_cell(0, 7, _sanitize_text(summary))

    pdf.ln(6)
    _card(pdf, "Rows", str(df_raw.shape[0]))
    _card(pdf, "Columns", str(df_raw.shape[1]))
    _card(pdf, "Missing Values", str(int(df_raw.isnull().sum().sum())))

    # ---------- Statistical Overview ---------- #
    pdf.add_page()
    pdf.set_font(pdf._pdf_font_family, "B", 14)
    pdf.cell(0, 8, "Statistical Overview", ln=True)

    pdf.set_font(pdf._pdf_font_family, "", 10)
    try:
        desc = df_raw.describe(include="all").fillna("")
        for col in desc.columns[:6]:
            pdf.multi_cell(0, 6, f"{col}: {desc[col].to_dict()}")
            pdf.ln(2)
    except Exception:
        pdf.multi_cell(0, 6, "Statistical summary could not be generated.")

    # ---------- Visual Insights ---------- #
    charts = render_and_save_charts(
        df_raw,
        json_file=json_file,
        output_folder="charts_output",
        display=False
    ) or []

    if charts:
        for chart in charts:
            path = chart.get("saved_path") or chart.get("path")
            if not path or not os.path.exists(path):
                continue

            pdf.add_page()
            title = generate_ai_chart_title(chart)

            pdf.set_font(pdf._pdf_font_family, "B", 14)
            pdf.cell(0, 8, _sanitize_text(title), ln=True)

            pdf.set_font(pdf._pdf_font_family, "", 10)
            pdf.multi_cell(0, 6, _sanitize_text(chart.get("explanation", "")))
            pdf.ln(4)

            pdf.image(path, x=15, w=pdf.w - 30)
    else:
        pdf.add_page()
        pdf.multi_cell(0, 6, "No visual insights could be generated.")

    # ---------- Key Observations ---------- #
    pdf.add_page()
    pdf.set_font(pdf._pdf_font_family, "B", 14)
    pdf.cell(0, 8, "Key Observations", ln=True)

    pdf.set_font(pdf._pdf_font_family, "", 11)
    pdf.multi_cell(
        0,
        7,
        "• Distribution and relationship patterns highlight key analytical signals.\n"
        "• Outliers and category imbalance were visually detected.\n"
        "• Identified trends can guide downstream modeling decisions."
    )

    # ---------- Output ---------- #
    outpath = output_path or os.path.join(
        OUTPUT_DIR,
        f"AI_Data_Insights_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )
    pdf.output(outpath)
    return outpath

