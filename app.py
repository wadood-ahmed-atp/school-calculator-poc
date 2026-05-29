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

# Title & Description for Stakeholders
st.title("🎓 School Placement & Financial Calculator")
st.markdown("### **Proof of Concept Blueprint**")
st.caption("This interactive prototype maps Google Sheet matrix formulas and Apps Script UI triggers directly into a clean web architecture.")
st.divider()

# ==============================================================================
# 1. APPLICATION STATE / EMULATED DATABASE
# ==============================================================================
if 'mock_schools' not in st.session_state:
    st.session_state.mock_schools = pd.DataFrame([
        {"School Name": "Alpha University", "Program": "BSN", "Status": "ACCEPTS", "Base Classes": 5, "Reentry Requirement": "Yes"},
        {"School Name": "Beta College of Nursing", "Program": "ASN", "Status": "ACCEPTS", "Base Classes": 11, "Reentry Requirement": "None"},
        {"School Name": "Gamma Institute", "Program": "BSN", "Status": "CONDITIONAL", "Base Classes": 3, "Reentry Requirement": "None"},
        {"School Name": "Delta State School", "Program": "ASN", "Status": "ACCEPTS", "Base Classes": 12, "Reentry Requirement": "Yes"},
    ])

# ==============================================================================
# 2. SIDEBAR: LEAD INPUTS (Emulates 'Lead Inputs' tab)
# ==============================================================================
st.sidebar.header("📋 Lead Inputs")

if st.sidebar.button("🔄 Reset Form & Inputs"):
    st.rerun()

student_name = st.sidebar.text_input("Student Name", placeholder="Jane Doe")
program_interest = st.sidebar.selectbox("Program Track (A2/G2 Logic)", ["ASN", "BSN"])
is_cna = st.sidebar.selectbox("Is the student a CNA/CMA? (V2 Logic)", ["No", "CNA/CMA"])

st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ Setup & Triggers")
dismissal_y = st.sidebar.checkbox("Has Prior Dismissal? (C2 Trigger)", value=False)
entrance_exam = st.sidebar.checkbox("Include Entrance Exam Prep? (AB2 Trigger)", value=False)
has_addons = st.sidebar.checkbox("Add-ons Selected? (Z2:AB2 Trigger)", value=False)

st.sidebar.markdown("---")
st.sidebar.subheader("📚 Transcript Deficiencies ('Need')")
needs_list = ["Anatomy & Phys", "Microbiology", "Statistics", "English Comp", "Psychology"]
selected_needs = [need for need in needs_list if st.sidebar.checkbox(need, value=False)]

# ==============================================================================
# 3. INTERACTIVE CALCULATOR ENGINE (Emulates Formulas T2, V2, AA2, AB2)
# ==============================================================================
st.header("⚡ Financial Calculation Engine")

col_calc_input, col_calc_output = st.columns([1, 1])

with col_calc_input:
    st.subheader("Financial Adjustments")
    deposit_input = st.number_input("Deposit Paid ($) [W2 Input]", min_value=0.0, value=0.0, step=50.0)
    grant_input = st.number_input("Discount Grant Amount ($) [Z2 Input]", min_value=0.0, value=0.0, step=50.0)
    
    st.markdown("**Discounts Selected [X2 Array Logic]:**")
    discount_match = st.checkbox("Deposit Match")
    discount_referral = st.checkbox("Referral")
    discount_military = st.checkbox("Military")
    discount_free_course = st.checkbox("Free Course")

