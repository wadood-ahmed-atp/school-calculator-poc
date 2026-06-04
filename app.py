import streamlit as st
import pandas as pd
import os
import re

# ==============================================================================
# 1. INITIALIZE PERSISTENT APP MEMORY VAULTS
# ==============================================================================
if "wizard_step" not in st.session_state: st.session_state["wizard_step"] = 1
if "confirmed_package" not in st.session_state: st.session_state["confirmed_package"] = None
if "addon_state" not in st.session_state: st.session_state["addon_state"] = False
if "active_school_view" not in st.session_state: st.session_state["active_school_view"] = None
if "modal_include_exam_prep" not in st.session_state: st.session_state["modal_include_exam_prep"] = False

# Form Memory Values
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
# 2. DATA SOURCE ROUTING LOADER
# ==============================================================================
SCHOOLS_CSV = "schools.csv"
TRANSCRIPT_CSV = "transcript_rules.csv"

if os.path.exists(SCHOOLS_CSV):
    try: master_schools_df = pd.read_csv(SCHOOLS_CSV, encoding='utf-8')
    except Exception: master_schools_df = pd.read_csv(SCHOOLS_CSV, encoding='latin1', errors='replace')
    for col in master_schools_df.select_dtypes(include=['object']).columns:
        master_schools_df[col] = master_schools_df[col].astype(str).str.strip()
else:
    st.error("⚠️ Database missing: schools.csv not found.")
    st.stop()

if os.path.exists(TRANSCRIPT_CSV):
    try: transcript_rules_df = pd.read_csv(TRANSCRIPT_CSV, encoding='utf-8')
    except Exception: transcript_rules_df = pd.read_csv(TRANSCRIPT_CSV, encoding='latin1', errors='replace')
    for col in transcript_rules_df.select_dtypes(include=['object']).columns:
        transcript_rules_df[col] = transcript_rules_df[col].astype(str).str.strip()
    transcript_rules_df.columns = transcript_rules_df.columns.str.strip()
else:
    st.error("⚠️ Validation rules missing: transcript_rules.csv not found.")
    st.stop()

# ==============================================================================
# 3. GLOBAL CONFIG MATRICES
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
# 4. SIDEBAR NAVIGATION DECK LAYER
# ==============================================================================
with st.sidebar:
    st.title("🧭 Navigation Deck")
    
    step_labels = [
        "1. Identity Profile",
        "2. Baseline Profile",
        "3. Transcripts Review",
        "4. School Matches"
    ]
    
    # Track the active navigation option using an index state pointer mapping
    selected_nav_label = st.radio(
        "Jump directly to any process step:",
        options=step_labels,
        index=st.session_state["wizard_step"] - 1,
        key="sidebar_nav_radio"
    )
    
    # Sync radio click actions back to core state machine cleanly
    nav_index = step_labels.index(selected_nav_label) + 1
    if nav_index != st.session_state["wizard_step"]:
        st.session_state["wizard_step"] = nav_index
        st.rerun()
        
    st.divider()
    if st.button("🔄 Reset Form Data", use_container_width=True, type="secondary"):
        restart_wizard()

current_step = st.session_state["wizard_step"]

# Main Layout Heading
st.title("🗺️ Bridge Plan Generator")
st.markdown(f"#### **Step {current_step} of 4: {step_labels[current_step-1][3:]}**")
st.divider()

# Set standard responsive split parameters across layouts
if current_step == 4:
    col_input_flow, col_ledger_flow = st.columns([1.4, 1.0], gap="medium")
else:
    col_input_flow = st.container()
    col_ledger_flow = None

