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
    .stButton>button {background-color: #1E3A8A; color: white; border-radius: 5px; width: 100%; height: 35px;}
    .stButton>button:hover {background-color: #3B82F6; color: white;}
    div[data-testid="stMetricValue"] {font-size: 24px; color: #10B981;}
    .matrix-row {background-color: white; padding: 15px; border-radius: 5px; margin-bottom: 10px; border: 1px solid #e2e8f0;}
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
    "Select state", 
    "AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI", "IA", 
    "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MO", "MS", 
    "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", 
    "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI", "WV", "WY"
]
BINARY_OPTIONS = ["Yes", "No"]
DISMISSAL_OPTIONS = ["No", "Yes"]
LICENSE_OPTIONS = ["None", "LPN", "CNA/CMA"]
TRACK_OPTIONS = ["BSN", "ASN"]

if "reset_counter" not in st.session_state: 
    st.session_state["reset_counter"] = 0
if "addon_state" not in st.session_state: 
    st.session_state["addon_state"] = False
if "confirmed_package" not in st.session_state:
    st.session_state["confirmed_package"] = None

st.sidebar.header("📋 Lead Profile")

# Clear Reset Flow
if st.sidebar.button("🔄 Reset Form"):
    st.session_state["reset_counter"] += 1
    st.session_state["addon_state"] = False
    st.session_state["confirmed_package"] = None
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

travel_ok = st.sidebar.selectbox("Are you okay with regional clinical travel?", options=BINARY_OPTIONS, index=0, key=f"travel_{version}")
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
    st.info(f"### **Next Steps Required for {student_name if student_name else 'Applicant'}:**\nApplicants under the age of 18 are not permitted to complete an independent digital registration or contract confirmation.")
elif student_state == "Select state":
    st.warning("⚠️ **Lead State Required:** Please select a valid state territory from the sidebar dropdown list to unlock matrix filtering features.")
else:
    base_count = len(needed_courses)
    raw_base_classes = base_count if base_count > 0 else 1
    raw_main_price = 1179 if raw_base_classes >= 10 else (1229 if raw_base_classes >= 4 else 1289)
    baseline_only_total = raw_base_classes * raw_main_price

    st.sidebar.markdown("---")
    st.sidebar.subheader("🛠️ Class Triggers")

    if baseline_only_total >= 14500 and base_count > 0:
        st.sidebar.warning("⚠️ Package limit reached ($14,500 Floor). Add-on triggers forced off.")
        has_addons = False
        st.session_state["addon_state"] = False
    else:
        has_addons = st.sidebar.checkbox("Add-ons Selected?", value=st.session_state["addon_state"], key=f"chk_addon_{version}")
        
        test_base = (base_count if base_count > 0 else 1)
        test_addons = 2 if has_addons else 0
        test_total_classes = test_base + test_addons
        
        test_main_price = 1179 if test_base >= 10 else (1229 if test_base >= 4 else 1289)
        test_addon_price = 749 if test_total_classes >= 10 else (799 if test_total_classes >= 4 else 859)
        projected_total = (test_base * test_main_price) + (test_addons * test_addon_price)
        
        if projected_total >= 14500 and (base_count > 0 or has_addons):
            st.sidebar.warning("⚠️ Selection blocked: Combined total breaches the $14,500 Package Floor limit.")
            st.session_state["addon_state"] = False
            st.rerun()
        else:
            st.session_state["addon_state"] = has_addons

    # --- SHOW CONFIRMED PACKAGE CELEBRATION CARD ---
    if st.session_state["confirmed_package"]:
        pkg = st.session_state["confirmed_package"]
        st.balloons()
        st.success(f"🎉 **Enrollment Successfully Finalized for {student_name if student_name else 'Lead'}!**")
        
        inv1, inv2, inv3 = st.columns(3)
        inv1.markdown(f"**Institution Secured:**\n### {pkg['school_name']}")
        inv2.metric("Final Balance Due", f"${pkg['final_total']:,.2f}")
        inv3.metric("Registration Fee", f"${pkg['reg_fee']:,.2f}")
        
        with st.expander("📄 View Itemized Invoice Audit Ledger"):
            st.json(pkg)
        st.divider()

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
        
        is_completely_empty = (base_count == 0 and not has_addons)
        base_classes = base_count if base_count > 0 else 1
        addons_count = 2 if has_addons else 0
        total_classes = (base_count if base_count > 0 else 0) + addons_count
        
        main_price = 1179 if base_classes >= 10 else (1229 if base_classes >= 4 else 1289)
        addon_price = 749 if total_classes >= 10 else (799 if total_classes >= 4 else 859)
        
        if base_count == 0:
            base_total = (addons_count * addon_price)
        else:
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
            if total_classes == 0: reg_fee = 0
            elif total_classes <= 2: reg_fee = 150
            elif total_classes <= 7: reg_fee = 175
            elif total_classes <= 10: reg_fee = 200
            elif total_classes <= 15: reg_fee = 250
            else: reg_fee = 300
        else:
            if total_classes == 0: reg_fee = 0
            elif total_classes <= 2: reg_fee = 300
            elif total_classes <= 7: reg_fee = 325
            elif total_classes <= 10: reg_fee = 375
            elif total_classes <= 15: reg_fee = 475
            else: reg_fee = 600

        txt_base_total = "$0.00" if is_completely_empty else f"${base_total:,.2f}"
        txt_reg_fee = "$0.00" if is_completely_empty else f"${reg_fee:,.2f}"
        txt_final_total = "$0.00" if is_completely_empty else f"${final_total:,.2f}"
        txt_pending_bal = "$0.00" if is_completely_empty else f"${pending_bal:,.2f}"

        m1, m2 = st.columns(2)
        m1.metric("Base Total", txt_base_total)
        m2.metric("Registration Fee", txt_reg_fee)
        
        m3, m4 = st.columns(2)
        m3.metric("Final Balance", txt_final_total)
        m4.metric("Pending Balance", txt_pending_bal)

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

    # DIALOG MODAL EXECUTION ENGINE
    @st.dialog("Confirm & Lock Enrollment Package")
    def render_institutional_modal(school_name, school_exam_type):
        st.markdown(f"### 📋 Reviewing: **{school_name}**")
        st.markdown("---")
        
        modal_base_count = len(needed_courses)
        modal_addons = 2 if has_addons else 0
        
        if school_exam_type == "--" or school_exam_type == "":
            st.info("ℹ️ **No Entrance Exam Required:** This institution does not mandate an entrance examination baseline parameter.")
            include_exam_prep = False
        else:
            st.markdown(f"#### 🔒 Entrance Exam Compliance Gating")
            user_has_passed = st.radio(f"Have you already taken and passed the required **{school_exam_type}** exam?", ["No", "Yes"], horizontal=True)
            
            if user_has_passed == "Yes":
                st.success(f"✅ Verified: Applicant is already compliant for the {school_exam_type} test track.")
                include_exam_prep = False
            else:
                current_test_base = (modal_base_count if modal_base_count > 0 else 1)
                current_test_total = current_test_base + modal_addons
                current_main_p = 1179 if current_test_base >= 10 else (1229 if current_test_base >= 4 else 1289)
                current_addon_p = 749 if current_test_total >= 10 else (799 if current_test_total >= 4 else 859)
                
                if modal_base_count == 0:
                    current_pre_total = (modal_addons * current_addon_p)
                else:
                    current_pre_total = (current_test_base * current_main_p) + (modal_addons * current_addon_p)
                    
                current_final_total = max(0.0, current_pre_total - credits_sum)
                
                if current_final_total >= 14500:
                    st.warning("⚠️ **Exam Prep Unavailable:** The current package layout has reached the $14,500 threshold limitation.")
                    include_exam_prep = False
                else:
                    include_exam_prep = st.checkbox(f"Add **{school_exam_type}** Prep Course to Package? (+$1,289 Floor Baseline)")

        st.markdown("---")
        st.markdown("#### Itemized Balance Preview")
        
        final_base_classes = modal_base_count if modal_base_count > 0 else 1
        if include_exam_prep:
            final_base_classes = modal_base_count + 1 if modal_base_count > 0 else 1
            
        final_total_classes = (modal_base_count if modal_base_count > 0 else 0) + (1 if include_exam_prep else 0) + modal_addons
        
        m_main_p = 1179 if final_base_classes >= 10 else (1229 if final_base_classes >= 4 else 1289)
        m_addon_p = 749 if final_total_classes >= 10 else (799 if final_total_classes >= 4 else 859)
        
        if modal_base_count == 0 and include_exam_prep:
            final_base_total = (1 * m_main_p) + (modal_addons * m_addon_p)
        elif modal_base_count == 0 and not include_exam_prep:
            final_base_total = (modal_addons * m_addon_p)
        else:
            final_base_total = (final_base_classes * m_main_p) + (modal_addons * m_addon_p)
            
        modal_final_total = max(0.0, final_base_total - credits_sum)
        
        if is_cna == "CNA/CMA":
            if final_total_classes == 0: m_reg = 0
            elif final_total_classes <= 2: m_reg = 150
            elif final_total_classes <= 7: m_reg = 175
            elif final_total_classes <= 10: m_reg = 200
            elif final_total_classes <= 15: m_reg = 250
            else: m_reg = 300
        else:
            if final_total_classes == 0: m_reg = 0
            elif final_total_classes <= 2: m_reg = 300
            elif final_total_classes <= 7: m_reg = 325
            elif final_total_classes <= 10: m_reg = 375
            elif final_total_classes <= 15: m_reg = 475
            else: m_reg = 60
