import streamlit as st
from src.parser import parse_ingredients
from src.analyzer import load_ingredient_database, analyze_ingredients
import pandas as pd
import matplotlib.pyplot as plt

# ------------------ Streamlit Config ------------------ #
st.set_page_config(
    page_title="Skincare Ingredient Analyzer",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ------------------ Custom CSS ------------------ #
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Raleway:wght@400;600&display=swap');

        html, body, [class*="css"]  {
            font-family: 'Raleway', sans-serif !important;
        }

        .stDataFrame th, .stDataFrame td {
            text-align: left !important;
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
st.markdown("Paste a skincare product's full ingredient list below (comma-separated), and we’ll analyze it.")

# ------------------ Input ------------------ #
raw_text = st.text_area("Ingredient List:", height=150, placeholder="e.g. Aqua (Water), Glycerin, Salicylic Acid...")

# ------------------ Analyze ------------------ #
if st.button("🔍 Analyze") and raw_text:
    parsed = parse_ingredients(raw_text)
    db = load_ingredient_database()
    results = analyze_ingredients(parsed, db)
    df = pd.DataFrame(results)

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df.rename(columns={
        "ingredient": "Ingredient",
        "function": "Function",
        "risk_level": "Risk Level",
        "description": "Description"
    }, inplace=True)

    df["Risk Level"] = df["Risk Level"].str.capitalize()

    st.success(f"Analyzed {len(parsed)} ingredients.")

    # ------------------ Full Table ------------------ #
    st.subheader("🔎 Full Analysis Table")

    def highlight_row(row):
        risk = row["Risk Level"].lower()
        if risk == "high":
            return ['background-color: #FFCDD2'] * len(row)
        elif risk == "medium":
            return ['background-color: #FFF3CD'] * len(row)
        elif risk == "low":
            return ['background-color: #C8E6C9'] * len(row)
        return [''] * len(row)

    styled_html = df.style \
        .apply(highlight_row, axis=1) \
        .set_table_styles([
            {'selector': 'th', 'props': [('text-align', 'left'), ('font-weight', 'bold'), ('text-transform', 'uppercase')]}
        ]) \
        .hide(axis="index") \
        .to_html()

    st.markdown(styled_html, unsafe_allow_html=True)

    # ------------------ High Risk Alert ------------------ #
    high_risk = df[df["Risk Level"].str.lower() == "high"]
    if not high_risk.empty:
        st.warning("⚠️ High-risk ingredients detected! These may cause irritation or other issues.")

    # ------------------ Pie Chart ------------------ #
    st.subheader("📊 Ingredient Function Breakdown")
    func_counts = df['Function'].value_counts()

    fig, ax = plt.subplots(figsize=(5, 5))
    pink_palette = ['#ffc0cb', '#ffb6c1', '#ff99aa', '#ff7f9f', '#ff4d6d']
    ax.pie(func_counts, labels=func_counts.index, autopct="%1.1f%%", colors=pink_palette, startangle=90)
    ax.set_title("How each ingredient contributes")
    plt.tight_layout()
    st.pyplot(fig)

    # ------------------ Download CSV ------------------ #
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Report (CSV)", csv, "ingredient_report.csv", "text/csv")
