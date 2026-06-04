import streamlit as st
import pandas as pd
import os
import re

# ==============================================================================
# 0. DESKTOP GRID & ENTERPRISE INFRASTRUCTURE TOOLBAR REMOVALS
# ==============================================================================
st.set_page_config(page_title="Bridge Plan Generator", layout="wide")

st.markdown("""
    <style>
    /* 🚫 SURGICALLY REMOVE ONLY TOOLBAR CONTROL ITEMS (SHARE, EDIT, GITHUB, STAR) */
    div[data-testid="stStatusWidget"], 
    .stToolbar, 
    header[data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
        width: 0px !important;
        height: 0px !important;
    }
    
    /* Centers and caps the main form body layout so fields don't stretch infinitely */
    .block-container {
        max-width: 1200px !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        padding-top: 2rem !important;
    }
    
    /* Interactive action controls responsiveness rules */
    .stButton>button {
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. FAULTLESS STATE INITIALIZATION STORAGE VAULT
# ==============================================================================
def initialize_base_states(force_reset=False):
    """Safely handles pristine initialization of memory vaults without race conditions"""
    defaults = {
        "wizard_step": 1,
        "confirmed_package": None,
        "addon_state": False,
        "active_school_view": None,
        "selected_school_id": None,
        "modal_include_exam_prep": False,
        "modal_score_logged": "",
        "modal_classes_waived": 0,
        "val_name": "",
        "val_state": "Select state",
        "val_zip": "",
        "val_adult": "Yes",
        "val_gpa": 3.5, # 🔧 Rounded default float tracker down to single decimal precision parameters
        "val_gpa_unknown": False,
        "val_lic": "None / Other",
        "val_exp": None,
        "val_dismiss": "No",
        "val_dismiss_mos": None,
        "val_travel": "Yes",
        "val_track": "BSN",
        "val_courses": [],
        "val_deposit": 0.0,
        "val_grant": 0.0,
        "val_promo": "No",
        "val_ref": "No",
        "val_mil": "No"
    }
    for key, value in defaults.items():
        if force_reset or key not in st.session_state:
            st.session_state[key] = value

# Run baseline memory hydration safely
initialize_base_states()

def execute_safe_restart():
    """Wipes session memory clean and instantly hits the breaker switch to prevent execution bleed crashes"""
    initialize_base_states(force_reset=True)
    st.rerun()

# ==============================================================================
# 2. DATA SOURCE IMPORT PIPELINE LOADER
# ==============================================================================
SCHOOLS_CSV = "schools.csv"
TRANSCRIPT_CSV = "transcript_rules.csv"

if os.path.exists(SCHOOLS_CSV):
    try: master_schools_df = pd.read_csv(SCHOOLS_CSV, encoding='utf-8')
    except Exception: master_schools_df = pd.read_csv(SCHOOLS_CSV, encoding='latin1', errors='replace')
    for col in master_schools_df.select_dtypes(include=['object']).columns:
        master_schools_df[col] = master_schools_df[col].astype(str).str.strip()
else:
    st.error("⚠️ Master database file schools.csv not found.")
    st.stop()

if os.path.exists(TRANSCRIPT_CSV):
    try: transcript_rules_df = pd.read_csv(TRANSCRIPT_CSV, encoding='utf-8')
    except Exception: transcript_rules_df = pd.read_csv(TRANSCRIPT_CSV, encoding='latin1', errors='replace')
    for col in transcript_rules_df.select_dtypes(include=['object']).columns:
        transcript_rules_df[col] = transcript_rules_df[col].astype(str).str.strip()
    transcript_rules_df.columns = transcript_rules_df.columns.str.strip()
else:
    st.error("⚠️ Transcript validation file transcript_rules.csv not found.")
    st.stop()

# ==============================================================================
# 3. GLOBAL LOOKUP PARAMETERS
# ==============================================================================
STATE_OPTIONS = [
    "Select state", "AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
    "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", 
    "MO", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", 
    "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI", "WV", "WY"
]
BINARY_OPTIONS = ["Yes", "No"]
DISMISSAL_OPTIONS = ["No", "Yes"]
LICENSE_OPTIONS = ["None / Other", "LPN", "CNA/CMA"]
TRACK_OPTIONS = ["BSN", "ASN"]

course_list = [
    "Eng Comp 1", "College Algebra", "Statistics", "Humanities 1", "Humanities 2", 
    "Humanities 3", "Human Growth & Development", "Psychology", "Sociology", "Speech", 
    "General Biology", "Chemistry", "Government", "History", "Foreign Language", 
    "Macro/Micro Economics", "Elective 1", "Elective 2"
]

current_step = st.session_state["wizard_step"]
is_finalized = st.session_state["confirmed_package"] is not None

# Dashboard Master Title Header
st.markdown("## 🗺️ Bridge Plan Generator")

# Compute Step Progress States Natively
if current_step == 1: s1_col, s1_w = "#1E3A8A", "bold"
else: s1_col, s1_w = "#10B981", "normal"

if current_step == 2: s2_col, s2_w = "#1E3A8A", "bold"
elif current_step > 2: s2_col, s2_w = "#10B981", "normal"
else: s2_col, s2_w = "#2563EB", "normal"

if current_step == 3: s3_col, s3_w = "#1E3A8A", "bold"
elif current_step > 3: s3_col, s3_w = "#10B981", "normal"
else: s3_col, s3_w = "#2563EB", "normal"

if is_finalized: s4_col, s4_w = "#10B981", "normal"
elif current_step == 4: s4_col, s4_w = "#1E3A8A", "bold"
else: s4_col, s4_w = "#2563EB", "normal"

st.markdown(
    f"""
    <div style="font-family: sans-serif; font-size: 15px; font-weight: 500; color: #475569; padding-bottom: 25px; padding-top: 5px;">
        <span style="color: {s1_col}; font-weight: {s1_w};">{'✅ ' if current_step>1 else ''}1. Identity Profile</span> 
        <span style="color: #cbd5e1;">&nbsp;&nbsp;➔&nbsp;&nbsp;</span>
        <span style="color: {s2_col}; font-weight: {s2_w};">{'✅ ' if current_step>2 else ''}2. Baseline Profile</span> 
        <span style="color: #cbd5e1;">&nbsp;&nbsp;➔&nbsp;&nbsp;</span>
        <span style="color: {s3_col}; font-weight: {s3_w};">{'✅ ' if current_step>3 else ''}3. Prerequisite Review</span> 
        <span style="color: #cbd5e1;">&nbsp;&nbsp;➔&nbsp;&nbsp;</span>
        <span style="color: {s4_col}; font-weight: {s4_w};">{'✅ ' if is_finalized else ''}4. School Matches</span>
    </div>
    """, 
    unsafe_allow_html=True
)

# Globally Scoped Admissions GATING DIALOG WINDOW MODULE
@st.dialog("Verify Entrance Exam Compliance")
def render_institutional_modal(school_name, school_exam_type, school_exam_notes, valid_courses_list, school_card_ref, school_unique_id):
    st.markdown(f"### 📋 Checking Gating for: **{school_name}**")
    st.markdown("---")
    
    modal_base_count = len(valid_courses_list)
    classes_waived = 0
    waived_course_name = ""
    user_score_logged = ""
    local_include_prep = False
    
    if school_exam_type in ["--", "", "nan"] or pd.isna(school_exam_type):
        st.info("ℹ️ Entrance testing validation controls waived for this partner track blueprint.")
        local_include_prep = False
    else:
        st.markdown(f"#### 🔒 Entrance Exam Compliance Gating")
        user_has_passed = st.radio(f"Have you already taken and passed the required **{school_exam_type}** exam?", ["No", "Yes"], horizontal=True, key="modal_has_passed_radio")
        
        if user_has_passed == "No":
            st.warning(f"⚠️ Notice: We have added the required **{school_exam_type} Prep Course** to your configuration bundle layout.")
            local_include_prep = st.checkbox(f"Keep **{school_exam_type} Prep Course** included in tuition bundle?", value=True, key="opt_out_chk_1")
        else:
            raw_input_score = st.text_input("Enter your official testing score number:", placeholder="e.g., 75 or 740")
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
                        st.error(f"🛑 Testing standard parameters report sub-admissions averages. Injecting **{school_exam_type} Prep Course** layout options.")
                        local_include_prep = st.checkbox(f"Keep **{school_exam_type} Prep Course** included in tuition bundle?", value=True, key="opt_out_chk_2")
                    elif matched_rule_type == "pass":
                        if age_limit_years:
                            st.markdown("##### ⏳ Verification Check Required:")
                            exam_age = st.slider(age_question_text, min_value=0, max_value=10, value=1)
                            if exam_age > age_limit_years:
                                st.error(f"🛑 Active testing score profile has expired. Pre-adding verification bundle.")
                                local_include_prep = True
                            else:
                                st.success(f"✅ Verified: Compliance testing variables remain valid and verified!")
                                local_include_prep = False
                        else:
                            st.success(f"✅ Verified: Gating layer parameters cleared safely.")
                            local_include_prep = False
                    elif matched_rule_type == "retest":
                        st.warning(f"⚠️ Registration parameters update checked. {custom_message}")
                        local_include_prep = st.checkbox(f"Add **{school_exam_type} Advanced Retest Prep** variables?", value=True, key="opt_out_chk_4")
                    elif matched_rule_type == "exempt":
                        st.success(f"🎉 Exemption waiver layer unlocked from **{waived_course_name}**.")
                        local_include_prep = False

    st.markdown("---")
    if st.button("🟢 OK", key="modal_ok_btn", use_container_width=True):
        st.session_state["modal_include_exam_prep"] = local_include_prep
        st.session_state["modal_score_logged"] = user_score_logged
        st.session_state["modal_classes_waived"] = classes_waived
        st.session_state["active_school_view"] = school_card_ref
        st.session_state["selected_school_id"] = school_unique_id
        st.rerun()

# Layout Splitting Setup
if current_step == 4:
    col_input_flow, col_ledger_flow = st.columns([1.5, 1.0], gap="large")
else:
    col_input_flow = st.container()
    col_ledger_flow = None

with col_input_flow:

    # --------------------------------------------------------------------------
    # STEP 1: IDENTITY PROFILE WORKSPACE
    # --------------------------------------------------------------------------
    if current_step == 1:
        st.subheader("Step 1: Identity Profile Parameters")
        st.markdown("Capture your residency parameters to parse localized regional partner program accessibility options.")
        st.divider()
        
        i_name = st.text_input("What is your name?", value=st.session_state["val_name"], placeholder="Enter full name", disabled=is_finalized)
        i_state = st.selectbox("Select your residency home state:", options=STATE_OPTIONS, index=STATE_OPTIONS.index(st.session_state["val_state"]), disabled=is_finalized)
        i_zip = st.text_input("What is your zip code?", value=st.session_state["val_zip"], placeholder="e.g. 19013", max_chars=14, disabled=is_finalized)
        i_adult = st.selectbox("Are you 18 years of age or older?", options=BINARY_OPTIONS, index=BINARY_OPTIONS.index(st.session_state["val_adult"]), disabled=is_finalized)
        
        i_gpa_unknown = st.checkbox("I don't know my cumulative GPA", value=st.session_state["val_gpa_unknown"], disabled=is_finalized)
        if i_gpa_unknown:
            # 🔑 REMOVED GHOST CHECKS: Force locks evaluation back into perfect 4.0 bounds automatically
            st.session_state["val_gpa"] = 4.0
            i_gpa = st.number_input("What is your current cumulative GPA Score?.", min_value=0.0, max_value=4.0, value=4.0, step=0.1, format="%.1f", disabled=True)
        else:
            # 🔑 ROUNDED PRECISION PARSER: Forces input masks down into clean 1-decimal view frameworks
            i_gpa = st.number_input("What is your current cumulative GPA Score?.", min_value=0.0, max_value=4.0, value=float(st.session_state["val_gpa"]), step=0.1, format="%.1f", disabled=is_finalized)
        
        st.divider()
        b_reset_col, b_spacer, b_continue_col = st.columns([1.0, 1.5, 1.0])
        with b_reset_col:
            if st.button("🔄 Restart Process", use_container_width=True, type="secondary", key="step1_reset_btn"):
                execute_safe_restart()
        with b_continue_col:
            if st.button("Continue ➡️", use_container_width=True, type="primary", key="step1_continue_action", disabled=is_finalized):
                if i_state == "Select state":
                    st.warning("⚠️ Please select a valid state territory before moving forward.")
                elif i_adult == "No":
                    st.error("🛑 Registration Blocked: Applicants under 18 require agent validation.")
                else:
                    st.session_state["val_name"] = i_name
                    st.session_state["val_state"] = i_state
                    st.session_state["val_zip"] = i_zip
                    st.session_state["val_adult"] = i_adult
                    st.session_state["val_gpa"] = i_gpa
                    st.session_state["val_gpa_unknown"] = i_gpa_unknown
                    st.session_state["wizard_step"] = 2
                    st.rerun()

    # --------------------------------------------------------------------------
    # STEP 2: PROFESSIONAL HEALTHCARE BACKGROUND
    # --------------------------------------------------------------------------
    elif current_step == 2:
        st.subheader("Step 2: Professional Licensing & History")
        st.markdown("Tell us about your healthcare background parameters to clear licensing experience rows.")
        st.divider()
        
        i_lic = st.selectbox("What is your current nursing license tier?", options=LICENSE_OPTIONS, index=LICENSE_OPTIONS.index(st.session_state["val_lic"]), disabled=is_finalized)
        i_exp = st.session_state["val_exp"]
        if i_lic == "LPN":
            i_exp = st.number_input("Total months of active LPN Work Experience:", min_value=0, max_value=120, value=st.session_state["val_exp"], step=1, placeholder="0", disabled=is_finalized)
            
        i_dismiss = st.selectbox("Do you possess a prior academic nursing program dismissal?", options=DISMISSAL_OPTIONS, index=DISMISSAL_OPTIONS.index(st.session_state["val_dismiss"]), disabled=is_finalized)
        i_dismiss_mos = st.session_state["val_dismiss_mos"]
        if i_dismiss == "Yes":
            i_dismiss_mos = st.number_input("Months elapsed since your historical academic dismissal date:", min_value=0, max_value=300, value=st.session_state["val_dismiss_mos"], step=1, placeholder="0", disabled=is_finalized)
            
        i_travel = st.selectbox("Are you amenable to regional clinical onsite travel loops?", options=BINARY_OPTIONS, index=BINARY_OPTIONS.index(st.session_state["val_travel"]), disabled=is_finalized)
        i_track = st.selectbox("Which nursing track are you targeting?", options=TRACK_OPTIONS, index=TRACK_OPTIONS.index(st.session_state["val_track"]), disabled=is_finalized)
        
        st.divider()
        b_reset_col, b_spacer, b_back_col, b_continue_col = st.columns([1.0, 0.5, 1.0, 1.0])
        with b_reset_col:
            if st.button("🔄 Restart Process", use_container_width=True, type="secondary", key="step2_reset_btn"):
                execute_safe_restart()
        with b_back_col:
            if st.button("⬅️ Back", use_container_width=True, key="step2_back_action", disabled=is_finalized):
                st.session_state["wizard_step"] = 1
                st.rerun()
        with b_continue_col:
            if st.button("Continue ➡️", use_container_width=True, type="primary", key="step2_continue_action", disabled=is_finalized):
                st.session_state["val_lic"] = i_lic
                st.session_state["val_exp"] = i_exp if i_exp is not None else 0
                st.session_state["val_dismiss"] = i_dismiss
                st.session_state["val_dismiss_mos"] = i_dismiss_mos if i_dismiss_mos is not None else 0
                st.session_state["val_travel"] = i_travel
                st.session_state["val_track"] = i_track
                st.session_state["wizard_step"] = 3
                st.rerun()

    # --------------------------------------------------------------------------
    # STEP 3: CREDIT TRANSCRIPT REVIEW CHECKLIST PANELS
    # --------------------------------------------------------------------------
    elif current_step == 3:
        st.subheader("Step 3: Foundational Transcript Review")
        st.markdown("Check off any credit course deficiencies you still need to fulfill through a partner track program.")
        st.divider()
        
        st.multiselect(
            "Check the boxes for courses you still NEED to complete:",
            options=course_list,
            default=st.session_state["val_courses"],
            key="temp_courses",
            disabled=is_finalized
        )
        st.session_state["val_courses"] = st.session_state["temp_courses"]
        
        st.markdown("#### **Promotional Qualifications & Discounts**")
        # 🔑 WIPE THE AGENT PARSER SLATE: Trimmed down phrasing parameter targets cleanly
        w_ref = st.radio("Were you referred by a student?", ["No", "Yes"], index=["No", "Yes"].index(st.session_state["val_ref"]), horizontal=True, disabled=is_finalized)
        w_mil = st.radio("Are you affiliated with the Military (Veteran/Active/Spouse)?", ["No", "Yes"], index=["No", "Yes"].index(st.session_state["val_mil"]), horizontal=True, disabled=is_finalized)
        
        st.session_state["val_ref"] = w_ref
        st.session_state["val_mil"] = w_mil
        st.session_state["addon_state"] = False

        st.divider()
        b_reset_col, b_spacer, b_back_col, b_continue_col = st.columns([1.0, 0.5, 1.0, 1.0])
        with b_reset_col:
            if st.button("🔄 Restart Process", use_container_width=True, type="secondary", key="step3_reset_btn"):
                execute_safe_restart()
        with b_back_col:
            if st.button("⬅️ Back", use_container_width=True, key="step3_back_action", disabled=is_finalized):
                st.session_state["wizard_step"] = 2
                st.rerun()
        with b_continue_col:
            if st.button("Find Matches ➡️", use_container_width=True, type="primary", key="step3_continue_action", disabled=is_finalized):
                st.session_state["wizard_step"] = 4
                st.rerun()

    # --------------------------------------------------------------------------
    # STEP 4: SECURE PARTNER BLUEPRINT INSTITUTION MATCHES
    # --------------------------------------------------------------------------
    elif current_step == 4:
        st.subheader("Secure Institutional Match Alignment")
        st.markdown("Review eligible program choices generated by your background profiles filter arrays:")
        st.divider()
        
        student_state = st.session_state["val_state"]
        selected_state = str(student_state).strip().upper()
        selected_track = str(st.session_state["val_track"]).strip().upper()
        license_type = st.session_state["val_lic"]
        lpn_exp = st.session_state["val_exp"] if st.session_state["val_exp"] is not None else 0
        gpa_val = st.session_state["val_gpa"]
        travel_ok = st.session_state["val_travel"]
        dismissal_y = True if st.session_state["val_dismiss"] == "Yes" else False
        dismissal_months = st.session_state["val_dismiss_mos"] if st.session_state["val_dismiss_mos"] is not None else 0
        needed_courses = st.session_state["val_courses"]

        working_schools_df = master_schools_df.copy()
        if "ASN/BSN" in working_schools_df.columns:
            working_schools_df = working_schools_df[working_schools_df["ASN/BSN"].str.upper() == selected_track]
        if "States Accepted" in working_schools_df.columns:
            working_schools_df = working_schools_df[working_schools_df["States Accepted"].str.upper().str.contains(selected_state)]
        if "LPN Required?" in working_schools_df.columns and license_type in ["None", "None / Other"]:
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

        if not filtered_df.empty:
            card_rows = []
            for idx, school_row in filtered_df.iterrows():
                raw_name = str(school_row["School Name"]).strip()
                if raw_name in ["", "nan"] or pd.isna(school_row["School Name"]):
                    raw_name = f"Partner Institution Platform Ref #{idx}"
                    
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
                
                unique_hash_id = f"sch_{idx}_{re.sub(r'[^a-zA-Z0-9]', '_', raw_name)}"
                
                card_rows.append({
                    "id": unique_hash_id,
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
                is_this_card_selected = (st.session_state["selected_school_id"] == card["id"])
                courses_text_string = ", ".join(card["accepted_courses"]) if card["accepted_courses"] else "None Required"
                
                if is_this_card_selected:
                    st.success(f"🎯 **{card['name']} (SELECTED)**")
                    st.markdown(f"**Degree Track Program:** `{card['track']}`")
                    st.markdown(f"🧬 *Deficiencies Fulfilled ({len(card['accepted_courses'])}):* **{courses_text_string}**")
                else:
                    with st.container(border=True):
                        st.markdown(f"### 🏫 {card['name']}")
                        s_left_col, s_right_col = st.columns([2.8, 1.2])
                        with s_left_col:
                            st.markdown(f"**Degree Track Program:** `{card['track']}`")
                            st.markdown(f"🧬 *Deficiencies Fulfilled ({len(card['accepted_courses'])}):* **{courses_text_string}**")
                        with s_right_col:
                            # 🔑 VARIABLE LABEL ALIGNMENT: Shifted text layout parameter indexes to "Estimated Cost"
                            st.metric(label="Estimated Cost", value=f"${card['profit']:,.2f}")
                
                btn_label = "✓ Active Selection Unlocked" if is_this_card_selected else "Select School & Fulfill Deficiencies"
                if st.button(btn_label, key=f"btn_card_sel_{card['id']}", use_container_width=True, type="secondary" if is_this_card_selected else "primary", disabled=is_finalized):
                    st.session_state["active_school_view"] = card
                    st.session_state["selected_school_id"] = card["id"]
                    render_institutional_modal(card["name"], card["exam"], card["notes"], card["accepted_courses"], card, card["id"])
                    
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.warning("No partner institutions match your background parameters configuration parameters.")
        
        st.divider()
        b_reset_col, b_spacer, b_back_col = st.columns([1.0, 1.5, 1.0])
        with b_reset_col:
            if st.button("🔄 Restart Process", use_container_width=True, type="secondary", key="step4_reset_btn"):
                execute_safe_restart()
        with b_back_col:
            if st.button("⬅️ Back to Review", use_container_width=True, key="step4_reverse_button_action", disabled=is_finalized):
                st.session_state["val_courses"] = list(st.session_state["val_courses"])
                st.session_state["wizard_step"] = 3
                st.rerun()

# --------------------------------------------------------------------------
# 🛒 sideBAR ITEMIZED INVOICE CART
# --------------------------------------------------------------------------
if col_ledger_flow is not None:
    with col_ledger_flow:
        st.subheader("🛒 Itemized Invoice Cart")
        
        if st.session_state["selected_school_id"] is None or st.session_state["active_school_view"] is None:
            st.info("👉 Please click 'Select School' on any partner institution row option on the left to verify compliance data and unlock itemized ledger statements calculations details.")
        else:
            needed_courses = st.session_state["active_school_view"]["accepted_courses"]
            school_name = st.session_state["active_school_view"]["name"]
            st.success(f"🎯 Target Locked: **{school_name}**")

            extra_exam_count = 1 if st.session_state.get("modal_include_exam_prep", False) else 0
            base_classes = len(needed_courses) + extra_exam_count
            total_classes = base_classes
            is_completely_empty = (total_classes == 0)
            
            m_classes_tier = base_classes if base_classes > 0 else 1
            main_price = 1179 if m_classes_tier >= 10 else (1229 if m_classes_tier >= 4 else 1289)
            base_total = base_classes * main_price
            
            st.markdown("#### Adjustments & Grants Parameters")
            deposit_input = st.number_input("Enrollment Deposit Amount ($)", min_value=0.0, value=st.session_state["val_deposit"], step=50.0, key="ledger_deposit_input_field", disabled=is_finalized)
            grant_input = st.number_input("Institutional Grant Amount ($)", min_value=0.0, value=st.session_state["val_grant"], step=50.0, key="ledger_grant_input_field", disabled=is_finalized)
            
            st.session_state["val_deposit"] = deposit_input
            st.session_state["val_grant"] = grant_input

            q_ref = st.session_state["val_ref"]
            q_mil = st.session_state["val_mil"]
            
            if len(needed_courses) >= 3:
                q_promo = st.radio("Do you possess a promotional code for a complimentary course?", ["No", "Yes"], index=["No", "Yes"].index(st.session_state["val_promo"]), horizontal=True, key="ledger_promo_radio", disabled=is_finalized)
                st.session_state["val_promo"] = q_promo
            else:
                st.session_state["val_promo"] = "No"
                q_promo = "No"

            calc_dep_match = min(deposit_input, 1000.0) if (deposit_input >= 300) else 0.0
            calc_referral = 50.0 if q_ref == "Yes" else 0.0
            calc_military = 200.0 if q_mil == "Yes" else 0.0
            calc_free_course = float(main_price) if (q_promo == "Yes" and len(needed_courses) >= 3) else 0.0
            
            credits_sum = calc_dep_match + calc_referral + calc_military + calc_free_course + grant_input
            final_total = max(0.0, base_total - credits_sum)

            st.divider()
            st.markdown(f"**Gross Base Tuition Balance:** `${0.00 if is_completely_empty else base_total:,.2f}`")
            
            st.markdown("##### 🎖️ Applied Fee Waivers & Adjustments:")
            if calc_dep_match > 0:
                st.markdown(f"🏷️ *Deposit Match Program Incentive:* `-${calc_dep_match:,.2f}`")
            if calc_referral > 0:
                st.markdown(f"🏷️ *Student Referral Credit:* `-${calc_referral:,.2f}`")
            if calc_military > 0:
                st.markdown(f"🏷️ *Active/Veteran Military Waiver:* `-${calc_military:,.2f}`")
            if calc_free_course > 0:
                st.markdown(f"🏷️ *Complimentary Course Promo Code:* `-${calc_free_course:,.2f}`")
            if grant_input > 0:
                st.markdown(f"🏷️ *Direct Institutional Grant Award:* `-${grant_input:,.2f}`")
            if credits_sum == 0:
                st.markdown("🏷️ *No programmatic credits applied to this profile context.*")
                
            st.markdown(f"**Total Consolidated Deductions:** `-${credits_sum:,.2f}`")
            st.markdown(f"## **Balance Due: ${0.00 if is_completely_empty else final_total:,.2f}**")
            
            st.divider()
            if st.button("🔒 Lock in Enrollment Package", key="ledger_final_lock_action_btn", use_container_width=True, type="primary", disabled=is_finalized):
                st.session_state["confirmed_package"] = {
                    "school_name": school_name,
                    "student_name": st.session_state["val_name"],
                    "base_total": base_total,
                    "reg_fee": 0.0,
                    "final_total": final_total,
                    "courses_included": needed_courses,
                    "entrance_exam_prep_added": st.session_state["modal_include_exam_prep"],
                    "entrance_exam_score_logged": st.session_state["modal_score_logged"],
                    "classes_waived_count": st.session_state["modal_classes_waived"],
                    "addons_active": False
                }
                st.rerun()

if is_finalized:
    pkg = st.session_state["confirmed_package"]
    st.balloons()
    st.success(f"🎉 **Bridge Plan Successfully Finalized for {pkg['student_name']}!**")
    st.markdown(f"### Selected School Locked: **{pkg['school_name']}**")
    st.metric("Final Bill Statement Due", f"${pkg['final_total']:,.2f}")
    with st.expander("📄 View Final Signed Voucher Audit Manifest Parameters"):
        st.json(pkg)
