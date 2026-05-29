import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Data Debugger Tool", layout="wide")

st.title("🔍 Multi-CSV Database Debugger Dashboard")
st.markdown("This version prints out exactly what Python sees in your files to catch formatting errors instantly.")
st.divider()

# ==============================================================================
# 1. RAW FILE INSPECTOR
# ==============================================================================
st.header("📁 Step 1: File Presence Check")
schools_exist = os.path.exists("schools.csv")
rules_exist = os.path.exists("transcript_rules.csv")

c1, c2 = st.columns(2)
with c1:
    st.metric("schools.csv Loaded?", "YES" if schools_exist else "NO")
with c2:
    st.metric("transcript_rules.csv Loaded?", "YES" if rules_exist else "NO")

if not schools_exist or not rules_exist:
    st.error("Stop! Both files must be uploaded to GitHub for the engine to connect.")
    st.stop()

# Load files
df_schools = pd.read_csv("schools.csv")
df_rules = pd.read_csv("transcript_rules.csv")

# Clean column spaces just for display safety
df_schools.columns = df_schools.columns.str.strip()
df_rules.columns = df_rules.columns.str.strip()

st.divider()

# ==============================================================================
# 2. MATCHING LOGIC CHECK
# ==============================================================================
st.header("🔀 Step 2: Critical Header Mappings")

st.subheader("📋 Core Dataset Headers (From schools.csv)")
st.write(list(df_schools.columns))

st.subheader("📚 Transcript Mapping Headers (From transcript_rules.csv)")
st.write(list(df_rules.columns))

st.divider()

st.header("🏫 Step 3: School Name Alignment Map")
st.caption("For the engine to work, names on the left must match names on the right EXACTLY character-for-character.")

schools_list_A = df_schools["School Name"].dropna().unique().tolist()
schools_list_B = df_rules["School Name"].dropna().unique().tolist()

col_a, col_b = st.columns(2)
with col_a:
    st.markdown("**Names in `schools.csv`:**")
    st.write(schools_list_A)
with col_b:
    st.markdown("**Names in `transcript_rules.csv`:**")
    st.write(schools_list_B)

st.divider()

# ==============================================================================
# 4. LIVE FILTER SIMULATION
# ==============================================================================
st.header("⚡ Step 4: Live Data Interrogation")

# Simple Interactive Controls
interest = st.selectbox("Select Track to Test", ["ASN", "BSN"])
state_test = st.text_input("Enter State to Test (Caps)", value="KY")
course_test = st.selectbox("Select Course to Test Requirement", list(df_rules.columns)[1:])

st.markdown("### **Simulation Output Table:**")

# Run basic track filtering
mask1 = df_schools["ASN/BSN"].astype(str).str.upper() == interest.upper()
res = df_schools[mask1].copy()

# Run basic state filtering
mask2 = res["States Accepted"].astype(str).str.upper().str.contains(state_test.upper())
res = res[mask2]

if not res.empty:
    st.subheader("Matched from Demographics Profile:")
    st.dataframe(res[["School Name", "ASN/BSN", "States Accepted"]])
    
    st.subheader("Transcript Matrix Lookup Status:")
    for idx, row in res.iterrows():
        s_name = row["School Name"]
        match_rule = df_rules[df_rules["School Name"].astype(str).str.strip().str.upper() == str(s_name).strip().upper()]
        
        if not match_rule.empty:
            val = match_rule[course_test].values[0]
            st.info(f" School: **{s_name}** | Column checked: '{course_test}' | Value found in row: **'{val}'**")
        else:
            st.error(f"❌ School **{s_name}** is missing completely from your transcript_rules.csv tab!")
else:
    st.warning("No data found matching those basic track and state profiles.")
