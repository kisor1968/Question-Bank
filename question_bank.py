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
        
        # Safely remove .0 decimals from year/exam columns as strings
        for col in df.columns:
            if any(k in col.lower() for k in ['year', 'exam']):
                df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True)
                df[col] = df[col].replace(['nan', 'None', ''], '')
                
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
header_col1, header_col2 = st.columns([1, 9], vertical_alignment="center")
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

# Load and clean data globally
df = load_sheet_data()

# Safe column finder helper
def find_col(keywords):
    if df.empty:
        return None
    for col in df.columns:
        if any(k in col.lower() for k in keywords):
            return col
    return None

dept_col = find_col(['dept', 'department'])

if not df.empty and dept_col:
    df = df[df[dept_col].notna() & (df[dept_col].astype(str).str.strip() != "")]
    total_qp = len(df)
    total_depts = df[dept_col].nunique()
else:
    total_qp, total_depts = 0, 0

# ==========================================
# 0. HOME & DYNAMIC FRONTAL OVERVIEW
# ==========================================
if app_mode == "🏠 Home & Overview":
    
    # 1. Stunning Hero Banner
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); padding: 35px; border-radius: 15px; color: white; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h1 style="color: white; margin-bottom: 10px; font-size: 32px;">Welcome to PJC Academic Repository 🎓</h1>
        <p style="font-size:
