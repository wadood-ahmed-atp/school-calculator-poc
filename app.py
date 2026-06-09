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
        "science_years_elapsed": 1,
        "exam_prep_manually_toggled": False,
        "val_exam_passed_status": "No"  
    }
    for key, value in defaults.items():
        if force_reset or key not in st.session_state:
            st.session_state[key] = value

initialize_base_states()

def execute_safe_restart():
    """Wipes session memory clean and instantly hits the breaker switch to prevent execution bleed crashes"""
    initialize_base_states(force_reset=True)
    st.rerun()

# 🧠 INTERACTIVE STATE CALLBACK REPLICATORS (OPTIMIZED FOR PERFORMANCE)
def sync_exam_prep_state_callback():
    """Bypasses garbage collection by archiving widget clicks directly to the session pool"""
    if "ex_prep_live_widget_key" in st.session_state:
        st.session_state["modal_include_exam_prep"] = st.session_state["ex_prep_live_widget_key"]
        st.session_state["exam_prep_manually_toggled"] = True

def sync_entrance_radio_callback():
    """Locks the entrance exam passed state radio selection firmly into memory cache"""
    if "entrance_radio_live_key" in st.session_state:
        st.session_state["val_exam_passed_status"] = st.session_state["entrance_radio_live_key"]

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

current_step = st.session_state["wizard_step"]
is_finalized = st.session_state["confirmed_package"] is not None

s_cols = ["#10B981" if current_step > i else ("#1E3A8A" if current_step == i else "#2563EB") for i in range(1, 8)]
s_whts = ["bold" if current_step == i else "normal" for i in range(1, 8)]

st.markdown(
    f"""
    <div style="font-family: sans-serif; font-size: 13px; font-weight: 500; color: #475569; padding-bottom: 25px; padding-top: 5px;">
        <span style="color: {s_cols[0]}; font-weight: {s_whts[0]};">{'✅ ' if current_step>1 else ''}1. Profile</span> <span style="color: #cbd5e1;">➔</span>
        <span style="color: {s_cols[1]}; font-weight: {s_whts[1]};">{'✅ ' if current_step>2 else ''}2. Licensing</span> <span style="color: #cbd5e1;">➔</span>
        <span style="color: {s_cols[2]}; font-weight: {s_whts[2]};">{'✅ ' if current_step>3 else ''}3. Transcript</span> <span style="color: #cbd5e1;">➔</span>
        <span style="color: {s_cols[3]}; font-weight: {s_whts[3]};">{'✅ ' if current_step>4 else ''}4. Schools</span> <span style="color: #cbd5e1;">➔</span>
        <span style="color: {s_cols[4]}; font-weight: {s_whts[4]};">{'✅ ' if current_step>5 else ''}5. Guided Support</span> <span style="color: #cbd5e1;">➔</span>
        <span style="color: {s_cols[5]}; font-weight: {s_whts[5]};">{'✅ ' if current_step>6 else ''}6. Entrance Exam</span> <span style="color: #cbd5e1;">➔</span>
        <span style="color: {s_cols[6]}; font-weight: {s_whts[6]};">{'✅ ' if is_finalized else ''}7. Summary Receipt</span>
    </div>
    """, 
    unsafe_allow_html=True
)

