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
    st.error("⚠️ Master database file schools.csv not found.")
    st.stop()

if os.path.exists(TRANSCRIPT_CSV):
    transcript_rules_df = pd.read_csv(TRANSCRIPT_CSV)
    for col in transcript_rules_df.select_dtypes(include=['object']).columns:
        transcript_rules_df[col] = transcript_rules_df[col].astype(str).str.strip()
    transcript_rules_df.columns = transcript_rules_df.columns.str.strip()
else:
    st.error("⚠️ Transcript validation file transcript_rules.csv not found.")
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
    
    # 1. Class Counting Math
    base_classes = len(needed_courses) if len(needed_courses) > 0 else 1
    if entrance_exam:
        base_classes += 1
        
    addons_count = 2 if has_addons else 0
    total_classes = base_classes + addons_count
    
    # 2. Pricing Tier Formulas
    main_price = 1179 if base_classes >= 10 else (1229 if base_classes >= 4 else 1289)
    addon_price = 749 if total_classes >= 10 else (799 if total_classes >= 4 else 859)
    base_total = (base_classes * main_price) + (addons_count * addon_price)
    
    # 3. Discount Evaluation Formulas
    dep_min = 150 if is_cna == "CNA/CMA" else 300
    calc_dep_match = min(deposit_input, 1000.0) if (discount_match and deposit_input >= dep_min) else 0.0
    calc_referral = 50.0 if discount_referral else 0.0
    calc_military = 200.0 if discount_military else 0.0
    calc_free_course = float(main_price) if discount_free_course else 0.0
    
    # 4. Balancing Ledger Math Rules
    credits_sum = calc_dep_match + calc_referral + calc_military + calc_free_course + grant_input
    final_total = max(0.0, base_total - credits_sum)
    pending_bal = max(0.0, final_total - deposit_input)
    
    # 5. Registration Fee Multi-tier Logic
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
        
    # 6. Addons Space Logic
    room_left = 14500.0 - final_total
    max_additional_addons = max(0, int(room_left // 749))
    projected_addons = addons_count + max_additional_addons

    # 7. Safe Output String Formats (No inline operations)
    txt_base_total = f"${base_total:,.2f}"
    txt_reg_fee = f"${reg_fee:,.2f}"
    txt_final_total = f"${final_total:,.2f}"
    txt_pending_bal = f"${pending_bal:,.2f}"
    txt_projected_addons = f"{projected_addons} max courses"

    m1, m2 = st.columns(2)
    m1.metric("Base Total", txt_base_total)
    m2.metric("Registration Fee", txt_reg_fee)
    
    m3, m4 = st.columns(2)
    m3.metric("Final Balance Due", txt_final_total)
    m4.metric("Pending Balance", txt_pending_bal)
    
    st.metric("Max Add-ons Room Left", txt_projected_addons)

st.divider()

# ==============================================================================
# 4. MULTI-SCHOOL RANKED OUTPUT GRID
# ==============================================================================
st.header("🏫 Ranked Schools Result Output Matrix")

available_cols = master_schools_df.columns.tolist()

# Demographic Filters
selected_track = str(program_interest).strip().upper()
if "ASN/BSN" in available_cols:
    master_schools_df = master_schools_df[master_schools_df["ASN/BSN"].str.upper() == selected_track]

selected_state = str(student_state).strip().upper()
if "States Accepted" in available_cols:
    master_schools_df = master_schools_df[master_schools_df["States Accepted"].str.upper().str.contains(selected_state)]

if "Min Work Experience Required (mos)" in available_cols:
    master_schools_df["Min Work Experience Required (mos)"] = pd.to_numeric(master_schools_df["Min Work Experience Required (mos)"], errors='coerce').fillna(0)
    master_schools_df = master_schools_df[master_schools_df["Min Work Experience Required (mos)"] <= lpn_exp]

if "Min GPA" in available_cols:
    master_schools_df["Min GPA"] = pd.to_numeric(master_schools_df["Min GPA"], errors='coerce').fillna(0.0)
    master_schools_df = master_schools_df[master_schools_df["Min GPA"] <= gpa_val]

if "Clinical Travel?" in available_cols and travel_ok == "No":
    master_schools_df = master_schools_df[master_schools_df["Clinical Travel?"].str.upper() != "YES"]

filtered_df = master_schools_df.copy()

# Transcript Checking Logic
if not filtered_df.empty:
    status_log = []
    
    for _, school_row in filtered_df.iterrows():
        raw_name = str(school_row["School Name"]).strip()
        rule_row = transcript_rules_df[transcript_rules_df["School Name"].str.upper() == raw_name.upper()]
        
        if not rule_row.empty:
            has_all_courses = True
            for required_course in needed_courses:
                if required_course in rule_row.columns:
                    accepted_status = str(rule_row[required_course].values[0]).strip().upper()
                    if accepted_status != "Y":
                        has_all_courses = False
                        break
                else:
                    has_all_courses = False
                    break
            
            if has_all_courses:
                status_log.append("Perfect Match")
            else:
                status_log.append("Missing Needed CBE Courses")
        else:
            status_log.append("Perfect Match")
            
    filtered_df["Match Status"] = status_log
    
    if needed_courses:
        filtered_df["Transcript Deficiencies Fixed"] = ", ".join(needed_courses)
    else:
        filtered_df["Transcript Deficiencies Fixed"] = "None"

    preferred_cols = ["School Name", "ASN/BSN", "Match Status", "School State", "County", "States Accepted", "Min GPA", "Transcript Deficiencies Fixed"]
    columns_to_show = [col for col in preferred_cols if col in filtered_df.columns]

    if dismissal_y and "Reentry Requirements" in filtered_df.columns:
        columns_to_show.append("Reentry Requirements")

    final_display_df = filtered_df[columns_to_show].copy()

    def style_legibility_flags(df):
        style_matrix = pd.DataFrame('', index=df.index, columns=df.columns)
        mismatch_mask = df["Match Status"] == "Missing Needed CBE Courses"
        style_matrix.loc[mismatch_mask, "Match Status"] = 'color: #DC2626; font-weight: bold;'
        style_matrix.loc[mismatch_mask, "School Name"] = 'color: #D97706; font-weight: bold;'
        return style_matrix

    if not final_display_df.empty:
        styled_df = final_display_df.style.apply(style_legibility_flags, axis=None)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.warning("No schools match your base demographic filtration parameters.")
else:
    st.warning("No schools match your base demographic filtration parameters.")
