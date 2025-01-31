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

# Insulins that must be titrated in 2-unit increments
TWO_UNIT_TITRATION_INSULINS = {"Toujeo Doublestar", "Tresiba U-200"}

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
insulin_category = st.radio("Select Insulin Category", ["Standard Long-Acting", "Ultra Long-Acting", "Rapid-Acting"])

# Determine the appropriate question based on insulin category
if insulin_category == "Rapid-Acting":
    is_existing_insulin = st.radio("Is the patient already on a rapid insulin?", ["Yes", "No"])
else:
    is_existing_insulin = st.radio("Is the patient already taking a long acting insulin?", ["Yes", "No"])

if is_existing_insulin == "No":
    if insulin_category == "Ultra Long-Acting":
        tdd = 70  # Awiqli starts at 70 units weekly
    elif insulin_category == "Rapid-Acting":
        weight = st.number_input("Enter patient weight (kg):", min_value=10, max_value=200, value=70)
        tdd = round(weight * 0.2, -1)  # Weight-based dosing, rounded to nearest 10
    else:
        weight = st.number_input("Enter patient weight (kg):", min_value=10, max_value=200, value=70)
        tdd = round(weight * 0.2, -1)  # Standard long-acting insulin weight-based
else:
    tdd_label = "Total Daily Dose of Rapid Acting Insulin" if insulin_category == "Rapid-Acting" else "Total Daily Dose of Long Acting Insulin"
    tdd = st.number_input(tdd_label, min_value=1, value=50)

insulin_type = st.radio("Select Insulin", list(STANDARD_LONG_ACTING_OPTIONS.keys() if insulin_category == "Standard Long-Acting" else ULTRA_LONG_ACTING_OPTIONS.keys() if insulin_category == "Ultra Long-Acting" else RAPID_ACTING_OPTIONS.keys()))
options = STANDARD_LONG_ACTING_OPTIONS if insulin_category == "Standard Long-Acting" else ULTRA_LONG_ACTING_OPTIONS if insulin_category == "Ultra Long-Acting" else RAPID_ACTING_OPTIONS
concentration = st.radio("Select Concentration", list(options[insulin_type].keys()))
device_type = st.radio("Select Device Type", list(options[insulin_type][concentration].keys()))

# Additional Awiqli-specific logic for existing basal insulin users
if insulin_type == "Awiqli" and is_existing_insulin == "Yes":
    has_high_bg = st.radio("Is fasting BG consistently >10 mmol/L?", ["Yes", "No"])
    has_hypo_risk = st.radio("Is there a risk of hypoglycemia?", ["Yes", "No"])

# Adjust titration increment for specific insulins
if insulin_type == "Tresiba" and concentration == "U-200":
    titration_increment = 2
elif insulin_type == "Toujeo" and device_type == "Doublestar":
    titration_increment = 2 
elif insulin_type in TWO_UNIT_TITRATION_INSULINS:
    titration_increment = 2
else:
    titration_increment = 1
    
# Calculate total required insulin for 90 days
required_units = tdd * 90
device_capacity = options[insulin_type][concentration][device_type]
n_devices = math.ceil(required_units / device_capacity)

# Determine packaging
if "Pen" in device_type or "Cartridge" in device_type:
    box_size = 5
    boxes_needed = math.ceil(n_devices / box_size)
else:
    boxes_needed = n_devices  # Vials are individual, no boxes

# Generate prescription wording
prescription_text = ""
if insulin_type in RAPID_ACTING_INSULINS:
    meal_dose = round(tdd / 3, -1)
    meal_range_low = max(1, round(meal_dose * 0.5, -1))
    meal_range_high = meal_dose + meal_range_low
    snack_dose_low = max(1, round(meal_dose * 0.25, -1))
    snack_dose_high = max(1, round(meal_dose * 0.75, -1))
    prescription_text = (
        f"Rx: {insulin_type} {concentration}\n"
        f"Directions: Give {meal_range_low}-{meal_range_high} units before each meal, adjust based on carbohydrate intake and post-prandial glucose target (5-10 mmol/L).\n"
        f"As needed: {snack_dose_low}-{snack_dose_high} units for snacks, adjusting based on intake and response.\n"
        f"Quantity: {required_units} units total\n"
        f"Dispense: {boxes_needed} boxes of {device_type.lower()}(s)\n"
        f"Duration: 90 days (3-month supply)\n"
    )
