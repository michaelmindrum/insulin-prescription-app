import streamlit as st
import math
import pandas as pd

# Load insulin data from Excel file
import os
file_path = os.path.join(os.getcwd(), "Insulin_Rx.xlsx")
df = pd.read_excel(file_path, sheet_name="Sheet1")

# Define insulin types
STANDARD_LONG_ACTING_INSULINS = {"Tresiba", "Toujeo", "Lantus", "Basaglar", "Levemir"}  # Traditional long-acting insulins
ULTRA_LONG_ACTING_INSULINS = {"Awiqli"}  # Awiqli is in a unique category
RAPID_ACTING_INSULINS = {"Trurapi", "NovoRapid", "Humalog", "Apidra", "Fiasp"}

# Process insulin data into dictionary format
INSULIN_OPTIONS = {}
STANDARD_LONG_ACTING_OPTIONS = {}
ULTRA_LONG_ACTING_OPTIONS = {}
RAPID_ACTING_OPTIONS = {}

for _, row in df.iterrows():
    insulin_type = row["Insulin Type"]
    
    # Ensure concentration is not NaN before conversion
    if pd.notna(row['Concentration u/ml']):
        concentration = f"U-{int(row['Concentration u/ml'])}"
    else:
        concentration = "Unknown"  # Assign a default value for missing data

    device_type = row["Form"]
    device_capacity = row["Amount/Device"]
    
    if pd.notna(insulin_type) and pd.notna(concentration) and pd.notna(device_type) and pd.notna(device_capacity):
        if insulin_type in STANDARD_LONG_ACTING_INSULINS:
            if insulin_type not in STANDARD_LONG_ACTING_OPTIONS:
                STANDARD_LONG_ACTING_OPTIONS[insulin_type] = {}
            if concentration not in STANDARD_LONG_ACTING_OPTIONS[insulin_type]:
                STANDARD_LONG_ACTING_OPTIONS[insulin_type][concentration] = {}
            STANDARD_LONG_ACTING_OPTIONS[insulin_type][concentration][device_type] = device_capacity
        elif insulin_type in ULTRA_LONG_ACTING_INSULINS:
            if insulin_type not in ULTRA_LONG_ACTING_OPTIONS:
                ULTRA_LONG_ACTING_OPTIONS[insulin_type] = {}
            if concentration not in ULTRA_LONG_ACTING_OPTIONS[insulin_type]:
                ULTRA_LONG_ACTING_OPTIONS[insulin_type][concentration] = {}
            ULTRA_LONG_ACTING_OPTIONS[insulin_type][concentration][device_type] = device_capacity
        elif insulin_type in RAPID_ACTING_INSULINS:
            if insulin_type not in RAPID_ACTING_OPTIONS:
                RAPID_ACTING_OPTIONS[insulin_type] = {}
            if concentration not in RAPID_ACTING_OPTIONS[insulin_type]:
                RAPID_ACTING_OPTIONS[insulin_type][concentration] = {}
            RAPID_ACTING_OPTIONS[insulin_type][concentration][device_type] = device_capacity

# Streamlit UI
st.title("Insulin Rx Guide")

# User Inputs
is_new_rx = st.radio("Is this a new insulin prescription?", ["Yes", "No"])

if is_new_rx == "Yes":
    weight = st.number_input("Enter patient weight (kg):", min_value=10, max_value=200, value=70)
    if weight < 50:
        tdd = round(weight * 0.2, -1)  # Weight-based dosing for <50kg, rounded to nearest 10
    else:
        tdd = 70  # Default starting dose for basal insulin
else:
    tdd = st.number_input("Total Daily Dose (units per day)", min_value=1, value=50)

col1, col2 = st.columns(2)
with col1:
    insulin_category = st.radio("Select Insulin Category", ["Standard Long-Acting", "Ultra Long-Acting", "Rapid-Acting"])
    if insulin_category == "Standard Long-Acting":
        insulin_type = st.selectbox("Select Standard Long-Acting Insulin", list(STANDARD_LONG_ACTING_OPTIONS.keys()))
    elif insulin_category == "Ultra Long-Acting":
        insulin_type = st.selectbox("Select Ultra Long-Acting Insulin", list(ULTRA_LONG_ACTING_OPTIONS.keys()))
    else:
        insulin_type = st.selectbox("Select Rapid-Acting Insulin", list(RAPID_ACTING_OPTIONS.keys()))

with col2:
    if insulin_category == "Standard Long-Acting":
        concentration = st.selectbox("Select Concentration", list(STANDARD_LONG_ACTING_OPTIONS[insulin_type].keys()))
        device_type = st.selectbox("Select Device Type", list(STANDARD_LONG_ACTING_OPTIONS[insulin_type][concentration].keys()))
    elif insulin_category == "Ultra Long-Acting":
        concentration = st.selectbox("Select Concentration", list(ULTRA_LONG_ACTING_OPTIONS[insulin_type].keys()))
        device_type = st.selectbox("Select Device Type", list(ULTRA_LONG_ACTING_OPTIONS[insulin_type][concentration].keys()))
    else:
        concentration = st.selectbox("Select Concentration", list(RAPID_ACTING_OPTIONS[insulin_type].keys()))
        device_type = st.selectbox("Select Device Type", list(RAPID_ACTING_OPTIONS[insulin_type][concentration].keys()))

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
        f"Directions: Start at {tdd * 7} units weekly. Adjust by ±20 units/week based on fasting BG.\n"
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
    '[📄 Click here for the Diabetes Canada Insulin Prescription Guide](https://www.diabetes.ca/DiabetesCanadaWebsite/media/Managing-My-Diabetes/Tools%20and%20Resources/Insulin_Prescription_03_22.pdf?ext=.pdf)'
)
