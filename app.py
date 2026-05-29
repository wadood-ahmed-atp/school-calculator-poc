import streamlit as st
import pandas as pd

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
st.markdown("### **Proof of Concept Blueprint**")
st.caption("This interactive prototype maps Google Sheet matrix formulas and Apps Script UI triggers directly into a clean web architecture.")
st.divider()

# ==============================================================================
# 1. CORE DATA SOURCE (Now including Wilson College!)
# ==============================================================================
schools_data = [
    # BSN Tracks
    {"School Name": "Western Governors University", "Program": "BSN", "State": "KY, Y", "Status": "ACCEPTS", "Base Classes": 4, "Reentry Requirement": "None"},
    {"School Name": "Herzing University BSN", "Program": "BSN", "State": "KY, Y", "Status": "ACCEPTS", "Base Classes": 6, "Reentry Requirement": "None"},
    {"School Name": "Capella University", "Program": "BSN", "State": "KY, Y", "Status": "ACCEPTS", "Base Classes": 5, "Reentry Requirement": "None"},
    {"School Name": "Chamberlain University", "Program": "BSN", "State": "KY, Y", "Status": "ACCEPTS", "Base Classes": 7, "Reentry Requirement": "None"},
    {"School Name": "Wilson College", "Program": "BSN", "State": "ANY, NY, KY, Y, AL, AK, AZ, AR, CA, CO, CT, DE, FL, GA, HI, ID, IL, IN, IA, KS, KY, LA, ME, MD, MA, MI, MN, MS, MO, MT, NE, NV, NH, NJ, NM, NY, NC, ND, OH, OK, OR, PA, RI, SC, SD, TN, TX, UT, VT, VA, WA, WV, WI, WY", "Status": "ACCEPTS", "Base Classes": 5, "Reentry Requirement": "None"},
    
    # ASN Tracks
    {"School Name": "Herzing University ASN", "Program": "ASN", "State": "KY, Y", "Status": "ACCEPTS", "Base Classes": 5, "Reentry Requirement": "None"},
    {"School Name": "Excelsior University", "Program": "ASN", "State": "NY, KY, Y", "Status": "ACCEPTS", "Base Classes": 6, "Reentry Requirement": "None"}
]

master_schools_df = pd.DataFrame(schools_data)

# ==============================================================================
# 2. SIDEBAR: LEAD INPUTS & MULTI-COURSE TRANSCRIPT MATRIX
# ==============================================================================
st.sidebar.header("📋 Lead Inputs")

if st.sidebar.button("🔄 Reset Form & Inputs"):
    st.rerun()

student_name = st.sidebar.text_input("Student Name", value="Jane Doe")

# 1. Student State
student_state = st.sidebar.selectbox("Student State", [
    "NY", "KY", "Y", "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", 
    "HI", "ID", "IL", "IN", "IA", "KS", "LA", "ME", "MD", 
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
])

# 2. GPA
gpa_input = st.sidebar.text_input("GPA (Leave Blank if unsure)", value="4.00")

# 3. Prior Nursing Dismissal?
dismissal_selection = st.sidebar.selectbox("Prior Nursing Dismissal?", ["No", "Yes"])
dismissal_y = True if dismissal_selection == "Yes" else False

# 4. LPN or CNA/CMA License?
license_type = st.sidebar.selectbox("LPN or CNA/CMA License?", ["LPN", "CNA/CMA", "None"])
is_cna = "CNA/CMA" if license_type == "CNA/CMA" else "No"

# 5. Months of LPN Work Experience
lpn_exp = 0
if license_type == "LPN":
    lpn_exp = st.sidebar.number_input("Months of LPN Work Experience", min_value=0, max_value=24, value=6)

# 6. Travel for Clinicals ok?
travel_ok = st.sidebar.selectbox("Travel for Clinicals ok?", ["Yes", "No"])

# 7. ASN or BSN
program_interest = st.sidebar.selectbox("Program Track: ASN or BSN (A2/G2 Logic)", ["ASN", "BSN"])

st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ Class Triggers")
entrance_exam = st.sidebar.checkbox("Include Entrance Exam Prep? (AB2 Trigger)", value=False)
has_addons = st.sidebar.checkbox("Add-ons Selected? (Z2:AB2 Trigger)", value=False)

st.sidebar.markdown("---")
st.sidebar.subheader("📚 Transcript Review Engine")
st.sidebar.caption("Toggle courses between Taken and Needed to feed Formula A2 array filters.")

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
# 3. INTERACTIVE CALCULATOR ENGINE (Emulates Formulas T2, V2, AA2, AB2)
# ==============================================================================
st.header("⚡ Financial Calculation Engine")

