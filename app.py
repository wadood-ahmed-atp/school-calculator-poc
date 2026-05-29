import streamlit as st
import pandas as pd
import os

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
st.markdown("### **Production Matrix Engine (High-Legibility Model)**")
st.divider()

# ==============================================================================
# 1. DUAL-DATABASE DATA LOADER
# ==============================================================================
SCHOOLS_CSV = "schools.csv"
TRANSCRIPT_CSV = "transcript_rules.csv"

# Load Master School Dataset
if os.path.exists(SCHOOLS_CSV):
    master_schools_df = pd.read_csv(SCHOOLS_CSV)
    for col in master_schools_df.select_dtypes(include=['object']).columns:
        master_schools_df[col] = master_schools_df[col].astype(str).str.strip()
else:
    st.error(f"⚠️ Master database file '{SCHOOLS_CSV}' not found in your GitHub repository.")
    st.stop()

# Load Transcript Review Dataset Matrix
if os.path.exists(TRANSCRIPT_CSV):
    transcript_rules_df = pd.read_csv(TRANSCRIPT_CSV)
    for col in transcript_rules_df.select_dtypes(include=['object']).columns:
        transcript_rules_df[col] = transcript_rules_df[col].astype(str).str.strip()
    transcript_rules_df.columns = transcript_rules_df.columns.str.strip()
else:
    st.error(f"⚠️ Transcript validation file '{TRANSCRIPT_CSV}' not found in your GitHub repository.")
    st.stop()

# ==============================================================================
# 2. SIDEBAR: LEAD INPUTS & MULTI-COURSE TRANSCRIPT MATRIX
# ==============================================================================
st.sidebar.header("📋 Lead Inputs")

if st.sidebar.button("🔄 Reset Form & Inputs"):
    st.rerun()

student_name = st.sidebar.text_input("Student Name", value="Jane Doe")

# 1. Student State
student_state = st.sidebar.selectbox("Student State", [
    "KY", "NY", "Y", "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", 
    "HI", "ID", "IL", "IN", "IA", "KS", "LA", "ME", "MD", 
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
])

# 2. GPA
gpa_val = st.sidebar.number_input("GPA Score", min_value=0.0, max_value=4.0, value=4.0, step=0.1)

# 3. Prior Nursing Dismissal?
dismissal_selection = st.sidebar.selectbox("Prior Nursing Dismissal?", ["No", "Yes"])
dismissal_y = True if dismissal_selection == "Yes" else False

# 4. LPN or CNA/CMA License?
license_type = st.sidebar.selectbox("LPN or CNA/CMA License?", ["LPN", "CNA/CMA", "None"])
is_cna = "CNA/CMA" if license_type == "CNA/CMA" else "No"

# 5. Months of LPN Work Experience
lpn_exp = 0
if license_type == "LPN":
    lpn_exp = st.sidebar.number_input("Months of LPN Work Experience", min_value=0, max_value=120, value=6)

# 6. Travel for Clinicals ok?
travel_ok = st.sidebar.selectbox("Travel for Clinicals ok?", ["Yes", "No"])

# 7. ASN or BSN
program_interest = st.sidebar.selectbox("Program Track: ASN or BSN", ["ASN", "BSN"])

st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ Class Triggers")
entrance_exam = st.sidebar.checkbox("Include Entrance Exam Prep? (AB2 Trigger)", value=False)
has_addons = st.sidebar.checkbox("Add-ons Selected? (Z2:AB2 Trigger)", value=False)

st.sidebar.markdown("---")
st.sidebar.subheader("📚 Transcript Review
