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
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR-_lVqargGK2c_8W-U9_orAY62PvBY8qPJuj9XC45p68CCmGZg1qaSnNVRPsPowdBbxQMQ-7Qfx3Eu/pub?output=csv"
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/19b_w04j5vIQl1U2SvAfzcqhcVwW_cU6FlYGL5d4qk9U/viewform"
FACULTY_PASSWORD = "PJC_Faculty@2026"

@st.cache_data(ttl=30)
def load_sheet_data():
    if not SHEET_CSV_URL:
        return pd.DataFrame()
    try:
        return pd.read_csv(SHEET_CSV_URL)
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
    st.markdown("<p style='color: #1E3A8A; font-size: 16px; font-weight: 500; margin-top: 5px;'>Centralized repository featuring University Question Papers (PYQs) and Departmental Syllabi (CBCS & CCF).</p>", unsafe_allow_html=True)

st.markdown("---")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Select View:", [
    "🔍 Search & Browse Question Bank", 
    "📚 Syllabi Archive (CBCS & CCF)", 
    "🔒 Faculty Upload Portal", 
    "❓ FAQs"
])

st.sidebar.markdown("---")
st.sidebar.subheader("📖 Quick Guide")
st.sidebar.markdown("""
1. **Search**: Filter question papers or syllabi by department and semester.
2. **Preview**: Expand any document card to view the PDF directly inside the app.
3. **Faculty Upload**: Secure login required to upload verified documents.
""")

# Load and clean data
df = load_sheet_data()
if not df.empty:
    df.columns = df.columns.str.strip()

# ==========================================
# 1. SEARCH & BROWSE QUESTION BANK
# ==========================================
if app_mode == "🔍 Search & Browse Question Bank":
    st.markdown("<h3 style='color: #1E3A8A;'>Search & Filter Question Bank</h3>", unsafe_allow_html=True)
    
    if df.empty:
        st.warning("⚠️ No data found in the Google Sheet. Please check your CSV publishing link.")
    else:
        # Filter controls
        f_col1, f_col2, f_col3 = st.columns(3)
        
        with f_col1:
            depts = ["All"] + sorted(df["Department"].dropna().unique().tolist()) if "Department" in df.columns else ["All"]
            selected_dept = st.selectbox("Department", depts)
            
        with f_col2:
            sems = ["All"] + sorted(df["Semester"].dropna().unique().tolist()) if "Semester" in df.columns else ["All"]
            selected_sem = st.selectbox("Semester", sems)
            
        with f_col3:
            search_text = st.text_input("Keyword Search", placeholder="Paper code or title...")
            
        # Apply filters
        filtered_df = df.copy()
        if selected_dept != "All" and "Department" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Department"] == selected_dept]
        if selected_sem != "All" and "Semester" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["Semester"] == selected_sem]
        if search_text:
            mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_text, case=False)).any(axis=1)
            filtered_df = filtered_df[mask]
            
        st.markdown("---")
        
        # Results header & CSV Export button
        res_col1, res_col2 = st.columns([7, 3], vertical_alignment="center")
        with res_col1:
            st.subheader(f"Question Papers Found: {len(filtered_df)}")
        with res_col2:
            if not filtered_df.empty:
                csv_data = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Export Filtered CSV",
                    data=csv_data,
                    file_name="pjc_question_papers_export.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        if filtered_df.empty:
            st.info("No question papers found matching your criteria.")
        else:
            for index, row in filtered_df.iterrows():
                with st.container(border=True):
                    dept = row.get("Department", "N/A")
                    sem = row.get("Semester", "N/A")
                    paper_code = row.get("Paper Code", "Question Paper")
                    year = row.get("Year of Examination", "N/A")
                    struct = row.get("Course Structure", "")
                    file_link = row.get("Question Paper file", "")
                    
                    st.markdown(f"**Paper Code / Title:** `{paper_code}`")
                    st.caption(f"📂 **Dept:** {dept} | 📚 **Semester:** {sem} | 📅 **Year:** {year} | 📖 **Structure:** {struct}")
                    
                    if pd.notna(file_link) and str(file_link).startswith("http"):
                        st.markdown(f"🔗 [📥 Open External Document Link]({file_link})")
                        
                        with st.expander("👁️ Preview Document Inside App"):
                            embed_url = get_embeddable_url(str(file_link))
                            st.markdown(
                                f'<iframe src="{embed_url}" width="100%" height="500px" style="border: none; border-radius: 8px;"></iframe>',
                                unsafe_allow_html=True
                            )
                    else:
                        st.warning("⚠️ No valid file link attached to this record.")

