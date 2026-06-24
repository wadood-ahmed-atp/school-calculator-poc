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
        "val_adult": "No Selection",
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
        "expired_sciences_set": [],
        
        "attended_college_before": "No",
        "selected_prior_institutions": [],
        "institutions_accreditation_map": {},
        "is_transfer_eligible": True,
        "course_grades_map": {},
        
        "other_school_custom_name": ""
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
def load_and_sanitize_source_data(schools_path, rules_path, accreditation_path):
    """Loads CSV files into rapid RAM memory cache and auto-trims string column whitespace boundaries"""
    if not os.path.exists(schools_path) or not os.path.exists(rules_path):
        return None, None, None
        
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
    
    accred_df = None
    if os.path.exists(accreditation_path):
        try:
            accred_df = pd.read_csv(accreditation_path, encoding='utf-8', usecols=['INSTNM', 'ACCREDAGENCY'])
        except Exception:
            accred_df = pd.read_csv(accreditation_path, encoding='latin1', errors='replace', usecols=['INSTNM', 'ACCREDAGENCY'])
        accred_df['INSTNM'] = accred_df['INSTNM'].astype(str).str.strip()
        accred_df['ACCREDAGENCY'] = accred_df['ACCREDAGENCY'].astype(str).str.strip()
    
    return schools_df, rules_df, accred_df

master_schools_df, transcript_rules_df, regional_accreditation_df = load_and_sanitize_source_data(
    "schools.csv", "transcript_rules.csv", "Regionally_Accredited_Institution.csv"
)

if master_schools_df is None or transcript_rules_df is None:
    st.error("⚠️ Master CSV data files could not be successfully loaded into RAM.")
    st.stop()

# ==============================================================================
# 3. GLOBAL MATRIX REPOSITORIES & DEFINITIONS
# ==============================================================================
REGIONAL_AGENCIES = {
    "Southern Association of Colleges and Schools Commission on Colleges",
    "Higher Learning Commission",
    "Northwest Commission on Colleges and Universities",
    "Western Association of Schools and Colleges Accrediting Commission for Community and Junior Colleges",
    "Western Association of Schools and Colleges Senior Colleges and University Commission",
    "New England Commission on Higher Education",
    "Middle States Commission on Higher Education"
}

STATE_OPTIONS = [
    "Select state", "AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
    "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", 
    "MO", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", 
    "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI", "WV", "WY"
]
BINARY_OPTIONS = ["Yes", "No"]
DISMISSAL_OPTIONS = ["No", "Yes"]
LICENSE_OPTIONS = ["None / Other", "LPN", "ASN"]
TRACK_OPTIONS = ["BSN", "ASN"]
GRADE_OPTIONS = ["A", "B", "C", "D", "F"]

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

SCIENCE_COURSES_SET = {"Biology", "Chemistry", "Microbiology", "AP1", "AP2", "Statistics"}
SCIENCE_COURSES_LABEL_MAPPING = {
    "AP1": "Anatomy & Physiology I (A&P I)",
    "AP2": "Anatomy & Physiology II (A&P II)",
    "Microbiology": "Microbiology",
    "Biology": "Biology",
    "Chemistry": "Chemistry",
    "Statistics": "Statistics"
}

current_step = st.session_state["wizard_step"]
is_finalized = st.session_state["confirmed_package"] is not None

st.markdown("<h1 style='padding-top: 0px; margin-top: -10px; font-family: sans-serif; font-size: 32px; font-weight: 700; color: #1E3A8A;'>🧮 Bridge Plan Generator</h1>", unsafe_allow_html=True)

s_cols = ["#10B981" if current_step > i else ("#1E3A8A" if current_step == i else "#2563EB") for i in range(1, 9)]
s_whts = ["bold" if current_step == i else "normal" for i in range(1, 9)]