with col_input_flow:

    # --------------------------------------------------------------------------
    # STEP 1: IDENTITY PROFILE AREA
    # --------------------------------------------------------------------------
    if current_step == 1:
        st.markdown("### Welcome & Identity Profile")
        st.markdown("Let's capture your baseline state parameters to parse regional institutional compliance loops.")
        
        i_name = st.text_input("What is your name?", value=st.session_state["val_name"], placeholder="Enter full name")
        i_state = st.selectbox("Select your residency home state:", options=STATE_OPTIONS, index=STATE_OPTIONS.index(st.session_state["val_state"]))
        i_zip = st.text_input("What is your zip code?", value=st.session_state["val_zip"], placeholder="e.g. 19013", max_chars=14)
        i_adult = st.selectbox("Are you 18 years of age or older?", options=BINARY_OPTIONS, index=BINARY_OPTIONS.index(st.session_state["val_adult"]))
        i_gpa = st.number_input("What is your current cumulative GPA Score?", min_value=0.0, max_value=4.0, value=st.session_state["val_gpa"], step=0.01)
        
        st.divider()
        b_col1, b_col2 = st.columns([3.0, 1.0])
        with b_col2:
            if st.button("Continue ➡️", use_container_width=True, type="primary"):
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
                    st.session_state["wizard_step"] = 2
                    st.rerun()

    # --------------------------------------------------------------------------
    # STEP 2: HEALTHCARE PROFILE LAYERS
    # --------------------------------------------------------------------------
    elif current_step == 2:
        st.markdown("### Professional Licensing & History")
        st.markdown("Tell us about your background to clear experience validation matrices.")
        
        i_lic = st.selectbox("What is your current nursing license tier?", options=LICENSE_OPTIONS, index=LICENSE_OPTIONS.index(st.session_state["val_lic"]))
        i_exp = st.session_state["val_exp"]
        if i_lic == "LPN":
            i_exp = st.number_input("Total months of active LPN Work Experience:", min_value=0, max_value=120, value=st.session_state["val_exp"], step=1)
            
        i_dismiss = st.selectbox("Do you possess a prior academic nursing program dismissal?", options=DISMISSAL_OPTIONS, index=DISMISSAL_OPTIONS.index(st.session_state["val_dismiss"]))
        i_dismiss_mos = st.session_state["val_dismiss_mos"]
        if i_dismiss == "Yes":
            i_dismiss_mos = st.number_input("Months elapsed since your historical dismissal date:", min_value=0, max_value=300, value=st.session_state["val_dismiss_mos"], step=1)
            
        i_travel = st.selectbox("Are you amenable to regional clinical onsite travel loops?", options=BINARY_OPTIONS, index=BINARY_OPTIONS.index(st.session_state["val_travel"]))
        i_track = st.selectbox("Which nursing track are you targeting?", options=TRACK_OPTIONS, index=TRACK_OPTIONS.index(st.session_state["val_track"]))
        
        st.divider()
        b_col1, b_col2, b_col3 = st.columns([2.0, 1.0, 1.0])
        with b_col2:
            if st.button("⬅️ Back", use_container_width=True):
                st.session_state["val_lic"] = i_lic
                st.session_state["val_exp"] = i_exp
                st.session_state["val_dismiss"] = i_dismiss
                st.session_state["val_dismiss_mos"] = i_dismiss_mos
                st.session_state["val_travel"] = i_travel
                st.session_state["val_track"] = i_track
                st.session_state["wizard_step"] = 1
                st.rerun()
        with b_col3:
            if st.button("Continue ➡️", use_container_width=True, type="primary"):
                st.session_state["val_lic"] = i_lic
                st.session_state["val_exp"] = i_exp
                st.session_state["val_dismiss"] = i_dismiss
                st.session_state["val_dismiss_mos"] = i_dismiss_mos
                st.session_state["val_travel"] = i_travel
                st.session_state["val_track"] = i_track
                st.session_state["wizard_step"] = 3
                st.rerun()

    # --------------------------------------------------------------------------
    # STEP 3: TRANSCRIPT review FORM
    # --------------------------------------------------------------------------
    elif current_step == 3:
        st.markdown("### Foundational Transcript Review")
        st.markdown("Select your required prerequisite deficiencies and apply discount criteria parameters.")
        
        st.multiselect(
            "Check the boxes for courses you still NEED to complete:",
            options=course_list,
            default=st.session_state["val_courses"],
            key="temp_courses" 
        )
        st.session_state["val_courses"] = st.session_state["temp_courses"]
        
        st.markdown("#### Promotional Qualifications & Discounts")
        w_ref = st.radio("Were you referred by a student or agent?", ["No", "Yes"], index=["No", "Yes"].index(st.session_state["val_ref"]), horizontal=True)
        w_mil = st.radio("Are you affiliated with the Military (Veteran/Active/Spouse)?", ["No", "Yes"], index=["No", "Yes"].index(st.session_state["val_mil"]), horizontal=True)
        
        if len(st.session_state["val_courses"]) >= 3:
            w_promo = st.radio("Do you possess a promotional code for a complimentary course?", ["No", "Yes"], index=["No", "Yes"].index(st.session_state["val_promo"]), horizontal=True)
            st.session_state["val_promo"] = w_promo
        else:
            st.session_state["val_promo"] = "No"
        
        st.session_state["val_ref"] = w_ref
        st.session_state["val_mil"] = w_mil
        st.session_state["addon_state"] = False

        st.divider()
        b_col1, b_col2, b_col3 = st.columns([2.0, 1.0, 1.0])
        with b_col2:
            if st.button("⬅️ Back", use_container_width=True):
                st.session_state["wizard_step"] = 2
                st.rerun()
        with b_col3:
            if st.button("Find Matches ➡️", use_container_width=True, type="primary"):
                st.session_state["active_school_view"] = None
                st.session_state["wizard_step"] = 4
                st.rerun()

    # --------------------------------------------------------------------------
    # STEP 4: INSTITUTIONAL MATCH GENERATOR ROWS
    # --------------------------------------------------------------------------
    elif current_step == 4:
        st.markdown("### Secure Institutional Match Alignment")
        st.markdown("Review the eligible educational institutions calculated from your intake profile parameters:")
        
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
        # STANDARD DIALOG MODAL LAYOUT INFRASTRUCTURE
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
                st.info("ℹ️ Entrance exam parameter checks waived for this campus blueprint.")
                local_include_prep = False
            else:
                st.markdown(f"#### 🔒 Entrance Exam Compliance Gating")
                user_has_passed = st.radio(f"Have you already taken and passed the required **{school_exam_type}** exam?", ["No", "Yes"], horizontal=True, key="modal_has_passed_radio")
                
                if user_has_passed == "No":
                    st.warning(f"⚠️ Notice: We have added the required **{school_exam_type} Prep Course** package to your configuration list.")
                    local_include_prep = st.checkbox(f"Keep **{school_exam_type} Prep Course** included in bundle?", value=True, key="opt_out_chk_1")
                else:
                    raw_input_score = st.text_input("Enter your official exam score number:", placeholder="e.g., 75 or 740")
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
                                st.error(f"🛑 Score below target threshold values. Adding **{school_exam_type} Prep Course** layout bundle parameters.")
                                local_include_prep = st.checkbox(f"Keep **{school_exam_type} Prep Course** included in bundle?", value=True, key="opt_out_chk_2")
                            elif matched_rule_type == "pass":
                                if age_limit_years:
                                    st.markdown("##### ⏳ Verification Check Required:")
                                    exam_age = st.slider(age_question_text, min_value=0, max_value=10, value=1)
                                    if exam_age > age_limit_years:
                                        st.error(f"🛑 Historical evaluation parameter expired. Pre-adding the prep bundle.")
                                        local_include_prep = st.checkbox(f"Keep **{school_exam_type} Prep Course** included in bundle?", value=True, key="opt_out_chk_3")
                                    else:
                                        st.success(f"✅ Verified: Score tracking variables remain active and verified!")
                                        local_include_prep = False
                                else:
                                    st.success(f"✅ Verified: Compliance verified for this campus track choice framework.")
                                    local_include_prep = False
                            elif matched_rule_type == "retest":
                                st.warning(f"⚠️ Verification conditional layer cleared. {custom_message}")
                                local_include_prep = st.checkbox(f"Add **{school_exam_type} Retest Prep** to maximize credit value?", value=True, key="opt_out_chk_4")
                            elif matched_rule_type == "exempt":
                                st.success(f"🎉 Automatic credit waiver exemption unlocked from **{waived_course_name}**.")
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
            calc_free_course = float(m_price_tier) if (st.session_state["val_promo"] == "Yes" and modal_base_count >= 3) else 0.0
            modal_credits_sum = calc_dep_match + calc_referral + calc_military + calc_free_course + grant_input
            modal_final_total = max(0.0, final_base_total - modal_credits_sum)

            st.metric("Adjusted Base Tuition Total", f"${final_base_total:,.2f}")
            st.metric("Final Balance Due", f"${modal_final_total:,.2f}")
            
            if st.button("🔒 Lock in Enrollment Package", key="modal_lock_btn", use_container_width=True):
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

        # Render program card match frames list
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
                    sc1, sc2, sc3 = st.columns([1.0, 2.5, 1.2])
                    with sc1:
                        if st.button("Select School", key=f"btn_card_sel_{card['idx']}", use_container_width=True, type="primary"):
                            render_institutional_modal(card["name"], card["exam"], card["notes"], card["accepted_courses"], card)
                    with sc2:
                        st.markdown(f"🏫 **{card['name']}** ({card['track']} Track)")
                        courses_string = ", ".join(card["accepted_courses"]) if card["accepted_courses"] else "None Required"
                        st.markdown(f"🧬 *Deficiencies Met ({len(card['accepted_courses'])}):* `{courses_string}`")
                    with sc3:
                        st.metric("Est Profit Margin", f"${card['profit']:,.2f}")
        else:
            st.warning("No partner institutions match your geofencing filters profile layout matrix parameters.")
        
        st.divider()
        b_col1, b_col2 = st.columns([3.0, 1.0])
        with b_col2:
            if st.button("⬅️ Back to Review", use_container_width=True):
                st.session_state["val_courses"] = list(st.session_state["val_courses"])
                st.session_state["wizard_step"] = 3
                st.rerun()

