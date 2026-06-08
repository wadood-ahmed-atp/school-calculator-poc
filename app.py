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
        "val_courses": [], 
        "val_deposit": 0, 
        "val_promo": "No",
        "val_promo_code_input": "", 
        "val_ref": "No",
        "val_mil": "No",
        "customer_exam_prep_toggle": False,
        "selected_odts": [],
        "odt_hydrated_for_school": None # Safety lock to avoid dropping selections on live view updates
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
# 3. GLOBAL LOOKUP PARAMETERS & DATA MAPPING BRIDGE
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
    "Humanities 3", "Human Growth & Dev", "Psychology", "Sociology", "Speech", 
    "General Biology", "Chemistry", "Government", "History", "Foreign Language", 
    "Macro/Micro Econ", "Elective 1", "Elective 2", "Microbiology", 
    "Anatomy & Physiology 1", "Anatomy & Physiology 2", "Pathophysiology"
]

course_mapping_bridge = {
    "Human Growth & Dev": "Human Growth &",
    "General Biology": "Biology",
    "Macro/Micro Econ": "Macro/Micro=Economics",
    "Anatomy & Physiology 1": "AP1",
    "Anatomy & Physiology 2": "AP2"
}

odt_translation_bridge = {
    "AP1": "Anatomy & Physiology 1",
    "AP2": "Anatomy & Physiology 2",
    "Microbiology": "Microbiology",
    "Pathophysiology": "Pathophysiology",
    "Chemistry": "Chemistry"
}

current_step = st.session_state["wizard_step"]
is_finalized = st.session_state["confirmed_package"] is not None

# Dashboard Master Title Header
st.markdown("## 🗺️ Bridge Plan Generator")

# Compute 7-Step Progress States Natively
if current_step == 1: s1_col, s1_w = "#1E3A8A", "bold"
else: s1_col, s1_w = "#10B981", "normal"

if current_step == 2: s2_col, s2_w = "#1E3A8A", "bold"
elif current_step > 2: s2_col, s2_w = "#10B981", "normal"
else: s2_col, s2_w = "#2563EB", "normal"

if current_step == 3: s3_col, s3_w = "#1E3A8A", "bold"
elif current_step > 3: s3_col, s3_w = "#10B981", "normal"
else: s3_col, s3_w = "#2563EB", "normal"

if current_step == 4: s4_col, s4_w = "#1E3A8A", "bold"
elif current_step > 4: s4_col, s4_w = "#10B981", "normal"
else: s4_col, s4_w = "#2563EB", "normal"

if current_step == 5: s5_col, s5_w = "#1E3A8A", "bold"
elif current_step > 5: s5_col, s5_w = "#10B981", "normal"
else: s5_col, s5_w = "#2563EB", "normal"

if current_step == 6: s6_col, s6_w = "#1E3A8A", "bold"
elif current_step > 6: s6_col, s6_w = "#10B981", "normal"
else: s6_col, s6_w = "#2563EB", "normal"

if is_finalized: s7_col, s7_w = "#10B981", "normal"
elif current_step == 7: s7_col, s7_w = "#1E3A8A", "bold"
else: s7_col, s7_w = "#2563EB", "normal"