if current_step == 7:
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
            
        i_dismiss = st.selectbox("Have you ever been dismissed from a nursing program in the past?", options=DISMISSAL_OPTIONS, index=DISMISSAL_OPTIONS.index(st.session_state["val_dismiss"]), disabled=is_finalized)
        i_dismiss_mos = st.session_state["val_dismiss_mos"]
        if i_dismiss == "Yes":
            i_dismiss_mos = st.number_input("Months elapsed since that dismissal date:", min_value=0, max_value=300, value=i_dismiss_mos if i_dismiss_mos is not None else 0, step=1, disabled=is_finalized)
            
        i_travel = st.selectbox("Are you willing to travel regionally for clinical rotations?", options=BINARY_OPTIONS, index=BINARY_OPTIONS.index(st.session_state["val_travel"]), disabled=is_finalized)
        i_track = st.selectbox("Which degree program track are you targeting?", options=TRACK_OPTIONS, index=TRACK_OPTIONS.index(st.session_state["val_track"]), disabled=is_finalized)

        cust_state = str(st.session_state["val_state"]).strip().lower()
        state_schools = master_schools_df[master_schools_df["States Accepted"].str.lower().str.contains(cust_state, na=False)]
        has_state_bsn = not state_schools[state_schools["ASN/BSN"].str.upper() == "BSN"].empty
        has_state_asn = not state_schools[state_schools["ASN/BSN"].str.upper() == "ASN"].empty

        st.divider()
        
        if i_track == "ASN" and has_state_bsn and not has_state_asn:
            st.info("💡 **Important Regional Notice:** There is no online ADN bridge option available in your state. However, there are online BSN choices available. Would you like to review the Bachelor's route?")
            y_col, n_col = st.columns(2)
            with y_col:
                if st.button("Yes, review the BSN option", use_container_width=True, type="primary"):
                    st.session_state.update({"val_lic": i_lic, "val_exp": int(i_exp) if i_exp else 0, "val_dismiss": i_dismiss, "val_dismiss_mos": int(i_dismiss_mos) if i_dismiss_mos else 0, "val_travel": i_travel, "val_track": "BSN", "wizard_step": 3})
                    st.rerun()
            with n_col:
                if st.button("No, thank you", use_container_width=True): st.warning("Reviewing local options...")

        elif i_track == "BSN" and has_state_asn and not has_state_bsn:
            st.info("💡 **Important Regional Notice:** Direct online BSN paths are unavailable in your jurisdiction. We recommend starting with an online ASN first to sit for boards faster. Would you like to switch to ASN?")
            y_col, n_col = st.columns(2)
            with y_col:
                if st.button("Yes, start with the ADN first", use_container_width=True, type="primary"):
                    st.session_state.update({"val_lic": i_lic, "val_exp": int(i_exp) if i_exp else 0, "val_dismiss": i_dismiss, "val_dismiss_mos": int(i_dismiss_mos) if i_dismiss_mos else 0, "val_travel": i_travel, "val_track": "ASN", "wizard_step": 3})
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
                    st.session_state.update({"val_lic": i_lic, "val_exp": int(i_exp) if i_exp else 0, "val_dismiss": i_dismiss, "val_dismiss_mos": int(i_dismiss_mos) if i_dismiss_mos else 0, "val_travel": i_travel, "val_track": i_track, "wizard_step": 3})
                    st.rerun()

    # --------------------------------------------------------------------------
    # STEP 3: PREREQUISITE BUTTON SELECTION GRID
    # --------------------------------------------------------------------------
    elif current_step == 3:
        st.subheader("Step 3: Foundational Prerequisite Review")
        st.markdown("Select any general education or prerequisite courses you still need to complete:")
        st.divider()
        
        btn_all_col, btn_clear_col, btn_spacer = st.columns([1.2, 1.2, 3.0])
        with btn_all_col:
            if st.button("Select All Prerequisites", use_container_width=True):
                st.session_state["val_courses"] = list(course_list)
                st.rerun()
        with btn_clear_col:
            if st.button("Clear All Selections", use_container_width=True):
                st.session_state["val_courses"] = []
                st.rerun()
                
        st.markdown("<br>", unsafe_allow_html=True)
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
                    
                    if st.button(f"{btn_prefix}{course}", key=f"gb_{course.replace(' ', '_')}", use_container_width=True, type=btn_type, disabled=is_finalized):
                        if is_toggled: current_selections.remove(course)
                        else: current_selections.add(course)
                        st.session_state["val_courses"] = list(current_selections)
                        st.rerun()
                        
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
                st.session_state["wizard_step"] = 4
                st.rerun()

    # --------------------------------------------------------------------------
    # STEP 4: INSTITUTIONAL SCHOOL MATCHES
    # --------------------------------------------------------------------------
    elif current_step == 4:
        st.subheader("Step 4: Your Eligible Matches")
        st.info(f"🎯 Current Selected Track: **{st.session_state['val_track']}** program options")
        st.divider()
        
        selected_state = str(st.session_state["val_state"]).strip().lower()
        selected_track = str(st.session_state["val_track"]).strip().lower()
        license_type = st.session_state["val_lic"]
        lpn_exp = int(st.session_state["val_exp"]) if st.session_state["val_exp"] is not None else 0
        gpa_val = round(float(st.session_state["val_gpa"]), 1)
        travel_ok = st.session_state["val_travel"]
        dismissal_y = (st.session_state["val_dismiss"] == "Yes")
        dismissal_months = int(st.session_state["val_dismiss_mos"]) if st.session_state["val_dismiss_mos"] is not None else 0
        needed_courses = st.session_state["val_courses"]

        working_schools_df = master_schools_df.copy()
        
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

        if not working_schools_df.empty:
            card_rows = []
            for idx, school_row in working_schools_df.iterrows():
                raw_name = str(school_row["School Name"]).strip()
                s_exam = str(school_row.get("Entrance Exam", "--")).strip()
                s_notes = str(school_row.get("Entrance Exam Notes", "")).strip()
                s_blanket = str(school_row.get("Blanket Statement", "")).strip()
                s_odt_rules = str(school_row.get("Science/Math ODTs", "")).strip()
                s_odt_notes = str(school_row.get("Science/Math ODT Notes", "")).strip()
                
                if "HERZ" in raw_name.upper() or "HERI" in raw_name.upper():
                    rule_row = transcript_rules_df[transcript_rules_df["School Name"].str.upper().str.contains("HERZ|HERI", na=False)]
                elif "EXCEL" in raw_name.upper():
                    rule_row = transcript_rules_df[transcript_rules_df["School Name"].str.upper().str.contains("EXCEL", na=False)]
                else: 
                    rule_row = transcript_rules_df[transcript_rules_df["School Name"].str.upper() == raw_name.upper()]
                
                school_accepted_list = []
                has_all_courses = True
                
                if not rule_row.empty:
                    for required_course in needed_courses:
                        if required_course == "Government History":
                            if str(rule_row['Government'].values[0]).strip().upper() == "Y" or str(rule_row['History'].values[0]).strip().upper() == "Y":
                                school_accepted_list.append(required_course)
                            else: has_all_courses = False
                        else:
                            check_course = course_mapping_bridge.get(required_course, required_course)
                            if check_course in rule_row.columns and str(rule_row[check_course].values[0]).strip().upper() == "Y":
                                school_accepted_list.append(required_course)
                            else: has_all_courses = False
                    s_status = "Perfect Match" if (not needed_courses or has_all_courses) else "Missing Needed CBE Courses"
                else:
                    s_status = "Perfect Match"
                    school_accepted_list = list(needed_courses)
                
                unique_hash_id = f"sch_{idx}_{re.sub(r'[^a-zA-Z0-9]', '_', raw_name)}"
                card_rows.append({
                    "id": unique_hash_id, "idx": idx, "name": raw_name, "exam": s_exam, "notes": s_notes,
                    "blanket": s_blanket, "odt_rules": s_odt_rules, "odt_notes": s_odt_notes,
                    "track": school_row["ASN/BSN"], "status": s_status, "accepted_courses": school_accepted_list
                })
            
            for card in card_rows:
                is_selected = (st.session_state["selected_school_id"] == card["id"])
                courses_str = ", ".join(card["accepted_courses"]) if card["accepted_courses"] else "None Required"
                
                with st.container(border=True):
                    st.markdown(f"### 🏫 {card['name']}")
                    st.markdown(f"**Degree Track Program:** `{card['track']}`")
                    st.markdown(f"🧬 *Prerequisites Fulfilled ({len(card['accepted_courses'])}):* **{courses_str}**")
                    
                    btn_lbl = "✓ Active Selection Unlocked" if is_selected else "Select School & Fulfill Prerequisites"
                    if st.button(btn_lbl, key=f"bc_{card['id']}", use_container_width=True, type="secondary" if is_selected else "primary"):
                        st.session_state.update({
                            "active_school_view": card, 
                            "selected_school_id": card["id"], 
                            "wizard_step": 5,
                            "exam_prep_manually_toggled": False 
                        })
                        st.rerun()
        else:
            st.warning("No online options match your filters at this time.")
        
        st.divider()
        b_reset_col, b_spacer, b_back_col = st.columns([1.0, 1.5, 1.0])
        with b_reset_col:
            if st.button("🔄 Restart Process", use_container_width=True, type="secondary"): execute_safe_restart()
        with b_back_col:
            if st.button("⬅️ Back to Review", use_container_width=True):
                st.session_state["wizard_step"] = 3
                st.rerun()

    # --------------------------------------------------------------------------
    # STEP 5: DYNAMIC GUIDED COURSE SUPPORT TERMINAL
    # --------------------------------------------------------------------------
    elif current_step == 5:
        card = st.session_state["active_school_view"]
        school_name = card["name"]
        school_id = card["id"]
        odt_rules_string = card["odt_rules"]
        odt_notes_string = card.get("odt_notes", "")
        needed_courses = st.session_state["val_courses"]
        
        if str(odt_notes_string).strip().lower() in ["", "nan", "--", "none"]:
            odt_notes_string = ""
            
        st.subheader("Step 5: Guided Course Support & Institutional Requirements")
        st.markdown(f"Reviewing academic support enhancements for target program path: **{school_name}**")
        st.divider()
        
        if card["blanket"] and str(card["blanket"]).lower() not in ["", "nan", "--"]:
            st.info(f"📋 **Institutional Policy Notice:**\n\n{card['blanket']}")
            
        is_force_locked, is_pre_checked_only, rule_threshold_years, rule_display_message = False, False, 99, ""
        
        if odt_notes_string and ":" in odt_notes_string:
            try:
                parts = odt_notes_string.split(":")
                rule_threshold_years = int(parts[0].strip())
                policy_type = parts[1].strip().lower()
                rule_display_message = parts[2].strip()
                
                st.markdown("##### ⏳ Credit Recency Verification")
                user_age_input = st.slider("How many years ago did you complete your core science credits?", min_value=0, max_value=25, value=st.session_state["science_years_elapsed"], key="science_slider")
                st.session_state["science_years_elapsed"] = user_age_input
                
                if user_age_input > rule_threshold_years:
                    if policy_type == "mandatory":
                        is_force_locked = True
                        st.error(f"🛑 **Strict Policy Cutoff Met:** {rule_display_message} Guided Course Support locked into plan.")
                    elif policy_type == "recommended":
                        is_pre_checked_only = True
                        st.warning(f"⚠️ **Regional Window Recommendation:** {rule_display_message} Support highly recommended.")
                else:
                    st.success(f"✅ Verified: Your science credits fall within the acceptable {rule_threshold_years}-year window.")
            except Exception:
                if odt_notes_string: st.info(odt_notes_string)
        elif odt_notes_string:
            st.info(odt_notes_string)

        triggered_odt_options = [c.strip() for c in odt_rules_string.split(",")] if odt_rules_string and str(odt_rules_string).lower() not in ["", "nan", "--"] else []
        triggered_odt_options = [c for c in triggered_odt_options if c in needed_courses]

        if not triggered_odt_options:
            st.success("✅ Clean Path: No mandatory Guided Course Support tracks are required for this configuration.")
            st.session_state.update({"selected_odts": [], "odt_hydrated_for_school": school_id})
        else:
            if st.session_state.get("odt_hydrated_for_school") != school_id:
                st.session_state.update({"selected_odts": list(triggered_odt_options), "odt_hydrated_for_school": school_id})
                
            st.markdown("#### 🎓 Recommended Support Bundles")
            st.markdown("The following courses cannot be bypassed via exam. Please choose support options to include:")
            
            chosen_odts = []
            current_selections_set = set(st.session_state["selected_odts"])
            
            for formal_course in triggered_odt_options:
                if is_force_locked:
                    st.checkbox(formal_course, value=True, disabled=True, key=f"odt_fz_{formal_course}")
                    chosen_odts.append(formal_course)
                else:
                    was_checked = formal_course in current_selections_set or is_pre_checked_only
                    if st.checkbox(formal_course, value=was_checked, key=f"odt_act_{formal_course}"):
                        chosen_odts.append(formal_course)
            
            st.session_state["selected_odts"] = chosen_odts if not is_force_locked else list(set(chosen_odts).union(current_selections_set))

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
    # STEP 6: STANDALONE ENTRANCE EXAM WORKSPACE (100% Dynamic Alert Matrix Fixed)
    # --------------------------------------------------------------------------
    elif current_step == 6:
        card = st.session_state["active_school_view"]
        school_name = card["name"]
        school_exam_type = card["exam"]
        school_exam_notes = card["notes"]
        
        st.subheader(f"Step 6: Reviewing Exam Requirements & Waivers")
        st.markdown(f"Configuring standard entrance benchmarks for targeted program path: **{school_name}**")
        st.divider()
        
        classes_waived = 0
        waived_course_name = ""
        user_score_logged = st.session_state.get("modal_score_logged", "")
        
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
                # 🧪 DYNAMIC NOTICE RENDER ENGINE: Only triggers alert box text if checkbox is ACTIVELY checked in state vault
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
                st.session_state["modal_include_exam_prep"] = False
                raw_input_score = st.text_input("Enter your official score:", value=user_score_logged, placeholder="Enter score here", key="step6_score")
                user_score_logged = raw_input_score
                
                if raw_input_score:
                    clean_score_str = re.sub(r'[^\d.]', '', raw_input_score)
                    score_num = float(clean_score_str) if clean_score_str else 0.0
                    
                    if score_num >= 75.0:
                        matched_rule_type, custom_message, age_limit_years = "pass", "", None
                    else:
                        rules = str(school_exam_notes).strip().split('|')
                        matched_rule_type, custom_message, age_limit_years, age_question_text = "fail", "", None, ""
                        
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
                            if st.session_state["modal_include_exam_prep"]:
                                st.error(f"🛑 This score is below the automatic waiver threshold. We've added a **{school_exam_type} Prep Course**.")
                            if not st.session_state["exam_prep_manually_toggled"]:
                                st.session_state["modal_include_exam_prep"] = True
                            st.checkbox(f"Keep **{school_exam_type} Prep Course** included?", value=st.session_state["modal_include_exam_prep"], key="ex_prep_live_widget_key", on_change=sync_exam_prep_state_callback)
                        elif matched_rule_type in ["pass", "exempt"]:
                            if age_limit_years:
                                st.markdown("##### ⏳ Verification Check:")
                                exam_age = st.slider(age_question_text, min_value=0, max_value=10, value=1, key="exam_age_slider")
                                st.session_state["modal_include_exam_prep"] = (exam_age > age_limit_years)
                                if exam_age > age_limit_years: st.error("🛑 Your test score has expired. Adding a refresher course.")
                                else: st.success("✅ Verified: Your score is active and valid!")
                            else:
                                if matched_rule_type == "exempt": st.success(f"🎉 Exemption unlocked! Waived out of **{waived_course_name}**.")
                                else: st.success("✅ Verified: Entrance testing requirements met!")
                                st.session_state["modal_include_exam_prep"] = False
                        elif matched_rule_type == "retest":
                            st.warning(f"⚠️ {custom_message}")
                            if not st.session_state["exam_prep_manually_toggled"]:
                                st.session_state["modal_include_exam_prep"] = True
                            st.checkbox(f"Add **{school_exam_type} Advanced Retest Prep**?", value=st.session_state["modal_include_exam_prep"], key="ex_prep_live_widget_key", on_change=sync_exam_prep_state_callback)

        st.divider()
        b_back_col, b_spacer, b_continue_col = st.columns([1.0, 1.5, 1.0])
        with b_back_col:
            if st.button("⬅   Back to Guided Support", use_container_width=True):
                st.session_state["wizard_step"] = 5
                st.rerun()
        with b_continue_col:
            if st.button("Continue to Summary ➡️", use_container_width=True, type="primary"):
                st.session_state["wizard_step"] = 7
                st.rerun()

    # --------------------------------------------------------------------------
    # STEP 7: REVIEW SUMMARY SUMMARY RECEIPT TERMINAL
    # --------------------------------------------------------------------------
    elif current_step == 7:
        card = st.session_state["active_school_view"]
        st.subheader("Step 7: Final Package Summary Review")
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
                exam_status_txt = "✓ Pass/Exempt Verified" if not st.session_state["modal_include_exam_prep"] else "⚠️ Prep Course Attached"
                st.markdown(f"**Entrance Benchmark Requirement:** `{exam_status_txt if card['exam'] != '--' else 'Exempt / None'}`")

        st.markdown("<br>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("### 🧬 Academic Parameter Configurations")
            st.markdown("<br>", unsafe_allow_html=True)
            col_cbe, col_odt = st.columns(2, gap="large")
            
            with col_cbe:
                st.markdown(f"##### 🔹 Prerequisites via Credit-by-Exam ({len(card['accepted_courses'])})")
                if card["accepted_courses"]:
                    for course_item in card["accepted_courses"]: st.markdown(f"✅ &nbsp; {course_item}")
                else: st.markdown("*No prerequisites selected for testing out.*")
                    
            with col_odt:
                active_odts = st.session_state.get("selected_odts", [])
                st.markdown(f"##### 🎓 Guided Course Support Added ({len(active_odts)})")
                if active_odts:
                    for odt_item in active_odts: st.markdown(f"🚀 &nbsp; {odt_item}")
                else: st.markdown("*No custom tutoring support tracks selected.*")

        st.divider()
        if st.button("⬅   Adjust Parameters", use_container_width=True, disabled=is_finalized):
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
        active_odts = st.session_state.get("selected_odts", [])
        
        total_products = len(needed_courses) + extra_exam_count + len(active_odts)
        
        if total_products >= 10:
            prep_rate, odt_rate = 1179.0, 749.0
        elif total_products >= 4:
            prep_rate, odt_rate = 1229.0, 799.0
        else:
            prep_rate, odt_rate = 1289.0, 859.0
            
        gened_subtotal = len(needed_courses) * prep_rate
        entrance_subtotal = extra_exam_count * prep_rate
        base_total = int(gened_subtotal + entrance_subtotal)
        total_odt_fees = int(len(active_odts) * odt_rate)
        
        st.markdown("#### Adjustments & Savings")
        st.session_state["val_deposit"] = 0
        q_ref, q_mil = st.session_state["val_ref"], st.session_state["val_mil"]
        calc_free_course, promo_tier_name = 0, ""
        
        if len(needed_courses) >= 3:
            q_promo = st.radio("Do you possess a promotional code?", ["No", "Yes"], index=["No", "Yes"].index(st.session_state["val_promo"]), horizontal=True, disabled=is_finalized)
            st.session_state["val_promo"] = q_promo
            
            if q_promo == "Yes":
                promo_input = st.text_input("Enter promotional code:", value=st.session_state["val_promo_code_input"], placeholder="Enter code here", disabled=is_finalized)
                st.session_state["val_promo_code_input"] = promo_input
                if str(promo_input).strip().upper() in ["FREECOURSE", "FREE COURSE"]:
                    calc_free_course = int(prep_rate)
                    promo_tier_name = f"FreeCourse_Model8_Tier_{total_products}"
                    st.success(f"🎉 Code Approved! Discount (-${calc_free_course:,})")
                elif str(promo_input).strip() != "":
                    st.error("❌ Invalid promotional code.")
        else:
            st.session_state.update({"val_promo": "No", "val_promo_code_input": ""})

        calc_referral = 50 if q_ref == "Yes" else 0
        calc_military = 200 if q_mil == "Yes" else 0
        credits_sum = calc_referral + calc_military + calc_free_course
        final_total = max(0, (base_total + total_odt_fees) - credits_sum)

        st.divider()
        st.markdown(f"**Gross Base Tuition:** `${base_total:,}`")
        st.caption(f"({len(needed_courses)} Gen-Eds & {extra_exam_count} Entrance Prep at ${int(prep_rate):,} each)")
        
        if total_odt_fees > 0:
            st.markdown(f"➕ **Guided Course Support ({len(active_odts)}):** `${total_odt_fees:,}`")
            st.caption(f"({len(active_odts)} ODT Bundles at ${int(odt_rate):,} each)")
        
        st.markdown("##### 🎖️ Levant Discounts Applied:")
        if calc_referral: st.markdown(f"🏷️ *Student Referral Credit:* `-${calc_referral:,}`")
        if calc_military: st.markdown(f"🏷️ *Active Duty / Veteran Waiver:* `-${calc_military:,}`")
        if calc_free_course: st.markdown(f"🏷️ *Complimentary Course Code:* `-${calc_free_course:,}`")
        if not credits_sum: st.markdown("🏷️ *No additional discounts applied.*")
            
        st.markdown(f"**Total Savings:** `-${credits_sum:,}`")
        st.markdown(f"## **Balance Due: ${0 if (base_total==0 and total_odt_fees==0) else final_total:,}**")
        
        st.divider()
        if st.button("🔒 Lock in Enrollment Package", key="lock_package_btn", use_container_width=True, type="primary", disabled=is_finalized):
            st.session_state["confirmed_package"] = {
                "school_name": school_name, "student_name": st.session_state["val_name"],
                "base_total": int(base_total), "odt_fees_added": int(total_odt_fees), "odt_courses_selected": active_odts,
                "final_total": int(final_total), "courses_included": needed_courses, "entrance_exam_prep_added": st.session_state["modal_include_exam_prep"],
                "entrance_exam_score_logged": st.session_state["modal_score_logged"], "classes_waived_count": st.session_state["modal_classes_waived"],
                "promo_tier_applied": promo_tier_name, "addons_active": bool(total_odt_fees > 0)
            }
            st.rerun()

if is_finalized:
    pkg = st.session_state["confirmed_package"]
    st.balloons()
    st.success(f"🎉 **Your Bridge Plan has been successfully finalized, {pkg['student_name']}!**")
    st.markdown(f"### School Selection Locked: **{pkg['school_name']}**")
    st.metric("Final Balance Due", f"${int(pkg['final_total']):,}")
    with st.expander("📄 View Your Signed Enrollment Summary Manifest"): st.json(pkg)