elif insulin_type in STANDARD_LONG_ACTING_INSULINS:
    prescription_text = (
        f"Rx: {insulin_type} {concentration}\n"
        f"Directions: Start at {tdd} units at bedtime. Increase by {titration_increment} unit/day until fasting BG reaches 4-7 mmol/L.\n"
        f"Quantity: {required_units} units total\n"
        f"Dispense: {boxes_needed} boxes of {device_type.lower()}(s)\n"
        f"Duration: 90 days (3-month supply)\n"
    )
elif insulin_type in ULTRA_LONG_ACTING_INSULINS:
    if is_existing_insulin == "Yes":
        awiqli_start_dose = tdd * 7
        if has_high_bg == "Yes" and has_hypo_risk == "No":
            awiqli_start_dose *= 1.5  # Boost first dose if conditions met
    else:
        awiqli_start_dose = 70  # Awiqli starts at 70 units weekly for new users
    prescription_text = (
        f"Rx: {insulin_type} {concentration}\n"
        f"Directions: Start at {awiqli_start_dose} units for the first week, then continue with {tdd * 7} units weekly.\n"
        f"Adjust dose by ±20 units/week based on fasting BG.\n"
        f"Dispense: {boxes_needed} boxes of {device_type.lower()}(s)\n"
        f"Duration: 90 days (3-month supply)\n"
    )
elif insulin_type in ULTRA_LONG_ACTING_INSULINS:
    prescription_text = (
        f"Rx: {insulin_type} {concentration}\n"
        f"Directions: Start at {tdd} units weekly if new prescription.\n"
        f"Adjust dose by ±20 units/week based on fasting BG.\n"
        f"Dispense: One 3 mL pen per {tdd} units weekly, rounded up as needed\n"
        f"Duration: 90 days (3-month supply)\n"
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
# App logic explanation in a dropdown
with st.expander("App Logic Explanation"):
    st.markdown(
        """
        **App Logic:**
        1. **User Inputs:**
            - Insulin Category: Standard Long-Acting, Ultra Long-Acting, Rapid-Acting
            - Existing Insulin Usage: Yes/No
            - Patient Weight (if applicable)
            - Total Daily Dose (TDD) calculation based on weight or user input
        2. **Insulin Type Selection:**
            - Based on the selected category, the user selects the specific insulin type, concentration, and device type.
        3. **Titration Increment Adjustment:**
            - Specific insulins have a 2-unit titration increment.
        4. **Dose Calculations:**
            - **Rapid-Acting Insulin:**
                - Meal dose: TDD / 3, rounded to the nearest 10
                - Meal range: 50% to 150% of the meal dose
                - Snack dose: 25% to 75% of the meal dose
                - Total required units for 90 days: TDD * 90
            - **Standard Long-Acting Insulin:**
                - Starting dose: TDD (e.g., if TDD is 50 units, start with 50 units)
                - Titration increments: 1 or 2 units per day
                - Total required units for 90 days: TDD * 90 (e.g., 50 units/day * 90 days = 4500 units)
            - **Ultra Long-Acting Insulin (Awiqli):**
                - Starting dose for new users: 70 units weekly
                - Starting dose for existing users: TDD * 7 (e.g., if TDD is 50 units, start with 50 * 7 = 350 units), potentially boosted by 1.5x if conditions are met
                - Weekly unit requirements: TDD * 7
                - Total required units for 90 days: TDD * 90 (e.g., 50 units/day * 90 days = 4500 units)
        5. **Packaging and Prescription Generation:**
            - **Calculate the number of devices needed:**
                - Required units: TDD * 90 (e.g., 50 units/day * 90 days = 4500 units)
                - Device capacity: Based on selected concentration and device type
                - Number of devices: Required units / device capacity, rounded up (e.g., if device capacity is 300 units, then 4500 / 300 = 15 devices)
            - **Packaging:**
                - Pens or cartridges: 5 devices per box (e.g., 15 devices / 5 = 3 boxes)
                - Vials: Individual packaging
            - **Prescription Text Generation:**
                - Rapid-Acting Insulin: Includes meal dose range, snack dose range, total units, number of boxes, and duration
                - Standard Long-Acting Insulin: Includes starting dose, titration increments, total units, number of boxes, and duration
                - Ultra Long-Acting Insulin: Includes starting dose, weekly dose adjustments, total units, number of boxes, and duration
        """
    )
st.markdown(
    '[📄 Click here for the Diabetes Canada Insulin Prescription Guide](https://www.diabetes.ca/DiabetesCanadaWebsite/media/Managing-My-Diabetes/Tools%20and%20Resources/Insulin_Prescription_03_22.pdf)'
)
