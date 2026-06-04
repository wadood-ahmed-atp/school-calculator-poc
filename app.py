import streamlit as st
import pandas as pd
import os
import re

# ==============================================================================
# 0. PAGE CONFIG & STICKY HEADER FIXED CSS OVERRIDES
# ==============================================================================
st.set_page_config(page_title="Bridge Plan Generator", layout="wide")

# Advanced production layout injection block
st.markdown("""
    <style>
    /* 🚫 ELIMINATE STREAMLIT MENU & TOP INFRASTRUCTURE COMPLETELY */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display: none;}
    
    /* 📌 FIXED LAYER: Lock the entire top application header area out of scroll streams */
    [data-testid="stHeader"] {
        display: none !important;
    }
    
    /* Force main app structural margins to sit flush with fixed layer ceilings */
    .block-container {
        padding-top: 0px !important;
        margin-top: 0px !important;
    }
    
    .main {background-color: #f8f9fa;}
    h1, h2, h3 {color: #1E3A8A; font-family: 'Inter', sans-serif;}
    
    /* Sticky Top Container Wrapper Box Structuring */
    .sticky-header-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: #f8f9fa;
        z-index: 999;
        padding: 15px 5rem 10px 5rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    
    /* Adjust body clearance offsets to clear fixed menu elements overhead */
    .scrollable-body-content {
        margin-top: 260px !important;
        padding-bottom: 50px;
    }
    
    /* Elevated responsive content card formatting rules */
    .content-card {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.03);
        margin-bottom: 20px;
    }
    
    /* 🎨 CUSTOM TAB NAVIGATION INTERACTIVE STYLING OVERRIDES */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        border-bottom: none !important; /* 🚫 REMOVES RESIDUAL UNDERLINE WHITE BAR */
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 8px !important;
        background-color: #ffffff;
        border: 1px solid #e2e8f0 !important;
        padding: 0px 24px !important;
        font-weight: 600 !important;
        color: #64748b !important;
        transition: all 0.2s ease-in-out;
    }
    /* Active step focus alignment tracking style indicators */
    .stTabs [aria-selected="true"] {
        background-color: #1E3A8A !important;
        color: white !important;
        border-color: #1E3A8A !important;
    }
    
    /* Premium action button layouts tracking frames */
    .stButton>button {
        border-radius: 8px !important;
        height: 44px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        transition: all 0.2s ease-in-out !important;
    }
    div.primary-btn>div>button {
        background-color: #1E3A8A !important;
        color: white !important;
        border: none !important;
    }
    div.primary-btn>div>button:hover {
        background-color: #2563EB !important;
        transform: translateY(-1px);
    }
    div.secondary-btn>div>button {
        background-color: #ffffff !important;
        color: #475569 !important;
        border: 1px solid #cbd5e1 !important;
    }
    div.secondary-btn>div>button:hover {
        background-color: #f8f9fa !important;
    }
    div.utility-btn>div>button {
        background-color: transparent !important;
        color: #94a3b8 !important;
        border: 1px dashed #cbd5e1 !important;
        height: 34px !important;
    }
    div.utility-btn>div>button:hover {
        color: #ef4444 !important;
        border-color: #fca5a5 !important;
        background-color: #fef2f2 !important;
    }

    @media (max-width: 992px) {
        .sticky-header-container { padding: 15px 1rem 10px 1rem; }
        .scrollable-body-content { margin-top: 320px !important; }
        div[data-testid="stHorizontalBlock"] { flex-direction: column !important; }
        div[data-testid="stColumn"] { width: 100% !important; margin: 0px 0px 20px 0px !important; }
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. PERSISTENT BACKSTAGE SESSION STATE VAULT HOOKS
# ==============================================================================
if "confirmed_package" not in st.session_state: st.session_state["confirmed_package"] = None
if "active_school_view" not in st.session_state: st.session_state["active_school_view"] = None
if "modal_include_exam_prep" not in st.session_state: st.session_state["modal_include_exam_prep"] = False

# Memory storage slots for continuous value tracking retention
if "val_name" not in st.session_state: st.session_state["val_name"] = ""
if "val_state" not in st.session_state: st.session_state["val_state"] = "Select state"
if "val_zip" not in st.session_state: st.session_state["val_zip"] = ""
if "val_adult" not in st.session_state: st.session_state["val_adult"] = "Yes"
if "val_gpa" not in st.session_state: st.session_state["val_gpa"] = 4.00

if "val_lic" not in st.session_state: st.session_state["val_lic"] = "None"
if "val_exp" not in st.session_state: st.session_state["val_exp"] = 0
if "val_dismiss" not in st.session_state: st.session_state["val_dismiss"] = "No"
if "val_dismiss_mos" not in st.session_state: st.session_state["val_dismiss_mos"] = 72
if "val_travel" not in st.session_state: st.session_state["val_travel"] = "Yes"
if "val_track" not in st.session_state: st.session_state["val_track"] = "BSN"

if "val_courses" not in st.session_state: st.session_state["val_courses"] = []
if "val_deposit" not in st.session_state: st.session_state["val_deposit"] = 0.0
if "val_grant" not in st.session_state: st.session_state["val_grant"] = 0.0
if "val_ref" not in st.session_state: st.session_state["val_ref"] = "No"
if "val_mil" not in st.session_state: st.session_state["val_mil"] = "No"
if "val_promo" not in st.session_state: st.session_state["val_promo"] = "No"

def restart_wizard():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ==============================================================================
# 2. DATA IMPORT ENGINE LOADER
# ==============================================================================
SCHOOLS_CSV = "schools.csv"
TRANSCRIPT_CSV = "transcript_rules.csv"

if os.path.exists(SCHOOLS_CSV):
    try: master_schools_df = pd.read_csv(SCHOOLS_CSV, encoding='utf-8')
    except Exception: master_schools_df = pd.read_csv(SCHOOLS_CSV, encoding='latin1', errors='replace')
    for col in master_schools_df.select_dtypes(include=['object']).columns:
        master_schools_df[col] = master_schools_df[col].astype(str).str.strip()
else:
    st.error("⚠️ Master database schools.csv input missing.")
    st.stop()

if os.path.exists(TRANSCRIPT_CSV):
    try: transcript_rules_df = pd.read_csv(TRANSCRIPT_CSV, encoding='utf-8')
    except Exception: transcript_rules_df = pd.read_csv(TRANSCRIPT_CSV, encoding='latin1', errors='replace')
    for col in transcript_rules_df.select_dtypes(include=['object']).columns:
        transcript_rules_df[col] = transcript_rules_df[col].astype(str).str.strip()
    transcript_rules_df.columns = transcript_rules_df.columns.str.strip()
else:
    st.error("⚠️ Validation rules transcript_rules.csv input missing.")
    st.stop()

# ==============================================================================
# 3. OPTIONS METRIC OPTION ARRAYS
# ==============================================================================
STATE_OPTIONS = [
    "Select state", "AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
    "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", 
    "MO", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", 
    "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI", "WV", "WY"
]
BINARY_OPTIONS = ["Yes", "No"]
DISMISSAL_OPTIONS = ["No", "Yes"]
LICENSE_OPTIONS = ["None", "LPN", "CNA/CMA"]
TRACK_OPTIONS = ["BSN", "ASN"]

course_list = [
    "Eng Comp 1", "College Algebra", "Statistics", "Humanities 1", "Humanities 2", 
    "Humanities 3", "Human Growth & Development", "Psychology", "Sociology", "Speech", 
    "General Biology", "Chemistry", "Government", "History", "Foreign Language", 
    "Macro/Micro Economics", "Elective 1", "Elective 2"
]

# ==============================================================================
# 4. FIXED LOCK LAYER DESIGN ENGINE (PINNED STICKY HEADERS MATRIX)
# ==============================================================================
st.markdown("<div class='sticky-header-container'>", unsafe_allow_html=True)
header_title_col, header_utility_col = st.columns([3.0, 1.0])
with header_title_col:
    st.markdown("<h1 style='margin:0;'>🗺️ Bridge Plan Generator</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin:0; font-weight:400; color:#475569;'>Self-Serve Enrollment Matrix</h3>", unsafe_allow_html=True)
with header_utility_col:
    st.markdown("<div class='utility-btn' style='padding-top: 10px;'>", unsafe_allow_html=True)
    if st.button("🔄 Reset Form Data", use_container_width=True):
        restart_wizard()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Determine the status symbols for steps
step1_lbl = "✅ 1. Identity Profile" if st.session_state["val_state"] != "Select state" else "1. Identity Profile"
step2_lbl = "✅ 2. Baseline Profile" if st.session_state["val_lic"] != "None" or st.session_state["val_exp"] > 0 else "2. Baseline Profile"
step3_lbl = "✅ 3. Transcripts Review" if len(st.session_state["val_courses"]) > 0 else "3. Transcripts Review"
step4_lbl = "✅ 4. School Matches" if st.session_state["confirmed_package"] is not None else "4. School Matches"

# 🔑 RE-ENGINEERING CORE TRIGGER: Interactive, clickable native container tab frames
tab_id, tab_base, tab_transcript, tab_matches = st.tabs([step1_lbl, step2_lbl, step3_lbl, step4_lbl])
st.markdown("</div>", unsafe_allow_html=True)

# Open scrollable area container row block
st.markdown("<div class='scrollable-body-content'>", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# TAB 1: IDENTITY PROFILE AREA
# --------------------------------------------------------------------------
with tab_id:
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("### **Step 1: Welcome & Identity Profile**")
    st.markdown("Let's capture your baseline territory parameters to filter institutional regional availability.")
    st.divider()
    
    st.session_state["val_name"] = st.text_input("What is your name?", value=st.session_state["val_name"], placeholder="Enter full name")
    st.session_state["val_state"] = st.selectbox("Select your residency home state:", options=STATE_OPTIONS, index=STATE_OPTIONS.index(st.session_state["val_state"]))
    st.session_state["val_zip"] = st.text_input("What is your zip code?", value=st.session_state["val_zip"], placeholder="e.g. 19013", max_chars=14)
    st.session_state["val_adult"] = st.selectbox("Are you 18 years of age or older?", options=BINARY_OPTIONS, index=BINARY_OPTIONS.index(st.session_state["val_adult"]))
    st.session_state["val_gpa"] = st.number_input("What is your current cumulative GPA Score?", min_value=0.0, max_value=4.0, value=st.session_state["val_gpa"], step=0.01)
    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# TAB 2: PROFESSIONAL BASELINE AREA
# --------------------------------------------------------------------------
with tab_base:
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("### **Step 2: Professional Licensing & History**")
    st.markdown("Tell us about your background to clear nursing experience validation layers.")
    st.divider()
    
    st.session_state["val_lic"] = st.selectbox("What is your current nursing license tier?", options=LICENSE_OPTIONS, index=LICENSE_OPTIONS.index(st.session_state["val_lic"]))
    if st.session_state["val_lic"] == "LPN":
        st.session_state["val_exp"] = st.number_input("Total months of active LPN Work Experience:", min_value=0, max_value=120, value=st.session_state["val_exp"], step=1)
        
    st.session_state["val_dismiss"] = st.selectbox("Do you possess a prior academic nursing program dismissal?", options=DISMISSAL_OPTIONS, index=DISMISSAL_OPTIONS.index(st.session_state["val_dismiss"]))
    if st.session_state["val_dismiss"] == "Yes":
        st.session_state["val_dismiss_mos"] = st.number_input("Months elapsed since your historical dismissal date:", min_value=0, max_value=300, value=st.session_state["val_dismiss_mos"], step=1)
        
    st.session_state["val_travel"] = st.selectbox("Are you amenable to regional clinical onsite travel loops?", options=BINARY_OPTIONS, index=BINARY_OPTIONS.index(st.session_state["val_travel"]))
    st.session_state["val_track"] = st.selectbox("Which nursing track are you targeting?", options=TRACK_OPTIONS, index=TRACK_OPTIONS.index(st.session_state["val_track"]))
    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# TAB 3: TRANSCRIPT REVIEW AREA (CLEAN BROAD SINGLE COLUMN LAYOUT)
# --------------------------------------------------------------------------
with tab_transcript:
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.markdown("### **Step 3: Transcript Review & Qualifications**")
    st.markdown("Select your prerequisite deficiencies and apply your discount triggers here.")
    st.divider()
    
    st.multiselect(
        "Check the boxes for courses you still NEED to complete:",
        options=course_list,
        default=st.session_state["val_courses"],
        key="temp_courses" 
    )
    st.session_state["val_courses"] = st.session_state["temp_courses"]
    
    st.markdown("#### 🎖️ Promotional Qualifications & Discounts")
    st.session_state["val_ref"] = st.radio("Were you referred by a student or agent?", ["No", "Yes"], index=["No", "Yes"].index(st.session_state["val_ref"]), horizontal=True)
    st.session_state["val_mil"] = st.radio("Are you affiliated with the Military (Veteran/Active/Spouse)?", ["No", "Yes"], index=["No", "Yes"].index(st.session_state["val_mil"]), horizontal=True)
    
    # 🔎 DYNAMIC STEP LOOKAHEAD GUARD: Only unlocks if global count is 3 or greater
    if len(st.session_state["val_courses"]) >= 3:
        st.session_state["val_promo"] = st.radio("Do you possess a promotional code for a complimentary course?", ["No", "Yes"], index=["No", "Yes"].index(st.session_state["val_promo"]), horizontal=True)
    else:
        st.session_state["val_promo"] = "No"
        
    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# TAB 4: INSTITUTIONAL MATCH RESPONSIVE SPLIT WORKSPACE
# --------------------------------------------------------------------------
with tab_matches:
    col_input_flow, col_ledger_flow = st.columns([1.5, 1.0], gap="large")
    
    with col_input_flow:
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.markdown("### **Step 4: Secure Institutional Match Alignment**")
        st.markdown("Review the eligible educational institutions calculated from your intake profile parameters:")
        st.divider()
        
        student_state = st.session_state["val_state"]
        selected_state = str(student_state).strip().upper()
        selected_track = str(st.session_state["val_track"]).strip().upper()
        license_type = st.session_state["val_lic"]
        lpn_exp = st.session_state["val_exp"]
        gpa_val = st.session_state["val_gpa"]
        travel_ok = st.session_state["val_travel"]
        dismissal_y = True if st.session_state["val_dismiss"] == "Yes" else False
        dismissal_months = st.session_state["val_dismiss_mos"]
        needed_courses = st.session_state["val_courses"]

        working_schools_df = master_schools_df.copy()
        if "ASN/BSN" in working_schools_df.columns:
            working_schools_df = working_schools_df[working_schools_df["ASN/BSN"].str.upper() == selected_track]
        if "States Accepted" in working_schools_df.columns:
            working_schools_df = working_schools_df[working_schools_df["States Accepted"].str.upper().str.contains(selected_state)]
        if "LPN Required?" in working_schools_df.columns and license_type in ["None", "CNA/CMA"]:
            working_schools_df = working_schools_df[working_schools_df["LPN Required?"].astype(str).str.upper().str.strip() != "Y"]
        if "Min Work Experience Required (mos)" in working_schools_df.columns:
            working_schools_df["Min Work Experience Required (mos)"] = pd.to_numeric(working_schools_df["Min Work Experience Required (mos)"], errors='coerce').fillna(0)
            working_schools_df = working_schools_df[working_schools_df["Min Work Experience Required (mos)"] <= lpn_exp]
        if "Min GPA" in working_schools_df.columns:
            working_schools_df["Min GPA"] = pd.to_numeric(working_schools_df["Min GPA"], errors='coerce').fillna(0.0)
            working_schools_df = working_schools_df[working_schools_df["Min GPA"] <= gpa_val]
        if "Clinical Travel?" in working_schools_df.columns and travel_ok == "No":
            travel_clean = working_schools_df["Clinical Travel?"].astype(str).str.upper().str.strip()
            working_schools_df = working_schools_df[travel_clean.isin(["NO", "N", "NONE", "0"])]
        if "Prior Nursing Dismissal Policy" in working_schools_df.columns and dismissal_y:
            if dismissal_months <= 60:
                working_schools_df = working_schools_df[working_schools_df["Prior Nursing Dismissal Policy"].astype(str).str.upper().str.strip() != "DOES NOT ACCEPT"]

        filtered_df = working_schools_df.copy()

        # ==============================================================================
        # MODAL COMPLIANCE DIALOG ENGINE
        # ==============================================================================
        @st.dialog("Confirm & Lock Enrollment Package")
        def render_institutional_modal(school_name, school_exam_type, school_exam_notes, valid_courses_list, school_card_ref):
            st.markdown(f"### 📋 Reviewing: **{school_name}**")
            st.markdown("---")
            
            modal_base_count = len(valid_courses_list)
            classes_waived = 0
            waived_course_name = ""
            user_score_logged = ""
            
            deposit_input = st.session_state["val_deposit"]
            grant_input = st.session_state["val_grant"]
            local_include_prep = False
            
            if school_exam_type in ["--", "", "nan"] or pd.isna(school_exam_type):
                st.info("ℹ️ **No Entrance Exam Required:** This institution does not mandate an entrance examination baseline parameter.")
                local_include_prep = False
            else:
                st.markdown(f"#### 🔒 Entrance Exam Compliance Gating")
                user_has_passed = st.radio(f"Have you already taken and passed the required **{school_exam_type}** exam?", ["No", "Yes"], horizontal=True, key="modal_has_passed_radio")
                
                if user_has_passed == "No":
                    st.warning(f"⚠️ **Notice:** We have pre-added the **{school_exam_type} Prep Course** package to your shopping bundle cart.")
                    local_include_prep = st.checkbox(f"Keep **{school_exam_type} Prep Course** included in tuition bundle?", value=True, key="opt_out_chk_1")
                else:
                    raw_input_score = st.text_input("Enter your official exam score or percentage number:", placeholder="e.g., 75 or 740")
                    user_score_logged = raw_input_score
                    
                    if raw_input_score:
                        clean_score_str = re.sub(r'[^\d.]', '', raw_input_score)
                        score_num = float(clean_score_str) if clean_score_str else 0.0
                        
                        notes_str = str(school_exam_notes).strip()
                        rules = notes_str.split('|')
                        
                        matched_rule_type = "fail" 
                        custom_message = ""
                        age_limit_years = None
                        age_question_text = ""
                        
                        for rule in rules:
                            parts = rule.split(':')
                            if not parts or parts[0] == "": continue
                            condition = parts[0].strip()
                            
                            if '-' in condition:
                                try:
                                    low, high = map(float, condition.split('-'))
                                    if low <= score_num <= high:
                                        matched_rule_type = parts[1].strip()
                                        custom_message = parts[2].strip() if len(parts) > 2 else ""
                                except ValueError: pass
                            elif '+' in condition:
                                try:
                                    floor_val = float(condition.replace('+', ''))
                                    if score_num >= floor_val:
                                        matched_rule_type = parts[1].strip()
                                        if matched_rule_type == "exempt":
                                            classes_waived = int(parts[2].strip())
                                            waived_course_name = parts[3].strip()
                                        elif matched_rule_type == "pass" and len(parts) > 2:
                                            custom_message = parts[2].strip()
                                except ValueError: pass
                            elif condition == "age":
                                age_limit_years = int(parts[1].strip())
                                age_question_text = parts[2].strip()

                        if score_num > 0:
                            if matched_rule_type == "fail":
                                st.error(f"🛑 **Score Below Target:** Pre-adding the **{school_exam_type} Prep Course** bundle.")
                                local_include_prep = st.checkbox(f"Keep **{school_exam_type} Prep Course** included in tuition bundle?", value=True, key="opt_out_chk_2")
                            elif matched_rule_type == "pass":
                                if age_limit_years:
                                    st.markdown("##### ⏳ Verification Check Required:")
                                    exam_age = st.slider(age_question_text, min_value=0, max_value=10, value=1)
                                    if exam_age > age_limit_years:
                                        st.error(f"🛑 **Score Expired:** Outdated timeline parameters. Pre-adding the prep bundle.")
                                        local_include_prep = st.checkbox(f"Keep **{school_exam_type} Prep Course** included in tuition bundle?", value=True, key="opt_out_chk_3")
                                    else:
                                        st.success(f"✅ Verified: Score parameter is active and compliant for enrollment!")
                                        local_include_prep = False
                                else:
                                    st.success(f"✅ Verified: Applicant is compliant for the track.")
                                    local_include_prep = False
                            elif matched_rule_type == "retest":
                                st.warning(f"⚠️ **Admission Approved!** {custom_message}")
                                local_include_prep = st.checkbox(f"Add **{school_exam_type} Advanced Retest Prep** to maximize exemptions?", value=True, key="opt_out_chk_4")
                            elif matched_rule_type == "exempt":
                                st.success(f"🎉 **Elite Score Unlocked!** Automatic exemption granted from **{waived_course_name}**.")
                                local_include_prep = False

            st.markdown("---")
            st.markdown("#### Itemized Balance Preview")
            
            final_base_classes = modal_base_count
            if local_include_prep:
                final_base_classes = modal_base_count + 1
            elif classes_waived > 0:
                final_base_classes = max(0, modal_base_count - classes_waived)
                
            m_classes_tier = final_base_classes if final_base_classes > 0 else 1
            m_price_tier = 1179 if m_classes_tier >= 10 else (1229 if m_classes_tier >= 4 else 1289)
            final_base_total = final_base_classes * m_price_tier
            
            calc_dep_match = min(deposit_input, 1000.0) if (deposit_input >= 300) else 0.0
            calc_referral = 50.0 if st.session_state["val_ref"] == "Yes" else 0.0
            calc_military = 200.0 if st.session_state["val_mil"] == "Yes" else 0.0
            
            # 🔑 REAL-TIME LOCAL CONTEXT EVALUATION ENGINE HOOK
            calc_free_course = float(m_price_tier) if (st.session_state["val_promo"] == "Yes" and modal_base_count >= 3) else 0.0
            modal_credits_sum = calc_dep_match + calc_referral + calc_military + calc_free_course + grant_input
            modal_final_total = max(0.0, final_base_total - modal_credits_sum)

            st.metric("Adjusted Base Tuition", f"${final_base_total:,.2f}")
            st.metric("Final Balance Due", f"${modal_final_total:,.2f}")
            
            if st.button("🔒 Lock in Enrollment Package", key="modal_lock_btn"):
                st.session_state["modal_include_exam_prep"] = local_include_prep
                st.session_state["active_school_view"] = school_card_ref
                st.session_state["confirmed_package"] = {
                    "school_name": school_name,
                    "student_name": st.session_state["val_name"],
                    "base_total": final_base_total,
                    "reg_fee": 0.0,
                    "final_total": modal_final_total,
                    "courses_included": valid_courses_list,
                    "entrance_exam_prep_added": local_include_prep,
                    "entrance_exam_score_logged": user_score_logged,
                    "classes_waived_count": classes_waived,
                    "addons_active": False
                }
                st.rerun()

        # Render list of dynamic matching rows
        if not filtered_df.empty:
            card_rows = []
            for idx, school_row in filtered_df.iterrows():
                raw_name = str(school_row["School Name"]).strip()
                s_exam = str(school_row.get("Entrance Exam", "--")).strip()
                s_notes = str(school_row.get("Entrance Exam Notes", "")).strip()
                
                if "HERZ" in raw_name.upper() or "HERI" in raw_name.upper():
                    rule_row = transcript_rules_df[transcript_rules_df["School Name"].str.upper().str.contains("HERZ|HERI", na=False)]
                elif "EXCEL" in raw_name.upper():
                    rule_row = transcript_rules_df[transcript_rules_df["School Name"].str.upper().str.contains("EXCEL", na=False)]
                else: rule_row = transcript_rules_df[transcript_rules_df["School Name"].str.upper() == raw_name.upper()]
                
                school_accepted_list = []
                has_all_courses = True
                
                if not rule_row.empty:
                    for required_course in needed_courses:
                        if required_course in rule_row.columns:
                            if str(rule_row[required_course].values[0]).strip().upper() == "Y":
                                school_accepted_list.append(required_course)
                            else: has_all_courses = False
                        else: has_all_courses = False
                    s_status = "Perfect Match" if (len(needed_courses) == 0 or has_all_courses) else "Missing Needed CBE Courses"
                else:
                    s_status = "Perfect Match"
                    school_accepted_list = list(needed_courses)
                
                c_count = len(school_accepted_list)
                c_base_classes = c_count if c_count > 0 else 1
                c_main_price = 1179 if c_base_classes >= 10 else (1229 if c_base_classes >= 4 else 1289)
                
                school_revenue_potential = c_count * float(c_main_price)
                tuition_cost_raw = str(school_row.get("Tuition", "0")).replace("$", "").replace(",", "").strip()
                tuition_cost = pd.to_numeric(tuition_cost_raw, errors='coerce') if pd.isna(pd.to_numeric(tuition_cost_raw, errors='coerce')) == False else 0.0
                est_profit = max(0.0, school_revenue_potential - float(tuition_cost))
                
                card_rows.append({
                    "idx": idx,
                    "name": raw_name,
                    "exam": s_exam,
                    "notes": s_notes,
                    "track": school_row["ASN/BSN"],
                    "status": s_status,
                    "accepted_courses": school_accepted_list,
                    "profit": est_profit
                })
            
            card_rows = sorted(card_rows, key=lambda x: x["profit"], reverse=True)

            for card in card_rows:
                with st.container(border=True):
                    sc1, sc2, sc3 = st.columns([1.5, 3.0, 1.5])
                    with sc1:
                        st.markdown("<div class='primary-btn'>", unsafe_allow_html=True)
                        if st.button("Select School", key=f"btn_card_sel_{card['idx']}", use_container_width=True):
                            render_institutional_modal(card["name"], card["exam"], card["notes"], card["accepted_courses"], card)
                        st.markdown("</div>", unsafe_allow_html=True)
                    with sc2:
                        st.markdown(f"🏫 **{card['name']}** ({card['track']} Track)")
                        courses_string = ", ".join(card["accepted_courses"]) if card["accepted_courses"] else "None Required"
                        st.markdown(f"🧬 *Deficiencies Fulfilled ({len(card['accepted_courses'])}):* `{courses_string}`")
                    with sc3:
                        st.metric("Est Profit Margin", f"${card['profit']:,.2f}")
        else:
            st.warning("No partner institutions match your core background or geofencing matrix filters.")
        st.markdown("</div>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # SHOPPING CART LEDGER COMPONENT (WIRED WITH CONTEXT FILTER SAFEGUARDS)
    # --------------------------------------------------------------------------
    with col_ledger_flow:
        st.markdown("<div style='background-color: #ffffff; padding: 25px; border-radius: 12px; border: 2px solid #1E3A8A; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
        st.subheader("🛒 Itemized Invoice Cart")
        
        # 🔑 Core Gate Checklist Switch: Keeps screen blank until formal button lock trigger submittal records register
        if st.session_state["confirmed_package"] is None:
            st.info("👉 Please select an institutional partner row on the left and finalize your entrance exam compliance settings to generate your custom itemized checkout ledger statement.")
        else:
            needed_courses = st.session_state["active_school_view"]["accepted_courses"]
            st.markdown(f"🎯 *Active Locked Context:* **{st.session_state['active_school_view']['name']}**")

            extra_exam_count = 1 if st.session_state.get("modal_include_exam_prep", False) else 0
            base_classes = len(needed_courses) + extra_exam_count
            total_classes = base_classes
            is_completely_empty = (total_classes == 0)
            
            m_classes_tier = base_classes if base_classes > 0 else 1
            main_price = 1179 if m_classes_tier >= 10 else (1229 if m_classes_tier >= 4 else 1289)
            base_total = base_classes * main_price
            
            st.markdown("#### Adjustments & Grants")
            deposit_input = st.number_input("Enrollment Deposit Amount ($)", min_value=0.0, value=st.session_state["val_deposit"], step=50.0)
            grant_input = st.number_input("Institutional Grant Amount ($)", min_value=0.0, value=st.session_state["val_grant"], step=50.0)
            
            st.session_state["val_deposit"] = deposit_input
            st.session_state["val_grant"] = grant_input

            q_ref = st.session_state["val_ref"]
            q_mil = st.session_state["val_mil"]
            
            # 🔑 CONTEXT SAFEGUARD LAYER: Evaluate promo code visibility directly against school-accepted list length
            if len(needed_courses) >= 3:
                q_promo = st.radio("Do you possess a promotional code for a complimentary course?", ["No", "Yes"], index=["No", "Yes"].index(st.session_state["val_promo"]), horizontal=True, key="ledger_promo_radio")
                st.session_state["val_promo"] = q_promo
            else:
                st.session_state["val_promo"] = "No"
                q_promo = "No"

            calc_dep_match = min(deposit_input, 1000.0) if (deposit_input >= 300) else 0.0
            calc_referral = 50.0 if q_ref == "Yes" else 0.0
            calc_military = 200.0 if q_mil == "Yes" else 0.0
            
            # Use school base count instead of global array count to prevent over-credit anomalies
            calc_free_course = float(main_price) if (q_promo == "Yes" and len(needed_courses) >= 3) else 0.0
            
            credits_sum = calc_dep_match + calc_referral + calc_military + calc_free_course + grant_input
            final_total = max(0.0, base_total - credits_sum)

            st.divider()
            st.markdown(f"**Gross Base Tuition:** `${0.00 if is_completely_empty else base_total:,.2f}`")
            st.markdown(f"**Waivers & Grants Applied:** `-${credits_sum:,.2f}`")
            st.markdown(f"## **Balance Due: ${0.00 if is_completely_empty else final_total:,.2f}**")
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Post-Process final vouchers layout generation
if st.session_state["confirmed_package"]:
    pkg = st.session_state["confirmed_package"]
    st.balloons()
    st.success(f"🎉 **Bridge Plan Successfully Finalized for {pkg['student_name']}!**")
    st.markdown(f"### Selected School Locked: **{pkg['school_name']}**")
    st.metric("Final Adjusted Price", f"${pkg['final_total']:,.2f}")
    with st.expander("📄 View Final Signed Voucher Audit Manifest"):
        st.json(pkg)
