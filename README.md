# InsightPilot – AI-Powered Data Analyst Agent

InsightPilot is an end-to-end **AI-powered data analysis platform** built with **Streamlit**. It enables users to upload datasets, perform automated exploratory data analysis, generate AI-driven insights, visualize recommended charts, and export **professional executive-ready PDF reports and dashboard images**.

This project is designed to demonstrate **practical data analytics, AI integration, and production-grade reporting**, suitable for academic projects, portfolios, and early-stage SaaS prototypes.

---

## 🚀 Features

### 🔹 Data Handling

* Upload CSV / Excel datasets
* Automatic data cleaning and inspection
* Summary statistics for numeric & categorical columns

### 🔹 AI-Powered Insights (Google Gemini)

* AI-generated dataset explanation
* Intelligent chart recommendations
* Insight-driven chart titles (AI-generated)

### 🔹 Advanced Analytics

* Clustering using **KMeans**
* Anomaly detection using **Isolation Forest**
* Correlation analysis

### 🔹 Visualization

* Automatically rendered charts
* Saved visual outputs for reuse
* Dashboard image generation (2×2 professional layout)

### 🔹 Export Options

* **Premium PDF Report** with:

  * Executive summary
  * AI insights
  * Statistical overview
  * Charts with explanations
* Dashboard image export

---

## 🧠 Tech Stack

| Category      | Tools                               |
| ------------- | ----------------------------------- |
| Frontend      | Streamlit                           |
| Data          | Pandas, NumPy                       |
| ML            | Scikit-learn                        |
| Visualization | Matplotlib, Seaborn, Plotly         |
| AI            | Google Gemini (google-generativeai) |
| Reports       | FPDF (Unicode-enabled)              |
| Utilities     | Python-dotenv, Requests             |

---

## 📁 Project Structure

```
data_analyst_ai_agent/
│
├── app.py                         # Main Streamlit app
├── data_analysis_agent.py         # AI analysis & chart recommendation logic
├── regression_model.py            # Regression & ML pipelines
├── report_export_agent.py         # Premium PDF generation
├── visualization.py               # Chart rendering & saving
│
├── fonts/
│   └── DejaVuSans.ttf             # Unicode font (MANDATORY)
│
├── charts_output/                 # Saved charts
├── outputs/                       # Generated PDF reports
├── requirements.txt
└── README.md
```

---

## 🔑 Google API Key Setup (MANDATORY)

This project **requires Google Gemini API**.

### Option 1: Local (.env file)

Create a `.env` file in the root directory:

```
GOOGLE_API_KEY=your_api_key_here
```

### Option 2: Streamlit Cloud Secrets

Add this in **Streamlit → App Settings → Secrets**:

```toml
GOOGLE_API_KEY = "your_api_key_here"
```

> ⚠️ Do NOT commit API keys to GitHub.

---

## 🔤 Unicode Font Requirement (VERY IMPORTANT)

PDF export **will fail** without a Unicode font.

### Required File

```
fonts/DejaVuSans.ttf
```

### Download From

* [https://dejavu-fonts.github.io/](https://dejavu-fonts.github.io/)

Commit this file to GitHub. Do **NOT** add `fonts/` to `.gitignore`.

---

## 🛠 Installation & Setup

### 1️⃣ Clone the Repository

```
git clone https://github.com/<your-username>/InsightPilot.git
cd InsightPilot
```

### 2️⃣ Create Virtual Environment (Recommended)

```
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

### 4️⃣ Run the Application

```
streamlit run app.py
```

---

## 📄 How to Generate a PDF Report

1. Upload a dataset
2. Clean & inspect data
3. Run **AI Analysis**
4. Navigate to **PDF Export** tab
5. Click **Generate PDF Report**
6. Download executive-ready report

---

## 📊 Dashboard Image Export

* Generates a professional dashboard image
* Includes KPI cards + insight-driven charts
* Suitable for presentations & reports

---

## 👥 Team Members

| Name         |  Contact           |
| ------------ | ------------------ |
| Bhoomika H M |  LinkedIn / GitHub |
| Chinmayi R   |  Contact           |
| Isiri P      |  Contact           |
| Kanmani D B  |  Contact           |

---

## 🔗 Important Links

* **GitHub Repository:** [https://github.com/](https://github.com/bhoomikahm-123/DATA_ANALYST_AI_AGENT)
* **Live App (Streamlit Cloud):** [https://<your-app-name>.streamlit.app](https://data-analysis-ai-agent.streamlit.app/)
* **Google Gemini API Docs:** [https://ai.google.dev/](https://ai.google.dev/)

---

## ⚠️ Known Limitations

* Requires internet access for AI features
* Large datasets may slow PDF generation
* Google API quota limits apply

---

## 📌 Future Enhancements

* Multi-model AI support
* User authentication
* Scheduled report generation
* Database integration
* SaaS billing layer

---

## 📜 License

This project is licensed for **educational and portfolio use**.
Commercial usage requires additional permissions.

---

## ⭐ Acknowledgements

* Google Gemini API
* Streamlit Community
* Open-source Python ecosystem

---

> Built with a focus on **real-world analytics, AI integration, and professional reporting standards**.
