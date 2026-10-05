import streamlit as st
import pandas as pd

# --- PAGE CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="Prabhu Jagatbandhu College - Question Bank",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS for light blue background, blue theme accents, and header alignment
st.markdown("""
<style>
    /* Main app background color */
    .stApp {
        background-color: #EBF4FF;
    }
    
    /* Sidebar background styling */
    [data-testid="stSidebar"] {
        background-color: #D6E4FD;
    }
    
    /* Headers and text styling */
    h1, h2, h3 {
        color: #1E3A8A;
    }
</style>
""", unsafe_allow_html=True)

# --- GOOGLE SHEET CONFIGURATION ---
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR-_lVqargGK2c_8W-U9_orAY62PvBY8qPJuj9XC45p68CCmGZg1qaSnNVRPsPowdBbxQMQ-7Qfx3Eu/pub?output=csv"
GOOGLE_FORM_URL = "https://forms.gle/ukm1N3SyHaVdNmi3A"

# --- FACULTY PASSWORD CONFIGURATION ---
FACULTY_PASSWORD = "PJC_Faculty@2026"  # You can change this password anytime here

@st.cache_data(ttl=30)
def load_sheet_data():
    if not SHEET_CSV_URL or "YOUR_PUBLISHED" in SHEET_CSV_URL:
        return pd.DataFrame()
    try:
        return pd.read_csv(SHEET_CSV_URL)
    except Exception:
        return pd.DataFrame()

# --- TOP HEADER WITH LOGO & TITLE ---
header_col1, header_col2 = st.columns([1, 9], vertical_alignment="center")

with header_col1:
    try:
        st.image("logo_pjc.png", width=90)
    except Exception:
        st.write("🎓")

with header_col2:
    st.markdown("<h2 style='color: #1E3A8A; margin-bottom: 0px;'>Prabhu Jagatbandhu College Question Bank & Archive</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #1E3A8A; font-size: 16px; font-weight: 500; margin-top: 5px;'>Centralized repository featuring University Previous Years' Questions (PYQs) for Major, MDC, and Minor courses.</p>", unsafe_allow_html=True)

st.markdown("---")

# --- SIDEBAR NAVIGATION & GUIDE ---
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Select View:", ["🔍 Search & Browse Bank", "🔒 Faculty Upload Portal", "❓ FAQs"])

st.sidebar.markdown("---")
st.sidebar.subheader("📖 Quick Guide")
st.sidebar.markdown("""
1. **Search**: Select your Department, Semester, or Year to filter papers.
2. **Download**: Click the view/download link under any result.
3. **Faculty Upload**: Secure login required to upload verified question papers.
""")

# ==========================================
# 1. SEARCH & BROWSE QUESTION BANK
# ==========================================
if app_mode == "🔍 Search & Browse Bank":
    st.markdown("<h3 style='color: #1E3A8A;'>Search & Filter Question Bank</h3>", unsafe_allow_html=True)
    
    df = load_sheet_data()
    
    if df.empty:
        st.warning("⚠️ Google Sheet URL is not configured yet or no submissions have been made.")
    else:
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Dynamically find column names based on common headers
        dept_col = next((col for col in df.columns if 'department' in col.lower()), None)
        sem_col = next((col for col in df.columns if 'semester' in col.lower()), None)
        year_col = next((col for col in df.columns if 'year' in col.lower()), None)
        ug_pg_col = next((col for col in df.columns if 'ug' in col.lower() or 'pg' in col.lower() or 'level' in col.lower()), None)
        ccf_cbcs_col = next((col for col in df.columns if 'ccf' in col.lower() or 'cbcs' in col.lower() or 'system' in col.lower()), None)
        
        # Filter controls layout - Row 1
        f_col1, f_col2, f_col3 = st.columns(3)
        
        with f_col1:
            dept_options = ["All"] + list(df[dept_col].dropna().unique()) if dept_col else ["All"]
            selected_dept = st.selectbox("Department", dept_options)
            
        with f_col2:
            sem_options = ["All"] + list(df[sem_col].dropna().unique()) if sem_col else ["All"]
            selected_sem = st.selectbox("Semester", sem_options)
            
        with f_col3:
            year_options = ["All"] + list(df[year_col].dropna().unique()) if year_col else ["All"]
            selected_year = st.selectbox("Year of Examination", year_options)

        # Filter controls layout - Row 2
        f_col4, f_col5, f_col6 = st.columns(3)

        with f_col4:
            ug_pg_options = ["All"] + list(df[ug_pg_col].dropna().unique()) if ug_pg_col else ["All"]
            selected_ug_pg = st.selectbox("UG / PG", ug_pg_options)

        with f_col5:
            ccf_cbcs_options = ["All"] + list(df[ccf_cbcs_col].dropna().unique()) if ccf_cbcs_col else ["All"]
            selected_ccf_cbcs = st.selectbox("CCF / CBCS", ccf_cbcs_options)

        with f_col6:
            search_text = st.text_input("Keyword Search", placeholder="Paper code or text...")
            
        # Apply filters
        filtered_df = df.copy()
        if selected_dept != "All" and dept_col:
            filtered_df = filtered_df[filtered_df[dept_col] == selected_dept]
        if selected_sem != "All" and sem_col:
            filtered_df = filtered_df[filtered_df[sem_col] == selected_sem]
        if selected_year != "All" and year_col:
            filtered_df = filtered_df[filtered_df[year_col] == selected_year]
        if selected_ug_pg != "All" and ug_pg_col:
            filtered_df = filtered_df[filtered_df[ug_pg_col] == selected_ug_pg]
        if selected_ccf_cbcs != "All" and ccf_cbcs_col:
            filtered_df = filtered_df[filtered_df[ccf_cbcs_col] == selected_ccf_cbcs]
        if search_text:
            mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_text, case=False)).any(axis=1)
            filtered_df = filtered_df[mask]
            
        st.markdown("---")
        st.subheader(f"Results Found: {len(filtered_df)}")
        
        if filtered_df.empty:
            st.info("No questions found matching your criteria.")
        else:
            for index, row in filtered_df.iterrows():
                with st.container(border=True):
                    dept_val = row[dept_col] if dept_col and dept_col in row else "N/A"
                    sem_val = row[sem_col] if sem_col and sem_col in row else "N/A"
                    year_val = row[year_col] if year_col and year_col in row else "N/A"
                    
                    paper_info = row.iloc[2] if len(row) > 2 else "Question Paper"
                    
                    # Dynamically find the valid HTTP file link across all columns
                    file_link = ""
                    for col in df.columns:
                        val = str(row[col])
                        if val.startswith("http"):
                            file_link = val
                            break
                    
                    st.markdown(f"**Paper Details:** {paper_info}")
                    
                    # Build caption dynamically including UG/PG and CCF/CBCS if present
                    caption_parts = [f"📂 **Dept:** {dept_val}", f"📚 **Semester:** {sem_val}", f"📅 **Year:** `{year_val}`"]
                    if ug_pg_col and ug_pg_col in row and pd.notna(row[ug_pg_col]):
                        caption_parts.append(f"🎓 **Level:** {row[ug_pg_col]}")
                    if ccf_cbcs_col and ccf_cbcs_col in row and pd.notna(row[ccf_cbcs_col]):
                        caption_parts.append(f"⚙️ **System:** {row[ccf_cbcs_col]}")
                    st.caption(" | ".join(caption_parts))
                    
                    if pd.notna(file_link) and file_link.startswith("http"):
                        # Handle multiple links if separated by comma
                        urls = [u.strip() for u in file_link.split(",")]
                        for i, url in enumerate(urls):
                            st.markdown(f"🔗 [📥 View / Download Document {i+1}]({url})")
                    else:
                        st.warning("⚠️ No file link available for this submission.")

