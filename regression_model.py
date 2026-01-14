import streamlit as st
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from google.generativeai import TextGeneration

def regression_model_pipeline(df, target_col=None, api_key=None):
    """Perform regression analysis with explanations and plots."""
    st.subheader("📈 Regression Model Results")

    if target_col is None:
        target_col = st.selectbox("Select Target Column (Y):", df.columns)

    st.info(f"This regression model predicts **{target_col}**, a continuous numeric variable, "
            "based on other factors (features) in your dataset.")

    X = df.drop(columns=[target_col])
    y = df[target_col]

    # Encode categorical features
    X = pd.get_dummies(X, drop_first=True)

    # Ensure target is numeric
    if y.dtype not in ['float64', 'int64']:
        try:
            y = pd.to_numeric(y)
        except:
            y = pd.factorize(y)[0]

    if X.shape[1] == 0:
        st.error("❌ No valid features available after encoding. Please check your data.")
        return

    # Train model
    try:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LinearRegression()
        model.fit(X_train, y_train)
        preds = model.predict(X_test)

        r2 = r2_score(y_test, preds)
        mse = mean_squared_error(y_test, preds)
        rmse = np.sqrt(mse)

        # Show metrics
        st.write(f"✅ **R² Score:** {r2:.2f}")
        st.write(f"✅ **MSE:** {mse:.2f}")
        st.write(f"✅ **RMSE:** {rmse:.2f}")

        # Plot Actual vs Predicted
        fig1, ax1 = plt.subplots()
        ax1.scatter(y_test, preds, alpha=0.6)
        ax1.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
        ax1.set_xlabel("Actual")
        ax1.set_ylabel("Predicted")
        ax1.set_title(f"Actual vs Predicted: {target_col}")
        st.pyplot(fig1)

        # Plot Residuals
        residuals = y_test - preds
        fig2, ax2 = plt.subplots()
        sns.histplot(residuals, kde=True, ax=ax2)
        ax2.set_title("Residuals Distribution")
        ax2.set_xlabel("Residuals")
        st.pyplot(fig2)

        # --- Optional AI Explanation ---
        if api_key:
            try:
                gen = TextGeneration(model="models/gemini-2.5-flash")
                prompt = f"""
You are a professional data analyst.
The regression model predicts {target_col}.
Metrics:
- R²: {r2:.2f}
- MSE: {mse:.2f}
- RMSE: {rmse:.2f}

Explain these metrics and the model's predictive performance in simple, non-technical language for a beginner. Keep it under 150 words.
"""
                response = gen.generate(prompt=prompt, api_key=api_key)
                ai_text = response.text
                st.markdown("### 🧠 AI Explanation")
                st.info(ai_text)
            except Exception as e:
                st.warning(f"⚠️ Could not generate AI explanation: {e}")

        return {
            "r2": r2,
            "mse": mse,
            "rmse": rmse,
            "actual_vs_predicted_fig": fig1,
            "residuals_fig": fig2
        }

    except Exception as e:
        st.error(f"❌ Regression error: {e}")
        return
