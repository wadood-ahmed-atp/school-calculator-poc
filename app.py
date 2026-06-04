import streamlit as st
import pandas as pd
import os
import re

# ==============================================================================
# 0. WEB PAGE CONFIG & STYLING
# ==============================================================================
st.set_page_config(page_title="Bridge Plan Generator", layout="wide")

st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    h1, h2, h3 {color: #1E3A8A;}
    .stButton>button {background-color: #1E3A8A; color: white; border-radius: 5px; width: 100%; height: 40px; font-weight: bold;}
    .stButton>button:hover {background-color: #3B82F6; color: white;}
    div[data-testid="stMetricValue"] {font-size: 24px; color: #10B981;}
    .wizard-header {background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 25px; text-align: center;}
    .step-badge {background-color: #1E3A8A; color: white; padding: 4px 12px; border-radius: 20px; font-size: 14px; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. PERSISTENT WIZARD STATE MANAGEMENT
# ==============================================================================
if "wizard_step" not in st.session_state:
    st.session_state["wizard_step"] = 1
if "confirmed_package" not in st.session_state:
    st.session_state["confirmed_package"] = None
if "addon_state" not in st.session_state:
    st.session_state["addon_state"] = False

def restart_wizard():
    # Clear selections but preserve structural infrastructure states
    for key in list(st.session_state.keys()):
        if key not in ["schools_df", "transcript_df"]:
            del st.session_state[key]
    st.session_state["wizard_step"] = 1
    st.session_state["confirmed_package"] = None
    st.session_state["addon_state"] = False
    st.rerun()

# ==============================================================================
# 2. DATA LOADER
# ==============================================================================
SCHOOLS_CSV = "schools.csv"
TRANSCRIPT_CSV = "transcript_rules.csv"

if os.path.exists(SCHOOLS_CSV):
    try:
        master_schools_df = pd.read_csv(SCHOOLS_CSV, encoding='utf-8')
    except Exception:
        master_schools_df = pd.read_csv(SCHOOLS_CSV, encoding='latin1', errors='replace')
    for col in master_schools_df.select_dtypes(include=['object']).columns:
        master_schools_df[col] = master_schools_df[col].astype(str).str.strip()
else:
    st.error("⚠️ Master database file schools.csv not found.")
    st.stop()

if os.path.exists(TRANSCRIPT_CSV):
    try:
        transcript_rules_df = pd.read_csv(TRANSCRIPT_CSV, encoding='utf-8')
    except Exception:
        transcript_rules_df = pd.read_csv(TRANSCRIPT_CSV, encoding='latin1', errors='replace')
    for col in transcript_rules_df.select_dtypes(include=['object']).columns:
        transcript_rules_df[col] = transcript_rules_df[col].astype(str).str.strip()
    transcript_rules_df.columns = transcript_rules_df.columns.str.strip()
else:
    st.error("⚠️ Transcript validation file transcript_rules.csv not found.")
    st.stop()

# ==============================================================================
# 3. GLOBAL OPTIONS ARRAYS
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
# 4. WIZARD PROGRESS TRACKER RENDERER
# ==============================================================================
current_step = st.session_state["wizard_step"]

st.title("🗺️ Bridge Plan Generator")
st.markdown("### **Self-Serve Enrollment Matrix**")

# Interactive Progress Steps Bar Layout
step_cols = st.columns(4)
step_names = ["1. Identity Profile", "2. Professional Baseline", "3. Transcript Review", "4. Institutional Matches"]
for i, name in enumerate(step_names):
    step_num = i + 1
    with step_cols[i]:
        if current_step == step_num:
            st.markdown(f"<div style='text-align: center; border-bottom: 4px solid #1E3A8A; font-weight: bold; color: #1E3A8A; padding-bottom: 5px;'>{name}</div>", unsafe_allow_html=True)
        elif current_step > step_num:
            st.markdown(f"<div style='text-align: center; border-bottom: 4px solid #10B981; color: #10B981; padding-bottom: 5px;'>✅ {name}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align: center; border-bottom: 4px solid #e2e8f0; color: #94a3b8; padding-bottom: 5px;'>{name}</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# 5. DYNAMIC WORKFLOW ROUTER CHANNELS
# ==============================================================================
# Determine Layout Split Strategy: Full-width for steps 1-2, Split-width with Ledger for steps 3-4
if current_step >= 3:
    col_input_flow, col_ledger_flow = st.columns([1.4, 1.0], gap="large")
else:
    col_input_flow = st.container()
    col_ledger_flow = None

with col_input_flow:
    # --------------------------------------------------------------------------
    # WIZARD STEP 1: IDENTITY PROFILE
    # --------------------------------------------------------------------------
    if current_step == 1:
        st.markdown("### **Step 1: Welcome & Identity Profile**")
        st.markdown("Let's capture your baseline state territory parameters to filter institutional availability rules.")
        st.divider()
        
        st.text_input("What is your name?", placeholder="Enter full name", key="w_name")
        st.selectbox("Select your residency home state:", options=STATE_OPTIONS, index=0, key="w_state")
        st.text_input("What is your zip code?", placeholder="e.g. 19013", max_chars=14, key="w_zip")
        st.selectbox("Are you 18 years of age or older?", options=BINARY_OPTIONS, index=0, key="w_adult")
        st.number_input("What is your current cumulative GPA Score?", min_value=0.0, max_value=4.0, value=4.00, step=0.01, key="w_gpa")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Continue to Professional Baseline ➡️"):
            if st.session_state.get("w_state") == "Select state":
                st.warning("⚠️ Please select a valid state territory before moving forward.")
            elif st.session_state.get("w_adult") == "No":
                st.error("🛑 Registration Blocked: Applicants under 18 require internal agent authorization verification.")
            else:
                st.session_state["wizard_step"] = 2
                st.rerun()

    # --------------------------------------------------------------------------
    # WIZARD STEP 2: PROFESSIONAL BASELINE
    # --------------------------------------------------------------------------
    elif current_step == 2:
        st.markdown("### **Step 2: Professional Licensing & History**")
        st.markdown("Tell us about your healthcare background parameters to clear nursing experience validation layers.")
        st.divider()
        
        st.selectbox("What is your current nursing license tier?", options=LICENSE_OPTIONS, index=0, key="w_lic")
        
        # Conditional expansion based on license selected
        if st.session_state.get("w_lic") == "LPN":
            st.number_input("Total months of active LPN Work Experience:", min_value=0, max_value=120, value=0, step=1, key="w_exp")
            
        st.selectbox("Do you possess a prior academic nursing program dismissal?", options=DISMISSAL_OPTIONS, index=0, key="w_dismiss")
        
        # Conditional expansion based on dismissal selection
        if st.session_state.get("w_dismiss") == "Yes":
            st.number_input("Months elapsed since your historical academic dismissal date:", min_value=0, max_value=300, value=72, step=1, key="w_dismiss_mos")
            
        st.selectbox("Are you amenable to regional clinical onsite travel loops?", options=BINARY_OPTIONS, index=0, key="w_travel")
        st.selectbox("Which nursing program graduation credential tier are you targeting?", options=TRACK_OPTIONS, index=0, key="w_track")
        
        st.markdown("<br>", unsafe_allow_html=True)
        nav_b1, nav_b2 = st.columns(2)
        if nav_b1.button("⬅️ Back"):
            st.session_state["wizard_step"] = 1
            st.rerun()
        if nav_b2.button("Continue to Transcript Review ➡️"):
            st.session_state["wizard_step"] = 3
            st.rerun()

    # --------------------------------------------------------------------------
    # WIZARD STEP 3: TRANSCRIPT REVIEW
    # --------------------------------------------------------------------------
    elif current_step == 3:
        st.markdown("### **Step 3: Foundational Transcript Review**")
        st.markdown("Select any core prerequisite deficiencies you still need to fulfill. Your **Live Ledger Balance Cart** has now slid open on the right.")
        st.divider()
        
        needed_courses = st.multiselect(
            "Check the boxes for courses you still NEED to complete:",
            options=course_list,
            default=st.session_state.get("w_courses", []),
            key="w_courses"
        )
        
        # Core Class Addon Validation Triggers Area (Locked inside layout floor safety parameters)
        st.markdown("#### Add-on Packages Configuration")
        base_count = len(needed_courses)
        temp_base_classes = base_count if base_count > 0 else 1
        temp_main_p = 1179 if temp_base_classes >= 10 else (1229 if temp_base_classes >= 4 else 1289)
        baseline_only_total = temp_base_classes * temp_main_p
        
        if baseline_only_total >= 14500 and base_count > 0:
            st.warning("⚠️ Package ceiling limit reached ($14,500 Floor cap). Advanced add-on switches forced offline.")
            st.session_state["addon_state"] = False
            has_addons = False
        else:
            has_addons = st.checkbox("Include General Platform Support Add-ons?", value=st.session_state["addon_state"], key="chk_addon_wizard")
            
            # Recalculate package breach variables
            t_addons = 2 if has_addons else 0
            t_total_classes = temp_base_classes + t_addons
            t_main_p = 1179 if temp_base_classes >= 10 else (1229 if temp_base_classes >= 4 else 1289)
            t_addon_p = 749 if t_total_classes >= 10 else (799 if t_total_classes >= 4 else 859)
            projected_total = (temp_base_classes * t_main_p) + (t_addons * t_addon_p)
            
            if projected_total >= 14500 and (base_count > 0 or has_addons):
                st.error("🛑 Selection Defeated: Combined structural total breaches the $14,500 Package limit threshold rules.")
                st.session_state["addon_state"] = False
                st.rerun()
            else:
                st.session_state["addon_state"] = has_addons

        st.markdown("<br>", unsafe_allow_html=True)
        nav_b1, nav_b2 = st.columns(2)
        if nav_b1.button("⬅️ Back"):
            st.session_state["wizard_step"] = 2
            st.rerun()
        if nav_b2.button("Generate Institutional Matches ➡️"):
            st.session_state["wizard_step"] = 4
            st.rerun()

    # --------------------------------------------------------------------------
    # WIZARD STEP 4: INSTITUTIONAL MATCHES
    # --------------------------------------------------------------------------
    elif current_step == 4:
        st.markdown("### **Step 4: Secure Institutional Match Alignment**")
        st.markdown("Review the eligible educational institutions calculated from your intake profile parameters:")
        st.divider()
        
        # Extraction logic variables mapping
        student_state = st.session_state.get("w_state", "Select state")
        selected_state = str(student_state).strip().upper()
        selected_track = str(st.session_state.get("w_track", "ASN")).strip().upper()
        license_type = st.session_state.get("w_lic", "None")
        lpn_exp = st.session_state.get("w_exp", 0)
        gpa_val = st.session_state.get("w_gpa", 4.00)
        travel_ok = st.session_state.get("w_travel", "Yes")
        dismissal_y = True if st.session_state.get("w_dismiss") == "Yes" else False
        dismissal_months = st.session_state.get("w_dismiss_mos", 0)
        needed_courses = st.session_state.get("w_courses", [])
        has_addons = st.session_state.get("addon_state", False)
        
        # Financial variables mirroring values parsed dynamically
        base_count = len(needed_courses)
        base_classes = base_count if base_count > 0 else 1
        main_price = 1179 if base_classes >= 10 else (1229 if base_classes >= 4 else 1289)

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
        # MODAL INTELLIGENT INTERPRETER DIALOG MECHANISM
        # ==============================================================================
        @st.dialog("Confirm & Lock Enrollment Package")
        def render_institutional_modal(school_name, school_exam_type, school_exam_notes):
            st.markdown(f"### 📋 Reviewing: **{school_name}**")
            st.markdown("---")
            
            modal_base_count = len(needed_courses)
            modal_addons = 2 if has_addons else 0
            
            include_exam_prep = False
            classes_waived = 0
            waived_course_name = ""
            user_score_logged = ""
            
            # Calculation variables injection mapping parameters
            deposit_input = st.session_state.get("w_deposit_input", 0.0)
            grant_input = st.session_state.get("w_grant_input", 0.0)
            discount_match = True
            is_cna = "CNA/CMA" if license_type == "CNA/CMA" else "No"
            
            calc_dep_match = min(deposit_input, 1000.0) if (discount_match and deposit_input >= (150 if is_cna == "CNA/CMA" else 300)) else 0.0
            calc_referral = 50.0 if st.session_state.get("w_ref_input") == "Yes" else 0.0
            calc_military = 200.0 if st.session_state.get("w_mil_input") == "Yes" else 0.0
            calc_free_course = float(main_price) if st.session_state.get("w_promo_input") == "Yes" else 0.0
            modal_credits_sum = calc_dep_match + calc_referral + calc_military + calc_free_course + grant_input
            
            if school_exam_type in ["--", "", "nan"] or pd.isna(school_exam_type):
                st.info("ℹ️ **No Entrance Exam Required:** This institution does not mandate an entrance examination baseline parameter.")
            else:
                st.markdown(f"#### 🔒 Entrance Exam Compliance Gating")
                user_has_passed = st.radio(f"Have you already taken and passed the required **{school_exam_type}** exam?", ["No", "Yes"], horizontal=True)
                
                if user_has_passed == "No":
                    st.warning(f"⚠️ **Notice:** A passing {school_exam_type} score is required for enrollment. We have added the **{school_exam_type} Prep Course** to your bundle automatically.")
                    include_exam_prep = st.checkbox(f"Keep **{school_exam_type} Prep Course** included in cart?", value=True)
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
                                st.error(f"🛑 **Score Below Target:** Adding **{school_exam_type} Prep Course** to cart on an automated opt-out basis.")
                                include_exam_prep = st.checkbox(f"Keep **{school_exam_type} Prep Course** included in cart?", value=True)
                            elif matched_rule_type == "pass":
                                if age_limit_years:
                                    st.markdown("##### ⏳ Verification Check Required:")
                                    exam_age = st.slider(age_question_text, min_value=0, max_value=10, value=0)
                                    if exam_age > age_limit_years:
                                        st.error(f"🛑 **Score Expired:** Older than {age_limit_years} years. Adding Prep Course package.")
                                        include_exam_prep = st.checkbox(f"Keep **{school_exam_type} Prep Course** included in cart?", value=True)
                                    else: st.success(f"✅ Verified: Score is active and compliant for enrollment!")
                                else: st.success(f"✅ Verified: Applicant is compliant for the {school_exam_type} track.")
                            elif matched_rule_type == "retest":
                                st.warning(f"⚠️ **Admission Approved!** {custom_message}")
                                include_exam_prep = st.checkbox(f"Add **{school_exam_type} Advanced Retest Prep** to maximize credit exemptions?", value=True)
                            elif matched_rule_type == "exempt":
                                st.success(f"🎉 **Elite Score Unlocked!** Automatic exemption granted from **{waived_course_name}** (Saves {classes_waived * 3} credits).")

            st.markdown("---")
            st.markdown("#### Itemized Balance Preview")
            
            final_base_classes = modal_base_count if modal_base_count > 0 else 1
            if include_exam_prep: final_base_classes = (modal_base_count + 1) if modal_base_count > 0 else 1
            elif classes_waived > 0: final_base_classes = max(0, modal_base_count - classes_waived)
                
            final_total_classes = (modal_base_count if modal_base_count > 0 else 0) + (1 if include_exam_prep else 0) + modal_addons - classes_waived
            final_total_classes = max(0, final_total_classes)
            
            m_main_p = 1179 if final_base_classes >= 10 else (1229 if final_base_classes >= 4 else 1289)
            m_addon_p = 749 if final_total_classes >= 10 else (799 if final_total_classes >= 4 else 859)
            
            if modal_base_count == 0 and include_exam_prep: final_base_total = (1 * m_main_p) + (modal_addons * m_addon_p)
            elif modal_base_count == 0 and not include_exam_prep: final_base_total = (modal_addons * m_addon_p)
            else: final_base_total = (final_base_classes * m_main_p) + (modal_addons * m_addon_p)
                
            modal_final_total = max(0.0, final_base_total - modal_credits_sum)
            
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
                else: m_reg = 600

            c1, c2 = st.columns(2)
            c1.metric("Adjusted Base Total", f"${final_base_total:,.2f}")
            c2.metric("Registration Fee", f"${m_reg:,.2f}")
            st.metric("Final Balance Due", f"${modal_final_total:,.2f}")
            
            if st.button("🔒 Lock in Enrollment Package", key="modal_lock_btn"):
                st.session_state["confirmed_package"] = {
                    "school_name": school_name,
                    "student_name": st.session_state.get("w_name", "Unnamed Lead"),
                    "base_total": final_base_total,
                    "reg_fee": m_reg,
                    "final_total": modal_final_total,
                    "courses_included": needed_courses,
                    "entrance_exam_prep_added": include_exam_prep,
                    "entrance_exam_score_logged": user_score_logged,
                    "classes_waived_count": classes_waived,
                    "addons_active": has_addons
                }
                st.rerun()

        # Render list of dynamic cards
        if not filtered_df.empty:
            status_log, cash_yield_margins, deficiencies_resolved_log, exam_requirements_list, exam_notes_list = [], [], [], [], []
            for _, school_row in filtered_df.iterrows():
                raw_name = str(school_row["School Name"]).strip()
                exam_requirements_list.append(str(school_row.get("Entrance Exam", "--")).strip())
                exam_notes_list.append(str(school_row.get("Entrance Exam Notes", "")).strip())
                
                if "HERZ" in raw_name.upper() or "HERI" in raw_name.upper():
                    rule_row = transcript_rules_df[transcript_rules_df["School Name"].str.upper().str.contains("HERZ|HERI", na=False)]
                elif "EXCEL" in raw_name.upper():
                    rule_row = transcript_rules_df[transcript_rules_df["School Name"].str.upper().str.contains("EXCEL", na=False)]
                else: rule_row = transcript_rules_df[transcript_rules_df["School Name"].str.upper() == raw_name.upper()]
                
                offered_courses_count = 0
                has_all_courses = True
                school_accepted_list = []
                
                if not rule_row.empty:
                    for required_course in needed_courses:
                        if required_course in rule_row.columns:
                            if str(rule_row[required_course].values[0]).strip().upper() == "Y":
                                offered_courses_count += 1
                                school_accepted_list.append(required_course)
                            else: has_all_courses = False
                        else: has_all_courses = False
                    status_log.append("Perfect Match" if (len(needed_courses) == 0 or has_all_courses) else "Missing Needed CBE Courses")
                else: status_log.append("Perfect Match")
                    
                deficiencies_resolved_log.append(", ".join(school_accepted_list) if school_accepted_list else "None")
                school_revenue_potential = offered_courses_count * float(main_price)
                tuition_cost_raw = str(school_row.get("Tuition", "0")).replace("$", "").replace(",", "").strip()
                tuition_cost = pd.to_numeric(tuition_cost_raw, errors='coerce') if pd.isna(pd.to_numeric(tuition_cost_raw, errors='coerce')) == False else 0.0
                cash_yield_margins.append(max(0.0, school_revenue_potential - float(tuition_cost)))
                    
            filtered_df["Match Status"] = status_log
            filtered_df["Estimated Revenue Profit"] = cash_yield_margins
            filtered_df["Deficiencies Met"] = deficiencies_resolved_log
            filtered_df["Entrance Exam Requirement"] = exam_requirements_list
            filtered_df["Entrance Exam Notes Column"] = exam_notes_list

            final_display_df = filtered_df[["School Name", "Estimated Revenue Profit", "ASN/BSN", "Match Status", "Entrance Exam Requirement", "Entrance Exam Notes Column", "Deficiencies Met"]].copy()
            final_display_df["_sort_profit"] = pd.to_numeric(final_display_df["Estimated Revenue Profit"], errors="coerce").fillna(0.0)
            final_display_df = final_display_df.sort_values(by="_sort_profit", ascending=False)

            for idx, row in final_display_df.iterrows():
                with st.container(border=True):
                    sc1, sc2, sc3 = st.columns([1.5, 3.0, 1.5])
                    with sc1:
                        if st.button("Select School", key=f"btn_wiz_sel_{idx}"):
                            render_institutional_modal(row["School Name"], row["Entrance Exam Requirement"], row["Entrance Exam Notes Column"])
                    with sc2:
                        st.markdown(f"🏫 **{row['School Name']}** ({row['ASN/BSN']} Track)")
                        st.markdown(f"🧬 *Deficiencies Fulfilled:* `{row['Deficiencies Met']}`")
                    with sc3:
                        st.metric("Est Profit Margin", f"${row['_sort_profit']:,.2f}")
        else:
            st.warning("No partner institutions match your core background or geofencing matrix filters.")

        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("⬅️ Back to Transcript Review"):
            st.session_state["wizard_step"] = 3
            st.rerun()

# ==============================================================================
# 6. SLIDING FINANCIAL LEDGER SHOPPING CART COMPONENT
# ==============================================================================
if current_step >= 3 and col_ledger_flow is not None:
    with col_ledger_flow:
        st.markdown("<div style='background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #1E3A8A;'>", unsafe_allow_html=True)
        st.subheader("🛒 Itemized Invoice Cart")
        
        needed_courses = st.session_state.get("w_courses", [])
        has_addons = st.session_state.get("addon_state", False)
        license_type = st.session_state.get("w_lic", "None")
        
        is_completely_empty = (len(needed_courses) == 0 and not has_addons)
        base_classes = len(needed_courses) if len(needed_courses) > 0 else 1
        addons_count = 2 if has_addons else 0
        total_classes = (len(needed_courses) if len(needed_courses) > 0 else 0) + addons_count
        
        main_price = 1179 if base_classes >= 10 else (1229 if base_classes >= 4 else 1289)
        addon_price = 749 if total_classes >= 10 else (799 if total_classes >= 4 else 859)
        
        if len(needed_courses) == 0: base_total = (addons_count * addon_price)
        else: base_total = (base_classes * main_price) + (addons_count * addon_price)
        
        st.markdown("#### **Adjustments & Grants**")
        deposit_input = st.number_input("Enrollment Deposit Amount ($)", min_value=0.0, value=0.0, step=50.0, key="w_deposit_input")
        grant_input = st.number_input("Institutional Grant Amount ($)", min_value=0.0, value=0.0, step=50.0, key="w_grant_input")
        
        q_ref = st.radio("Referred by student/agent?", ["No", "Yes"], horizontal=True, key="w_ref_input")
        q_mil = st.radio("Affiliated with Military?", ["No", "Yes"], horizontal=True, key="w_mil_input")
        
        q_promo = "No"
        if len(needed_courses) >= 3:
            q_promo = st.radio("Possess free course promo code?", ["No", "Yes"], horizontal=True, key="w_promo_input")

        # Calculations
        dep_min = 150 if license_type == "CNA/CMA" else 300
        calc_dep_match = min(deposit_input, 1000.0) if (deposit_input >= dep_min) else 0.0
        calc_referral = 50.0 if q_ref == "Yes" else 0.0
        calc_military = 200.0 if q_mil == "Yes" else 0.0
        calc_free_course = float(main_price) if q_promo == "Yes" else 0.0
        
        credits_sum = calc_dep_match + calc_referral + calc_military + calc_free_course + grant_input
        final_total = max(0.0, base_total - credits_sum)
        pending_bal = max(0.0, final_total - deposit_input)
        
        is_cna = "CNA/CMA" if license_type == "CNA/CMA" else "No"
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

        st.divider()
        st.markdown(f"**Gross Base Tuition:** `${0.00 if is_completely_empty else base_total:,.2f}`")
        st.markdown(f"**Registration Fee:** `${0.00 if is_completely_empty else reg_fee:,.2f}`")
        st.markdown(f"**Waivers & Grants Applied:** `-${credits_sum:,.2f}`")
        st.markdown(f"## **Balance Due: ${0.00 if is_completely_empty else final_total:,.2f}**")
        st.markdown("</div>", unsafe_allow_html=True)

# Global Clear / Reset Footer Button
st.markdown("<br><br>", unsafe_allow_html=True)
if st.button("🔄 Restart Process from Beginning", type="secondary"):
    restart_wizard()

# Success state print block container
if st.session_state["confirmed_package"]:
    pkg = st.session_state["confirmed_package"]
    st.balloons()
    st.success(f"🎉 **Bridge Plan Successfully Finalized for {pkg['student_name']}!**")
    st.markdown(f"### Selected School Locked: **{pkg['school_name']}**")
    st.metric("Final Adjusted Price", f"${pkg['final_total']:,.2f}")
    with st.expander("📄 View Final Signed Voucher Audit Manifest"):
        st.json(pkg)
