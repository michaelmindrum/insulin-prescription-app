import streamlit as st
import math
import pandas as pd

# Load insulin data from Excel file
file_path = "Insulin_Rx.xlsx"
df = pd.read_excel(file_path, sheet_name="Sheet1")

# Process insulin data into dictionary format
INSULIN_OPTIONS = {}

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
        if insulin_type not in INSULIN_OPTIONS:
            INSULIN_OPTIONS[insulin_type] = {}
        if concentration not in INSULIN_OPTIONS[insulin_type]:
            INSULIN_OPTIONS[insulin_type][concentration] = {}
        INSULIN_OPTIONS[insulin_type][concentration][device_type] = device_capacity

# Streamlit UI
st.title("Insulin Prescription Calculator")

# User Inputs
col1, col2 = st.columns(2)
with col1:
    tdd = st.number_input("Total Daily Dose (units per day)", min_value=1, value=50)
    insulin_type = st.selectbox("Select Insulin Type", list(INSULIN_OPTIONS.keys()))
with col2:
    concentration = st.selectbox("Select Concentration", list(INSULIN_OPTIONS[insulin_type].keys()))
    device_type = st.selectbox("Select Device Type", list(INSULIN_OPTIONS[insulin_type][concentration].keys()))

# Calculate total required insulin for 90 days
required_units = tdd * 90

device_capacity = INSULIN_OPTIONS[insulin_type][concentration][device_type]
n_devices = math.ceil(required_units / device_capacity)

# Determine packaging (assuming pens/cartridges come in boxes of 5, vials have no boxes)
if "Pen" in device_type or "Cartridge" in device_type:
    box_size = 5
    boxes_needed = math.ceil(n_devices / box_size)
else:
    boxes_needed = "N/A"  # Vials are individual, no boxes

# Display Results
st.subheader("Prescription Details")
st.write(f"### **Total Insulin Needed:** {required_units} units")
st.write(f"### **Number of {device_type}s Needed:** {n_devices}")
st.write(f"### **Boxes Required (if applicable):** {boxes_needed}")

# Suggested prescription wording
prescription_text = (
    f"Dispense {n_devices} {device_type.lower()}(s) of {insulin_type} {concentration}, "
    f"each containing {device_capacity} units. Use {tdd} units per day. "
    "Duration: 90 days."
)
st.text_area("Suggested Prescription Wording:", prescription_text, height=100)