with col_calc_output:
    st.subheader("Live Ledger Math (Formulas AA2 / V2 / T2)")
    
    base_classes = 6 
    if entrance_exam:
        base_classes += 1
        
    addons_count = 2 if has_addons else 0
    total_classes = base_classes + addons_count
    
    main_price = 1179 if base_classes >= 10 else (1229 if base_classes >= 4 else 1289)
    addon_price = 749 if total_classes >= 10 else (799 if total_classes >= 4 else 859)
    base_total = (base_classes * main_price) + (addons_count * addon_price)
    
    dep_min = 150 if is_cna == "CNA/CMA" else 300
    calc_dep_match = min(deposit_input, 1000.0) if (discount_match and deposit_input >= dep_min) else 0.0
    calc_referral = 50.0 if discount_referral else 0.0
    calc_military = 200.0 if discount_military else 0.0
    calc_free_course = float(main_price) if discount_free_course else 0.0
    
    final_total = max(0.0, base_total - calc_dep_match - calc_referral - calc_military - calc_free_course - grant_input)
    
    if is_cna == "CNA/CMA":
        reg_fee = 150 if total_classes <= 2 else (175 if total_classes <= 7 else (200 if total_classes <= 10 else (250 if total_classes <= 15 else 300)))
    else:
        reg_fee = 300 if total_classes <= 2 else (325 if total_classes <= 7 else (375 if total_classes <= 10 else (475 if total_classes <= 15 else 600)))
        
    room_left = 14500 - final_total
    max_additional_addons = max(0, int(room_left // 749))
    projected_addons = addons_count + max_additional_addons

    m1, m2 = st.columns(2)
    m1.metric("Base Total (Before Credits)", f"${base_total:,.2f}")
    m2.metric("Registration Fee (V2 Formula)", f"${reg_fee}")
    
    m3, m4 = st.columns(2)
    m3.metric("Final Balance Due (AA2 Formula)", f"${final_total:,.2f}")
    m4.metric("Pending Balance (AB2 Formula)", f"${max(0.0, final_total - deposit_input):,.2f}")
    
    st.metric("Max Add-ons Room Left (T2 Formula)", f"{projected_addons} max courses")

st.divider()

# ==============================================================================
# 4. RANKED OUTPUT GRID (Emulates Formula A2 & UI Toggling Apps Script Logic)
# ==============================================================================
st.header("🏫 Ranked Schools Result Output Matrix")
st.caption("Replicates the nested multi-criteria sorting from Excel cell A2 + Apps Script responsive view handlers.")

filtered_df = st.session_state.mock_schools[st.session_state.mock_schools["Program"] == program_interest].copy()

filtered_df["Transcript Deficiencies Fixed"] = ", ".join(selected_needs) if selected_needs else "None"
filtered_df["Injected Modules"] = "Entrance Exam Prep" if entrance_exam else "Standard Entry"

columns_to_show = ["School Name", "Program", "Status", "Base Classes", "Transcript Deficiencies Fixed", "Injected Modules"]

if dismissal_y:
    filtered_df["Reentry Review Req."] = filtered_df["Reentry Requirement"]
    columns_to_show.append("Reentry Review Req.")
    st.info("💡 Apps Script Trigger Active: 'Reentry Review' Column N made visible due to selection updates.")

if has_addons:
    filtered_df["Add-ons Active"] = "Yes - Multi-Tier Pricing"
    columns_to_show.append("Add-ons Active")
    st.info("💡 Apps Script Trigger Active: 'Add-ons' Column R made visible dynamically.")

if discount_free_course:
    filtered_df["Free Course Token Allocation"] = "FREE COURSE CONVERTED"
    columns_to_show.append("Free Course Token Allocation")
    st.info("💡 Apps Script Trigger Active: 'Free Course Code' Column Y unhidden.")

st.dataframe(filtered_df[columns_to_show], use_container_width=True)

st.divider()

# ==============================================================================
# 5. DEVELOPER HANDOFF INSTRUCTIONS
# ==============================================================================
with st.expander("🛠️ Developer Architecture Blueprint & Code Mapping Notes"):
    st.markdown("""
    ### Technical Specification Notes for Core Integration
    Dear Developer, this POC translates legacy spreadsheet workbook code blocks directly into centralized, functional web blocks:
    
    1. **Formula A2 (Array Engine):** Mimicked using Pandas vector constraints `st.session_state.mock_schools[df['Program'] == program_interest]`. In production, this should map to an SQL `SELECT... INNER JOIN` targeting your institutional tables.
    2. **Formula AA2 (Pricing Ledger Matrix):** Translated natively into cascading Python parameters. Clean pricing bands (`1179`, `1229`, `1289`) are extracted away from cellular loops into procedural rules.
    3. **UI Triggers (`onEditHandler`):** Streamlit's implicit input states handle your dynamic column toggling automatically, removing the need for layout flush functions.
    """)
