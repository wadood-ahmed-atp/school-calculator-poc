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
# 1. PERMANENT STATE MEMORY INITIALIZATION
# ==============================================================================
def initialize_base_states(force_reset=False):
    """Safely handles pristine initialization of memory vaults without race conditions"""
    defaults = {
        "wizard_step": 1,
        "confirmed_package": None,
        "active_school_view": None,
        "selected_school_id": None,
        "modal_include_exam_prep": True, 
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
        "val_courses": [], 
        "val_deposit": 0, 
        "val_promo": "No",
        "val_promo_code_input": "", 
        "val_ref": "No",
        "val_mil": "No",
        "selected_odts": [],
        "odt_hydrated_for_school": None,
        "exam_prep_manually_toggled": False,
        "val_exam_passed_status": "No",
        "modal_include_nclex_prep": True,          
        "nclex_prep_manually_toggled": False,
        "science_credits_expired": False,
        "exam_age_input_cache": 0,
        "expired_sciences_set": [] 
    }
    for key, value in defaults.items():
        if force_reset or key not in st.session_state:
            st.session_state[key] = value

initialize_base_states()

def execute_safe_restart():
    """Wipes session memory clean and instantly hits the breaker switch to prevent execution bleed crashes"""
    initialize_base_states(force_reset=True)
    st.rerun()

# 🧠 INTERACTIVE STATE CALLBACK REPLICATORS
def sync_exam_prep_state_callback():
    """Bypasses garbage collection by archiving widget clicks directly to the session pool"""
    if "ex_prep_live_widget_key" in st.session_state:
        st.session_state["modal_include_exam_prep"] = st.session_state["ex_prep_live_widget_key"]
        st.session_state["exam_prep_manually_toggled"] = True

def sync_nclex_prep_state_callback():
    """Archives Step 7 NCLEX selections cleanly to protect state against navigation redraw wipes"""
    if "nclex_prep_live_widget_key" in st.session_state:
        st.session_state["modal_include_nclex_prep"] = st.session_state["nclex_prep_live_widget_key"]
        st.session_state["nclex_prep_manually_toggled"] = True

def sync_entrance_radio_callback():
    """Locks the entrance exam passed state radio selection firmly into memory cache"""
    if "entrance_radio_live_key" in st.session_state:
        st.session_state["val_exam_passed_status"] = st.session_state["entrance_radio_live_key"]

def sync_entrance_score_callback():
    """Saves revised test scores instantly to dynamic storage preventing fallback desyncs"""
    if "step6_score_live_key" in st.session_state:
        st.session_state["modal_score_logged"] = str(st.session_state["step6_score_live_key"]).strip()

# ==============================================================================
# 2. HIGH-SPEED MEMORY CACHE LOADING PIPELINE
# ==============================================================================
@st.cache_data(ttl=600)
def load_and_sanitize_source_data(schools_path, rules_path):
    """Loads CSV files into rapid RAM memory cache and auto-trims string column whitespace boundaries"""
    if not os.path.exists(schools_path) or not os.path.exists(rules_path):
        return None, None
        
    try:
        schools_df = pd.read_csv(schools_path, encoding='utf-8')
    except Exception:
        schools_df = pd.read_csv(schools_path, encoding='latin1', errors='replace')
        
    for col in schools_df.select_dtypes(include=['object']).columns:
        schools_df[col] = schools_df[col].astype(str).str.strip()
        
    try:
        rules_df = pd.read_csv(rules_path, encoding='utf-8')
    except Exception:
        rules_df = pd.read_csv(rules_path, encoding='latin1', errors='replace')
        
    for col in rules_df.select_dtypes(include=['object']).columns:
        rules_df[col] = rules_df[col].astype(str).str.strip()
    rules_df.columns = rules_df.columns.str.strip()
    
    return schools_df, rules_df

master_schools_df, transcript_rules_df = load_and_sanitize_source_data("schools.csv", "transcript_rules.csv")

if master_schools_df is None or transcript_rules_df is None:
    st.error("⚠️ Master CSV data files could not be successfully loaded into RAM.")
    st.stop()

# ==============================================================================
# 3. GLOBAL MATRIX REPOSITORIES & DEFINITIONS
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
    "Government History", "Foreign Language", "Macro/Micro Econ", "Biology", 
    "Chemistry", "Microbiology", "AP1", "AP2", "Pathophysiology", 
    "Elective 1", "Elective 2"
]

course_mapping_bridge = {
    "Human Growth & Development": "Human Growth & Development",
    "Biology": "Biology",
    "Chemistry": "Chemistry",
    "Microbiology": "Microbiology",
    "AP1": "AP1",
    "AP2": "AP2",
    "Pathophysiology": "Pathophysiology"
}

SCIENCE_COURSES_SET = {"Biology", "Chemistry", "Microbiology", "AP1", "AP2"}
SCIENCE_COURSES_LABEL_MAPPING = {
    "AP1": "Anatomy & Physiology I (A&P I)",
    "AP2": "Anatomy & Physiology II (A&P II)",
    "Microbiology": "Microbiology",
    "Biology": "Biology",
    "Chemistry": "Chemistry"
}

current_step = st.session_state["wizard_step"]
is_finalized = st.session_state["confirmed_package"] is not None

st.markdown("<h1 style='padding-top: 0px; margin-top: -10px; font-family: sans-serif; font-size: 32px; font-weight: 700; color: #1E3A8A;'>🧮 Bridge Plan Generator</h1>", unsafe_allow_html=True)

s_cols = ["#10B981" if current_step > i else ("#1E3A8A" if current_step == i else "#2563EB") for i in range(1, 9)]
s_whts = ["bold" if current_step == i else "normal" for i in range(1, 9)]

