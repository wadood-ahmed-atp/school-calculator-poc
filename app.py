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
st.markdown("### **Production Matrix Engine**")
st.divider()

# ==============================================================================
# 1. DUAL-DATABASE DATA LOADER
# ==============================================================================
SCHOOLS_CSV = "schools.csv"
TRANSCRIPT_CSV = "transcript_rules.csv"

if os.path.exists(SCHOOLS_CSV):
    master_schools_df = pd.read_csv(SCHOOLS_CSV)
    for col in master_schools_df.select_dtypes(include=['object']).columns:
        master_schools_df[col] = master_schools_df[col].astype(str).str.strip()
else:
    st.error(f"⚠️ Master database file '{SCHOOLS_CSV}' not found.")
    st.stop()

if os.path.exists(TRANSCRIPT_CSV):
    transcript_rules_df = pd.read_csv(TRANSCRIPT_CSV)
    for col in transcript_rules_df.select_dtypes(include=['object']).columns:
        transcript_rules_df[col] = transcript_rules_df[col].astype(str).str.strip()
    transcript_rules_df.columns = transcript_rules_df.columns.str.strip()
else:
    st.error(f"⚠️ Transcript validation file '{TRANSCRIPT_CSV}' not found.")
    st.stop()

# ==============================================================================
# 2. SIDEBAR: LEAD INPUTS & MULTI-COURSE TRANSCRIPT MATRIX
# ==============================================================================
st.sidebar.header("📋 Lead Inputs")

if st.sidebar.button("🔄 Reset Form"):
    st.rerun()

student_name = st.sidebar.text_input("Student Name", value="Jane Doe")

student_state = st.sidebar.selectbox("Student State", [
    "KY", "NY", "Y", "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", 
    "HI", "ID", "IL", "IN", "IA", "KS", "LA", "ME", "MD", 
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
])

gpa_val = st.sidebar.number_input("GPA Score", min_value=0.0, max_value=4.0, value=4.0, step=0.1)
dismissal_selection = st.sidebar.selectbox("Prior Nursing Dismissal?", ["No", "Yes"])
dismissal_y = True if dismissal_selection == "Yes" else False

license_type = st.sidebar.selectbox("License?", ["LPN", "CNA/CMA", "None"])
is_cna = "CNA/CMA" if license_type == "CNA/CMA" else "No"

lpn_exp = 0
if license_type == "LPN":
    lpn_exp = st.sidebar.number_input("LPN Months Exp", min_value=0, max_value=120, value=6)

travel_ok = st.sidebar.selectbox("Clinical Travel ok?", ["Yes", "No"])
program_interest = st.sidebar.selectbox("Track?", ["ASN", "BSN"])

st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ Class Triggers")
entrance_exam = st.sidebar.checkbox("Include Entrance Exam Prep?", value=False)
has_addons = st.sidebar.checkbox("Add-ons Selected?", value=False)

st.sidebar.markdown("---")
st.sidebar.subheader("📚 Transcript Review")

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

needed_courses = [course for course, status in transcript_status.items() if status == "Need"]

# ==============================================================================
# 3. INTERACTIVE CALCULATOR ENGINE
# ==============================================================================
st.header("⚡ Financial Calculation Engine")

col_calc_input, col_calc_output = st.columns([1, 1])

with col_calc_input:
    st.subheader("Financial Adjustments")
    deposit_input = st.number_input("Deposit Paid ($)", min_value=0.0, value=0.0, step=50.0)
    grant_input = st.number_input("Discount Grant Amount ($)", min_value=0.0, value=0.0, step=50.0)
    
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
    m1.metric("Base Total", f"${base_total:,.2f}")
    m2.metric("Registration Fee", f"${reg_fee}")
    
    m3, m4 = st.columns(2)
    m3.metric("Final Balance Due", f"${final_total:,.2f}")
    m4.metric("Pending Balance", f"${max
