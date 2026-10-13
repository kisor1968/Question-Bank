import streamlit as st
import pandas as pd

# --- PAGE CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="Prabhu Jagatbandhu College - Academic Repository",
    page_icon="🎓",
    layout="wide"
)

st.markdown("""
<style>
    .stApp { background-color: #EBF4FF; }
    [data-testid="stSidebar"] { background-color: #D6E4FD; }
    h1, h2, h3 { color: #1E3A8A; }
</style>
""", unsafe_allow_html=True)

# --- GOOGLE SHEET CONFIGURATION ---
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR-_lVqargGK2c_8W-U9_orAY62PvBY8qPJuj9XC45p68CCmGZg1qaSnNVRPsPowdBbxQMQ-7Qfx3Eu/pub?output=csv"
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/19b_w04j5vIQl1U2SvAfzcqhcVwW_cU6FlYGL5d4qk9U/viewform"
FACULTY_PASSWORD = "PJC_Faculty@2026"

@st.cache_data(ttl=10) # Shortened TTL for testing so updates show instantly
def load_sheet_data():
    if not SHEET_CSV_URL:
        return pd.DataFrame()
    try:
        return pd.read_csv(SHEET_CSV_URL)
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return pd.DataFrame()

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

# --- TOP HEADER ---
header_col1, header_col2 = st.columns([1, 9], vertical_alignment="center")
with header_col1:
    st.write("🎓")
with header_col2:
    st.markdown("<h2 style='color: #1E3A8A; margin-bottom: 0px;'>Prabhu Jagatbandhu College Academic Repository</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #1E3A8A; font-size: 16px; font-weight: 500; margin-top: 5px;'>Centralized repository featuring University Question Papers (PYQs) and Departmental Syllabi (CBCS & CCF).</p>", unsafe_allow_html=True)

st.markdown("---")

# --- SIDEBAR ---
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Select View:", [
    "🏠 Home & Overview",
    "🔍 Search & Browse Question Bank", 
    "📚 Syllabi Archive (CBCS & CCF)", 
    "🔒 Faculty Upload Portal", 
    "❓ FAQs"
])

# Load Data
df = load_sheet_data()

# Sidebar Debugger to help you see what columns Streamlit detected
with st.sidebar.expander("🛠️ Admin Data Debugger"):
    if df.empty:
        st.warning("DataFrame is empty. Check Google Sheet publishing.")
    else:
        st.write(f"Total Rows: {len(df)}")
        st.write("Columns found:", df.columns.tolist())

if not df.empty:
    df.columns = df.columns.str.strip()
    # Flexible column matchers
    dept_col = next((col for col in df.columns if any(k in col.lower() for k in ['dept', 'department'])), df.columns[1] if len(df.columns)>1 else None)
    doc_type_col = next((col for col in df.columns if any(k in col.lower() for k in ['doc', 'type', 'document'])), None)
    
    total_docs = len(df)
    if doc_type_col and doc_type_col in df.columns:
        total_syl = df[df[doc_type_col].astype(str).str.contains("syllabus", case=False, na=False)].shape[0]
        total_qp = total_docs - total_syl
    else:
        total_syl = 0
        total_qp = total_docs
        
    total_depts = df[dept_col].nunique() if dept_col and dept_col in df.columns else 0
else:
    total_qp, total_syl, total_depts = 0, 0, 0
    dept_col, doc_type_col = None, None

# ==========================================
# 0. HOME & OVERVIEW
# ==========================================
if app_mode == "🏠 Home & Overview":
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); padding: 35px; border-radius: 15px; color: white; margin-bottom: 25px;">
        <h1 style="color: white; margin-bottom: 10px; font-size: 32px;">Welcome to PJC Academic Repository 🎓</h1>
        <p style="font-size: 16px; opacity: 0.9;">Your centralized institutional gateway for University Question Papers and Departmental Syllabi.</p>
    </div>
    """, unsafe_allow_html=True)

    # Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("📁 Question Papers", total_qp)
    m2.metric("📚 Syllabi", total_syl)
    m3.metric("🏛️ Departments", total_depts)

    if not df.empty and dept_col:
        st.markdown("---")
        st.subheader("📊 Submissions by Department")
        st.bar_chart(df[dept_col].value_counts(), color="#3B82F6")

# ==========================================
# 1. SEARCH & BROWSE QUESTION BANK
# ==========================================
elif app_mode == "🔍 Search & Browse Question Bank":
    st.markdown("<h3 style='color: #1E3A8A;'>Search & Filter Question Bank</h3>", unsafe_allow_html=True)
    
    if df.empty:
        st.warning("⚠️ No data found in the Google Sheet. Make sure your sheet is published to the web as CSV.")
    else:
        # Simple fallback filters that won't break if column names vary
        col_names = df.columns.tolist()
        
        f1, f2 = st.columns(2)
        with f1:
            selected_dept = st.selectbox("Department", ["All"] + sorted(df[dept_col].dropna().unique().tolist())) if dept_col else "All"
        with f2:
            search_query = st.text_input("Search Keyword", placeholder="Type paper code or title...")

        filtered_df = df.copy()
        if selected_dept != "All" and dept_col:
            filtered_df = filtered_df[filtered_df[dept_col] == selected_dept]
        if search_query:
            mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
            filtered_df = filtered_df[mask]

        st.markdown("---")
        st.subheader(f"Matching Documents: {len(filtered_df)}")

        if filtered_df.empty:
            st.info("No documents match your filter criteria.")
        else:
            for idx, row in filtered_df.iterrows():
                with st.container(border=True):
                    st.write(dict(row)) # Displays all row data so you can verify columns instantly
                    
                    # Find any column starting with http
                    file_link = next((str(row[c]) for c in df.columns if str(row[c]).startswith("http")), "")
                    if file_link:
                        st.markdown(f"🔗 [Open Document Link]({file_link})")
                        with st.expander("👁️ Preview Inside App"):
                            embed_url = get_embeddable_url(file_link)
                            st.markdown(f'<iframe src="{embed_url}" width="100%" height="450px" style="border:none;"></iframe>', unsafe_allow_html=True)

# ==========================================
# 2. SYLLABI ARCHIVE
# ==========================================
elif app_mode == "📚 Syllabi Archive (CBCS & CCF)":
    st.markdown("<h3 style='color: #1E3A8A;'>Department Syllabi Archive</h3>", unsafe_allow_html=True)
    if df.empty:
        st.warning("⚠️ No data available.")
    else:
        st.write("Switch to the Search tab or check your published sheet data to view syllabus records.")

# ==========================================
# 3. FACULTY UPLOAD PORTAL
# ==========================================
elif app_mode == "🔒 Faculty Upload Portal":
    st.markdown("<h3 style='color: #1E3A8A;'>Faculty Document Upload Portal</h3>", unsafe_allow_html=True)
    password = st.text_input("Enter Faculty Password", type="password")
    
    if password == FACULTY_PASSWORD:
        st.success("✅ Access Granted!")
        st.link_button("📤 Open Secure Faculty Submission Form", GOOGLE_FORM_URL, use_container_width=True)
    elif password != "":
        st.error("❌ Incorrect password. (Hint: PJC_Faculty@2026)")
    else:
        st.info("ℹ️ Enter the password to unlock the upload form button.")

# ==========================================
# 4. FAQS
# ==========================================
elif app_mode == "❓ FAQs":
    st.markdown("<h3 style='color: #1E3A8A;'>FAQs</h3>", unsafe_allow_html=True)
    st.write("Check your sidebar debugger if data isn't populating as expected.")