st.markdown(
    f"""
    <div style="font-family: sans-serif; font-size: 13px; font-weight: 500; color: #475569; padding-bottom: 25px; padding-top: 5px;">
        <span style="color: {s1_col}; font-weight: {s1_w};">{'✅ ' if current_step>1 else ''}1. Profile</span> 
        <span style="color: #cbd5e1;">&nbsp;➔&nbsp;</span>
        <span style="color: {s2_col}; font-weight: {s2_w};">{'✅ ' if current_step>2 else ''}2. Licensing</span> 
        <span style="color: #cbd5e1;">&nbsp;➔&nbsp;</span>
        <span style="color: {s3_col}; font-weight: {s3_w};">{'✅ ' if current_step>3 else ''}3. Transcript</span> 
        <span style="color: #cbd5e1;">&nbsp;➔&nbsp;</span>
        <span style="color: {s4_col}; font-weight: {s4_w};">{'✅ ' if current_step>4 else ''}4. Schools</span>
        <span style="color: #cbd5e1;">&nbsp;➔&nbsp;</span>
        <span style="color: {s5_col}; font-weight: {s5_w};">{'✅ ' if current_step>5 else ''}5. Guided Support</span>
        <span style="color: #cbd5e1;">&nbsp;➔&nbsp;</span>
        <span style="color: {s6_col}; font-weight: {s6_w};">{'✅ ' if current_step>6 else ''}6. Entrance Exam</span>
        <span style="color: #cbd5e1;">&nbsp;➔&nbsp;</span>
        <span style="color: {s7_col}; font-weight: {s7_w};">{'✅ ' if is_finalized else ''}7. Summary Receipt</span>
    </div>
    """, 
    unsafe_allow_html=True
)