st.markdown(
    f"""
    <div style="font-family: sans-serif; font-size: 12px; font-weight: 500; color: #475569; padding-bottom: 25px; padding-top: 5px;">
        <span style="color: {s_cols[0]}; font-weight: {s_whts[0]};">{'✅ ' if current_step>1 else ''}1. Profile</span> <span style="color: #cbd5e1;">➔</span>
        <span style="color: {s_cols[1]}; font-weight: {s_whts[1]};">{'✅ ' if current_step>2 else ''}2. Licensing</span> <span style="color: #cbd5e1;">➔</span>
        <span style="color: {s_cols[2]}; font-weight: {s_whts[2]};">{'✅ ' if current_step>3 else ''}3. Transcript</span> <span style="color: #cbd5e1;">➔</span>
        <span style="color: {s_cols[3]}; font-weight: {s_whts[3]};">{'✅ ' if current_step>4 else ''}4. Schools</span> <span style="color: #cbd5e1;">➔</span>
        <span style="color: {s_cols[4]}; font-weight: {s_whts[4]};">{'✅ ' if current_step>5 else ''}5. Support</span> <span style="color: #cbd5e1;">➔</span>
        <span style="color: {s_cols[5]}; font-weight: {s_whts[5]};">{'✅ ' if current_step>6 else ''}6. Entrance Exam</span> <span style="color: #cbd5e1;">➔</span>
        <span style="color: {s_cols[6]}; font-weight: {s_whts[6]};">{'✅ ' if current_step>7 else ''}7. Exit Exam</span> <span style="color: #cbd5e1;">➔</span>
        <span style="color: {s_cols[7]}; font-weight: {s_whts[7]};">{'✅ ' if is_finalized else ''}8. Summary Receipt</span>
    </div>
    """, 
    unsafe_allow_html=True
)

if current_step == 8:
    col_input_flow, col_ledger_flow = st.columns([1.5, 1.0], gap="large")
else:
    col_input_flow, col_ledger_flow = st.container(), None

with col_input_flow:

    # --------------------------------------------------------------------------
    # STEP 1: IDENTITY PROFILE WORKSPACE
    # --------------------------------------------------------------------------
    if current_step == 1:
        st.subheader("Step 1: Contact & Residency Details")
        st.markdown("Let's start with where you live so we can find the right online nursing options available in your area.")
        st.divider()
        
        i_name = st.text_input("What is your name?", value=st.session_state["val_name"], placeholder="Enter full name", disabled=is_finalized)
        i_state = st.selectbox("Select your home state:", options=STATE_OPTIONS, index=STATE_OPTIONS.index(st.session_state["val_state"]), disabled=is_finalized)
        i_zip = st.text_input("What is your zip code?", value=st.session_state["val_zip"], placeholder="e.g. 19013", max_chars=14, disabled=is_finalized)
        i_adult = st.selectbox("Are you 18 years of age or older?", options=BINARY_OPTIONS, index=BINARY_OPTIONS.index(st.session_state["val_adult"]), disabled=is_finalized)
        
        i_gpa_unknown = st.checkbox("I don't know my cumulative GPA", value=st.session_state["val_gpa_unknown"], disabled=is_finalized)
        i_gpa = 4.0 if i_gpa_unknown else st.number_input("What is your current cumulative GPA Score?.", min_value=0.0, max_value=4.0, value=float(st.session_state["val_gpa"]), step=0.1, format="%.1f", disabled=is_finalized or i_gpa_unknown)
        
        st.divider()
        
        if str(i_state).strip().upper() == "AZ":
            st.error("I apologize, but based on the current program availability and state restrictions, there are unfortunately no online nursing school options available in your state at this time, so let's look at a local opportunity to earn your degree.")
            if st.button("🔄 Restart Process", type="secondary", key="az_step1_reset_btn"): execute_safe_restart()
        else:
            b_reset_col, b_spacer, b_continue_col = st.columns([1.0, 1.5, 1.0])
            with b_reset_col:
                if st.button("🔄 Restart Process", use_container_width=True, type="secondary", key="step1_reset_btn"): execute_safe_restart()
            with b_continue_col:
                if st.button("Continue ➡️", use_container_width=True, type="primary", disabled=is_finalized):
                    if i_state == "Select state":
                        st.warning("⚠️ Please select your home state before continuing.")
                    elif i_adult == "No":
                        st.error("🛑 Registration Blocked: Applicants under 18 require admissions review.")
                    else:
                        st.session_state.update({"val_name": i_name, "val_state": i_state, "val_zip": i_zip, "val_adult": i_adult, "val_gpa": i_gpa, "val_gpa_unknown": i_gpa_unknown, "wizard_step": 2})
                        st.rerun()

    # --------------------------------------------------------------------------
    # STEP 2: PROFESSIONAL BACKGROUND & TRACK CHECK
    # --------------------------------------------------------------------------
    elif current_step == 2:
        st.subheader("Step 2: Professional Licensing & History")
        st.markdown("Tell us a bit about your healthcare background so we can match you with programs that fit your experience.")
        st.divider()
        
        i_lic = st.selectbox("What is your current nursing license tier?", options=LICENSE_OPTIONS, index=LICENSE_OPTIONS.index(st.session_state["val_lic"]), disabled=is_finalized)
        i_exp = st.session_state["val_exp"]
        if i_lic == "LPN":
            i_exp = st.number_input("Total months of active LPN Work Experience:", min_value=0, max_value=120, value=i_exp if i_exp is not None else 0, step=1, disabled=is_finalized)
            
        i_