col_calc_input, col_calc_output = st.columns([1, 1])

with col_calc_input:
    st.subheader("Financial Adjustments")
    deposit_input = st.number_input("Deposit Paid ($) [W2 Input]", min_value=0.0, value=0.0, step=50.0)
    grant_input = st.number_input("Discount Grant Amount ($) [Z2 Input]", min_value=0.0, value=0.0, step=50.0)
    
    st.markdown("**Discounts Selected [X2 Array Logic]:**")
    discount_match = st.checkbox("Deposit Match")
    discount_referral = st.checkbox("Referral")
    discount_military = st.checkbox("Military")
    discount_free_course = st.checkbox("Free Course")

with col_calc_output:
    st.subheader("Live Ledger Math (Formulas AA2 / V2 / T2)")
    
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
    
    # Cleaned, Multi-Line V2 Formula logic block
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
    
    st.metric("Max Add-ons Room Left (T2 Formula)", f"{projected_addons} max courses")

st.divider()

# ==============================================================================
# 4. MULTI-SCHOOL RANKED OUTPUT GRID
# ==============================================================================
st.header("🏫 Ranked Schools Result Output Matrix")
st.caption("Emulates full nested sorting options from your complex A2 Array Filter formula.")

# Step A: Filter by track (ASN/BSN)
selected_track = str(program_interest).strip().upper()
track_mask = master_schools_df["Program"].str.upper() == selected_track
filtered_df = master_schools_df[track_mask].copy()

# Step B: Filter by state selection securely
selected_state = str(student_state).strip().upper()
state_mask = filtered_df["State"].str.upper().str.contains(selected_state)
filtered_df = filtered_df[state_mask]

# Append output meta row attributes
filtered_df["Transcript Deficiencies Fixed"] = ", ".join(needed_courses) if needed_courses else "None (All Cleared)"
filtered_df["Injected Modules"] = "Entrance Exam Prep" if entrance_exam else "Standard Entry"
filtered_df["Base Classes"] = filtered_df["Base Classes"].apply(lambda x: max(1, x + len(needed_courses)))

columns_to_show = ["School Name", "Program", "Status", "Base Classes", "Transcript Deficiencies Fixed", "Injected Modules"]

if dismissal_y:
    filtered_df["Reentry Review Req."] = filtered_df["Reentry Requirement"]
    columns_to_show.append("Reentry Review Req.")
    st.info("💡 Apps Script Trigger Active: 'Reentry Review' Column N unhidden.")

if has_addons:
    filtered_df["Add-ons Active"] = "Yes - Multi-Tier Pricing"
    columns_to_show.append("Add-ons Active")
    st.info("💡 Apps Script Trigger Active: 'Add-ons' Column R unhidden.")

if discount_free_course:
    filtered_df["Free Course Token Allocation"] = "FREE COURSE CONVERTED"
    columns_to_show.append("Free Course Token Allocation")
    st.info("💡 Apps Script Trigger Active: 'Free Course Code' Column Y unhidden.")

# Output execution
if not filtered_df.empty:
    st.dataframe(filtered_df[columns_to_show].sort_values(by="Base Classes", ascending=True), use_container_width=True, hide_index=True)
else:
    st.warning("No schools match the current filtration parameters for this state. Please adjust Lead Inputs.")

st.divider()

# ==============================================================================
# 5. DEVELOPER HANDOFF INSTRUCTIONS
# ==============================================================================
with st.expander("🛠️ Developer Architecture Blueprint & Code Mapping Notes"):
    st.markdown(f"""
    ### Technical Specification Notes for Core Integration
    Dear Developer, this POC translates legacy spreadsheet workbook code blocks directly into centralized, functional web blocks:
    
    1. **Form Fields Map:**
       * State: `{student_state}`
       * GPA: `{gpa_input if gpa_input else 'Blank'}`
       * Dismissal Status: `{dismissal_selection}`
       * License Category: `{license_type}` (LPN Months Exp: {lpn_exp})
       * Travel Allowed: `{travel_ok}`
       * Total Courses Flagged with 'Need' Status: `{len(needed_courses)}`
    2. **Multi-Parameter Matrix Filtering:**
       * Replicates the complex multi-tab sheet lookups by using double-layered boolean masking rules in Pandas (`track_mask` and `state_mask`).
    """)
