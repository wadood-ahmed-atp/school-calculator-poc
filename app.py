import streamlit as st
import pandas as pd
import os
import re

# ==============================================================================
# 0. DESKTOP GRID & FIXED ENTERPRISE TOOLBAR REMOVALS
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
        "val_gpa": 4.00,
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

# Clean, Native Text Timelines Status Progress Tracker Bar
st.markdown(
    f"""
    <div style="font-family: sans-serif; font-size: 15px; font-weight: 500; color: #475569; padding-bottom: 25px; padding-top: 5px;">
        <span style="color: {'#1E3A8A' if current_step==1 else '#10B981'}; font-weight: {'bold' if current_step==1 else 'normal'};">{'✅ ' if current_step>1 else ''}1. Identity Profile</span> 
        <span style="color: #cbd5e1;">&nbsp;&nbsp;➔&nbsp;&nbsp;</span>
        <span style="color: {'#1E3A8A' if current_step==2 else ('#10B981' if current_step>2 else '#94a3b8')}; font-weight: {'bold' if current_step==2 else 'normal'};">{'✅ ' if current_step>2 else ''}2. Baseline Profile</span> 
        <span style="color: #cbd5e1;">&nbsp;&nbsp;➔&nbsp;&nbsp;</span>
        <span style="color: {'#1E3A8A' if current_step==3 else ('#10B981' if current_step>3 else '#94a3b8')}; font-weight: {'bold' if current_step==3 else 'normal'};">{'✅ ' if current_step>3 else ''}3. Transcripts Review</span> 
        <span style="color: #cbd5e1;">&nbsp;&nbsp;➔&nbsp;&nbsp;</span>
        <span style="color: {'#1E3A8A' if current_step==4 else '#10B981' if is_finalized else '#94a3b8'}; font-weight: {'bold' if current_step==4 else 'normal'};">{'✅ ' if is_finalized else ''}4. School Matches</span>
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
        st.info("ℹ️ Entrance testing validation controls bypassed for this partner track blueprint.")
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