# ==============================================================================
# 5. SMART INVOICE CHECKOUT LEDGER ENGINE MODULE
# ==============================================================================
if col_ledger_flow is not None:
    with col_ledger_flow:
        st.header("🛒 Itemized Invoice Cart")
        
        license_type = st.session_state["val_lic"]
        
        # Keep ledger hidden placeholder style until formal card button locks commit parameters
        if st.session_state["confirmed_package"] is None:
            st.info("👉 Please select a partner program card block option layout row on the left to verify compliance data and unlock ledger parameters calculation maps.")
        else:
            needed_courses = st.session_state["active_school_view"]["accepted_courses"]
            st.success(f"🎯 Locked Target: **{st.session_state['active_school_view']['name']}**")

            extra_exam_count = 1 if st.session_state.get("modal_include_exam_prep", False) else 0
            base_classes = len(needed_courses) + extra_exam_count
            total_classes = base_classes
            is_completely_empty = (total_classes == 0)
            
            m_classes_tier = base_classes if base_classes > 0 else 1
            main_price = 1179 if m_classes_tier >= 10 else (1229 if m_classes_tier >= 4 else 1289)
            base_total = base_classes * main_price
            
            st.markdown("#### Adjustments & Grants Parameters")
            deposit_input = st.number_input("Enrollment Deposit Amount ($)", min_value=0.0, value=st.session_state["val_deposit"], step=50.0)
            grant_input = st.number_input("Institutional Grant Amount ($)", min_value=0.0, value=st.session_state["val_grant"], step=50.0)
            
            st.session_state["val_deposit"] = deposit_input
            st.session_state["val_grant"] = grant_input

            q_ref = st.session_state["val_ref"]
            q_mil = st.session_state["val_mil"]
            
            # Context lookahead block calculation evaluation framework live check
            if len(needed_courses) >= 3:
                q_promo = st.radio("Do you possess a promotional code for a complimentary course?", ["No", "Yes"], index=["No", "Yes"].index(st.session_state["val_promo"]), horizontal=True, key="ledger_promo_radio")
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
            st.markdown(f"**Waivers & Promo Grants Applied:** `-${credits_sum:,.2f}`")
            st.markdown(f"### **Balance Due: ${0.00 if is_completely_empty else final_total:,.2f}**")

# Final success logging verification metrics blocks
if st.session_state["confirmed_package"]:
    pkg = st.session_state["confirmed_package"]
    st.balloons()
    st.success(f"🎉 **Bridge Plan Successfully Finalized for {pkg['student_name']}!**")
    st.markdown(f"### Selected School Locked: **{pkg['school_name']}**")
    st.metric("Final Adjusted Price Due", f"${pkg['final_total']:,.2f}")
    with st.expander("📄 View Final Signed Voucher Audit Manifest Record Parameters"):
        st.json(pkg)
