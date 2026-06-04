import streamlit as st
import pandas as pd
import os
import re

# ==============================================================================
# 0. WEB PAGE CONFIG & ADVANCED RESPONSIVE CSS INJECTION
# ==============================================================================
st.set_page_config(page_title="Bridge Plan Generator", layout="wide")

st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    h1, h2, h3 {color: #1E3A8A;}
    
    .content-card {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    .stButton>button {
        border-radius: 6px;
        height: 42px;
        font-weight: bold;
        transition: all 0.2s ease-in-out;
    }
    
    div.primary-btn>div>button {
        background-color: #1E3A8A !important;
        color: white !important;
        border: none !important;
    }
    div.primary-btn>div>button:hover {
        background-color: #3B82F6 !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    div.secondary-btn>div>button {
        background-color: #ffffff !important;
        color: #475569 !important;
        border: 1px solid #cbd5e1 !important;
    }
    div.secondary-btn>div>button:hover {
        background-color: #f8f9fa !important;
        border-color: #94a3b8 !important;
    }

    @media (max-width: 992px) {
        div[data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
        }
        div[data-testid="stColumn"] {
            width: 100% !important;
            margin-left: 0px !important;
            margin-right: 0px !important;
            margin-bottom: 20px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 1. NEW: PERSISTENT WIZARD VALUE INITIALIZATION ENGINE
# ==============================================================================
if "wizard_step" not in st.session_state: st.session_state["wizard_step"] = 1
if "confirmed_package" not in st.session_state: st.session_state["confirmed_package"] = None
if "addon_state" not in st.session_state: st.session_state["addon_state"] = False

# Form Memory Values (Hydrated to preserve memory across step switches)
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
# 2. DATA LOADER
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
# 3. GLOBAL ARRAYS
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

current_step = st.session_state["wizard_step"]

st.title("🗺️ Bridge Plan Generator")
st.markdown("### **Self-Serve Enrollment Matrix**")

# Interactive Progress Indicator Bar Layout
step_cols = st.columns(4)
step_names = ["1. Identity Profile", "2. Baseline Profile", "3. Transcripts Review", "4. School Matches"]
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
# 4. ADAPTIVE RESPONSIVE LAYOUT ENGINE ROUTER
# ==============================================================================
if current_step >= 3:
    col_input_flow, col_ledger_flow = st.columns([1.5, 1.0], gap="large")
else:
    col_input_flow = st.container()
    col_ledger_flow = None

with col_input_flow:
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # STEP 1: IDENTITY PROFILE
    # --------------------------------------------------------------------------
    if current_step == 1:
        st.markdown("### **Step 1: Welcome & Identity Profile**")
        st.markdown("Let's capture your baseline territory parameters to filter institutional regional availability.")
        st.divider()
        
        # Wired with explicit key/value bindings to preserve internal memory state
        i_name = st.text_input("What is your name?", value=st.session_state["val_name"], placeholder="Enter full name")
        i_state = st.selectbox("Select your residency home state:", options=STATE_OPTIONS, index=STATE_OPTIONS.index(st.session_state["val_state"]))
        i_zip = st.text_input("What is your zip code?", value=st.session_state["val_zip"], placeholder="e.g. 19013", max_chars=14)
        i_adult = st.selectbox("Are you 18 years of age or older?", options=BINARY_OPTIONS, index=BINARY_OPTIONS.index(st.session_state["val_adult"]))
        i_gpa = st.number_input("What is your current cumulative GPA Score?", min_value=0.0, max_value=4.0, value=st.session_state["val_gpa"], step=0.01)
        
        st.divider()
        btn_spacer, btn_container = st.columns([2.5, 1.0])
        with btn_container:
            st.markdown("<div class='primary-btn'>", unsafe_allow_html=True)
            if st.button("Continue to Profile ➡️", use_container_width=True):
                if i_state == "Select state":
                    st.warning("⚠️ Please select a valid state territory before moving forward.")
                elif i_adult == "No":
                    st.error("🛑 Registration Blocked: Applicants under 18 require internal agent validation verification.")
                else:
                    # Save local values into persistent vaults before step progression
                    st.session_state["val_name"] = i_name
                    st.session_state["val_state"] = i_state
                    st.session_state["val_zip"] = i_zip
                    st.session_state["val_adult"] = i_adult
                    st.session_state["val_gpa"] = i_gpa
                    
                    st.session_state["wizard_step"] = 2
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # STEP 2: PROFESSIONAL BASELINE
    # --------------------------------------------------------------------------
    elif current_step == 2:
        st.markdown("### **Step 2: Professional Licensing & History**")
        st.markdown("Tell us about your healthcare background parameters to clear nursing experience validation layers.")
        st.divider()
        
        i_lic = st.selectbox("What is your current nursing license tier?", options=LICENSE_OPTIONS, index=LICENSE_OPTIONS.index(st.session_state["val_lic"]))
        
        i_exp = st.session_state["val_exp"]
        if i_lic == "LPN":
            i_exp = st.number_input("Total months of active LPN Work Experience:", min_value=0, max_value=120, value=st.session_state["val_exp"], step=1)
            
        i_dismiss = st.selectbox("Do you possess a prior academic nursing program dismissal?", options=DISMISSAL_OPTIONS, index=DISMISSAL_OPTIONS.index(st.session_state["val_dismiss"]))
        
        i_dismiss_mos = st.session_state["val_dismiss_mos"]
        if i_dismiss == "Yes":
            i_dismiss_mos = st.number_input("Months elapsed since your historical academic dismissal date:", min_value=0, max_value=300, value=st.session_state["val_dismiss_mos"], step=1)
            
        i_travel = st.selectbox("Are you amenable to regional clinical onsite travel loops?", options=BINARY_OPTIONS, index=BINARY_OPTIONS.index(st.session_state["val_travel"]))
        i_track = st.selectbox("Which nursing program graduation credential tier are you targeting?", options=TRACK_OPTIONS, index=TRACK_OPTIONS.index(st.session_state["val_track"]))
        
        st.divider()
        btn_spacer, btn_b1, btn_b2 = st.columns([1.5, 0.9, 1.1])
        with btn_b1:
            st.markdown("<div class='secondary-btn'>", unsafe_allow_html=True)
            if st.button("⬅️ Back", use_container_width=True):
                # Save data state even when moving backwards
                st.session_state["val_lic"] = i_lic
                st.session_state["val_exp"] = i_exp
                st.session_state["val_dismiss"] = i_dismiss
                st.session_state["val_dismiss_mos"] = i_dismiss_mos
                st.session_state["val_travel"] = i_travel
                st.session_state["val_track"] = i_track
                
                st.session_state["wizard_step"] = 1
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        with btn_b2:
            st.markdown("<div class='primary-btn'>", unsafe_allow_html=True)
            if st.button("Continue ➡️", use_container_width=True):
                st.session_state["val_lic"] = i_lic
                st.session_state["val_exp"] = i_exp
                st.session_state["val_dismiss"] = i_dismiss
                st.session_state["val_dismiss_mos"] = i_dismiss_mos
                st.session_state["val_travel"] = i_travel
                st.session_state["val_track"] = i_track
                
                st.session_state["wizard_step"] = 3
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # STEP 3: TRANSCRIPT REVIEW
    # --------------------------------------------------------------------------
    elif current_step == 3:
        st.markdown("### **Step 3: Foundational Transcript Review**")
        st.markdown("Select any core prerequisite deficiencies you still need to fulfill. Your **Live Ledger Balance Cart** has now slid open on the right.")
        st.divider()
        
        i_courses = st.multiselect(
            "Check the boxes for courses you still NEED to complete:",
            options=course_list,
            default=st.session_state["val_courses"]
        )
        
        st.markdown("#### Add-on Packages Configuration")
        base_count = len(i_courses)
        temp_base_classes = base_count if base_count > 0 else 1
        temp_main_p = 1179 if temp_base_classes >= 10 else (1229 if temp_base_classes >= 4 else 1289)
        baseline_only_total = temp_base_classes * temp_main_p
        
        if baseline_only_total >= 14500 and base_count > 0:
            st.warning("⚠️ Package ceiling limit reached ($14,500 Floor cap). Advanced add-on switches forced offline.")
            st.session_state["addon_state"] = False
            has_addons = False
        else:
            has_addons = st.checkbox("Include General Platform Support Add-ons?", value=st.session_state["addon_state"])
            t_addons = 2 if has_addons else 0
            t_total_classes = temp_base_classes + t_addons
            t_main_p = 1179 if temp_base_classes >= 10 else (1229 if temp_base_classes >= 4 else 1289)
            t_addon_p = 749 if t_total_classes >= 10 else (799 if t_total_classes >= 4 else 859)
            projected_total = (temp_base_classes * t_main_p) + (t_addons * t_addon_p)
            
            if projected_total >= 14500 and (base_count > 0 or has_addons):
                st.error("🛑 Selection Defeated: Combined total breaches the $14,500 Package threshold rules.")
                st.session_state["addon_state"] = False
                st.rerun()
            else:
                st.session_state["addon_state"] = has_addons

        st.divider()
        btn_spacer, btn_b1, btn_b2 = st.columns([1.5, 0.9, 1.1])
        with btn_b1:
            st.markdown("<div class='secondary-btn'>", unsafe_allow_html=True)
            if st.button("⬅️ Back", use_container_width=True):
                st.session_state["val_courses"] = i_courses
                st.session_state["wizard_step"] = 2
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        with btn_b2:
            st.markdown("<div class='primary-btn'>", unsafe_allow_html=True)
            if st.button("Find Matches ➡️", use_container_width=True):
                st.session_state["val_courses"] = i_courses
                st.session_state["wizard_step"] = 4
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # STEP 4: INSTITUTIONAL MATCHES
    # --------------------------------------------------------------------------
    elif current_step == 4:
        st.markdown("### **Step 4: Secure Institutional Match Alignment**")
        st.markdown("Review the eligible educational institutions calculated from your intake profile parameters:")
        st.divider()
        
        # Read from persistent memory structures
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
        has_addons = st.session_state["addon_state"]
        
        base_count = len(needed_courses)
        base_classes = base_count if base_count > 0 else 1
        main_price = 1179 if base_classes >= 10 else (1229 if base_classes >= 4 else 1289)

        working_schools_df = master_schools_df.copy()
        if "ASN/BSN" in working_schools_df.columns:
