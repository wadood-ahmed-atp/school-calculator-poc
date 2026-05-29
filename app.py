import streamlit as st
import pandas as pd
import os

# ==============================================================================
# 0. WEB PAGE CONFIG & STYLING
# ==============================================================================
st.set_page_config(page_title="School Placement & Calculator POC", layout="wide")

st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    h1, h2, h3 {color: #1E3A8A;}
    .stButton>button {background-color: #1E3A8A; color: white; border-radius: 5px;}
    .stButton>button:hover {background-color: #3B82F6; color: white;}
    div[data-testid="stMetricValue"] {font-size: 24px; color: #10B981;}
    </style>
""", unsafe_allow_html=True)

st.title("🎓 School Placement & Financial Calculator")
st.markdown("### **Production Blueprint (Dual-CSV Matrix Engine)**")
st.caption("This engine co-evaluates institutional parameters alongside dynamic transcript deficiency matching tables.")
st.divider()

# ==============================================================================
# 1. DUAL-DATABASE DATA LOADER
# ==============================================================================
SCHOOLS_CSV = "schools.csv"
TRANSCRIPT_CSV = "transcript_rules.csv"

# Load Master School Dataset
if os.path.exists(SCHOOLS_CSV):
    master_schools_df = pd.read_csv(SCHOOLS_CSV)
else:
    st.error(f"⚠️ Master database file '{SCHOOLS_CSV}' not found.")
    st.stop()

# Load Transcript Review Dataset Matrix
if os.path.exists(TRANSCRIPT_CSV):
    transcript_rules_df = pd.read_csv(TRANSCRIPT_CSV)
else:
    st.warning(f"⚠️ '{TRANSCRIPT_CSV}' not detected. Dynamic transcript eligibility filtering is temporarily disabled.")
    transcript_rules_df = None

# ==============================================================================
# 2. SIDEBAR: LEAD INPUTS & MULTI-COURSE TRANSCRIPT MATRIX
# ==============================================================================
st.sidebar.header("📋 Lead Inputs")

if st.sidebar.button("🔄 Reset Form & Inputs"):
    st.rerun()

student_name = st.sidebar.text_input("Student Name", value="Jane Doe")

student_state = st.sidebar.selectbox("Student State", [
    "KY", "NY", "Y", "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", 
    "HI", "ID", "IL", "IN", "IA", "KS", "LA", "ME", "MD", 
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
])

gpa_input = st.sidebar.text_input("GPA (Leave Blank if unsure)", value="4.00")
dismissal_selection = st.sidebar.selectbox("Prior Nursing Dismissal?", ["No", "Yes"])
dismissal_y = True if dismissal_selection == "Yes" else False

license_type = st.sidebar.selectbox("LPN or CNA/CMA License?", ["LPN", "CNA/CMA", "None"])
is_cna = "CNA/CMA" if license_type == "CNA/CMA" else "No"

lpn_exp = 0
if license_type == "LPN":
    lpn_exp = st.sidebar.number_input("Months of LPN Work Experience", min_value=0, max_value=24, value=6)

travel_ok = st.sidebar.selectbox("Travel for Clinicals ok?", ["Yes", "No"])
program_interest = st.sidebar.selectbox("Program Track: ASN or BSN", ["ASN", "BSN"])

st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ Class Triggers")
entrance_exam = st.sidebar.checkbox("Include Entrance Exam Prep? (AB2 Trigger)", value=False)
has_addons = st.sidebar.checkbox("Add-ons Selected? (Z2:AB2 Trigger)", value=False)

st.sidebar.markdown("---")
st.sidebar.subheader("📚 Transcript Review Engine")

course_list = [
    "Eng Comp 1", "College Algebra", "Statistics", "Humanities 1", 
    "Humanities 2", "Humanities 3", "Human Growth & Development", 
    "Psychology", "Sociology", "Speech", "General Biology", 
    "Chemistry", "Government", "History", "Foreign Language", 
    "Macro/Micro Economics", "Elective 1", "Elective 2"
]

transcript_status = {}
for course in course_list:
    transcript_status[course] = st.sidebar.selectbox(f"{course}", ["Taken", "Need"], key=f"course_{course}")

# Generate list of ONLY the courses the student explicitly needs
needed_courses = [course for course, status in transcript_status.items() if status == "Need"]

# ==============================================================================
# 3. INTERACTIVE CALCULATOR ENGINE (Emulates Formulas T2, V2, AA2, AB2)
# ==============================================================================
st.header("⚡ Financial Calculation Engine")

col_calc_input, col_calc_output = st.columns([1, 1])

with col_calc_input:
    st.subheader("Financial Adjustments")
    deposit_input = st.number_input("Deposit Paid ($) [W2 Input]", min_value=0.0, value=0.0, step=50.0)
    grant_input = st.number_input("Discount Grant Amount ($) [Z2 Input]", min_value=0.0, value=0.0, step=50.0)
    
    st.markdown("**Discounts Selected:**")
    discount_match = st.checkbox("Deposit Match")
    discount_referral = st.checkbox("Referral")
    discount_military = st.checkbox("Military")
    discount_free_course = st.checkbox("Free Course")

with col_calc_output:
    st.subheader("Live Ledger Math")
    
    base_classes = len(needed_courses) if len(needed_courses) > 0 else 1
    if entrance_exam:
        base_classes += 1
        
    addons_count = 2 if has_addons else 0
    total_classes = base_classes + addons_count
    
    main_price = 1179 if base_classes >= 10 else (1229 if base_classes >= 4 else 1289)
    addon_price = 749 if total_classes >= 10 else (799 if total_classes >= 4 else 859)
    base_total = (base_classes * main_price) + (addons_count * addon_price)
    
    dep_min = 150 if is_cna == "CNA/CMA" else 300
    calc_dep_match = min(deposit_input, 1000.0) if (discount_match and deposit_input >= dep_min) else 0.0
    calc_referral = 50.0 if discount_referral else 0.0
    calc_military = 200.0 if discount_military else 0.0
    calc_free_course = float(main_price) if discount_free_course else 0.0
    
    final_total = max(0.0, base_total - calc_dep_match - calc_referral - calc_military - calc_free_course - grant_input)
    
    if is_cna == "CNA/CMA":
        if total_classes <= 2:
            reg_fee = 150
        elif total_classes <= 7:
            reg_fee = 175
        elif total_classes <= 10:
            reg_fee = 200
        elif total_classes <= 15:
            reg_fee = 250
        else:
            reg_fee = 300
    else:
        if total_classes <= 2:
            reg_fee = 300
        elif total_classes <= 7:
            reg_fee = 325
        elif total_classes <= 10:
            reg_fee = 375
        elif total_classes <= 15:
            reg_fee = 475
        else:
            reg_fee = 600
        
    room_left = 14500 - final_total
    max_additional_addons = max(0, int(room_left // 749))
    projected_addons = addons_count + max_additional_addons

    m1, m2 = st.columns(2)
    m1.metric("Base Total (Before Credits)", f"${base_total:,.2f}")
    m2.metric("Registration Fee (V2 Formula)", f"${reg_fee}")
    
    m3, m4 = st.columns(2)
    m3.metric("Final Balance Due (AA2 Formula)", f"${final_total:,.2f}")
    m4.metric("Pending Balance (AB2 Formula)", f"${max(0.0, final_total - deposit_input):,.2f}")
    
    st.metric("Max Add-ons Room Left", f"{projected_addons} max courses")

st.divider()

# ==============================================================================
# 4. MULTI-SCHOOL RANKED OUTPUT GRID (Evaluates General rules + Transcript rules)
# ==============================================================================
st.header("🏫 Ranked Schools Result Output Matrix")
st.caption("Replicates the nested spreadsheet logic matching demographics against your transcript validation rules matrices.")

# General Filters
selected_track = str(program_interest).strip().upper()
track_mask = master_schools_df["ASN/BSN"].str.upper() == selected_track
filtered_df = master_schools_df[track_mask].copy()

selected_state = str(student_state).strip().upper()
state_mask = filtered_df["States Accepted"].str.upper().str.contains(selected_state)
filtered_df = filtered_df[state_mask]

if selected_track == "ASN" and license_type == "LPN" and lpn_exp < 12:
    filtered_df = filtered_df[filtered_df["School Name"] != "Allegany College of Maryland"]

# --- TRANSCRIPT RULE ENGINE LINKAGE (Formula A2 / Transcript Review Sync) ---
if transcript_rules_df is not None and not filtered_df.empty:
    valid_school_names = []
    
    for _, school_row in filtered_df.iterrows():
        name = school_row["School Name"]
        
        # Pull matching row from transcript rules matrix
        rule_row = transcript_rules_df[transcript_rules_df["School Name"].str.upper() == name.upper()]
        
        if not rule_row.empty:
            is_eligible = True
            # Check every course the user marked as 'Need'
            for required_course in needed_courses:
                if required_course in rule_row.columns:
                    accepted_status = str(rule_row[required_course].values[0]).strip().upper()
                    if accepted_status != "Y":
                        is_eligible = False
                        break
            if is_eligible:
                valid_school_names.append(name)
        else:
            # If a school has no strict transcript limitations uploaded, pass it by default
            valid_school_names.append(name)
            
    # Apply the transcript mask filter
    filtered_df = filtered_df[filtered_df["School Name"].isin(valid_school_names)]

# Append UI properties
filtered_df["Transcript Deficiencies Fixed"] = ", ".join(needed_courses) if needed_courses else "None (All Cleared)"
filtered_df["Injected Modules"] = "Entrance Exam Prep" if entrance_exam else "Standard Entry"

available_cols = filtered_df.columns.tolist()
preferred_cols = ["School Name", "ASN/BSN", "School State", "County", "States Accepted", "Min GPA", "Transcript Deficiencies Fixed", "Injected Modules"]
columns_to_show = [col for col in preferred_cols if col in available_cols]

if dismissal_y and "Reentry Requirements" in available_cols:
    columns_to_show.append("Reentry Requirements")

if not filtered_df.empty:
    st.dataframe(filtered_df[columns_to_show], use_container_width=True, hide_index=True)
else:
    st.warning("No schools match the filtration parameters or accept the specified required transcript combinations.")

st.divider()

# ==============================================================================
# 5. DEVELOPER HANDOFF INSTRUCTIONS
# ==============================================================================
with st.expander("🛠️ Developer Architecture Blueprint & Code Mapping Notes"):
    st.markdown(f"""
    ### Production Technical Specification (Relational Mapping)
    Dear Developer, this app structure coregulates multi-conditional dependencies natively:
    
    1. **Primary Database (`schools.csv`):** Controls institutional eligibility properties[cite: 2, 8, 9].
    2. **Transcript Matrix (`transcript_rules.csv`):** Maps to legacy `Transcript Review` data[cite: 1, 14]. The code runs an lookup array mapping column matches where state input == 'Need'[cite: 1, 14, 15].
    """)