# ==========================================
# 2. SYLLABI ARCHIVE
# ==========================================
elif app_mode == "📚 Syllabi Archive (CBCS & CCF)":
    st.markdown("<h3 style='color: #1E3A8A;'>Department Syllabi Archive (CBCS & CCF)</h3>", unsafe_allow_html=True)
    st.markdown("Access official curriculum and syllabi structured strictly by department.")
    
    if df.empty:
        st.warning("⚠️ No data available.")
    else:
        depts = ["All"] + sorted(df["Department"].dropna().unique().tolist()) if "Department" in df.columns else ["All"]
        selected_syl_dept = st.selectbox("Department", depts, key="syl_dept_select")
        
        filtered_syl = df.copy()
        if selected_syl_dept != "All" and "Department" in filtered_syl.columns:
            filtered_syl = filtered_syl[filtered_syl["Department"] == selected_syl_dept]
            
        st.markdown("---")
        st.subheader(f"Syllabi Records Found: {len(filtered_syl)}")
        
        if filtered_syl.empty:
            st.info("No syllabi records found.")
        else:
            for index, row in filtered_syl.iterrows():
                with st.container(border=True):
                    dept = row.get("Department", "N/A")
                    file_link = row.get("Question Paper file", "")
                    
                    st.markdown(f"**Department Syllabus:** {dept}")
                    if pd.notna(file_link) and str(file_link).startswith("http"):
                        st.markdown(f"🔗 [📥 Open Syllabus Link]({file_link})")
                        with st.expander("👁️ Preview Syllabus Inside App"):
                            embed_url = get_embeddable_url(str(file_link))
                            st.markdown(
                                f'<iframe src="{embed_url}" width="100%" height="500px" style="border: none; border-radius: 8px;"></iframe>',
                                unsafe_allow_html=True
                            )

# ==========================================
# 3. FACULTY UPLOAD PORTAL
# ==========================================
elif app_mode == "🔒 Faculty Upload Portal":
    st.markdown("<h3 style='color: #1E3A8A;'>Faculty Document Upload Portal</h3>", unsafe_allow_html=True)
    st.markdown("🔒 *Restricted Access: Authorized Department Faculty Only.*")
    
    password_input = st.text_input("Enter Faculty Password", type="password")
    
    if password_input == "":
        st.info("ℹ️ Please enter the password provided by the administration to access the upload form.")
    elif password_input == FACULTY_PASSWORD:
        st.success("✅ Access Granted! You are authenticated as department faculty.")
        st.markdown("Use the secure submission link below to upload verified question papers or syllabi:")
        st.link_button("📤 Open Secure Faculty Submission Form", GOOGLE_FORM_URL, use_container_width=True)
    else:
        st.error("❌ Incorrect password.")

# ==========================================
# 4. FREQUENTLY ASKED QUESTIONS (FAQS)
# ==========================================
elif app_mode == "❓ FAQs":
    st.markdown("<h3 style='color: #1E3A8A;?>Frequently Asked Questions (FAQs)</h3>", unsafe_allow_html=True)
    
    with st.expander("1. How can I search for a specific question paper?"):
        st.write("Use the **Search & Browse Question Bank** tab from the sidebar to filter by Department, Semester, or keywords.")
    
    with st.expander("2. Can I view PDFs directly without downloading?"):
        st.write("Yes, click the **👁️ Preview Document Inside App** expander under any paper card.")
    
    with st.expander("3. How do faculty upload documents?"):
        st.write("Go to the **Faculty Upload Portal** and enter the secure department password.")

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666666; font-size: 14px;'>"
    "© 2026 Prabhu Jagatbandhu College &nbsp;|&nbsp; Developed & Maintained by <b>Dr. Kisor Mukhopadhyay</b>"
    "</div>", 
    unsafe_allow_html=True
)
