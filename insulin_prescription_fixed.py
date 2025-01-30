import streamlit as st
import math
import pandas as pd

# Load insulin data from Excel file
file_path = "Insulin_Rx.xlsx"
df = pd.read_excel(file_path, sheet_name="Sheet1")

# Define insulin types
LONG_ACTING_INSULINS = {"Tresiba", "Toujeo", "Lantus", "Basaglar", "Levemir"}
RAPID_ACTING_INSULINS = {"Trurapi", "NovoRapid", "Humalog", "Apidra", "Fiasp"}

# Process insulin data into dictionary format
INSULIN_OPTIONS = {}
LONG_ACTING_OPTIONS = {}
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
        if insulin_type in LONG_ACTING_INSULINS:
            if insulin_type not in LONG_ACTING_OPTIONS:
                LONG_ACTING_OPTIONS[insulin_type] = {}
            if concentration not in LONG_ACTING_OPTIONS[insulin_type]:
                LONG_ACTING_OPTIONS[insulin_type][concentration] = {}
            LONG_ACTING_OPTIONS[insulin_type][concentration][device_type] = device_capacity
        elif insulin_type in RAPID_ACTING_INSULINS:
            if insulin_type not in RAPID_ACTING_OPTIONS:
                RAPID_ACTING_OPTIONS[insulin_type] = {}
            if concentration not in RAPID_ACTING_OPTIONS[insulin_type]:
                RAPID_ACTING_OPTIONS[insulin_type][concentration] = {}
            RAPID_ACTING_OPTIONS[insulin_type][concentration][device_type] = device_capacity

# Streamlit UI
st.title("Insulin Prescription Calculator")

# User Inputs
is_new_rx = st.radio("Is this a new insulin prescription?", ["Yes", "No"])

if is_new_rx == "Yes":
    weight = st.number_input("Enter patient weight (kg):", min_value=10, max_value=200, value=70)
    if weight < 50:
        tdd = round(weight * 0.2)  # Weight-based dosing for <50kg
    else:
        tdd = 10  # Default starting dose for basal insulin
else:
    tdd = st.number_input("Total Daily Dose (units per day)", min_value=1, value=50)

col1, col2 = st.columns(2)
with col1:
    insulin_category = st.radio("Select Insulin Category", ["Long-Acting", "Rapid-Acting"])
    if insulin_category == "Long-Acting":
        insulin_type = st.selectbox("Select Long-Acting Insulin", list(LONG_ACTING_OPTIONS.keys()))
    else:
        insulin_type = st.selectbox("Select Rapid-Acting Insulin", list(RAPID_ACTING_OPTIONS.keys()))

with col2:
    if insulin_category == "Long-Acting":
        concentration = st.selectbox("Select Concentration", list(LONG_ACTING_OPTIONS[insulin_type].keys()))
        device_type = st.selectbox("Select Device Type", list(LONG_ACTING_OPTIONS[insulin_type][concentration].keys()))
    else:
        concentration = st.selectbox("Select Concentration", list(RAPID_ACTING_OPTIONS[insulin_type].keys()))
        device_type = st.selectbox("Select Device Type", list(RAPID_ACTING_OPTIONS[insulin_type][concentration].keys()))

# Calculate total required insulin for 90 days
required_units = tdd * 90

device_capacity = (
    LONG_ACTING_OPTIONS[insulin_type][concentration][device_type]
    if insulin_category == "Long-Acting"
    else RAPID_ACTING_OPTIONS[insulin_type][concentration][device_type]
)
n_devices = math.ceil(required_units / device_capacity)

# Determine packaging (assuming pens/cartridges come in boxes of 5, vials have no boxes)
if "Pen" in device_type or "Cartridge" in device_type:
    box_size = 5
    boxes_needed = math.ceil(n_devices / box_size)
else:
    boxes_needed = "N/A"  # Vials are individual, no boxes

# Display Results
st.subheader("Prescription Details")
st.write("**3 Month Supply**")

st.write(f"### **Total Insulin Needed:** {required_units} units")
st.write(f"### **Number of {device_type}s Needed:** {n_devices}")
st.write(f"### **Boxes Required (if applicable):** {boxes_needed}")

st.text_area("Suggested Prescription Wording:", prescription_text, height=140)
