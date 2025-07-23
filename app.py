import streamlit as st
from src.parser import parse_ingredients
from src.analyzer import load_ingredient_database, analyze_ingredients
import pandas as pd
import matplotlib.pyplot as plt
from rapidfuzz import process

# ------------------ Streamlit Config ------------------ #
st.set_page_config(page_title="Skincare Ingredient Analyzer", layout="centered")

# ------------------ Load Database ------------------ #
db = load_ingredient_database()
known_ingredients = list(db['Ingredient'].dropna().unique())

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
st.markdown("Start typing or select ingredients below. We'll handle typos and suggest corrections too.")

# ------------------ Ingredient Input ------------------ #
selected = st.multiselect("Select Ingredients:", known_ingredients, placeholder="Start typing Aqua, Glycerin, etc...")

manual_input = st.text_area("Or paste ingredients (comma-separated):", height=100, placeholder="e.g. Aqua (Water), Glycrin, Salicylic Acid")

# Combine selected and manual
all_input = selected.copy()
if manual_input:
    all_input += [x.strip() for x in manual_input.split(",") if x.strip()]

# ------------------ Analyze ------------------ #
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
        st.info("We found some possible typos and made suggestions:")
        for wrong, suggested, score in suggestions:
            st.markdown(f"🔸 **{wrong}** → **{suggested}** ({score:.0f}%)")
    
    # Run analysis
    results = analyze_ingredients(corrected, db)
    df = pd.DataFrame(results)

    # Clean columns
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df.rename(columns={
        "ingredient": "Ingredient",
        "function": "Function",
        "risk_level": "Risk_Level",
        "description": "Description"
    }, inplace=True)
    df["Risk_Level"] = df["Risk_Level"].str.capitalize()

    # Highlight risk
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

    # Warning for high risk
    high_risk = df[df["Risk_Level"].str.lower() == "high"]
    if not high_risk.empty:
        st.warning("⚠️ High-risk ingredients detected!")

    # Pie chart
    st.subheader("📊 Ingredient Function Breakdown")
    func_counts = df["Function"].value_counts()
    fig, ax = plt.subplots()
    pinks = ['#ffc0cb', '#ffb6c1', '#ff99aa', '#ff7f9f', '#ff4d6d']
    ax.pie(func_counts, labels=func_counts.index, autopct='%1.1f%%', colors=pinks, startangle=90)
    ax.set_title("Ingredient Functions")
    st.pyplot(fig)

    # Download
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", csv, "ingredient_report.csv", "text/csv")
