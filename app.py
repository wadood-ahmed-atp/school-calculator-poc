import streamlit as st
import pandas as pd
import os

# ==============================================================================
# 0. WEB PAGE CONFIG & STYLING
# ==============================================================================
st.set_page_config(page_title="Advisor Dashboard", layout="wide")

st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    h1, h2, h3 {color: #1E3A8A;}
    .stButton>button {background-color: #1E3A8A; color: white; border-radius: 5px;}
    .stButton>button:hover {background-color: #3B82F6; color: white;}
    div[data-testid="stMetricValue"] {font-size: 24px; color: #10B981;}
    </style>
""", unsafe_allow_html=True)

st.title("🎓 Advisor Dashboard")
st.markdown("### **System Framework Matrix**")
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
# 2. DEFINED ARRAYS WITH STAKEHOLDER PLACEHOLDERS
# ==============================================================================
STATE_OPTIONS = [
    "Select state", "FL", "GA", "WI", "AL", "DC", "KY", "NY", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", 
    "HI", "ID", "IL", "IN", "IA", "KS", "LA", "ME", "MD", 
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
    "NM", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]
BINARY_OPTIONS = ["Yes", "No"]
DISMISSAL_OPTIONS = ["No", "Yes"]
LICENSE_OPTIONS = ["None", "LPN", "CNA/CMA"]
TRACK_OPTIONS = ["BSN", "ASN"]

if "reset_counter" not in st.session_state: 
    st.session_state["reset_counter"] = 0
if "exam_state" not in st.session_state: 
    st.session_state["exam_state"] = False
if "addon_state" not in st.session_state: 
    st.session_state["addon_state"] = False

st.sidebar.header("📋 Lead Profile")

# Clear Reset Flow
if st.sidebar.button("🔄 Reset Form"):
    st.session_state["reset_counter"] += 1
    st.session_state["exam_state"] = False
    st.session_state["addon_state"] = False
    st.rerun()

version = st.session_state["reset_counter"]

# ==============================================================================
# 3. SIDEBAR WITH WIDGET PLACEHOLDERS & CONDITIONAL VISIBILITY
# ==============================================================================
student_name = st.sidebar.text_input("Student Name", placeholder="Enter Your name", value="", key=f"name_{version}")
student_state = st.sidebar.selectbox("Lead State", options=STATE_OPTIONS, index=0, key=f"state_{version}")
student_zip = st.sidebar.text_input("Zip Code", placeholder="Enter Your Zip", value="", max_chars=14, key=f"zip_{version}")

is_adult = st.sidebar.selectbox("Are you 18 years of age or older?", options=BINARY_OPTIONS, index=0, key=f"adult_{version}")
gpa_val = st.sidebar.number_input("What is your GPA Score?", min_value=0.0, max_value=4.0, value=4.00, step=0.01, key=f"gpa_{version}")

dismissal_selection = st.sidebar.selectbox("Do you have a prior nursing dismissal?", options=DISMISSAL_OPTIONS, index=0, key=f"dismiss_{version}")
dismissal_y = True if dismissal_selection == "Yes" else False

dismissal_months = 0
if dismissal_y:
    dismissal_months = st.sidebar.number_input("Months since your dismissal", min_value=0, max_value=300, value=72, step=1, key=f"dismiss_mos_{version}")

license_type = st.sidebar.selectbox("What is your current nursing license?", options=LICENSE_OPTIONS, index=0, key=f"lic_{version}")
is_cna = "CNA/CMA" if license_type == "CNA/CMA" else "No"

lpn_exp = 0
if license_type == "LPN":
    lpn_exp = st.sidebar.number_input("Months of LPN Experience (If less than 2 yrs)", min_value=0, max_value=120, value=0, step=1, key=f"exp_{version}")

travel_ok = st.sidebar.selectbox("Are you okay with local clinical travel?", options=BINARY_OPTIONS, index=0, key=f"travel_{version}")
program_interest = st.sidebar.selectbox("Which track are you interested in?", options=TRACK_OPTIONS, index=0, key=f"track_{version}")

st.sidebar.markdown("---")
st.sidebar.subheader("📚 Transcript Review")

course_list = [
    "Eng Comp 1", "College Algebra", "Statistics", "Humanities 1", 
    "Humanities 2", "Humanities 3", "Human Growth & Development", 
    "Psychology", "Sociology", "Speech", "General Biology", 
    "Chemistry", "Government", "History", "Foreign Language", 
    "Macro/Micro Economics", "Elective 1", "Elective 2"
]

needed_courses = st.sidebar.multiselect(
    "Select Needed Courses:",
    options=course_list,
    default=[],
    key=f"courses_{version}"
)

selected_track = str(program_interest).strip().upper()
selected_state = str(student_state).strip().upper()

# ==============================================================================
# 4. MAIN INTERACTIVE RENDERING / COMPLIANCE GATING
# ==============================================================================
if is_adult == "No":
    st.error("🛑 **Self-Serve Checkout Unavailable**")
    st.info(f"### **Next Steps Required for {student_name if student_name else 'Applicant'}:**\nApplicants under the age of 18 are not permitted to complete an independent digital registration or contract confirmation. \n\nTo advance your enrollment matrix, please schedule an appointment to speak with an admissions representative. \n**Note:** A parent, legal guardian, or sponsoring adult must accompany the applicant during the consultation call.")
elif student_state == "Select state":
    st.warning("⚠️ **Lead State Required:** Please select a valid state territory from the sidebar dropdown list to unlock matrix filtering features.")
else:
    # --- BACKGROUND PRE-FLIGHT BALANCING & COMPLIANCE GUARD ENGINE ---
    mock_base_classes = len(needed_courses) if len(needed_courses) > 0 else 1
    if st.session_state["exam_state"]: mock_base_classes += 1
    mock_addons_count = 2 if st.session_state["addon_state"] else 0

    mock_main_price = 1179 if mock_base_classes >= 10 else (1229 if mock_base_classes >= 4 else 1289)
    mock_addon_price = 749 if (mock_base_classes + mock_addons_count) >= 10 else (799 if (mock_base_classes + mock_addons_count) >= 4 else 859)
    mock_grand_total = (mock_base_classes * mock_main_price) + (mock_addons_count * mock_addon_price)

    if mock_grand_total >= 14500:
        st.session_state["exam_state"] = False
        st.session_state["addon_state"] = False
        mock_base_classes = len(needed_courses) if len(needed_courses) > 0 else 1
        mock_main_price = 1179 if mock_base_classes >= 10 else (1229 if mock_base_classes >= 4 else 1289)
        mock_grand_total = mock_base_classes * mock_main_price

    st.sidebar.markdown("---")
    st.sidebar.subheader("🛠️ Class Triggers")

    if mock_grand_total < 14500:
        entrance_exam = st.sidebar.checkbox("Include Entrance Exam Prep?", value=st.session_state["exam_state"], key=f"chk_exam_{version}")
        has_addons = st.sidebar.checkbox("Add-ons Selected?", value=st.session_state["addon_state"], key=f"chk_addon_{version}")
        st.session_state["exam_state"] = entrance_exam
        st.session_state["addon_state"] = has_addons
    else:
        st.sidebar.warning("⚠️ Package limit reached ($14,500 Floor). Add-on triggers forced off.")
        entrance_exam = False
        has_addons = False

    # --- FINANCIAL LEDGER ENGINE VIEW ---
    st.header("⚡ Financial Ledger")
    col_calc_input, col_calc_output = st.columns([1, 1])

    with col_calc_input:
        st.subheader("Adjustments & Waivers")
        deposit_input = st.number_input("Enrollment Deposit Paid ($)", min_value=0.0, value=0.0, step=50.0, key=f"dep_in_{version}")
        grant_input = st.number_input("Grant Allocation ($)", min_value=0.0, value=0.0, step=50.0, key=f"grant_in_{version}")
        
        st.markdown("#### **Qualification Profile**")
        st.info("✅ **Deposit Match Program:** Automatically applied.")
        discount_match = True
        
        q_referral = st.radio("Were you referred by someone?", ["No", "Yes"], horizontal=True, key=f"ref_{version}")
        discount_referral = True if q_referral == "Yes" else False
        
        q_military = st.radio("Are you associated with the military (Veteran/Active/Spouse)?", ["No", "Yes"], horizontal=True, key=f"mil_{version}")
        discount_military = True if q_military == "Yes" else False
        
        discount_free_course = False
        if len(needed_courses) >= 3:
            q_free_course = st.radio("Do you possess a promotional code for a complimentary course?", ["No", "Yes"], horizontal=True, key=f"promo_{version}")
            discount_free_course = True if q_free_course == "Yes" else False

    with col_calc_output:
        st.subheader("Ledger Balance")
        
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
        
        credits_sum = calc_dep_match + calc_referral + calc_military + calc_free_course + grant_input
        final_total = max(0.0, base_total - credits_sum)
        pending_bal = max(0.0, final_total - deposit_input)
        
        if is_cna == "CNA/CMA":
            if total_classes <= 2: reg_fee = 150
            elif total_classes <= 7: reg_fee = 175
            elif total_classes <= 10: reg_fee = 200
            elif total_classes <= 15: reg_fee = 250
            else: reg_fee = 300
        else:
            if total_classes <= 2: reg_fee = 300
            elif total_classes <= 7: reg_fee = 325
            elif total_classes <= 10: reg_fee = 375
            elif total_classes <= 15: reg_fee = 475
            else: reg_fee = 600
            
        room_left = 14500.0 - final_total
        max_additional_addons = max(0, int(room_left // 749))
        projected_addons = addons_count + max_additional_addons

        txt_base_total = f"${base_total:,.2f}"
        txt_reg_fee = f"${reg_fee:,.2f}"
        txt_final_total = f"${final_total:,.2f}"
        txt_pending_bal = f"${pending_bal:,.2f}"
        txt_projected_addons = f"{projected_addons} max courses"

        m1, m2 = st.columns(2)
        m1.metric("Base Total", txt_base_total)
        m2.metric("Registration Fee", txt_reg_fee)
        
        m3, m4 = st.columns(2)
        m3.metric("Final Balance", txt_final_total)
        m4.metric("Pending Balance", txt_pending_bal)
        
        st.metric("Max Add-ons Headroom", txt_projected_addons)

    st.divider()

    # --- ELIGIBLE INSTITUTION MATRIX VIEW ---
    st.header("🏫 Eligible Institution Matches")
    available_cols = master_schools_df.columns.tolist()

    working_schools_df = master_schools_df.copy()

    if "ASN/BSN" in available_cols:
        working_schools_df = working_schools_df[working_schools_df["ASN/BSN"].str.upper() == selected_track]

    if "States Accepted" in available_cols:
        working_schools_df = working_schools_df[working_schools_df["States Accepted"].str.upper().str.contains(selected_state)]

    if "LPN Required?" in available_cols and license_type in ["None", "CNA/CMA"]:
        working_schools_df["LPN Required?"] = working_schools_df["LPN Required?"].astype(str).str.upper().str.strip()
        working_schools_df = working_schools_df[working_schools_df["LPN Required?"] != "Y"]

    if "Min Work Experience Required (mos)" in available_cols:
        working_schools_df["Min Work Experience Required (mos)"] = pd.to_numeric(working_schools_df["Min Work Experience Required (mos)"], errors='coerce').fillna(0)
        working_schools_df = working_schools_df[working_schools_df["Min Work Experience Required (mos)"] <= lpn_exp]

    if "Min GPA" in available_cols:
        working_schools_df["Min GPA"] = pd.to_numeric(working_schools_df["Min GPA"], errors='coerce').fillna(0.0)
        working_schools_df = working_schools_df[working_schools_df["Min GPA"] <= gpa_val]

    if "Clinical Travel?" in available_cols:
        if travel_ok == "No":
            travel_clean = working_schools_df["Clinical Travel?"].astype(str).str.upper().str.strip()
            working_schools_df = working_schools_df[travel_clean.isin(["NO", "N", "NONE", "0", "0.0"])]

    if "Prior Nursing Dismissal Policy" in available_cols and dismissal_y:
        if dismissal_months <= 60:
            policy_clean = working_schools_df["Prior Nursing Dismissal Policy"].astype(str).str.upper().str.strip()
            working_schools_df = working_schools_df[policy_clean != "DOES NOT ACCEPT"]

    filtered_df = working_schools_df.copy()

    if not filtered_df.empty:
        status_log = []
        cash_yield_margins = []
        deficiencies_resolved_log = [] # Container to store school-specific allowed courses
        
        for _, school_row in filtered_df.iterrows():
            raw_name = str(school_row["School Name"]).strip()
            
            if "HERZ" in raw_name.upper() or "HERI" in raw_name.upper():
                word_pattern = "HERZ|HERI"
                rule_row = transcript_rules_df[transcript_rules_df["School Name"].str.upper().str.contains(word_pattern, na=False, case=False)]
            elif "EXCEL" in raw_name.upper():
                word_pattern = "EXCEL"
                rule_row = transcript_rules_df[transcript_rules_df["School Name"].str.upper().str.contains(word_pattern, na=False, case=False)]
            else:
                rule_row = transcript_rules_df[transcript_rules_df["School Name"].str.upper() == raw_name.upper()]
            
            offered_courses_count = 0
            has_all_courses = True
            school_accepted_list = [] # Tracker for courses that earn a 'Y' mark
            
            if not rule_row.empty:
                for required_course in needed_courses:
                    if required_course in rule_row.columns:
                        accepted_status = str(rule_row[required_course].values[0]).strip().upper()
                        if accepted_status == "Y":
                            offered_courses_count += 1
                            school_accepted_list.append(required_course) # Logs course as resolved
                        else:
                            has_all_courses = False
                    else:
                        has_all_courses = False
                
                if len(needed_courses) == 0:
                    status_log.append("Perfect Match")
                elif has_all_courses:
                    status_log.append("Perfect Match")
                else:
                    status_log.append("Missing Needed CBE Courses")
            else:
                status_log.append("Perfect Match")
                
            # FIXED: "Deficiencies Met" column logic now dynamically displays only true accepted matches
            if school_accepted_list:
                deficiencies_resolved_log.append(", ".join(school_accepted_list))
            else:
                deficiencies_resolved_log.append("None")
                
            revenue_per_course = float(main_price)
            school_revenue_potential = offered_courses_count * revenue_per_course
            
            tuition_cost_raw = str(school_row.get("Tuition", "0")).replace("$", "").replace(",", "").strip()
            tuition_cost = pd.to_numeric(tuition_cost_raw, errors='coerce')
            if pd.isna(tuition_cost):
                tuition_cost = 0.0
                
            calculated_margin = max(0.0, school_revenue_potential - float(tuition_cost))
            cash_yield_margins.append(calculated_margin)
                
        filtered_df["Match Status"] = status_log
        filtered_df["Estimated Revenue Profit"] = cash_yield_margins
        filtered_df["Deficiencies Met"] = deficiencies_resolved_log # Injects dynamic data array into table row data map

        preferred_cols = ["School Name", "Estimated Revenue Profit", "ASN/BSN", "Match Status", "Min GPA", "Clinical Travel?", "Deficiencies Met"]
        columns_to_show = [col for col in preferred_cols if col in filtered_df.columns]

        if dismissal_y and "Reentry Requirements" in filtered_df.columns:
            columns_to_show.append("Reentry Requirements")

        final_display_df = filtered_df[columns_to_show].copy()
        final_display_df = final_display_df.sort_values(by="Estimated Revenue Profit", ascending=False)

        if "Estimated Revenue Profit" in final_display_df.columns:
            final_display_df["Estimated Revenue Profit"] = final_display_df["Estimated Revenue Profit"].apply(lambda x: f"${x:,.2f}")
        
        if "Min GPA" in final_display_df.columns:
            final_display_df["Min GPA"] = final_display_df["Min GPA"].apply(lambda x: f"{x:.2f}")

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
            st.warning("No schools match your base profile parameters or dismissal compliance rules.")
    else:
        st.warning("No schools match your base profile parameters or dismissal compliance rules.")
