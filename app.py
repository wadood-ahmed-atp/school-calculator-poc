# --------------------------------------------------------------------------
    # STEP 6: STANDALONE ENTRANCE EXAM SCREEN WORKSPACE (FIXED BRACKET OVERFLOW)
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
                    
                    # 🚀 ADVANCED BRACKET OVERFLOW PROTECTION
                    # First check if the user score simply blows past the highest bracket definition in the CSV
                    highest_possible_defined_score = 0.0
                    highest_defined_action = "fail"
                    highest_defined_msg = ""
                    highest_waived_count = 0
                    highest_waived_course = ""
                    
                    for rule in rules:
                        parts = rule.split(':')
                        if not parts or parts[0] == "": continue
                        condition = parts[0].strip()
                        
                        if '-' in condition:
                            try:
                                low, high = map(float, condition.split('-'))
                                if high > highest_possible_defined_score:
                                    highest_possible_defined_score = high
                                    highest_defined_action = parts[1].strip()
                                    highest_defined_msg = parts[2].strip() if len(parts) > 2 else ""
                                    if highest_defined_action == "exempt" and len(parts) > 3:
                                        highest_waived_count = int(parts[2].strip())
                                        highest_waived_course = parts[3].strip()
                            except ValueError: pass
                        elif '+' in condition:
                            try:
                                floor_val = float(condition.replace('+', ''))
                                if floor_val > highest_possible_defined_score:
                                    highest_possible_defined_score = floor_val
                                    highest_defined_action = parts[1].strip()
                                    if highest_defined_action == "exempt" and len(parts) > 3:
                                        highest_waived_count = int(parts[2].strip())
                                        highest_waived_course = parts[3].strip()
                            except ValueError: pass
                    
                    # Run standard range logic loop
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
                    
                    # ⚡ OVERRIDE SAFETY SWITCH: If score overflows the ceiling, naturally absorb it into the pass tier
                    if score_num > highest_possible_defined_score and highest_possible_defined_score > 0:
                        matched_rule_type = highest_defined_action
                        custom_message = highest_defined_msg
                        if highest_defined_action == "exempt":
                            classes_waived = highest_waived_count
                            waived_course_name = highest_waived_course

                    if score_num > 0:
                        if matched_rule_type == "fail":
                            st.error(f"🛑 This score is below the automatic waiver threshold. We've added a **{school_exam_type} Prep Course** to help you prepare.")
                            st.checkbox(f"Keep **{school_exam_type} Prep Course** included in my cost estimate?", key="customer_exam_prep_toggle")
                        elif matched_rule_type in ["pass", "exempt"]:
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
                                if matched_rule_type == "exempt":
                                    st.success(f"🎉 Exemption unlocked! You have successfully waived out of **{waived_course_name}**.")
                                else:
                                    st.success(f"✅ Verified: Entrance testing requirements successfully met!")
                                st.session_state["customer_exam_prep_toggle"] = False
                        elif matched_rule_type == "retest":
                            st.warning(f"⚠️ {custom_message}")
                            st.checkbox(f"Add **{school_exam_type} Advanced Retest Preparation** to your layout?", key="customer_exam_prep_toggle")

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
