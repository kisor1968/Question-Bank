import streamlit as st
import pandas as pd

# --- PAGE CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="Prabhu Jagatbandhu College - Academic Repository",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS for light blue background, blue theme accents, and header alignment
st.markdown("""
<style>
    .stApp {
        background-color: #EBF4FF;
    }
    [data-testid="stSidebar"] {
        background-color: #D6E4FD;
    }
    h1, h2, h3 {
        color: #1E3A8A;
    }
</style>
""", unsafe_allow_html=True)

# --- GOOGLE SHEET CONFIGURATION ---
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTmVbhktPZiOsXXra7mqjElbUVxybeBGAMSqloH3kTrjXe0nziwqfYMf-gU7AjNDI_inkHQHLgZ61ki/pub?gid=1748417763&single=true&output=csv"
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/19b_w04j5vIQl1U2SvAfzcqhcVwW_cU6FlYGL5d4qk9U/viewform"
FACULTY_PASSWORD = "PJC_Faculty@2026"

@st.cache_data(ttl=30)
def load_sheet_data():
    if not SHEET_CSV_URL:
        return pd.DataFrame()
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        df = df.dropna(how='all')
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Format year column to integer string to prevent float representation (e.g., 2024.0 -> 2024)
        year_col_name = next((col for col in df.columns if any(k in col.lower() for k in ['year', 'exam'])), None)
        if year_col_name and year_col_name in df.columns:
            df[year_col_name] = pd.to_numeric(df[year_col_name], errors='coerce').fillna(0).astype(int).astype(str)
            df.loc[df[year_col_name] == '0', year_col_name] = ""
            
        return df
    except Exception:
        return pd.DataFrame()

# Helper function to convert Google Drive link to preview format
def get_embeddable_url(url):
    if not url or not isinstance(url, str):
        return ""
    url = url.strip()
    if "drive.google.com" in url:
        if "/file/d/" in url:
            file_id = url.split("/file/d/")[1].split("/")[0]
            return f"https://drive.google.com/file/d/{file_id}/preview"
        elif "id=" in url:
            file_id = url.split("id=")[1].split("&")[0]
            return f"https://drive.google.com/file/d/{file_id}/preview"
    return url

# --- TOP HEADER WITH LOGO & TITLE ---
header_col1, header_col2 = st.columns([1, 9])
with header_col1:
    try:
        st.image("logo_pjc.png", width=90)
    except Exception:
        st.write("🎓")

with header_col2:
    st.markdown("<h2 style='color: #1E3A8A; margin-bottom: 0px;'>Prabhu Jagatbandhu College Academic Repository</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #1E3A8A; font-size: 16px; font-weight: 500; margin-top: 5px;'>Centralized repository featuring University Question Papers (PYQs).</p>", unsafe_allow_html=True)

st.markdown("---")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Select View:", [
    "🏠 Home & Overview",
    "🔍 Search & Browse Question Bank", 
    "🔒 Faculty Upload Portal", 
    "❓ FAQs"
], index=0)

st.sidebar.markdown("---")
st.sidebar.subheader("📖 Quick Guide")
st.sidebar.markdown("""
1. **Explore Home**: Check live repository metrics and recent additions.
2. **Search**: Filter question papers by department and curriculum.
3. **Faculty Upload**: Secure login required to upload verified documents.
""")

# Load data globally and map column names safely
df = load_sheet_data()
if not df.empty:
    dept_col = next((col for col in df.columns if any(k in col.lower() for k in ['dept', 'department'])), None)
    sem_col = next((col for col in df.columns if any(k in col.lower() for k in ['sem', 'semester'])), None)
    year_col = next((col for col in df.columns if any(k in col.lower() for k in ['year', 'exam'])), None)
    ug_pg_col = next((col for col in df.columns if any(k in col.lower() for k in ['ug', 'pg', 'level', 'undergraduate'])), None)
    ccf_cbcs_col = next((col for col in df.columns if any(k in col.lower() for k in ['ccf', 'cbcs', 'system', 'curriculum'])), None)
    course_struct_col = next((col for col in df.columns if any(k in col.lower() for k in ['course structure', 'structure', 'programme'])), None)

    total_qp = len(df)
    total_depts = df[dept_col].nunique() if dept_col and dept_col in df.columns else 0
else:
    total_qp, total_depts = 0, 0
    dept_col = sem_col = year_col = ug_pg_col = ccf_cbcs_col = course_struct_col = None

# ==========================================
# 0. HOME & DYNAMIC FRONTAL OVERVIEW
# ==========================================
if app_mode == "🏠 Home & Overview":
    
    # 1. Stunning Hero Banner
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); padding: 35px; border-radius: 15px; color: white; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h1 style="color: white; margin-bottom: 10px; font-size: 32px;">Welcome to PJC Academic Repository 🎓</h1>
        <p style="font-size: 16px; opacity: 0.9; margin-bottom: 10px;">
            Your centralized institutional gateway for Prabhu Jagatbandhu College University Question Papers (PYQs).
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 2. Metric Cards
    col_metric1, col_metric2 = st.columns(2)
    with col_metric1:
        st.metric(label="📁 Question Papers Archived", value=total_qp)
    with col_metric2:
        st.metric(label="🏛️ Active Departments", value=total_depts)

    st.markdown("---")

    # 3. Quick Action Hub
    st.subheader("⚡ Quick Portal Navigation")
    q_col1, q_col2 = st.columns(2)
    
    with q_col1:
        with st.container(border=True):
            st.markdown("### 🔍 Question Bank")
            st.write("Browse and filter past university question papers by semester, year, and department.")
            st.info("👈 Select **Search & Browse** in the sidebar to begin.")
                
    with q_col2:
        with st.container(border=True):
            st.markdown("### 🔒 Faculty Portal")
            st.write("Secure, password-protected upload gateway for authorized department faculty.")
            st.info("👈 Select **Faculty Upload Portal** in the sidebar.")

    # 4. Department Distribution Chart & Recent Additions
    if not df.empty and dept_col and dept_col in df.columns:
        st.markdown("---")
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.subheader("📊 Submissions by Department")
            dept_counts = df[dept_col].value_counts()
            st.bar_chart(dept_counts, color="#3B82F6")
            
        with chart_col2:
            st.subheader("📢 Recently Added Documents")
            recent_df = df.tail(3).iloc[::-1]
            for _, row in recent_df.iterrows():
                with st.container(border=True):
                    doc_title = row.iloc[2] if len(row) > 2 else "Academic Document"
                    dept_name = row[dept_col] if pd.notna(row[dept_col]) else "General"
                    st.markdown(f"✨ **{doc_title}**")
                    st.caption(f"📂 Department of {dept_name}")

# ==========================================
# 1. SEARCH & BROWSE QUESTION BANK
# ==========================================
elif app_mode == "🔍 Search & Browse Question Bank":
    st.markdown("<h3 style='color: #1E3A8A;'>Search & Filter Question Bank</h3>", unsafe_allow_html=True)
    
    if df.empty:
        st.warning("⚠️ No data found in the Google Sheet. Please check your CSV publishing link.")
    else:
        # Filter controls layout - Row 1
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            dept_options = ["All"] + sorted(df[dept_col].dropna().unique().tolist()) if dept_col and dept_col in df.columns else ["All"]
            selected_dept = st.selectbox("Department", dept_options)
            
        with f_col2:
            sem_options
