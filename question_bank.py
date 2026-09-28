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
    st.title("Prabhu Jagatbandhu College Question Bank & Archive")
    st.markdown("<p style='color: #334155; font-size: 16px; margin-top: -15px;'>Centralized repository featuring Major, MDC, and University Previous Years' Questions (PYQs).</p>", unsafe_allow_html=True)

st.markdown("---")

# --- SIDEBAR NAVIGATION & GUIDE ---
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Select View:", ["🔍 Search & Browse Bank", "✍️ Submit Question / PYQ", "❓ FAQs"])

st.sidebar.markdown("---")
st.sidebar.subheader("📖 Quick Guide")
st.sidebar.markdown("""
1. **Search**: Select your Department, Semester, or Year to filter papers.
2. **Download**: Click the view/download link under any result.
3. **Contribute**: Use the submission tab to upload new question papers securely.
""")

# ==========================================
# 1. SEARCH & BROWSE QUESTION BANK
# ==========================================
if app_mode == "🔍 Search & Browse Bank":
    st.header("Search & Filter Question Bank")
    
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
        
        # Filter controls layout
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        
        with f_col1:
            dept_options = ["All"] + list(df[dept_col].dropna().unique()) if dept_col else ["All"]
            selected_dept = st.selectbox("Department", dept_options)
            
        with f_col2:
            sem_options = ["All"] + list(df[sem_col].dropna().unique()) if sem_col else ["All"]
            selected_sem = st.selectbox("Semester", sem_options)
            
        with f_col3:
            year_options = ["All"] + list(df[year_col].dropna().unique()) if year_col else ["All"]
            selected_year = st.selectbox("Year of Examination", year_options)
            
        with f_col4:
            search_text = st.text_input("Keyword Search", placeholder="Paper code or text...")
            
        # Apply filters
        filtered_df = df.copy()
        if selected_dept != "All" and dept_col:
            filtered_df = filtered_df[filtered_df[dept_col] == selected_dept]
        if selected_sem != "All" and sem_col:
            filtered_df = filtered_df[filtered_df[sem_col] == selected_sem]
        if selected_year != "All" and year_col:
            filtered_df = filtered_df[filtered_df[year_col] == selected_year]
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
                    st.caption(f"📂 **Dept:** {dept_val} | 📚 **Semester:** {sem_val} | 📅 **Year:** `{year_val}`")
                    
                    if pd.notna(file_link) and file_link.startswith("http"):
                        st.markdown(f"🔗 [📥 View / Download Document]({file_link})")
                    else:
                        st.warning("⚠️ No file link available for this submission.")

# ==========================================
# 2. SUBMIT QUESTION VIA GOOGLE FORM LINK
# ==========================================
elif app_mode == "✍️ Submit Question / PYQ":
    st.header("Upload Question Paper via Secure Google Form")
    st.markdown("Use the official form portal below to submit new question papers:")
    
    st.link_button("📤 Open PJC Question Submission Form", GOOGLE_FORM_URL, use_container_width=True)

# ==========================================
# 3. FREQUENTLY ASKED QUESTIONS (FAQS)
# ==========================================
elif app_mode == "❓ FAQs":
    st.header("Frequently Asked Questions (FAQs)")
    st.markdown("Got questions about how to use or contribute to the repository? Find answers below:")
    
    with st.expander("1. How can I search for a specific question paper?"):
        st.write("Navigate to the **Search & Browse Bank** tab. Use the dropdown filters to choose your Department, Semester, or Year of Examination, or type a paper code into the keyword search box.")
    
    with st.expander("2. How do I submit or upload a new previous year question (PYQ)?"):
        st.write("Go to the **Submit Question / PYQ** tab from the sidebar and click the button to open the official Google Form. Fill out the required details and upload your PDF/document file.")
    
    with st.expander("3. Where do uploaded files go in Google Drive?"):
        st.write("Files uploaded through the form are automatically processed and sorted into their respective departmental folders (e.g., Physics, Chemistry, Mathematics) inside the college's master Google Drive repository.")
    
    with st.expander("4. How quickly do newly submitted papers show up on the website?"):
        st.write("Submissions appear almost instantly on the website as soon as the Google Form is submitted and synced with the live archive sheet.")
    
    with st.expander("5. Who is allowed to access this question bank?"):
        st.write("This archive is fully open and accessible to all students and faculty members of Prabhu Jagatbandhu College for studying and academic preparation.")