if current_step == 7:
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

        cust_state = str(st.session_state["val_state"]).strip().lower()
        state_schools = master_schools_df[master_schools_df["States Accepted"].str.lower().str.contains(cust_state, na=False)]
        has_state_bsn = not state_schools[state_schools["ASN/BSN"].str.lower().str.strip() == "bsn"].empty
        has_state_asn = not state_schools[state_schools["ASN/BSN"].str.lower().str.strip() == "asn"].empty

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
                    st.session_state["val_exp"] = int(i_exp) if i_exp is not None else 0
                    st.session_state["val_dismiss"] = i_dismiss
                    st.session_state["val_dismiss_mos"] = int(i_dismiss_mos) if i_dismiss_mos is not None else 0
                    st.session_state["val_travel"] = i_travel
                    st.session_state["val_track"] = "ASN" 
                    st.success("🎉 Great choice! Switching your target option over to ASN...")
                    st.session_state["wizard_step"] = 3
                    st.rerun()
            with n_col:
                if st.button("No, thank you", use_container_width=True, key="inter_no_asn"):
                    st.warning("Let's look at a local degree option.")

        else:
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
                    st.session_state["val_exp"] = int(i_exp) if i_exp is not None else 0
                    st.session_state["val_dismiss"] = i_dismiss
                    st.session_state["val_dismiss_mos"] = int(i_dismiss_mos) if i_dismiss_mos is not None else 0
                    st.session_state["val_travel"] = i_travel
                    st.session_state["val_track"] = i_track
                    st.session_state["wizard_step"] = 3
                    st.rerun()

    # --------------------------------------------------------------------------
    # STEP 3: PREREQUISITE BUTTON MATRIX SELECTION GRID
    # --------------------------------------------------------------------------
    elif current_step == 3:
        st.subheader("Step 3: Foundational Prerequisite Review")
        st.markdown("Select any general education or prerequisite courses you still need to complete:")
        st.divider()
        
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
                    
                    if st.button(f"{btn_prefix}{course}", key=f"gen_badge_{course.replace(' ', '_')}", use_container_width=True, type=btn_type, disabled=is_finalized):
                        if is_toggled:
                            current_selections.remove(course)
                        else:
                            current_selections.add(course)
                        st.session_state["val_courses"] = list(current_selections)
                        st.rerun()
                        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### **Savings & Promotional Codes**")
        w_ref = st.radio("Were you referred by a student?", ["No", "Yes"], index=["No", "Yes"].index(st.session_state["val_ref"]), horizontal=True, disabled=is_finalized)
        w_mil = st.radio("Are you affiliated with the Military (Veteran/Active/Spouse)?", ["No", "Yes"], index=["No", "Yes"].index(st.session_state["val_mil"]), horizontal=True, disabled=is_finalized)
        
        st.session_state["val_ref"] = w_ref
        st.session_state["val_mil"] = w_mil

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
    # STEP 4: INSTITUTIONAL SCHOOL MATCHES (PRISTINE ROBUST TRIMMING LAYER)
    # --------------------------------------------------------------------------
    elif current_step == 4:
        st.subheader("Step 4: Your Eligible Matches")
        st.markdown("Based on your background, here are the schools that best match your goals:")
        st.divider()
        
        student_state = st.session_state["val_state"]
        selected_state = str(student_state).strip().lower()
        selected_track = str(st.session_state["val_track"]).strip().lower()
        license_type = st.session_state["val_lic"]
        lpn_exp = int(st.session_state["val_exp"]) if st.session_state["val_exp"] is not None else 0
        gpa_val = round(float(st.session_state["val_gpa"]), 1)
        travel_ok = st.session_state["val_travel"]
        dismissal_y = True if st.session_state["val_dismiss"] == "Yes" else False
        dismissal_months = int(st.session_state["val_dismiss_mos"]) if st.session_state["val_dismiss_mos"] is not None else 0
        needed_courses = st.session_state["val_courses"]

        working_schools_df = master_schools_df.copy()
        
        # 🟢 SECURE MATCH ENGINE: Upgraded parsing using robust lower casing and strict trimming rules
        if "ASN/BSN" in working_schools_df.columns:
            working_schools_df = working_schools_df[working_schools_df["ASN/BSN"].str.lower().str.strip() == selected_track]
        if "States Accepted" in working_schools_df.columns:
            working_schools_df = working_schools_df[working_schools_df["States Accepted"].str.lower().str.contains(selected_state, na=False)]
        if "LPN Required?" in working_schools_df.columns and license_type in ["None", "None / Other"]:
            working_schools_df = working_schools_df[working_schools_df["LPN Required?"].astype(str).str.lower().str.strip() != "y"]
        if "Min Work Experience Required (mos)" in working_schools_df.columns:
            working_schools_df["Min Work Experience Required (mos)"] = pd.to_numeric(working_schools_df["Min Work Experience Required (mos)"], errors='coerce').fillna(0)
            working_schools_df = working_schools_df[working_schools_df["Min Work Experience Required (mos)"] <= lpn_exp]
        if "Min GPA" in working_schools_df.columns:
            working_schools_df["Min GPA"] = pd.to_numeric(working_schools_df["Min GPA"], errors='coerce').fillna(0.0)
            working_schools_df = working_schools_df[working_schools_df["Min GPA"] <= gpa_val]
        if "Clinical Travel?" in working_schools_df.columns and travel_ok == "No":
            travel_clean = working_schools_df["Clinical Travel?"].astype(str).str.lower().str.strip()
            working_schools_df = working_schools_df[travel_clean.isin(["no", "n", "none", "0"])]
        if "Prior Nursing Dismissal Policy" in working_schools_df.columns and dismissal_y:
            if dismissal_months <= 60:
                working_schools_df = working_schools_df[working_schools_df["Prior Nursing Dismissal Policy"].astype(str).str.lower().str.strip() != "does not accept"]

        filtered_df = working_schools_df.copy()

        if not filtered_df.empty:
            card_rows = []
            for idx, school_row in filtered_df.iterrows():
                raw_name = str(school_row["School Name"]).strip()
                if raw_name in ["", "nan"] or pd.isna(school_row["School Name"]):
                    raw_name = f"Partner Institution Platform Ref #{idx}"
                    
                s_exam = str(school_row.get("Entrance Exam", "--")).strip()
                s_notes = str(school_row.get("Entrance Exam Notes", "")).strip()
                s_blanket = str(school_row.get("Blanket Statement", "")).strip()
                s_odt_rules = str(school_row.get("Science/Math ODTs", "")).strip()
                
                if "HERZ" in raw_name.upper() or "HERI" in raw_name.upper():
                    rule_row = transcript_rules_df[transcript_rules_df["School Name"].str.upper().str.contains("HERZ|HERI", na=False)]
                elif "EXCEL" in raw_name.upper():
                    rule_row = transcript_rules_df[transcript_rules_df["School Name"].str.upper().str.contains("EXCEL", na=False)]
                else: rule_row = transcript_rules_df[transcript_rules_df["School Name"].str.upper() == raw_name.upper()]
                
                school_accepted_list = []
                has_all_courses = True
                
                if not rule_row.empty:
                    for required_course in needed_courses:
                        check_course = course_mapping_bridge.get(required_course, required_course)
                        if check_course in rule_row.columns:
                            if str(rule_row[check_course].values[0]).strip().upper() == "Y":
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
                    "blanket": s_blanket,
                    "odt_rules": s_odt_rules,
                    "track": school_row["ASN/BSN"],
                    "status": s_status,
                    "accepted_courses": school_accepted_list,
                    "profit": int(est_profit) 
                })
            
            card_rows = sorted(card_rows, key=lambda x: x["profit"], reverse=True)

            for card in card_rows:
                is_this_card_selected = (st.session_state["selected_school_id"] == card["id"])
                courses_text_string = ", ".join(card["accepted_courses"]) if card["accepted_courses"] else "None Required"
                
                with st.container(border=True):
                    st.markdown(f"### 🏫 {card['name']}")
                    st.markdown(f"**Degree Track Program:** `{card['track']}`")
                    st.markdown(f"🧬 *Prerequisites Fulfilled ({len(card['accepted_courses'])}):* **{courses_text_string}**")
                    
                    btn_label = "✓ Active Selection Unlocked" if is_this_card_selected else "Select School & Fulfill Prerequisites"
                    if st.button(btn_label, key=f"btn_card_sel_{card['id']}", use_container_width=True, type="secondary" if is_this_card_selected else "primary", disabled=is_finalized):
                        st.session_state["active_school_view"] = card
                        st.session_state["selected_school_id"] = card["id"]
                        st.session_state["wizard_step"] = 5
                        st.rerun()
                    
                st.markdown("<br>", unsafe_allow_html=True)
        else:
            st.warning("No institutions currently match your background profile selection filters.")
        
        st.divider()
        b_reset_col, b_spacer, b_back_col = st.columns([1.0, 1.5, 1.0])
        with b_reset_col:
            if st.button("🔄 Restart Process", use_container_width=True, type="secondary", key="step4_reset_btn"):
                execute_safe_restart()
        with b_back_col:
            if st.button("⬅️ Back to Review", use_container_width=True, key="step4_reverse_button_action", disabled=is_finalized):
                st.session_state["wizard_step"] = 3
                st.rerun()

    # --------------------------------------------------------------------------
    # STEP 5: DYNAMIC GUIDED COURSE SUPPORT TERMINAL (REFINED HEADERS & AUTO PRE-CHECK)
    # --------------------------------------------------------------------------
    elif current_step == 5:
        card = st.session_state["active_school_view"]
        school_name = card["name"]
        school_id = card["id"]
        blanket_statement = card["blanket"]
        odt_rules_string = card["odt_rules"]
        needed_courses = st.session_state["val_courses"]
        
        st.subheader("Step 5: Guided Course Support & Institutional Requirements")
        st.markdown(f"Reviewing academic support enhancements for target program path: **{school_name}**")
        st.divider()
        
        if blanket_statement and blanket_statement.lower() not in ["", "nan", "--"]:
            st.info(f"📋 **Institutional Policy Notice:**\n\n{blanket_statement}")
            
        core_sciences = ["Microbiology", "Anatomy & Physiology 1", "Anatomy & Physiology 2", "Pathophysiology"]
        user_needs_sciences = any(s in needed_courses for s in core_sciences)
        
        if "EXCEL" in school_name.upper() and user_needs_sciences:
            st.warning("⏳ **Excelsior 5-Year Recency Requirement:**\n\nExcelsior requires core science courses to have been completed within the past 5 years. Adding Guided Course Support is highly recommended to guarantee passing scores on your first attempt.")

        # Map spreadsheet items to code names
        triggered_odt_options = []
        if odt_rules_string and odt_rules_string.lower() not in ["", "nan", "--"]:
            school_odt_list = [c.strip() for c in odt_rules_string.split(",")]
            for raw_csv_item in school_odt_list:
                translated_label = odt_translation_bridge.get(raw_csv_item, raw_csv_item)
                if translated_label in needed_courses:
                    triggered_odt_options.append(translated_label)

        if not triggered_odt_options:
            st.success("✅ Clean Path: No mandatory Guided Course Support tracks are required for your selected path configuration.")
            st.session_state["selected_odts"] = []
            st.session_state["odt_hydrated_for_school"] = school_id
        else:
            # 🔮 HYDRATION ENGINE: If this school hasn't been pre-checked yet, instantly check all boxes by default
            if st.session_state.get("odt_hydrated_for_school") != school_id:
                st.session_state["selected_odts"] = list(triggered_odt_options)
                st.session_state["odt_hydrated_for_school"] = school_id
                
            st.markdown("#### 🎓 Recommended Support Bundles")
            # 💡 REFINED DESIGN: Display the unified instruction string once as an elegant header block
            st.markdown(f"The following courses cannot be bypassed via exam at **{school_name}**. Please select the items you want to include Guided Course Support for:")
            
            current_selected_odts = set(st.session_state.get("selected_odts", []))
            for formal_course in triggered_odt_options:
                is_checked_by_default = formal_course in current_selected_odts
                
                # 💡 REFINED DESIGN: Checkboxes now display only the clean formal subject name
                if st.checkbox(formal_course, value=is_checked_by_default, key=f"odt_check_{formal_course.replace(' ', '_')}"):
                    current_selected_odts.add(formal_course)
                else:
                    if formal_course in current_selected_odts:
                        current_selected_odts.remove(formal_course)
            st.session_state["selected_odts"] = list(current_selected_odts)

        st.divider()
        b_back_col, b_spacer, b_continue_col = st.columns([1.0, 1.5, 1.0])
        with b_back_col:
            if st.button("⬅   Back to Schools", use_container_width=True, key="step5_back_btn"):
                st.session_state["wizard_step"] = 4
                st.rerun()
        with b_continue_col:
            if st.button("Verify Entrance Exams ➡️", use_container_width=True, type="primary", key="step5_continue_btn"):
                st.session_state["wizard_step"] = 6
                st.rerun()

    # --------------------------------------------------------------------------
    # STEP 6: STANDALONE ENTRANCE EXAM SCREEN WORKSPACE
    # --------------------------------------------------------------------------
    elif current_step == 6:
        card = st.session_state["active_school_view"]
        school_name = card["name"]
        school_exam_type = card["exam"]
        school_exam_notes = card["notes"]
        valid_courses_list = card["accepted_courses"]
        
        st.subheader(f"Step 6: Reviewing Exam Requirements & Waivers")
        st.markdown(f"Configuring standard entrance benchmarks for targeted program path: **{school_name}**")
        st.divider()
        
        classes_waived = 0
        waived_course_name = ""
        user_score_logged = st.session_state.get("modal_score_logged", "")
        
        if school_exam_type in ["--", "", "nan"] or pd.isna(school_exam_type):
            st.info("ℹ️ There are no entrance testing requirements for this specific nursing school.")
            st.session_state["customer_exam_prep_toggle"] = False
        else:
            st.markdown("#### 🔒 Entrance Exam Verification")
            user_has_passed = st.radio(f"Have you already taken and passed the required **{school_exam_type}** exam?", ["No", "Yes"], index=1 if user_score_logged else 0, horizontal=True, key="step6_has_passed_radio")
            
            if user_has_passed == "No":
                st.warning(f"⚠️ Note: A required **{school_exam_type} Prep Course** has been added to your preparation bundle.")
                st.checkbox(f"Keep **{school_exam_type} Prep Course** included in my cost estimate?", key="customer_exam_prep_toggle", value=st.session_state.get("customer_exam_prep_toggle", True))
            else:
                raw_input_score = st.text_input("Enter your official score:", value=user_score_logged, placeholder="Enter score here", key="step6_score_input")
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
                                exam_age = st.slider(age_question_text, min_value=0, max_value=10, value=1, key="step6_age_slider")
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

        st.divider()
        b_back_col, b_spacer, b_continue_col = st.columns([1.0, 1.5, 1.0])
        with b_back_col:
            if st.button("⬅   Back to Guided Support", use_container_width=True, key="step6_back_btn"):
                st.session_state["wizard_step"] = 5
                st.rerun()
        with b_continue_col:
            if st.button("Continue to Summary ➡️", use_container_width=True, type="primary", key="step6_continue_btn"):
                st.session_state["modal_include_exam_prep"] = st.session_state["customer_exam_prep_toggle"]
                st.session_state["modal_score_logged"] = user_score_logged
                st.session_state["modal_classes_waived"] = classes_waived
                st.session_state["wizard_step"] = 7
                st.rerun()

    # --------------------------------------------------------------------------
    # STEP 7: REVIEW SUMMARY CHECKOUT TERMINAL (LEFT PANEL)
    # --------------------------------------------------------------------------
    elif current_step == 7:
        card = st.session_state["active_school_view"]
        st.subheader("Step 7: Review Your Enrollment Parameters")
        st.markdown("Please verify your registration parameters. If you need to make corrections, click 'Adjust Parameters' below.")
        st.divider()
        
        st.markdown(f"👤 **Student Name:** `{st.session_state['val_name'] or 'Prospective Student'}`")
        st.markdown(f"🏫 **Target Institution Path:** `{card['name']}`")
        st.markdown(f"🎯 **Program Track:** `{card['track']}`")
        
        courses_txt = ", ".join(card["accepted_courses"]) if card["accepted_courses"] else "None selected / required"
        st.markdown(f"🧬 **Prerequisites Fulfilled ({len(card['accepted_courses'])}):** {courses_txt}")
        
        active_odts = st.session_state.get("selected_odts", [])
        if active_odts:
            st.markdown(f"🎓 **Guided Course Support Added: {', '.join(active_odts)}")
        
        if card['exam'] != "--":
            exam_status_txt = "Pass/Exempt Verified" if not st.session_state["modal_include_exam_prep"] else "Prep Course Bundle Attached"
            st.markdown(f"🔒  Requirement:** {exam_status_txt}")

        st.divider()
        if st.button("⬅   Adjust Parameters", use_container_width=True, key="step7_back_btn", disabled=is_finalized):
            st.session_state["wizard_step"] = 6
            st.rerun()