# ==========================================
# 2. PASSWORD-PROTECTED FACULTY UPLOAD PORTAL
# ==========================================
elif app_mode == "🔒 Faculty Upload Portal":
    st.markdown("<h3 style='color: #1E3A8A;'>Faculty Question Paper Upload Portal</h3>", unsafe_allow_html=True)
    st.markdown("🔒 *Restricted Access: Authorized Department Faculty Only to prevent spam/junk uploads.*")
    
    # Password text input box
    password_input = st.text_input("Enter Faculty Password", type="password")
    
    if password_input == "":
        st.info("ℹ️ Please enter the password provided by the administration to access the upload form.")
    elif password_input == FACULTY_PASSWORD:
        st.success("✅ Access Granted! You are authenticated as department faculty.")
        st.markdown("Use the secure submission link below to upload verified question papers:")
        st.link_button("📤 Open Secure Faculty Submission Form", GOOGLE_FORM_URL, use_container_width=True)
    else:
        st.error("❌ Incorrect password. Please contact the college administrator if you need assistance.")

# ==========================================
# 3. FREQUENTLY ASKED QUESTIONS (FAQS)
# ==========================================
elif app_mode == "❓ FAQs":
    st.markdown("<h3 style='color: #1E3A8A;'>Frequently Asked Questions (FAQs)</h3>", unsafe_allow_html=True)
    st.markdown("Got questions about how to use or contribute to the repository? Find answers below:")
    
    with st.expander("1. How can I search for a specific question paper?"):
        st.write("Navigate to the **Search & Browse Bank** tab. Use the dropdown filters to choose your Department, Semester, Year, UG/PG level, or CCF/CBCS system, or type a paper code into the keyword search box.")
    
    with st.expander("2. Why is the upload portal password-protected?"):
        st.write("To ensure that only verified previous years' question papers from authorized faculty members are added, protecting the database from spam, junk uploads, and unauthorized files.")
    
    with st.expander("3. Where do uploaded files go in Google Drive?"):
        st.write("Files uploaded by faculty through the verified form are automatically processed and sorted into their respective departmental folders (e.g., Physics, Chemistry, Mathematics) inside the college's master Google Drive repository.")
    
    with st.expander("4. How quickly do newly submitted papers show up on the website?"):
        st.write("Submissions appear almost instantly on the website as soon as the form is submitted and synced with the live archive sheet.")
    
    with st.expander("5. Who is allowed to browse and download from this question bank?"):
        st.write("The search and download archive is fully open and accessible to all students and faculty members under University of Calcutta.")

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666666; font-size: 14px;'>"
    "© 2026 Prabhu Jagatbandhu College &nbsp;|&nbsp; Developed & Maintained by <b>Dr. Kisor Mukhopadhyay</b>"
    "</div>", 
    unsafe_allow_html=True
)
