import streamlit as st
import pandas as pd
import os

# ==============================================================================
# 0. WEB PAGE CONFIG & STYLING
# ==============================================================================
st.set_page_config(page_title="Advisor Dashboard", layout="wide")

st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    h1, h2, h3 {color: #1E3A8A;}
    .stButton>button {background-color: #1E3A8A; color: white; border-radius: 5px;}
    .stButton>button:hover {background-color: #3B82F6; color: white;}
    div[data-testid="stMetricValue"] {font-size: 24px; color: #10B981;}
    </style>
""", unsafe_allow_html=True)

st.title("🎓 Advisor Dashboard")
st.markdown("### **System Framework Matrix**")
st.divider()

# ==============================================================================
# 1. DUAL-DATABASE DATA LOADER
# ==============================================================================
SCHOOLS_CSV = "schools.csv"
TRANSCRIPT_CSV = "transcript_rules.csv"

if os.path.exists(SCHOOLS_CSV):
    master_schools_df = pd.read_csv(SCHOOLS_CSV)
    for col in master_schools_df.select_dtypes(include=['object']).columns:
        master_schools_df[col] = master_schools_df[col].astype(str).str.strip()
else:
    st.error("⚠️ Master database file schools.csv not found.")
    st.stop()

if os.path.exists(TRANSCRIPT_CSV):
    transcript_rules_df = pd.read_csv(TRANSCRIPT_CSV)
    for col in transcript_rules_df.select_dtypes(include=['object']).columns:
        transcript_rules_df[col] = transcript_rules_df[col].astype(str).str.strip()
    transcript_rules_df.columns = transcript_rules_df.columns.str.strip()
else:
    st.error("⚠️ Transcript validation file transcript_rules.csv not found.")
    st.stop()

# ==============================================================================
# 2. DEFINED ARRAYS WITH STAKEHOLDER PLACEHOLDERS
# ==============================================================================
STATE_OPTIONS = [
    "Select state", "FL", "GA", "WI", "AL", "DC", "KY", "NY", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", 
    "HI", "ID", "IL", "IN", "IA", "KS", "LA", "ME", "MD", 
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
    "NM", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]
BINARY_OPTIONS = ["Yes", "No"]
DISMISSAL_OPTIONS = ["No", "Yes"]
LICENSE_OPTIONS = ["None", "LPN", "CNA/CMA"]
TRACK_OPTIONS = ["BSN", "ASN"]

if "reset_counter" not in st.session_state: 
    st.session_state["reset_counter"] = 0
if "exam_state" not in st.session_state: 
    st.session_state["exam_state"] = False
if "addon_state" not in st.session_state: 
    st.session_state["addon_state"] = False

st.sidebar.header("📋 Lead Profile")

# Clear Reset Flow
if st.sidebar.button("🔄 Reset Form"):
    st.session_state["reset_counter"] += 1
    st.session_state["exam_state"] = False
    st.session_state["addon_state"] = False
    st.rerun()

version = st.session_state["reset_counter"]

# ==============================================================================
# 3. SIDEBAR WITH WIDGET PLACEHOLDERS & CONDITIONAL VISIBILITY
# ==============================================================================
student_name = st.sidebar.text_input("Student Name", placeholder="Enter Your name", value="", key=f"name_{version}")
student_state = st.sidebar.selectbox("Lead State", options=STATE_OPTIONS, index=0, key=f"state_{version}")
student_zip = st.sidebar.text_input("Zip Code", placeholder="Enter Your Zip", value="", max_chars=14, key=f"zip_{version}")

is_adult = st.sidebar.selectbox("Are you 18 years of age or older?", options=BINARY_OPTIONS, index=0, key=f"adult_{version}")
gpa_val = st.sidebar.number_input("What is your GPA Score?", min_value=0.0, max_value=4.0, value=4.00, step=0.01, key=f"gpa_{version}")

dismissal_selection = st.sidebar.selectbox("Do you have a prior nursing dismissal?", options=DISMISSAL_OPTIONS, index=0, key=f"dismiss_{version}")
dismissal_y = True if dismissal_selection == "Yes" else False

dismissal_months = 0
if dismissal_y:
    dismissal_months = st.sidebar.number_input("Months since your dismissal", min_value=0, max_value=300, value=72, step=1, key=f"dismiss_mos_{version}")

license_type = st.sidebar.selectbox("What is your current nursing license?", options=LICENSE_OPTIONS, index=0, key=f"lic_{version}")
is_cna = "CNA/CMA" if license_type == "CNA/CMA" else "No"

# Dynamic Visibility Gate for LPN Experience Tracking Box
lpn_exp = 0
if license_type == "LPN":
    lpn_exp = st.sidebar.number_input("Months of LPN Experience (If less than 2 yrs)", min_value=0, max_value=120, value=0, step=1, key=f"exp_{version}")

travel_ok = st.sidebar.selectbox("Are you okay with local clinical travel?", options=BINARY_OPTIONS, index=0, key=f"travel_{version}")
program_interest = st.sidebar.selectbox("Which track are you interested in?", options=TRACK_OPTIONS, index=0, key=f"track_{version}")

st.sidebar.markdown("---")
st.sidebar.subheader("📚 Transcript Review")

course_list = [
    "Eng Comp 1", "College Algebra", "Statistics", "Humanities 1", 
    "Humanities 2", "Humanities 3", "Human Growth & Development", 
    "Psychology", "Sociology", "Speech", "General Biology", 
    "Chemistry", "Government", "History", "Foreign Language", 
    "Macro/Micro Economics", "Elective 1", "Elective 2"
]

needed_courses = st.sidebar.multiselect(
    "Select Needed Courses:",
    options=course_list,
    default=[],
    key=f"courses_{version}"
)

selected_track = str(program_interest).strip().upper()
selected_state = str(student_state).strip().upper()

# ==============================================================================
# 4. MAIN INTERACTIVE RENDERING / COMPLIANCE GATING
# ==============================================================================
if is_adult == "No":
    st.error("🛑 **Self-Serve Checkout Unavailable**")
    st.info(f"### **Next Steps Required for {student_name if student_name else 'Applicant'}:**\nApplicants under the age of 18 are not permitted to complete an independent digital registration or contract confirmation. \n\nTo advance your enrollment matrix, please schedule an appointment to speak with an admissions representative. \n**Note:** A parent, legal guardian, or sponsoring adult must accompany the applicant during the consultation call.")
elif student_state == "Select state":
    st.warning("⚠️ **Lead State Required:** Please select a valid state territory from the sidebar dropdown list to unlock matrix filtering features.")
else:
    # --- BACKGROUND PRE-FLIGHT BALANCING & COMPLIANCE GUARD ENGINE ---
    mock_base_classes = len(needed_courses) if len(needed_courses) > 0 else 1
    if st.session_state["exam_state"]: mock_base_classes += 1
    mock_addons_count = 2 if st.session_state["addon_state"] else 0

    mock_main_price = 1179 if mock_base_classes >= 10 else (1229 if mock_base_classes >= 4 else 1289)
    mock_addon_price = 749 if (mock_base_classes + mock_addons_count) >= 10 else (799 if (mock_base_classes + mock_addons_count) >= 4 else 859)
    mock_grand_total = (mock_base_classes * mock_main_price) + (mock_addons_count * mock_addon_price)

    if mock_grand_total >= 14500:
        st.session_state["exam_state"] = False
        st.session_state["addon_state"] = False
        mock_base_classes = len(needed_courses) if len(needed_courses) > 0 else 1
        mock_main_price = 1179 if mock_base_classes >= 10 else (1229 if mock_base_classes >= 4 else 1289)
        mock_grand_total = mock_base_classes * mock_main_price

    st.sidebar.markdown("---")
    st.sidebar.subheader("🛠️ Class Triggers")

    if mock_grand_total < 14500:
        entrance_exam = st.sidebar.checkbox("Include Entrance Exam Prep?", value=st.session_state["exam_state"], key=f"chk_exam_{version}")
        has_addons = st.sidebar.checkbox("Add-ons Selected?", value=st.session_state["addon_state"], key=f"chk_addon_{version}")
        st.session_state["exam_state"] = entrance_exam
        st.session_state["addon_state"] = has_addons
    else:
        st.sidebar.warning("⚠️ Package limit reached ($14,500 Floor). Add-on triggers forced off.")
        entrance_exam = False
        has_addons = False

    # --- FINANCIAL LEDGER ENGINE VIEW ---
    st.header("⚡ Financial Ledger")
    col_calc_input, col_calc_output = st.columns([1, 1])

    with col_calc_input:
        st.subheader("Adjustments & Waivers")
        deposit_input = st.number_input("Enrollment Deposit Paid ($)", min_value=0.0, value=0.0, step=50.0, key=f"dep_in_{version}")
        grant_input = st.number_input("Grant Allocation ($)", min_value=0.0, value=0.0, step=50.0, key=f"grant_in_{version}")
        
        st.markdown("#### **Qualification Profile**")
        st.info("✅ **Deposit Match Program:** Automatically applied.")
        discount_match = True
        
        q_referral = st.radio("Were you referred by someone?", ["No", "Yes"], horizontal=True, key=f"ref_{version}")
        discount_referral = True if q_referral == "Yes" else False
        
        q_military = st.radio("Are you associated with the military (Veteran/Active/Spouse)?", ["No", "Yes"], horizontal=True, key=f"mil_{version}")
        discount_military = True if q_military == "Yes" else False
        
        discount_free