# --------------------------------------------------------------------------
# 🛒 STEP 7 ONLY: RIGHT-SIDE ITEMIZIED CHECKOUT LEDGER TERMINAL
# --------------------------------------------------------------------------
if col_ledger_flow is not None:
    with col_ledger_flow:
        st.subheader("🛒 Final Checkout Receipt")
        
        active_school = st.session_state["active_school_view"]
        needed_courses = active_school["accepted_courses"]
        school_name = active_school["name"]
        
        extra_exam_count = 1 if st.session_state["modal_include_exam_prep"] else 0
        base_classes = len(needed_courses) + extra_exam_count
        is_completely_empty = (base_classes == 0)
        
        m_classes_tier = base_classes if base_classes > 0 else 1
        main_price = 1179 if m_classes_tier >= 10 else (1229 if m_classes_tier >= 4 else 1289)
        base_total = int(base_classes * main_price)
        
        # Calculate tutoring add-on balances natively
        active_odts = st.session_state.get("selected_odts", [])
        odt_price_raw = str(active_school.get("Science ODT Price", "0")).replace("$", "").replace(",", "").strip()
        odt_unit_price = float(pd.to_numeric(odt_price_raw, errors='coerce')) if not pd.isna(pd.to_numeric(odt_price_raw, errors='coerce')) else 0.0
        total_odt_fees = int(len(active_odts) * odt_unit_price)
        
        st.markdown("#### Adjustments & Savings")
        st.session_state["val_deposit"] = 0

        q_ref = st.session_state["val_ref"]
        q_mil = st.session_state["val_mil"]
        
        calc_free_course = 0
        promo_tier_name = ""
        
        if len(needed_courses) >= 3:
            q_promo = st.radio("Do you possess a promotional code for a complimentary course?", ["No", "Yes"], index=["No", "Yes"].index(st.session_state["val_promo"]), horizontal=True, key="ledger_promo_radio", disabled=is_finalized)
            st.session_state["val_promo"] = q_promo
            
            if q_promo == "Yes":
                promo_input = st.text_input("Enter promotional code:", value=st.session_state["val_promo_code_input"], placeholder="Enter code here", disabled=is_finalized)
                st.session_state["val_promo_code_input"] = promo_input
                
                clean_promo = str(promo_input).strip().upper()
                
                if clean_promo == "":
                    st.info("ℹ️ Please type your promotional code above to activate your discount.")
                elif clean_promo in ["FREECOURSE", "FREE COURSE"]:
                    if base_classes >= 10:
                        calc_free_course = 1179
                        promo_tier_name = "FreeCourse9"
                    elif base_classes >= 4:
                        calc_free_course = 1229
                        promo_tier_name = "FreeCourse8"
                    else:
                        calc_free_course = 1289
                        promo_tier_name = "FreeCourse7"
                            
                    st.success(f"🎉 Code Approved! Unlocked Tier: **{promo_tier_name}** (-${calc_free_course:,})")
                else:
                    st.error("❌ Invalid promotional code. Please check your spelling and try again.")
        else:
            st.session_state["val_promo"] = "No"
            st.session_state["val_promo_code_input"] = ""

        calc_referral = 50 if q_ref == "Yes" else 0
        calc_military = 200 if q_mil == "Yes" else 0
        
        credits_sum = calc_referral + calc_military + calc_free_course
        final_total = max(0, (base_total + total_odt_fees) - credits_sum)

        st.divider()
        st.markdown(f"**Gross Base Tuition:** `${0 if is_completely_empty else base_total:,}`")
        
        if total_odt_fees > 0:
            st.markdown(f"➕ **Guided Course Support ({len(active_odts)}):** `${total_odt_fees:,}`")
        
        st.markdown("##### 🎖️ Discounts & Savings Applied:")
        if calc_referral > 0:
            st.markdown(f"🏷️ *Student Referral Credit:* `-${calc_referral:,}`")
        if calc_military > 0:
            st.markdown(f"🏷️ *Active Duty / Veteran Waiver:* `-${calc_military:,}`")
        if calc_free_course > 0:
            st.markdown(f"🏷️ *Complimentary Course ({promo_tier_name}):* `-${calc_free_course:,}`")
        if credits_sum == 0:
            st.markdown("🏷️ *No additional discounts applied to this estimate.*")
            
        st.markdown(f"**Total Savings:** `-${credits_sum:,}`")
        st.markdown(f"## **Balance Due: ${0 if is_completely_empty and total_odt_fees==0 else final_total:,}**")
        
        st.divider()
        if st.button("🔒 Lock in Enrollment Package", key="ledger_final_lock_action_btn", use_container_width=True, type="primary", disabled=is_finalized):
            st.session_state["confirmed_package"] = {
                "school_name": school_name,
                "student_name": st.session_state["val_name"],
                "base_total": int(base_total),
                "odt_fees_added": int(total_odt_fees),
                "odt_courses_selected": active_odts,
                "final_total": int(final_total),
                "courses_included": needed_courses,
                "entrance_exam_prep_added": st.session_state["modal_include_exam_prep"],
                "entrance_exam_score_logged": st.session_state["modal_score_logged"],
                "classes_waived_count": st.session_state["modal_classes_waived"],
                "promo_tier_applied": promo_tier_name,
                "addons_active": True if total_odt_fees > 0 else False
            }
            st.rerun()

if is_finalized:
    pkg = st.session_state["confirmed_package"]
    st.balloons()
    st.success(f"🎉 **Your Bridge Plan has been successfully finalized, {pkg['student_name']}!**")
    st.markdown(f"### School Selection Locked: **{pkg['school_name']}**")
    st.metric("Final Balance Due", f"${int(pkg['final_total']):,}")
    with st.expander("📄 View Your Signed Enrollment Summary Manifest"):
        st.json(pkg)
