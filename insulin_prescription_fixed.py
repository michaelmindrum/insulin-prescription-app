import streamlit as st
import math
import pandas as pd
import os

# Load insulin data from Excel file
file_path = os.path.join(os.path.dirname(__file__), "Insulin_Rx.xlsx")
try:
    df = pd.read_excel(file_path, sheet_name="Sheet1")
except FileNotFoundError:
    st.error("Insulin data file not found.")
    st.stop()

# Define insulin types
STANDARD_LONG_ACTING_INSULINS = {"Tresiba", "Toujeo", "Lantus", "Basaglar", "Levemir"}
ULTRA_LONG_ACTING_INSULINS = {"Awiqli"}
RAPID_ACTING_INSULINS = {"Trurapi", "NovoRapid", "Humalog", "Apidra", "Fiasp"}

# Process insulin data into dictionary format
INSULIN_OPTIONS = {}
STANDARD_LONG_ACTING_OPTIONS = {}
ULTRA_LONG_ACTING_OPTIONS = {}
RAPID_ACTING_OPTIONS = {}

for _, row in df.iterrows():
    insulin_type = row["Insulin Type"]
    concentration = f"U-{int(row['Concentration u/ml'])}" if pd.notna(row['Concentration u/ml']) else "Unknown"
    device_type = row["Form"]
    device_capacity = row["Amount/Device"]

    if pd.notna(insulin_type) and pd.notna(concentration) and pd.notna(device_type) and pd.notna(device_capacity):
        if insulin_type in STANDARD_LONG_ACTING_INSULINS:
            STANDARD_LONG_ACTING_OPTIONS.setdefault(insulin_type, {}).setdefault(concentration, {})[device_type] = device_capacity
        elif insulin_type in ULTRA_LONG_ACTING_INSULINS:
            ULTRA_LONG_ACTING_OPTIONS.setdefault(insulin_type, {}).setdefault(concentration, {})[device_type] = device_capacity
        elif insulin_type in RAPID_ACTING_INSULINS:
            RAPID_ACTING_OPTIONS.setdefault(insulin_type, {}).setdefault(concentration, {})[device_type] = device_capacity

# Streamlit UI
st.title("Insulin Rx Guide")

# User Inputs
col1, col2 = st.columns(2)
with col1:
    insulin_category = st.radio("Select Insulin Category", ["Standard Long-Acting", "Ultra Long-Acting", "Rapid-Acting"])
    insulin_type = st.selectbox("Select Insulin", list(STANDARD_LONG_ACTING_OPTIONS.keys() if insulin_category == "Standard Long-Acting" else ULTRA_LONG_ACTING_OPTIONS.keys() if insulin_category == "Ultra Long-Acting" else RAPID_ACTING_OPTIONS.keys()))

with col2:
    options = STANDARD_LONG_ACTING_OPTIONS if insulin_category == "Standard Long-Acting" else ULTRA_LONG_ACTING_OPTIONS if insulin_category == "Ultra Long-Acting" else RAPID_ACTING_OPTIONS
    concentration = st.selectbox("Select Concentration", list(options[insulin_type].keys()))
    device_type = st.selectbox("Select Device Type", list(options[insulin_type][concentration].keys()))

is_new_rx = st.radio("Is this a new insulin prescription?", ["Yes", "No"])

if is_new_rx == "Yes":
    weight = st.number_input("Enter patient weight (kg):", min_value=10, max_value=200, value=70)
    tdd = round(weight * 0.2, -1) if weight < 50 else 70
else:
    tdd_label = "Total Daily Dose of Rapid Acting Insulin" if insulin_category == "Rapid-Acting" else "Total Daily Dose of Long Acting Insulin"
    tdd = st.number_input(tdd_label, min_value=1, value=50)

# Generate prescription wording
prescription_text = ""
if insulin_type in RAPID_ACTING_INSULINS:
    meal_dose = round(tdd / 3, -1)
    meal_range_low = max(1, round(meal_dose * 0.5, -1))
    meal_range_high = meal_dose + meal_range_low
    prescription_text = (
        f"Rx: {insulin_type} {concentration}\n"
        f"Directions: Give {meal_range_low}-{meal_range_high} units before each meal, adjust based on carbohydrate intake and post-prandial glucose target (5-10 mmol/L).\n"
    )
elif insulin_type in STANDARD_LONG_ACTING_INSULINS:
    prescription_text = (
        f"Rx: {insulin_type} {concentration}\n"
        f"Directions: Start at {tdd} units at bedtime. Increase by 1 unit/day until fasting BG reaches 4-7 mmol/L.\n"
    )
elif insulin_type in ULTRA_LONG_ACTING_INSULINS:
    prescription_text = (
        f"Rx: {insulin_type} {concentration}\n"
        f"Directions: Start at 70 units weekly if new prescription.\n"
        f"If transitioning from basal insulin, use TDD x 7 weekly.\n"
        f"If FBG >10 mmol/L and no hypoglycemia risk, start with 1.5 x TDD x 7 for the first week, then resume TDD x 7.\n"
        f"Adjust dose by ±20 units/week based on fasting BG.\n"
    )

st.text_area("Suggested Prescription Wording:", prescription_text, height=220)

# Disclaimer in a dropdown
with st.expander("Disclaimer"):
    st.markdown(
        """
        **Disclaimer:** This tool is intended for informational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment.
        Always consult a qualified healthcare provider before making any medical decisions.
        The authors of this tool assume no responsibility for any clinical decisions made based on the generated prescription guidance.
        """
    )

st.markdown(
    '[📄 Click here for the Diabetes Canada Insulin Prescription Guide](https://www.diabetes.ca/DiabetesCanadaWebsite/media/Managing-My-Diabetes/Tools%20and%20Resources/Insulin_Prescription_03_22.pdf)'
)