st.markdown(
    f"""
    <div style="font-family: sans-serif; font-size: 12px; font-weight: 500; color: #475569; padding-bottom: 25px; padding-top: 5px;">
        <span style="color: #get_s_cols(1); font-weight: {s_whts[0]};">1. Profile</span> <span style="color: #cbd5e1;">➔</span>
        <span style="color: #get_s_cols(2); font-weight: {s_whts[1]};">2. Licensing</span> <span style="color: #cbd5e1;">➔</span>
        <span style="color: #get_s_cols(3); font-weight: {s_whts[2]};">3. Transcript</span> <span style="color: #cbd5e1;">➔</span>
        <span style="color: #get_s_cols(4); font-weight: {s_whts[3]};">4. Schools</span> <span style="color: #cbd5e1;">➔</span>
        <span style="color: #get_s_cols(5); font-weight: {s_whts[4]};">5. Support</span> <span style="color: #cbd5e1;">➔</span>
        <span style="color: #get_s_cols(6); font-weight: {s_whts[5]};">6. Entrance Exam</span> <span style="color: #cbd5e1;">➔</span>
        <span style="color: #get_s_cols(7); font-weight: {s_whts[6]};">7. Exit Exam</span> <span style="color: #cbd5e1;">➔</span>
        <span style="color: #get_s_cols(8); font-weight: {s_whts[7]};">8. Summary Receipt</span>
    </div>
    """.replace("#get_s_cols(1)", s_cols[0]).replace("#get_s_cols(2)", s_cols[1]).replace("#get_s_cols(3)", s_cols[2]).replace("#get_s_cols(4)", s_cols[3]).replace("#get_s_cols(5)", s_cols[4]).replace("#get_s_cols(6)", s_cols[5]).replace("#get_s_cols(7)", s_cols[6]).replace("#get_s_cols(8)", s_cols[7]), 
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
                    else:
                        st.session_state.update({"val_name": i_name, "val_state": i_state, "val_zip": i_zip, "val_gpa": i_gpa, "val_gpa_unknown": i_gpa_unknown, "wizard_step": 2})
                        st.rerun()

    # --------------------------------------------------------------------------
    # STEP 2: PROFESSIONAL BACKGROUND & EXPERIENCE WORKSPACE
    # --------------------------------------------------------------------------
    elif current_step == 2:
        st.subheader("Step 2: Professional Licensing & History")
        st.markdown("Tell us a bit about your healthcare background so we can match you with programs that fit your experience.")
        st.divider()
        
        i_lic = st.selectbox("What is your current nursing license tier?", options=LICENSE_OPTIONS, index=LICENSE_OPTIONS.index(st.session_state["val_lic"]), disabled=is_finalized)
        i_exp = st.session_state["val_exp"]
        if i_lic == "LPN":
            i_exp = st.number_input(
                "Total months of active LPN Work Experience:", 
                min_value=0, max_value=120, 
                value=st.session_state["val_exp"] if st.session_state["val_exp"] is not None else 0, 
                step=1, 
                placeholder="Enter experience in months",
                disabled=is_finalized
            )
        elif i_lic == "ASN":
            i_exp = st.number_input(
                "Total months of active RN Work Experience:", 
                min_value=0, max_value=120, 
                value=st.session_state["val_exp"] if st.session_state["val_exp"] is not None else 0, 
                step=1, 
                placeholder="Enter experience in months",
                disabled=is_finalized
            )
            
        i_dismiss = st.selectbox("Have you ever been dismissed from a nursing program in the past?", options=DISMISSAL_OPTIONS, index=DISMISSAL_OPTIONS.index(st.session_state["val_dismiss"]), disabled=is_finalized)
        i_dismiss_mos = st.session_state["val_dismiss_mos"]
        if i_dismiss == "Yes":
            i_dismiss_mos = st.number_input("Months elapsed since that dismissal date:", min_value=0, max_value=300, value=i_dismiss_mos if i_dismiss_mos is not None else 0, step=1, disabled=is_finalized)
            
        i_travel = st.selectbox("Are you willing to travel regionally for clinical rotations?", options=BINARY_OPTIONS, index=BINARY_OPTIONS.index(st.session_state["val_travel"]), disabled=is_finalized)
        i_track = st.selectbox("Which degree program track are you targeting?", options=TRACK_OPTIONS, index=TRACK_OPTIONS.index(st.session_state["val_track"]), disabled=is_finalized)

        user_target_state_token = str(st.session_state["val_state"]).strip().upper()
        
        has_state_bsn = False
        has_state_asn = False
        
        for idx, row in master_schools_df.iterrows():
            raw_accepted_string = str(row.get("States Accepted", "")).strip().upper()
            allowed_permission_set = {t.strip() for t in raw_accepted_string.split(",") if t.strip()}
            
            if user_target_state_token in allowed_permission_set:
                school_tier_track = str(row.get("ASN/BSN", "")).strip().upper()
                if "BSN" in school_tier_track:
                    has_state_bsn = True
                if "ASN" in school_tier_track:
                    has_state_asn = True

        st.divider()
        
        if i_track == "ASN" and has_state_bsn and not has_state_asn:
            st.info("💡 **Important Regional Notice:** There is no online ADN bridge option available in your state. However, there are online BSN choices available. Would you like to review the Bachelor's route?")
            y_col, n_col = st.columns(2)
            with y_col:
                if st.button("Yes, review the BSN option", use_container_width=True, type="primary"):
                    st.session_state.update({"val_lic": i_lic, "val_exp": i_exp, "val_dismiss": i_dismiss, "val_dismiss_mos": int(i_dismiss_mos) if i_dismiss_mos else 0, "val_travel": i_travel, "val_track": "BSN", "wizard_step": 3})
                    st.rerun()
            with n_col:
                if st.button("No, thank you", use_container_width=True): st.warning("Reviewing local options...")

        elif i_track == "BSN" and has_state_asn and not has_state_bsn:
            st.info("💡 **Important Regional Notice:** Direct online BSN paths are unavailable in your jurisdiction. We recommend starting with an online ASN first to sit for boards faster. Would you like to switch to ASN?")
            y_col, n_col = st.columns(2)
            with y_col:
                if st.button("Yes, start with the ADN first", use_container_width=True, type="primary"):
                    st.session_state.update({"val_lic": i_lic, "val_exp": i_exp, "val_dismiss": i_dismiss, "val_dismiss_mos": int(i_dismiss_mos) if i_dismiss_mos else 0, "val_travel": i_travel, "val_track": "ASN", "wizard_step": 3})
                    st.rerun()
            with n_col:
                if st.button("No, thank you", use_container_width=True): st.warning("Reviewing local options...")
        else:
            b_reset_col, b_spacer, b_back_col, b_continue_col = st.columns([1.0, 0.5, 1.0, 1.0])
            with b_reset_col:
                if st.button("🔄 Restart Process", use_container_width=True, type="secondary"): execute_safe_restart()
            with b_back_col:
                if st.button("⬅️ Back", use_container_width=True):
                    st.session_state["wizard_step"] = 1
                    st.rerun()
            with b_continue_col:
                if st.button("Continue ➡️", use_container_width=True, type="primary"):
                    st.session_state.update({"val_lic": i_lic, "val_exp": i_exp, "val_dismiss": i_dismiss, "val_dismiss_mos": int(i_dismiss_mos) if i_dismiss_mos else 0, "val_travel": i_travel, "val_track": i_track, "wizard_step": 3})
                    st.rerun()

    # --------------------------------------------------------------------------
    # STEP 3: REGIONAL ACCREDITATION & TRANSCRIPT INGESTION PIPELINE
    # --------------------------------------------------------------------------
    elif current_step == 3:
        st.subheader("Step 3: Academic History & Institutional Accreditation")
        st.markdown("Please input details regarding your prior college attendance so we can calculate transfer mapping logic.")
        st.divider()
        
        q_attend = st.radio(
            "Have you attended college before?", 
            ["No", "Yes"], 
            index=["No", "Yes"].index(st.session_state["attended_college_before"]), 
            horizontal=True
        )
        st.session_state["attended_college_before"] = q_attend
        
        if q_attend == "Yes":
            st.markdown("#### 🏫 Prior Institution Registry")
            st.caption("Select all universities or community colleges attended. You can search by keywords or select 'Other'.")
            
            institution_pool = ["Other"]
            if regional_accreditation_df is not None:
                institution_pool = sorted(list(regional_accreditation_df['INSTNM'].unique())) + ["Other"]
                
            selected_schools = st.multiselect(
                "Search and select your prior institutions:",
                options=institution_pool,
                default=st.session_state["selected_prior_institutions"]
            )
            st.session_state["selected_prior_institutions"] = selected_schools
            
            custom_school_name = st.session_state["other_school_custom_name"]
            if "Other" in selected_schools:
                custom_school_name = st.text_input(
                    "Please enter the school name", 
                    value=st.session_state["other_school_custom_name"],
                    placeholder="Type unlisted college or training facility name here..."
                ).strip()
                st.session_state["other_school_custom_name"] = custom_school_name
            else:
                st.session_state["other_school_custom_name"] = ""
            
            accred_map = {}
            regional_accredited_schools_found = []
            national_unaccredited_schools_found = []
            
            for school in selected_schools:
                if school == "Other":
                    reported_display_key = custom_school_name if custom_school_name else "Other Unlisted School"
                    accred_map[reported_display_key] = {"agency": "Other Provider", "type": "Nationally Accredited / Not Regionally Accredited"}
                    national_unaccredited_schools_found.append(reported_display_key)
                else:
                    school_clean_upper = str(school).strip().upper()
                    match_rows = regional_accreditation_df[regional_accreditation_df['INSTNM'].str.upper().str.contains(school_clean_upper, regex=False, na=False)]
                    
                    if not match_rows.empty:
                        agency = str(match_rows['ACCREDAGENCY'].values[0]).strip()
                        if agency in ["", "nan", "NA", "Blank", "EXEMPT", "Unknown"]:
                            accred_map[school] = {"agency": "Unknown", "type": "Nationally Accredited / Not Regionally Accredited"}
                            national_unaccredited_schools_found.append(school)
                        elif agency in REGIONAL_AGENCIES:
                            accred_map[school] = {"agency": agency, "type": "Regionally Accredited"}
                            regional_accredited_schools_found.append(school)
                        else:
                            accred_map[school] = {"agency": agency, "type": "Nationally Accredited / Not Regionally Accredited"}
                            national_unaccredited_schools_found.append(school)
                    else:
                        accred_map[school] = {"agency": "Unknown", "type": "Nationally Accredited / Not Regionally Accredited"}
                        national_unaccredited_schools_found.append(school)
                        
            st.session_state["institutions_accreditation_map"] = accred_map
            
            if selected_schools:
                if regional_accredited_schools_found:
                    st.session_state["is_transfer_eligible"] = True
                else:
                    st.session_state["is_transfer_eligible"] = False
            else:
                st.session_state["is_transfer_eligible"] = True

            if selected_schools:
                st.divider()
                
                if regional_accredited_schools_found and not national_unaccredited_schools_found:
                    st.info(f"🎓 **Transfer Credit Guidance:** Please select the courses you completed at {', '.join(regional_accredited_schools_found)}. These credits are used to generate the most accurate transfer and testing recommendations for participating school programs.")
                
                elif regional_accredited_schools_found and national_unaccredited_schools_found:
                    st.info(f"🎓 **Transfer Credit Guidance:** We identified coursework from both nationally and regionally accredited institutions. For recommendation purposes, please select only the courses completed at {', '.join(regional_accredited_schools_found)}, as these credits are the basis for the transfer and testing recommendations provided by this tool.")
                
                elif national_unaccredited_schools_found and not regional_accredited_schools_found:
                    st.warning("🎓 **Transfer Credit Notice:** The institution(s) you selected are not regionally accredited. Because credits from these schools are not commonly accepted by nursing programs, we cannot use them to generate transfer and testing recommendations within this tool.")
                    st.session_state["val_courses"] = []
                    st.session_state["course_grades_map"] = {}

                if regional_accredited_schools_found:
                    btn_all_col, btn_clear_col, btn_spacer = st.columns([1.2, 1.2, 3.0])
                    with btn_all_col:
                        if st.button("Select All Completed", use_container_width=True):
                            st.session_state["val_courses"] = list(course_list)
                            st.rerun()
                    with btn_clear_col:
                        if st.button("Clear All Selections", use_container_width=True):
                            st.session_state["val_courses"] = []
                            st.session_state["course_grades_map"] = {}
                            st.rerun()
                            
                    st.markdown("")
                    current_selections = set(st.session_state["val_courses"])
                    cols_per_row = 4
                    
                    for idx in range(0, len(course_list), cols_per_row):
                        row_courses = course_list[idx:idx+cols_per_row]
                        cols = st.columns(cols_per_row)
                        for i, course in enumerate(row_courses):
                            with cols[i]:
                                is_toggled = course in current_selections
                                btn_type = "primary" if is_toggled else "secondary"
                                btn_prefix = "✓ " if is_toggled else "+ "
                                
                                if st.button(f"{btn_prefix}{course}", key=f"gb_{course.replace(' ', '_')}", use_container_width=True, type=btn_type):
                                    if is_toggled: 
                                        current_selections.remove(course)
                                        if course in st.session_state["course_grades_map"]:
                                            del st.session_state["course_grades_map"][course]
                                    else: 
                                        current_selections.add(course)
                                    st.session_state["val_courses"] = list(current_selections)
                                    st.rerun()
                                    
                    if st.session_state["val_courses"]:
                        st.markdown("")
                        st.markdown(f"🎓 **Transfer Eligibility Guidance:** The following courses should only be selected if they were completed at {', '.join(regional_accredited_schools_found)} and you earned a grade of C or better, as this is the minimum grade most nursing programs require for transfer consideration.")
                        st.markdown("##### 🏅 Course Grade Assignments")
                        for course in sorted(st.session_state["val_courses"]):
                            current_grade = st.session_state["course_grades_map"].get(course, "A")
                            idx_g = GRADE_OPTIONS.index(current_grade)
                            chosen_g = st.selectbox(f"Letter Grade earned for {course}:", GRADE_OPTIONS, index=idx_g, key=f"grade_{course.replace(' ', '_')}")
                            st.session_state["course_grades_map"][course] = chosen_g
                            
                            if chosen_g in ["D", "F"]:
                                st.error(f"❌ To receive transfer credit consideration for this course, a minimum grade of C is required. Based on the information provided, this course will not be eligible for transfer.")
        else:
            st.session_state["selected_prior_institutions"] = []
            st.session_state["other_school_custom_name"] = ""
            st.session_state["institutions_accreditation_map"] = {}
            st.session_state["val_courses"] = []
            st.session_state["course_grades_map"] = {}
            st.session_state["is_transfer_eligible"] = True

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### **Savings & Promotional Codes**")
        w_ref = st.radio("Were you referred by a student?", ["No", "Yes"], index=["No", "Yes"].index(st.session_state["val_ref"]), horizontal=True, disabled=is_finalized)
        w_mil = st.radio("Are you affiliated with the Military?", ["No", "Yes"], index=["No", "Yes"].index(st.session_state["val_mil"]), horizontal=True, disabled=is_finalized)
        st.session_state.update({"val_ref": w_ref, "val_mil": w_mil})

        st.divider()
        b_reset_col, b_spacer, b_back_col, b_continue_col = st.columns([1.0, 0.5, 1.0, 1.0])
        with b_reset_col:
            if st.button("🔄 Restart Process", use_container_width=True, type="secondary"): execute_safe_restart()
        with b_back_col:
            if st.button("⬅️ Back", use_container_width=True):
                st.session_state["wizard_step"] = 2
                st.rerun()
        with b_continue_col:
            if st.button("Find Matches ➡️", use_container_width=True, type="primary"):
                if q_attend == "Yes" and not st.session_state["selected_prior_institutions"]:
                    st.warning("⚠️ Please select at least one institution or choose 'No' to prior attendance.")
                elif q_attend == "Yes" and "Other" in st.session_state["selected_prior_institutions"] and not st.session_state["other_school_custom_name"]:
                    st.error("🛑 **Validation Error:** Please enter the school name to save your 'Other' institution selection profile before continuing.")
                else:
                    st.session_state["wizard_step"] = 4
                    st.rerun()

    # --------------------------------------------------------------------------
    # STEP 4: INSTITUTIONAL SCHOOL MATCHES
    # --------------------------------------------------------------------------
    elif current_step == 4:
        st.subheader("Step 4: Your Eligible Matches")
        
        if st.session_state["attended_college_before"] == "Yes" and not st.session_state["is_transfer_eligible"]:
            st.error("The school(s) you attended are not regionally accredited. Based on current transfer policies, coursework from these institutions generally cannot be transferred toward the programs we evaluate. Because of this, we will not ask you additional questions about your completed coursework.")
            st.info("ℹ️ Proceeding with lead match profile layout using full base deficiencies parameters.")
        
        st.info(f"🎯 Current Selected Track: **{st.session_state['val_track']}** program options")
        st.divider()
        
        user_state_token = str(st.session_state["val_state"]).strip().upper()
        selected_track = str(st.session_state["val_track"]).strip().lower()
        license_type = st.session_state["val_lic"]
        lpn_exp = st.session_state["val_exp"]
        lpn_exp_val = int(lpn_exp) if lpn_exp is not None else 0
        gpa_val = round(float(st.session_state["val_gpa"]), 1)
        travel_ok = st.session_state["val_travel"]
        dismissal_y = (st.session_state["val_dismiss"] == "Yes")
        dismissal_months = int(st.session_state["val_dismiss_mos"]) if st.session_state["val_dismiss_mos"] is not None else 0
        
        completed_courses = set()
        if st.session_state["is_transfer_eligible"]:
            for course in st.session_state["val_courses"]:
                grade_earned = st.session_state["course_grades_map"].get(course, "A")
                if grade_earned in ["A", "B", "C"]:
                    completed_courses.add(course)
                    
        needed_deficiencies = [c for c in course_list if c not in completed_courses]

        card_rows = []
        if not master_schools_df.empty:
            for idx, school_row in master_schools_df.iterrows():
                s_state = str(school_row.get("School State", "")).strip().upper()
                raw_accepted_string = str(school_row.get("States Accepted", "")).strip().upper()
                allowed_permission_set = {t.strip() for t in raw_accepted_string.split(",") if t.strip()}
                
                if s_state != user_state_token and user_state_token not in allowed_permission_set:
                    continue
                    
                if str(school_row.get("ASN/BSN", "")).strip().lower() != selected_track:
                    continue
                    
                if "LPN Required?" in school_row:
                    is_lpn_only_school = str(school_row["LPN Required?"]).strip().lower() == "y"
                    if is_lpn_only_school and license_type == "None / Other":
                        continue
                        
                raw_name = str(school_row["School Name"]).strip()
                s_exam = str(school_row.get("Entrance Exam", "--")).strip()
                s_notes = str(school_row.get("Entrance Exam Notes", "")).strip()
                s_blanket = str(school_row.get("Blanket Statement", "")).strip()
                s_odt_rules = str(school_row.get("Science/Math ODTs", "")).strip()
                s_odt_notes = str(school_row.get("Science/Math ODT Notes", "")).strip()
                s_county = str(school_row.get("County", "")).strip().lower()
                
                if "HERZ" in raw_name.upper() or "HERI" in raw_name.upper():
                    rule_row = transcript_rules_df[transcript_rules_df["School Name"].str.upper().str.contains("HERZ|HERI", na=False)]
                elif "EXCEL" in raw_name.upper():
                    rule_row = transcript_rules_df[transcript_rules_df["School Name"].str.upper().str.contains("EXCEL", na=False)]
                else: 
                    rule_row = transcript_rules_df[transcript_rules_df["School Name"].str.upper() == raw_name.upper()]
                
                school_accepted_list = []
                has_all_courses = True
                
                if not rule_row.empty:
                    for required_course in needed_deficiencies:
                        if required_course == "Government History":
                            if str(rule_row['Government'].values[0]).strip().upper() == "Y" or str(rule_row['History'].values[0]).strip().upper() == "Y":
                                school_accepted_list.append(required_course)
                            else: has_all_courses = False
                        else:
                            check_course = course_mapping_bridge.get(required_course, required_course)
                            if check_course in rule_row.columns and str(rule_row[check_course].values[0]).strip().upper() == "Y":
                                school_accepted_list.append(required_course)
                            else: has_all_courses = False
                    s_status = "Perfect Match" if (not needed_deficiencies or has_all_courses) else "Missing Needed CBE Courses"
                else:
                    s_status = "Perfect Match"
                    school_accepted_list = list(needed_deficiencies)
                
                try:
                    inc_fee = int(school_row.get("In-County Tuition", 99999))
                    ins_fee = int(school_row.get("In-StateTuition", 99999))
                    out_fee = int(school_row.get("Out-of-State Tuition", 99999))
                except ValueError:
                    inc_fee, ins_fee, out_fee = 99999, 99999, 99999
                
                if s_county and s_county in str(st.session_state["val_zip"]).strip().lower():
                    base_cost_metric = inc_fee
                elif s_state == user_state_token:
                    base_cost_metric = ins_fee
                else:
                    base_cost_metric = out_fee
                
                raw_odt_options = [c.strip() for c in s_odt_rules.split(",")] if s_odt_rules and str(s_odt_rules).lower() not in ["", "nan", "--"] else []
                raw_odt_options = [c for c in raw_odt_options if c in school_accepted_list]
                
                unique_hash_id = f"sch_{idx}_{re.sub(r'[^a-zA-Z0-9]', '_', raw_name)}"
                card_rows.append({
                    "id": unique_hash_id, "idx": idx, "name": raw_name, "exam": s_exam, "notes": s_notes,
                    "blanket": s_blanket, "odt_rules": s_odt_rules, "odt_notes": s_odt_notes,
                    "track": school_row["ASN/BSN"], "status": s_status, "accepted_courses": school_accepted_list,
                    "cost_metric": base_cost_metric, "odt_count_weight": len(raw_odt_options),
                    "raw_state_val": s_state
                })
            
            card_rows = sorted(card_rows, key=lambda x: (0 if x["raw_state_val"] == user_state_token else 1, x["cost_metric"]))
            
        if card_rows:
            for card in card_rows:
                is_selected = (st.session_state["selected_school_id"] == card["id"])
                display_exam = card['exam'] if card['exam'] not in ["", "nan", "--"] else "Exempt / None"
                
                tests_list_html = "".join([f"<li style='margin-bottom: 2px;'>✓ {test_item}</li>" for test_item in card['accepted_courses']]) if card['accepted_courses'] else "<li>No tests required</li>"
                
                html_template_string = f"""
                <div style="border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; margin-bottom: 16px; font-family: sans-serif;">
                    <div style="display: flex; flex-direction: row; justify-content: space-between; align-items: flex-start; width: 100%;">
                        
                        <div style="flex: 1.1; min-width: 280px; padding-right: 20px;">
                            <h3 style="margin: 0px 0px 4px 0px; font-size: 22px; font-weight: 700; color: #1E3A8A;">🏫 {card['name']}</h3>
                            <p style="margin: 0px 0px 8px 0px; font-size: 13px; color: #475569;">
                                <b>Location footprint:</b> {card['raw_state_val']} &nbsp;|&nbsp; <b>Program Option:</b> {card['track']}
                            </p>
                            <h4 style="margin: 0px; color: #10B981; font-size: 19px; font-weight: 700;">Estimated Cost: ${card['cost_metric']:,}</h4>
                        </div>
                        
                        <div style="flex: 1.4; min-width: 420px;">
                            <p style="font-size: 11px; color: #64748B; font-weight: 700; text-transform: uppercase; margin: 0px 0px 8px 0px; letter-spacing: 0.5px;">
                                Plan Optimization Metrics
                            </p>
                            <div style="display: flex; flex-direction: row; gap: 12px; width: 100%; margin-bottom: 12px;">
                                
                                <div style="flex: 1; border-left: 2px solid #1E3A8A; padding-left: 10px; text-align: left;">
                                    <span style="display: block; font-size: 11px; color: #64748B; font-weight: 500; margin-bottom: 2px;">🎯 Program Match</span>
                                    <span style="display: block; font-size: 14px; color: #1E3A8A; font-weight: 700;">Compatible</span>
                                </div>
                                
                                <div style="flex: 1; border-left: 2px solid #1E3A8A; padding-left: 10px; text-align: left;">
                                    <span style="display: block; font-size: 11px; color: #64748B; font-weight: 500; margin-bottom: 2px;">📋 Entrance Exam</span>
                                    <span style="display: block; font-size: 14px; color: #1E3A8A; font-weight: 700;">{display_exam}</span>
                                </div>
                                
                                <div style="flex: 1; border-left: 2px solid #10B981; padding-left: 10px; text-align: left;">
                                    <span style="display: block; font-size: 11px; color: #64748B; font-weight: 500; margin-bottom: 2px;">🧬 Credits via CBE</span>
                                    <span style="display: block; font-size: 14px; color: #10B981; font-weight: 700;">{len(card['accepted_courses'])} Courses</span>
                                </div>
                                
                            </div>
                        </div>
                        
                    </div>
                    
                    <div style="margin-top: 14px; padding-top: 12px; border-top: 1px solid #F1F5F9; width: 100%;">
                        <span style="display: block; font-size: 11px; color: #64748B; font-weight: 700; text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.5px;">🎓 Eligible Transfer Tests</span>
                        <ul style="margin: 0px; padding-left: 0px; list-style-type: none; font-size: 13px; color: #334155; display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 4px 16px;">
                            {tests_list_html}
                        </ul>
                    </div>
                    
                </div>
                """
                st.html(html_template_string)
                    
                b_side1, b_side2 = st.columns([1.1, 1.4])
                with b_side1:
                    btn_lbl = "✓ Selection Unlocked" if is_selected else "Select Institution"
                    if st.button(btn_lbl, key=f"bc_{card['id']}", use_container_width=True, type="secondary" if is_selected else "primary"):
                        st.session_state.update({
                            "active_school_view": card, 
                            "selected_school_id": card["id"], 
                            "wizard_step": 5,
                            "exam_prep_manually_toggled": False 
                        })
                        st.rerun()
                with b_side2:
                    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
        else:
            st.warning("No online options match your filters at this time in your state location context.")
        
        st.divider()
        b_reset_col, b_spacer, b_back_col = st.columns([1.0, 1.5, 1.0])
        with b_reset_col:
            if st.button("🔄 Restart Process", use_container_width=True, type="secondary"): execute_safe_restart()
        with b_back_col:
            if st.button("⬅️ Back to Review", use_container_width=True):
                st.session_state["wizard_step"] = 3
                st.rerun()

    # --------------------------------------------------------------------------
    # STEP 5: GUIDED COURSE SUPPORT & TIME RECENT METRICS
    # --------------------------------------------------------------------------
    elif current_step == 5:
        card = st.session_state["active_school_view"]
        school_name = card["name"]
        school_id = card["id"]
        odt_rules_string = card["odt_rules"]
        odt_notes_string = card.get("odt_notes", "")
        
        is_skipping_evaluation = (st.session_state["attended_college_before"] == "Yes" and not st.session_state["is_transfer_eligible"])
        
        completed_courses = set()
        if st.session_state["is_transfer_eligible"]:
            for course in st.session_state["val_courses"]:
                if st.session_state["course_grades_map"].get(course, "A") in ["A", "B", "C"]:
                    completed_courses.add(course)
                    
        needed_deficiencies = [c for c in course_list if c not in completed_courses]
        
        if str(odt_notes_string).strip().lower() in ["", "nan", "--", "none"]:
            odt_notes_string = ""
            
        st.subheader("Step 5: Guided Course Support & Institutional Requirements")
        st.markdown(f"Reviewing academic support enhancements for target program path: **{school_name}**")
        st.divider()
        
        if card["blanket"] and str(card["blanket"]).lower() not in ["", "nan", "--"]:
            st.info(f"📋 **Institutional Policy Notice:**\n\n{card['blanket']}")
            
        user_completed_sciences = [c for c in course_list if c in completed_courses and c in SCIENCE_COURSES_SET]
        
        is_force_locked, is_pre_checked_only, rule_threshold_years, rule_display_message = False, False, 99, ""
        any_course_expired = False
        expired_sciences_this_run = []
        
        if odt_notes_string and ":" in odt_notes_string:
            try:
                parts = odt_notes_string.split(":")
                rule_threshold_years = int(re.sub(r"[^\d]", "", parts[0].strip()))
                policy_type = parts[1].strip().lower()
                rule_display_message = parts[2].strip()
            except Exception:
                rule_threshold_years = 99
                policy_type = "none"
        else:
            rule_threshold_years = 99
            policy_type = "none"

        allowed_recency_sciences_whitelist = set()
        if odt_rules_string and str(odt_rules_string).lower() not in ["", "nan", "--"]:
            allowed_recency_sciences_whitelist = {c.strip().upper() for c in odt_rules_string.split(",")}

        if not is_skipping_evaluation and user_completed_sciences and rule_threshold_years < 99:
            st.markdown("##### ⏳ Credit Recency Verification")
            st.caption(f"University Registry Policy Cutoff Enforced: Core prerequisites cannot be older than {rule_threshold_years} years.")
            
            for science_key in user_completed_sciences:
                if science_key.upper() in allowed_recency_sciences_whitelist:
                    friendly_name = SCIENCE_COURSES_LABEL_MAPPING.get(science_key, science_key)
                    state_lookup_key = f"science_years_elapsed_{science_key}"
                    
                    if state_lookup_key not in st.session_state:
                        st.session_state[state_lookup_key] = 1
                        
                    course_age_input = st.slider(
                        f"How many years ago did you complete your {friendly_name} course?", 
                        min_value=0, max_value=25, 
                        value=int(st.session_state[state_lookup_key]), 
                        key=f"slider_act_{science_key}"
                    )
                    st.session_state[state_lookup_key] = course_age_input
                    
                    if int(st.session_state[state_lookup_key]) > rule_threshold_years:
                        any_course_expired = True
                        expired_sciences_this_run.append(science_key)
                        if policy_type == "mandatory":
                            is_force_locked = True
                        elif policy_type == "recommended":
                            is_pre_checked_only = True
        else:
            if is_skipping_evaluation:
                st.warning("⚠️ Prerequisite recency validation and course age validations are bypassed for this account profile due to regional accreditation restrictions.")

        st.session_state["science_credits_expired"] = any_course_expired
        st.session_state["expired_sciences_set"] = expired_sciences_this_run

        triggered_odt_options = [c.strip() for c in odt_rules_string.split(",")] if odt_rules_string and str(odt_rules_string).lower() not in ["", "nan", "--"] else []
        active_odt_pool = set(needed_deficiencies).union(set(st.session_state["expired_sciences_set"]))
        triggered_odt_options = [c for c in triggered_odt_options if c in active_odt_pool]

        mandatory_remediation_items = [c for c in triggered_odt_options if c in st.session_state["expired_sciences_set"]]
        elective_support_items = [c for c in triggered_odt_options if c not in mandatory_remediation_items]

        if not triggered_odt_options:
            st.success("✅ Clean Path: No mandatory Optional Enrichment Support Bundles are required for this configuration.")
            st.session_state.update({"selected_odts": [], "odt_hydrated_for_school": school_id})
        else:
            if st.session_state.get("odt_hydrated_for_school") != school_id:
                st.session_state.update({"selected_odts": list(triggered_odt_options), "odt_hydrated_for_school": school_id})
                
            if mandatory_remediation_items:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("### 📌 Required Institutional Track Modalities")
                for formal_course in mandatory_remediation_items:
                    friendly_name = SCIENCE_COURSES_LABEL_MAPPING.get(formal_course, formal_course)
                    st.error(f"🛑 **{friendly_name}:** Based on this school's requirements, your course credit falls outside the accepted timeframe. This school does not accept a CBE for {friendly_name}, meaning a mandatory support module is required and has been automatically attached to your enrollment summary package.")

            if elective_support_items:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("### 🎓 Optional Enrichment Support Bundles")
                chosen_odts = list(mandatory_remediation_items)
                current_selections_set = set(st.session_state["selected_odts"])
                
                for formal_course in elective_support_items:
                    was_checked = formal_course in current_selections_set or is_pre_checked_only
                    if st.checkbox(formal_course, value=was_checked, key=f"odt_act_{formal_course}"):
                        chosen_odts.append(formal_course)
                st.session_state["selected_odts"] = chosen_odts
            else:
                st.session_state["selected_odts"] = list(mandatory_remediation_items)

        st.divider()
        b_back_col, b_spacer, b_continue_col = st.columns([1.0, 1.5, 1.0])
        with b_back_col:
            if st.button("⬅   Back to Schools", use_container_width=True):
                st.session_state["wizard_step"] = 4
                st.rerun()
        with b_continue_col:
            if st.button("Verify Entrance Exams ➡️", use_container_width=True, type="primary"):
                st.session_state["wizard_step"] = 6
                st.rerun()

    # --------------------------------------------------------------------------
    # STEP 6: STANDALONE ENTRANCE EXAM WORKSPACE
    # --------------------------------------------------------------------------
    elif current_step == 6:
        card = st.session_state["active_school_view"]
        school_name = card["name"]
        school_exam_type = card["exam"]
        raw_exam_rules = str(card.get("notes", "")).strip()
        
        st.subheader(f"Step 6: Reviewing Entrance Testing Requirements")
        st.markdown(f"Configuring standard entrance benchmarks for targeted program path: **{school_name}**")
        st.divider()
        
        if school_exam_type in ["--", "", "nan"] or pd.isna(school_exam_type):
            st.info("ℹ️ There are no entrance testing requirements for this specific nursing school.")
            st.session_state["modal_include_exam_prep"] = False
        else:
            st.markdown("#### 🔒 Entrance Exam Verification")
            
            radio_default_index = ["No", "Yes"].index(st.session_state["val_exam_passed_status"])
            st.radio(
                f"Have you already taken and passed the required **{school_exam_type}** exam?", 
                ["No", "Yes"], 
                index=radio_default_index, 
                horizontal=True, 
                key="entrance_radio_live_key",
                on_change=sync_entrance_radio_callback
            )
            
            user_has_passed = st.session_state["val_exam_passed_status"]
            
            if user_has_passed == "No":
                if st.session_state["modal_include_exam_prep"]:
                    st.warning(f"⚠️ Note: A required **{school_exam_type} Prep Course** has been added to your preparation bundle.")
                
                if not st.session_state["exam_prep_manually_toggled"]:
                    st.session_state["modal_include_exam_prep"] = True
                
                st.checkbox(
                    f"Keep **{school_exam_type} Prep Course** included in my cost estimate?", 
                    value=st.session_state["modal_include_exam_prep"], 
                    key="ex_prep_live_widget_key",
                    on_change=sync_exam_prep_state_callback
                )
            else:
                has_age_restriction = False
                age_threshold_years = 99
                age_question_string = "How many years ago did you sit for this entrance examination?"
                fail_remediation_label = f"{school_exam_type} Prep Course"
                
                if raw_exam_rules and raw_exam_rules != "nan":
                    rule_tokens = raw_exam_rules.split("|")
                    for token in rule_tokens:
                        token = token.strip()
                        if token.lower().startswith("age:"):
                            try:
                                age_segments = token.split(":")
                                age_threshold_years = int(age_segments[1].strip())
                                age_question_string = age_segments[2].strip()
                                has_age_restriction = True
                            except (ValueError, IndexError):
                                pass
                
                st.text_input(
                    f"Enter your official **{school_exam_type}** numerical score percentage:", 
                    value=st.session_state["modal_score_logged"], 
                    placeholder="e.g. 78.5", 
                    key="step6_score_live_key",
                    on_change=sync_entrance_score_callback
                )
                
                score_str = st.session_state["modal_score_logged"]
                
                if score_str:
                    try:
                        parsed_score = float(score_str)
                        is_score_passing = True
                        matched_action_text = ""
                        
                        if raw_exam_rules and raw_exam_rules != "nan":
                            rule_tokens = raw_exam_rules.split("|")
                            for token in rule_tokens:
                                token = token.strip()
                                if ":" in token and not token.lower().startswith("age:"):
                                    parts = token.split(":")
                                    range_part = parts[0].strip()
                                    status_part = parts[1].strip().lower()
                                    
                                    if "–" in range_part or "-" in range_part:
                                        range_part = range_part.replace("–", "-")
                                        bounds = range_part.split("-")
                                        low_b = float(bounds[0].strip())
                                        high_b = float(bounds[1].strip())
                                        if low_b <= parsed_score <= high_b:
                                            matched_action_text = parts[2].strip() if len(parts) > 2 else ""
                                            if status_part == "fail":
                                                is_score_passing = False
                                    elif range_part.endswith("+"):
                                        low_b = float(range_part.replace("+", "").strip())
                                        if parsed_score >= low_b:
                                            matched_action_text = parts[2].strip() if len(parts) > 2 else ""
                                            if status_part == "fail":
                                                is_score_passing = False
                        
                        if not is_score_passing:
                            st.session_state["modal_include_exam_prep"] = True
                            st.error(f"🛑 **Exam Remediation Mandatory:** Your score falls below the required threshold bracket. We have attached the recommended **{matched_action_text or fail_remediation_label}** to your plan layout.")
                        else:
                            st.session_state["modal_include_exam_prep"] = False
                            st.success(f"✅ Pass Threshold Met: Score criteria verified successfully.")
                            
                        if has_age_restriction:
                            st.markdown("---")
                            st.markdown("##### ⏳ Testing Currency Guardrail")
                            user_exam_age = st.slider(
                                age_question_string,
                                min_value=0, max_value=15,
                                value=int(st.session_state["exam_age_input_cache"]),
                                key="live_entrance_exam_age_slider"
                            )
                            st.session_state["exam_age_input_cache"] = user_exam_age
                            
                            if user_exam_age > age_threshold_years:
                                st.session_state["modal_include_exam_prep"] = True
                                st.error(f"⚠️ **Exam Age Requirement Exceeded:** Your exam certificate is older than the institution's accepted {age_threshold_years}-year cutoff limit. Testing criteria cannot be treated as valid, and an automated remediation track has been added to your checkout bill.")
                            else:
                                if is_score_passing:
                                    st.success(f"✅ Full Testing Validation Unlocked: Both score brackets and age windows are confirmed compliant.")
                    except ValueError:
                        st.warning("⚠️ Please input a valid numerical score representation to compile tracking matrices.")

        st.divider()
        b_back_col, b_spacer, b_continue_col = st.columns([1.0, 1.5, 1.0])
        with b_back_col:
            if st.button("⬅   Back to Guided Support", use_container_width=True):
                st.session_state["wizard_step"] = 5
                st.rerun()
        with b_continue_col:
            if st.button("Configure Exit Exams ➡️", use_container_width=True, type="primary"):
                st.session_state["wizard_step"] = 7
                st.rerun()

    # --------------------------------------------------------------------------
    # STEP 7: STANDALONE EXIT EXAM WORKSPACE
    # --------------------------------------------------------------------------
    elif current_step == 7:
        card = st.session_state["active_school_view"]
        st.subheader("Step 7: Exit Exam Preparation (NCLEX-RN Layout)")
        st.markdown("Ensure state licensing board compliance by attaching an advanced Exit Exam preparation structure.")
        st.divider()
        
        st.markdown("#### 🎓 Licensing Board Test Readiness")
        st.info("💡 **Academic Recommendation:** Attaching an advanced NCLEX-RN Prep Course ensures comprehensive review metrics before graduation and safeguards first-attempt passing percentages.")
        
        if not st.session_state["nclex_prep_manually_toggled"]:
            st.session_state["modal_include_nclex_prep"] = True
            
        st.checkbox(
            "Include NCLEX-RN Board Review Preparation Course inside my cost summary layout?",
            value=st.session_state["modal_include_nclex_prep"],
            key="nclex_prep_live_widget_key",
            on_change=sync_nclex_prep_state_callback
        )
        
        st.divider()
        b_back_col, b_spacer, b_continue_col = st.columns([1.0, 1.5, 1.0])
        with b_back_col:
            if st.button("⬅   Back to Entrance Exams", use_container_width=True):
                st.session_state["wizard_step"] = 6
                st.rerun()
        with b_continue_col:
            if st.button("Continue to Summary ➡️", use_container_width=True, type="primary"):
                st.session_state["wizard_step"] = 8
                st.rerun()

    # --------------------------------------------------------------------------
    # STEP 8: REVIEW SUMMARY SUMMARY RECEIPT TERMINAL
    # --------------------------------------------------------------------------
    elif current_step == 8:
        card = st.session_state["active_school_view"]
        st.subheader("Step 8: Final Package Summary Review")
        st.markdown("Please review your synchronized registration overview parameters below:")
        st.divider()
        
        with st.container(border=True):
            col_left_profile, col_right_path = st.columns(2, gap="medium")
            with col_left_profile:
                st.markdown("### 👤 Student Profile Overview")
                st.markdown(f"**Full Applicant Name:** `{st.session_state['val_name'] or 'Prospective Student'}`")
                st.markdown(f"**Targeted Degree Track:** `{card['track']}`")
                st.markdown(f"**Residency Jurisdiction:** `{st.session_state['val_state']}`")
            with col_right_path:
                st.markdown("### 🏫 Institutional Placement")
                st.markdown(f"**Target Institution Path:** `{card['name']}`")
                
                if card['exam'] != "--" and st.session_state["modal_score_logged"]:
                    exam_status_txt = f"✓ Analytics Score Logged: {st.session_state['modal_score_logged']}%"
                else:
                    exam_status_txt = "✓ Pass/Exempt Verified" if not st.session_state["modal_include_exam_prep"] else "⚠️ Prep Course Attached"
                    
                st.markdown(f"**Entrance Benchmark Requirement:** `{exam_status_txt if card['exam'] != '--' else 'Exempt / None'}`")
                nclex_status_txt = "⚠️ NCLEX Prep Course Included" if st.session_state["modal_include_nclex_prep"] else "❌ Excluded from Plan"
                st.markdown(f"**Board Exit Requirement:** `{nclex_status_txt}`")

        st.markdown("<br>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("### 🧬 Academic Parameter Configurations")
            if st.session_state.get("science_credits_expired"):
                st.error("🛑 **Policy Expiration Enforced:** Science prerequisites fall outside the school-approved recency window. Required track remediation modules have been locked into this plan layout.")
            st.markdown("<br>", unsafe_allow_html=True)
            
            count_testing_modalities = 0
            if card['exam'] != "--":
                count_testing_modalities += 1
            if st.session_state["modal_include_nclex_prep"]:
                count_testing_modalities += 1

            col_cbe, col_exams, col_odt = st.columns(3, gap="medium")
            
            with col_cbe:
                final_cbe_clean_list = [c for c in card["accepted_courses"] if c not in st.session_state.get("expired_sciences_set", [])]
                st.markdown(f"##### 🔹 Prerequisites via CBE ({len(final_cbe_clean_list)})")
                if final_cbe_clean_list:
                    for course_item in final_cbe_clean_list: st.markdown(f"✅ &nbsp; {course_item}")
                else: st.markdown("*No prerequisites selected for testing out.*")
                
            with col_exams:
                st.markdown(f"##### 📝 Testing & Board Prep Modalities ({count_testing_modalities})")
                testing_entries_rendered = 0
                if card['exam'] != "--":
                    if st.session_state["modal_include_exam_prep"]:
                        st.markdown(f"⚡ &nbsp; **{card['exam']} Entrance Prep**")
                        testing_entries_rendered += 1
                    else:
                        st.markdown(f"✓ &nbsp; *{card['exam']} Benchmark Met*")
                        testing_entries_rendered += 1
                if st.session_state["modal_include_nclex_prep"]:
                    st.markdown("🎓 &nbsp; **NCLEX-RN Board Exit Review**")
                    testing_entries_rendered += 1
                if testing_entries_rendered == 0:
                    st.markdown("*No custom entrance or board testing reviews required.*")
                    
            with col_odt:
                active_odts = st.session_state.get("selected_odts", [])
                # 🎯 UX INTERFACE TERMINOLOGY ALIGNED SEAMLESSLY
                st.markdown(f"##### 🎓 Enrichment Support Bundles Added ({len(active_odts)})")
                if active_odts:
                    for odt_item in active_odts: st.markdown(f"🚀 &nbsp; {odt_item}")
                else: st.markdown("*No enrichment support tracks selected.*")

        st.divider()
        if st.button("⬅   Adjust Parameters", use_container_width=True, disabled=is_finalized):
            st.session_state["wizard_step"] = 7
            st.rerun()

# ==============================================================================
# 🛒 STEP 8 ONLY: RIGHT-SIDE ITEMIZIED CHECKOUT LEDGER TERMINAL
# ==============================================================================
if col_ledger_flow is not None:
    with col_ledger_flow:
        st.subheader("🛒 Final Checkout Receipt")
        
        active_school = st.session_state["active_school_view"]
        school_name = active_school["name"]
        
        completed_courses = set()
        if st.session_state["is_transfer_eligible"]:
            for course in st.session_state["val_courses"]:
                if st.session_state["course_grades_map"].get(course, "A") in ["A", "B", "C"]:
                    completed_courses.add(course)
        needed_deficiencies = [c for c in course_list if c not in completed_courses]
        
        final_cbe_clean_list = [c for c in active_school["accepted_courses"] if c not in st.session_state.get("expired_sciences_set", [])]
        
        triggered_odt_options = [c.strip() for c in str(active_school.get("odt_rules", "")).split(",")] if active_school.get("odt_rules") else []
        active_odt_pool = set(needed_deficiencies).union(set(st.session_state["expired_sciences_set"]))
        triggered_odt_options = [c for c in triggered_odt_options if c in active_odt_pool]
        
        if st.session_state.get("science_credits_expired") and triggered_odt_options:
            active_odts = list(set(triggered_odt_options))
            st.session_state["selected_odts"] = active_odts
        else:
            active_odts = st.session_state.get("selected_odts", [])
            
        extra_exam_count = 1 if st.session_state["modal_include_exam_prep"] else 0
        extra_nclex_count = 1 if st.session_state["modal_include_nclex_prep"] else 0
        
        total_products = len(final_cbe_clean_list) + extra_exam_count + extra_nclex_count + len(active_odts)
        
        if total_products >= 10:
            prep_rate, odt_rate = 1179.0, 749.0
        elif total_products >= 4:
            prep_rate, odt_rate = 1229.0, 799.0
        else:
            prep_rate, odt_rate = 1289.0, 859.0
            
        gened_subtotal = len(final_cbe_clean_list) * prep_rate
        entrance_subtotal = extra_exam_count * prep_rate
        nclex_subtotal = extra_nclex_count * prep_rate
        base_total = int(gened_subtotal + entrance_subtotal + nclex_subtotal)
        
        total_odt_fees = int(len(active_odts) * odt_rate)
        
        st.markdown("#### Adjustments & Savings")
        st.session_state["val_deposit"] = 0
        q_ref, q_mil = st.session_state["val_ref"], st.session_state["val_mil"]
        
        st.radio("Do you possess a promotional code?", ["No", "Yes"], index=["No", "Yes"].index(st.session_state["val_promo"]), horizontal=True, disabled=is_finalized, key="val_promo_radio_step8")
        st.session_state["val_promo"] = st.session_state["val_promo_radio_step8"]
        
        calc_free_course, promo_tier_name = 0, ""
        if st.session_state["val_promo"] == "Yes":
            promo_input = st.text_input(
                "Enter promotional code:", 
                value=st.session_state["val_promo_code_input"], 
                placeholder="Enter code here", 
                disabled=is_finalized,
                key="live_promo_input_vault_key"
            ).strip()
            st.session_state["val_promo_code_input"] = promo_input
            
            if promo_input.upper() in ["FREECOURSE", "FREE COURSE"]:
                calc_free_course = int(prep_rate)
                promo_tier_name = f"FreeCourse_Model8_Tier_{total_products}"
                st.success(f"🎉 Code Approved! Discount (-${calc_free_course:,})")
            elif promo_input != "":
                st.error("❌ Invalid promotional code.")

        calc_referral = 50 if q_ref == "Yes" else 0
        calc_military = 200 if q_mil == "Yes" else 0
        credits_sum = calc_referral + calc_military + calc_free_course
        final_total = max(0, (base_total + total_odt_fees) - credits_sum)

        st.divider()
        st.markdown(f"**Gross Base Tuition Breakdown:**")
        
        if final_cbe_clean_list:
            st.markdown(f"📝 *Prerequisite Prep ({len(final_cbe_clean_list)}):* `${int(len(final_cbe_clean_list) * prep_rate):,}`")
        if extra_exam_count > 0:
            st.markdown(f"🔒 *{active_school['exam']} Entrance Prep (1):* `${int(prep_rate):,}`")
        if extra_nclex_count > 0:
            st.markdown(f"🎓 *NCLEX-RN Board Exit Review (1):* `${int(prep_rate):,}`")
            
        st.markdown(f"**Total Base Tuition:** `${base_total:,}`")
        st.caption(f"(Calculated flat item tier rate of ${int(prep_rate):,} each across {total_products - len(active_odts)} core modules)")
        
        if total_odt_fees > 0:
            # 🎯 UX FINANCES TERMINOLOGY UNIFIED TO PREVENT MENTAL FRICTION
            st.markdown(f"➕ **Enrichment Support Bundles ({len(active_odts)}):** `${total_odt_fees:,}`")
            st.caption(f"({len(active_odts)} Support Modules at ${int(odt_rate):,} each)")
        
        if credits_sum > 0:
            st.markdown("##### 🎖️ Levant Discounts Applied:")
            if calc_referral: st.markdown(f"🏷️ *Student Referral Credit:* `-${calc_referral:,}`")
            if calc_military: st.markdown(f"🏷️ *Active Duty / Veteran Waiver:* `-${calc_military:,}`")
            if calc_free_course: st.markdown(f"🏷️ *Complimentary Course Code:* `-${calc_free_course:,}`")
            st.markdown(f"**Total Savings:** `-${credits_sum:,}`")
            
        st.markdown(f"## **Balance Due: ${0 if (base_total==0 and total_odt_fees==0) else final_total:,}**")
        
        st.divider()
        
        st.markdown("##### 📄 Terms & Agreement")
        i_adult_check = st.checkbox(
            "I explicitly confirm that I am 18 years of age or older and legally eligible to sign this program registration agreement.",
            value=(st.session_state["val_adult"] == "Yes"),
            disabled=is_finalized
        )
        st.session_state["val_adult"] = "Yes" if i_adult_check else "No"
        
        if st.button("🔒 Lock in Enrollment Package", key="lock_package_btn", use_container_width=True, type="primary", disabled=is_finalized):
            if st.session_state["val_adult"] != "Yes":
                st.error("🛑 **Registration Gate Enforced:** You must explicitly confirm that you are 18 years of age or older to finalize this bridge plan contract purchase summary.")
            else:
                st.session_state["confirmed_package"] = {
                    "school_name": school_name, "student_name": st.session_state["val_name"],
                    "base_total": int(base_total), "odt_fees_added": int(total_odt_fees), "odt_courses_selected": active_odts,
                    "final_total": int(final_total), "courses_included": final_cbe_clean_list, "entrance_exam_prep_added": bool(extra_exam_count),
                    "exit_exam_prep_added": bool(extra_nclex_count), "entrance_exam_score_logged": st.session_state["modal_score_logged"], 
                    "classes_waived_count": st.session_state["modal_classes_waived"], "promo_tier_applied": promo_tier_name, "addons_active": bool(total_odt_fees > 0)
                }
                st.rerun()

if is_finalized:
    pkg = st.session_state["confirmed_package"]
    st.balloons()
    st.success(f"🎉 **Your Bridge Plan has been successfully finalized, {pkg['student_name']}!**")
    st.markdown(f"### School Selection Locked: **{pkg['school_name']}**")
    st.metric("Final Balance Due", f"${int(pkg['final_total']):,}")
    with st.expander("📄 View Your Signed Enrollment Summary Manifest"): st.json(pkg)
