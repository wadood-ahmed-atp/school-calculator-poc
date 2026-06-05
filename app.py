import streamlit as st
import pandas as pd
import os
import re

# ==============================================================================
# 0. DESKTOP GRID & CUSTOM BUTTON CHECKBOX CSS INJECTIONS
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
        "val_gpa": 3.5, 
        "val_gpa_unknown": False,
        "val_lic": "None / Other",
        "val_exp": None, 
        "val_dismiss": "No",
        "val_dismiss_mos": None, 
        "val_travel": "Yes",
        "val_track": "BSN",
        "val_courses": [], # Array stores the custom string values toggled by button grids
        "val_deposit": 0, 
        "val_promo": "No",
        "val_ref": "No",
        "val_mil": "No",
        "customer_exam_prep_toggle": False 
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
@st.dialog("Reviewing Exam Requirements & Waivers")
def render_institutional_modal(school_name, school_exam_type, school_exam_notes, valid_courses_list, school_card_ref, school_unique_id):
    st.markdown(f"### 📋 Reviewing Exam Requirements & Waivers for: **{school_name}**")
    st.markdown("---")
    
    modal_base_count = len(valid_courses_list)
    classes_waived = 0
    waived_course_name = ""
    user_score_logged = ""
    
    if school_exam_type in ["--", "", "nan"] or pd.isna(school_exam_type):
        st.info("ℹ️ There are no entrance testing requirements for this specific nursing track configuration.")
        st.session_state["customer_exam_prep_toggle"] = False
    else:
        st.markdown(f"#### 🔒 Entrance Exam Verification")
        user_has_passed = st.radio(f"Have you already taken and passed the required **{school_exam_type}** exam?", ["No", "Yes"], horizontal=True, key="modal_has_passed_radio")
        
        if user_has_passed == "No":
            st.warning(f"⚠️ Note: A required **{school_exam_type} Prep Course** has been added to your preparation bundle.")
            st.checkbox(f"Keep **{school_exam_type} Prep Course** included in my cost estimate?", key="customer_exam_prep_toggle")
        else:
            raw_input_score = st.text_input("Enter your official score:", placeholder="e.g., 75 or 740")
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
                        st.error(f"🛑 This score is below the automatic waiver threshold. We've added a **{school_exam_type} Prep Course** to help you prepare.")
                        st.checkbox(f"Keep **{school_exam_type} Prep Course** included in my cost estimate?", key="customer_exam_prep_toggle")
                    elif matched_rule_type == "pass":
                        if age_limit_years:
                            st.markdown("##### ⏳ Verification Check:")
                            exam_age = st.slider(age_question_text, min_value=0, max_value=10, value=1)
                            if exam_age > age_limit_years:
                                st.error(f"🛑 Your test score has expired. Adding a refresher preparation course to your plan.")
                                st.session_state["customer_exam_prep_toggle"] = True
                            else:
                                st.success(f"✅ Verified: Your score is active and valid!")
                                st.session_state["customer_exam_prep_toggle"] = False
                        else:
                            st.success(f"✅ Verified: Entrance testing requirements successfully met!")
                            st.session_state["customer_exam_prep_toggle"] = False
                    elif matched_rule_type == "retest":
                        st.warning(f"⚠️ {custom_message}")
                        st.checkbox(f"Add **{school_exam_type} Advanced Retest Preparation** to your layout?", key="customer_exam_prep_toggle")
                    elif matched_rule_type == "exempt":
                        st.success(f"🎉 Exemption unlocked! You have successfully waived out of **{waived_course_name}**.")
                        st.session_state["customer_exam_prep_toggle"] = False

        st.markdown("---")
        extra_class_modifier = 1 if st.session_state["customer_exam_prep_toggle"] else 0
        computed_classes_count = modal_base_count + extra_class_modifier
        
        m_classes_tier = computed_classes_count if computed_classes_count > 0 else 1
        m_price_tier = 1179 if m_classes_tier >= 10 else (1229 if m_classes_tier >= 4 else 1289)
        final_base_total = int(computed_classes_count * m_price_tier)
        
        calc_dep_match = min(int(st.session_state["val_deposit"]), 1000) if (st.session_state["val_deposit"] >= 300) else 0
        calc_referral = 50 if st.session_state["val_ref"] == "Yes" else 0
        calc_military = 200 if st.session_state["val_mil"] == "Yes" else 0
        calc_free_course = m_price_tier if (st.session_state["val_promo"] == "Yes" and modal_base_count >= 3) else 0
        modal_credits_sum = calc_dep_match + calc_referral + calc_military + calc_free_course
        modal_final_total = max(0, final_base_total - modal_credits_sum)

        st.metric("Estimated Base Tuition", f"${final_base_total:,}")
        st.metric("Estimated Balance Due", f"${modal_final_total:,}")

    if st.button("🟢 OK", key="modal_ok_btn", use_container_width=True):
        st.session_state["modal_include_exam_prep"] = st.session_state["customer_exam_prep_toggle"]
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
        st.subheader("Step 1: Contact & Residency Details")
        st.markdown("Let's start with where you live so we can find the right nursing programs available in your area.")
        st.divider()
        
        i_name = st.text_input("What is your name?", value=st.session_state["val_name"], placeholder="Enter full name", disabled=is_finalized)
        i_state = st.selectbox("Select your home state:", options=STATE_OPTIONS, index=STATE_OPTIONS.index(st.session_state["val_state"]), disabled=is_finalized)
        i_zip = st.text_input("What is your zip code?", value=st.session_state["val_zip"], placeholder="e.g. 19013", max_chars=14, disabled=is_finalized)
        i_adult = st.selectbox("Are you 18 years of age or older?", options=BINARY_OPTIONS, index=BINARY_OPTIONS.index(st.session_state["val_adult"]), disabled=is_finalized)
        
        i_gpa_unknown = st.checkbox("I don't know my cumulative GPA", value=st.session_state["val_gpa_unknown"], disabled=is_finalized)
        if i_gpa_unknown:
            st.session_state["val_gpa"] = 4.0
            st.number_input("What is your current cumulative GPA Score?.", min_value=0.0, max_value=4.0, value=4.0, step=0.1, format="%.1f", disabled=True)
            i_gpa = 4.0
        else:
            i_gpa = st.number_input("What is your current cumulative GPA Score?.", min_value=0.0, max_value=4.0, value=float(st.session_state["val_gpa"]), step=0.1, format="%.1f", disabled=is_finalized)
        
        st.divider()
        
        if str(i_state).strip().upper() == "AZ":
            st.error("I apologize, but based on the current program availability and state restrictions, there are unfortunately no online nursing school options available in your state at this time, so let's look at a local opportunity to earn your degree.")
            if st.button("🔄 Restart Process", type="secondary", key="az_step1_reset_btn"):
                execute_safe_restart()
        else:
            b_reset_col, b_spacer, b_continue_col = st.columns([1.0, 1.5, 1.0])
            with b_reset_col:
                if st.button("🔄 Restart Process", use_container_width=True, type="secondary", key="step1_reset_btn"):
                    execute_safe_restart()
            with b_continue_col:
                if st.button("Continue ➡️", use_container_width=True, type="primary", key="step1_continue_action", disabled=is_finalized):
                    if i_state == "Select state":
                        st.warning("⚠️ Please select your home state before continuing.")
                    elif i_adult == "No":
                        st.error("🛑 Registration Blocked: Applicants under 18 require manual admissions review.")
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
    # STEP 2: PROFESSIONAL HEALTHCARE BACKGROUND & TRACK ALIGNMENT CHECK
    # --------------------------------------------------------------------------
    elif current_step == 2:
        st.subheader("Step 2: Professional Licensing & History")
        st.markdown("Tell us a bit about your healthcare background so we can match you with programs that fit your experience.")
        st.divider()
        
        i_lic = st.selectbox("What is your current nursing license tier?", options=LICENSE_OPTIONS, index=LICENSE_OPTIONS.index(st.session_state["val_lic"]), disabled=is_finalized)
        i_exp = st.session_state["val_exp"]
        if i_lic == "LPN":
            i_exp = st.number_input("Total months of active LPN Work Experience:", min_value=0, max_value=120, value=i_exp, step=1, placeholder="0", disabled=is_finalized)
            
        i_dismiss = st.selectbox("Have you ever been dismissed from a nursing program in the past?", options=DISMISSAL_OPTIONS, index=DISMISSAL_OPTIONS.index(st.session_state["val_dismiss"]), disabled=is_finalized)
        i_dismiss_mos = st.session_state["val_dismiss_mos"]
        if i_dismiss == "Yes":
            i_dismiss_mos = st.number_input("Months elapsed since that dismissal date:", min_value=0, max_value=300, value=i_dismiss_mos, step=1, placeholder="0", disabled=is_finalized)
            
        i_travel = st.selectbox("Are you willing to travel regionally for clinical rotations?", options=BINARY_OPTIONS, index=BINARY_OPTIONS.index(st.session_state["val_travel"]), disabled=is_finalized)
        i_track = st.selectbox("Which degree program track are you targeting?", options=TRACK_OPTIONS, index=TRACK_OPTIONS.index(st.session_state["val_track"]), disabled=is_finalized)

        cust_state = str(st.session_state["val_state"]).strip().upper()
        state_schools = master_schools_df[master_schools_df["States Accepted"].str.upper().str.contains(cust_state, na=False)]
        has_state_bsn = not state_schools[state_schools["ASN/BSN"].str.upper() == "BSN"].empty
        has_state_asn = not state_schools[state_schools["ASN/BSN"].str.upper() == "ASN"].empty

        st.divider()
        
        if i_track == "ASN" and has_state_bsn and not has_state_asn:
            st.info("💡 **Important Regional Notice:**\n\nThere is no online ADN bridge option available in your state. However, there are online BSN options. Going straight for the BSN can help maximize your career potential, especially if your goal is to work in a hospital, since many hospitals prefer or require BSN-prepared RNs. It also allows you to work toward becoming a BSN, RN through one school. Would you like to review the online Bachelor's option?")
            
            y_col, n_col = st.columns(2)
            with y_col:
                if st.button("Yes, review the BSN option", use_container_width=True, type="primary", key="inter_yes_bsn"):
                    st.session_state["val_lic"] = i_lic
                    st.session_state["val_exp"] = int(i_exp) if i_exp is not None else 0
                    st.session_state["val_dismiss"] = i_dismiss
                    st.session_state["val_dismiss_mos"] = int(i_dismiss_mos) if i_dismiss_mos is not None else 0
                    st.session_state["val_travel"] = i_travel
                    st.session_state["val_track"] = "BSN" 
                    st.success("🎉 Great choice! Switching your target option over to BSN...")
                    st.session_state["wizard_step"] = 3
                    st.rerun()
            with n_col:
                if st.button("No, thank you", use_container_width=True, key="inter_no_bsn"):
                    st.warning("Let's look at a local degree option.")

        elif i_track == "BSN" and has_state_asn and not has_state_bsn:
            st.info("💡 **Important Regional Notice:**\n\nI think earning your BSN is very important. However, in your state there is not a direct BSN bridge available. What I recommend most of my nurses do is get their RN by earning the Associate degree first, then bridge from RN to BSN, and we can make this feel like one seamless program. This way, you will be able to sit for your boards much sooner, start working as an RN, earn RN pay, and gain RN experience much sooner. That extra income could be helpful to then pursue your BSN. Knowing what you know now, would you like to start with the ADN first?")
            
            y_col, n_col = st.columns(2)
            with y_col:
                if st.button("Yes, start with the ADN first", use_container_width=True, type="primary", key="inter_yes_asn"):
                    st.session_state["val_lic"] = i_lic
                    st.session_state["val_exp"] = int(i_exp
