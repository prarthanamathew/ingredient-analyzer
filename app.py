import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from rapidfuzz import process
from src.parser import parse_ingredients
from src.analyzer import load_ingredient_database, analyze_ingredients

# ------------------ Page Config ------------------ #
st.set_page_config(page_title="Skincare Ingredient Analyzer", layout="centered")

# ------------------ Load Ingredient Database ------------------ #
db = load_ingredient_database()
known_ingredients = list(db['Ingredient'].dropna().unique())

# ------------------ Custom Styling ------------------ #
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Raleway:wght@400;600&display=swap');
        html, body, [class*="css"] {
            font-family: 'Raleway', sans-serif;
        }
        .stDataFrame th {
            text-transform: uppercase;
        }
        .stDataFrame tbody tr:hover {
            background-color: #ffe6ee !important;
        }
        .stDownloadButton button {
            background-color: #ff8fab;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------ Sidebar ------------------ #
st.sidebar.markdown("### 💡 Why This Tool?")
st.sidebar.write("""
Your skin deserves better than mystery ingredients.

With countless chemicals, allergens, and harsh additives lurking in everyday skincare products, knowing what you're putting on your face isn't just smart — it's essential.

**Give this tool a try. Give your skin the treatment it deserves.**
""")
st.sidebar.markdown("---")
st.sidebar.markdown("🧴 Made by Prarthana")

# ------------------ Main Title ------------------ #
st.title("🧴 Skincare Ingredient Analyzer")
st.markdown("Start typing or paste ingredients. We'll correct typos and analyze for safety.")

# ------------------ Input Fields ------------------ #
selected = st.multiselect("Select Ingredients:", known_ingredients, placeholder="Start typing Aqua, Glycerin, etc...")
manual_input = st.text_area("Or paste ingredients (comma-separated):", height=100, placeholder="e.g. Aqua (Water), Glycrin, Salicylic Acid")

# Combine inputs
all_input = selected.copy()
if manual_input:
    all_input += [x.strip() for x in manual_input.split(",") if x.strip()]

# ------------------ Analyze Button ------------------ #
if st.button("🔍 Analyze") and all_input:
    corrected = []
    suggestions = []

    for ing in all_input:
        if ing in known_ingredients:
            corrected.append(ing)
        else:
            match, score = process.extractOne(ing, known_ingredients)
            if score > 80:
                corrected.append(match)
            else:
                suggestions.append((ing, match, score))

    if suggestions:
        st.info("🛠️ We found some possible typos and made suggestions:")
        for wrong, suggested, score in suggestions:
            st.markdown(f"🔸 **{wrong}** → **{suggested}** ({score:.0f}%)")

    # Run ingredient analysis
    results = analyze_ingredients(corrected, db)
    df = pd.DataFrame(results)

    # Clean column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df.rename(columns={
        "ingredient": "Ingredient",
        "function": "Function",
        "risk_level": "Risk_Level",
        "description": "Description"
    }, inplace=True)
    df["Risk_Level"] = df["Risk_Level"].str.capitalize()

    # Style table rows based on risk level
    def highlight_risk(row):
        color = ''
        if row["Risk_Level"].lower() == "high":
            color = 'background-color: #ffcccc'
        elif row["Risk_Level"].lower() == "medium":
            color = 'background-color: #ffe6cc'
        elif row["Risk_Level"].lower() == "low":
            color = 'background-color: #e6ffcc'
        return [color] * len(row)

    st.subheader("🔎 Full Analysis Table")
    st.dataframe(df.style.apply(highlight_risk, axis=1), use_container_width=True)

    # Warning for high-risk ingredients
    high_risk = df[df["Risk_Level"].str.lower() == "high"]
    if not high_risk.empty:
        st.warning("⚠️ High-risk ingredients detected!")

    # ------------------ Risk Heatmap ------------------ #
    st.subheader("🔥 Ingredient Risk Heatmap")

    risk_mapping = {'Low': 1, 'Medium': 2, 'High': 3}
    df['Risk_Score'] = df['Risk_Level'].map(risk_mapping)

    heat_df = pd.DataFrame({
        'Ingredient': df['Ingredient'],
        'Risk Score': df['Risk_Score']
    }).set_index('Ingredient')

    fig, ax = plt.subplots(figsize=(6, max(1, len(heat_df) * 0.3)))
    sns.heatmap(
        heat_df.T,
        cmap=['#98fb98', '#ffb347', '#ff4d6d'],
        cbar=False,
        linewidths=0.5,
        ax=ax,
        annot=True,
        fmt="d"
    )
    ax.set_xlabel("Ingredients")
    ax.set_ylabel("")
    ax.set_title("Risk Heatmap (Low → High Risk)")
    st.pyplot(fig)

    # ------------------ Download Button ------------------ #
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", csv, "ingredient_report.csv", "text/csv")
