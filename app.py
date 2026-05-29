import streamlit as st
import pandas as pd

# ==============================================================================
# 0. WEB PAGE CONFIG & STYLING
# ==============================================================================
st.set_page_config(page_title="School Placement & Calculator POC", layout="wide")

st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    h1, h2, h3 {color: #1E3A8A;}
    .stButton>button {background-color: #1E3A8A; color: white; border-radius: 5px;}
    .stButton>button:hover {background-color: #3B82F6; color: white;}
    div[data-testid="stMetricValue"] {font-size: 24px; color: #10B981;}
    </style>
""", unsafe_allow_html=True)

st.title("🎓 School Placement & Financial Calculator")
st.markdown("### **Proof of Concept Blueprint**")
st.caption("This interactive prototype maps Google Sheet matrix formulas and Apps Script UI triggers directly into a clean web architecture.")
st.divider()

# ==============================================================================
# 1. ACTUAL PARTNER DATABASE MATRIX (FIXED: State explicitly defined for all rows)
# ==============================================================================
if 'mock_schools' not in st.session_state:
    st.session_state.mock_schools = pd.DataFrame([
        # BSN Schools
        {"School Name": "Western Governors University", "Program": "BSN", "State": "KY, Y", "Status": "ACCEPTS", "Base Classes": 4, "Reentry Requirement": "None"},
        {"School Name": "Herzing University BSN", "Program": "BSN", "State": "KY, Y", "Status": "ACCEPTS", "Base Classes": 6, "Reentry Requirement": "None"},
        {"School Name": "Capella University", "Program": "BSN", "State": "KY, Y", "Status": "ACCEPTS", "Base Classes": 5, "Reentry Requirement": "None"},
        {"School Name": "Chamberlain University", "Program": "BSN", "State": "KY, Y", "Status": "ACCEPTS", "Base Classes": 7, "Reentry Requirement": "None"},
        
        # ASN Schools
        {"School Name": "Herzing University ASN", "Program": "ASN", "State": "KY, Y", "Status": "ACCEPTS", "Base Classes": 5, "Reentry Requirement": "None"},
        {"School Name": "Excelsior University", "Program": "ASN", "State": "NY, KY, Y", "Status": "ACCEPTS", "Base Classes": 6, "Reentry Requirement": "None"}
    ])

# ==============================================================================
# 2. SIDEBAR: LEAD INPUTS & MULTI-COURSE TRANSCRIPT MATRIX
# ==============================================================================
st.sidebar.header("📋 Lead Inputs")

if st.sidebar.button("🔄 Reset Form & Inputs"):
    st.rerun()

student_name = st.sidebar.text_input("Student Name", value="Jane Doe")

# 1. Student State
student_state = st.sidebar.selectbox("Student State", [
    "NY", "KY", "Y", "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", 
    "HI", "ID", "IL", "IN", "IA", "KS", "LA", "ME", "MD", 
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
])

# 2. GPA
gpa_input = st.sidebar.text_input("GPA (Leave Blank if unsure)", value="4.00")

# 3. Prior Nursing Dismissal?
dismissal_selection = st.sidebar.selectbox("Prior Nursing Dismissal?", ["No", "Yes"])
dismissal_y = True if dismissal_selection == "Yes" else False

# 4. LPN or CNA/CMA License?
license_type = st.sidebar.selectbox("LPN or CNA/CMA License?", ["LPN", "CNA/CMA", "None"])
is_cna = "CNA/CMA" if license_type == "CNA/CMA" else "No"

# 5. Months of LPN Work Experience
lpn_exp = 0
if license_type == "LPN":
    lpn_exp = st.sidebar.number_input("Months of LPN Work Experience", min_value=0, max_value=24, value=6)

# 6. Travel for Clinicals ok?
travel_ok = st.sidebar.selectbox("Travel for Clinicals ok?", ["Yes", "No"])

# 7. ASN or BSN
program_interest = st.sidebar.selectbox("Program Track: ASN or BSN (A2/G2 Logic)", ["ASN", "BSN"])

st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ Class Triggers")
entrance_exam = st.sidebar.checkbox("Include Entrance Exam Prep? (AB2 Trigger)", value=False)
has_addons = st.sidebar.checkbox("Add-ons Selected? (Z2:AB2 Trigger)", value=False)

# 📚 Comprehensive Transcript Status Board
st.sidebar.markdown("---")
st.sidebar.subheader("📚 Transcript Review Engine")
st.sidebar.caption("Toggle courses between Taken and Needed to feed Formula A2 array filters.")

course_list =
