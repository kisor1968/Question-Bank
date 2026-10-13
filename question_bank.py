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
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/19b_w04j5vIQl1U2SvAfzcqhcVwW_cU6FlYGL5d4qk9U/viewform"

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

# Helper function to convert standard Google Drive view links to embeddable preview links
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

# --- SIDEBAR NAVIGATION & GUIDE ---
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
1. **Search**: Filter question papers or syllabi by department and curriculum.
2. **Preview**: Expand any document card to view the PDF directly inside the app.
3. **Faculty Upload**: Secure login required to upload verified documents.
""")

# ==========================================
# LOAD DATA & COMPUTE METRICS GLOBALLY
# ==========================================
df = load_sheet_data()
if not df.empty:
    df.columns = df.columns.str.strip()
    dept_col = next((col for col in df.columns if any(k in col.lower() for k in ['dept', 'department'])), None)
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

# ==========================================
# 1. SEARCH & BROWSE QUESTION BANK
# ==========================================
if app_mode == "🔍 Search & Browse Question Bank":
    st.markdown("<h3 style='color: #1E3A8A;'>Search & Filter Question Bank</h3>", unsafe_allow_html=True)
    
    # Perfectly Aligned Custom Metric Cards
    st.markdown(f"""
    <div style="display: flex; gap: 15px; margin-bottom: 25px;">
        <div style="flex: 1; background: #ffffff; padding: 18px; border-radius: 10px; border: 1px solid #C7D2FE; box-shadow: 0 1px 3px rgba(0,0,0,0.05); text-align: center;">
            <div style="color: #4B5563; font-size: 14px; font-weight: 600; margin-bottom: 5px;">📁 Question Papers Archived</div>
            <div style="color: #1E3A8A; font-size: 30px; font-weight: 700;">{total_qp}</div>
        </div>
        <div style="flex: 1; background: #ffffff; padding: 18px; border-radius: 10px; border: 1px solid #C7D2FE; box-shadow: 0 1px 3px rgba(0,0,0,0.05); text-align: center;">
            <div style="color: #4B5563; font-size: 14px; font-weight: 600; margin-bottom: 5px;">📚 Syllabi Available</div>
            <div style="color: #1E3A8A; font-size: 30px; font-weight: 700;">{total_syl}</div>
        </div>
        <div style="flex: 1; background: #ffffff; padding: 18px; border-radius: 10px; border: 1px solid #C7D2FE; box-shadow: 0 1px 3px rgba(0,0,0,0.05); text-align: center;">
            <div style="color: #4B5563; font-size: 14px; font-weight: 600; margin-bottom: 5px;">🏛️ Active Departments</div>
            <div style="color: #1E3A8A; font-size: 30px; font-weight: 700;">{total_depts}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if df.empty:
        st.warning("⚠️ Google Sheet URL is not configured yet or no submissions have been made.")
    else:
        # Robust dynamic column finders
        sem_col = next((col for col in df.columns if any(k in col.lower() for k in ['sem', 'semester'])), None)
        year_col = next((col for col in df.columns if any(k in col.lower() for k in ['year', 'exam'])), None)
        ug_pg_col = next((col for col in df.columns if any(k in col.lower() for k in ['ug', 'pg', 'level', 'undergraduate'])), None)
        ccf_cbcs_col = next((col for col in df.columns if any(k in col.lower() for k in ['ccf', 'cbcs', 'system', 'curriculum'])), None)
        course_struct_col = next((col for col in df.columns if any(k in col.lower() for k in ['course structure', 'structure', 'programme'])), None)
        
        # Filter controls layout - Row 1
        f_col1, f_col2, f_col3 = st.columns(3)
        
        with f_col1:
            dept_options = ["All"] + sorted(df[dept_col].dropna().unique().tolist()) if dept_col and dept_col in df.columns else ["All"]
            selected_dept = st.selectbox("Department", dept_options)
            
        with f_col2:
            sem_options = ["All"] + sorted(df[sem_col].dropna().unique().tolist()) if sem_col and sem_col in df.columns else ["All"]
            selected_sem = st.selectbox("Semester", sem_options)
            
        with f_col3:
            year_options = ["All"] + [str(y) for y in range(2022, 2027)]
            selected_year = st.selectbox("Year of Examination", year_options)

        # Filter controls layout - Row 2
        f_col4, f_col5, f_col6, f_col7 = st.columns(4)

        with f_col4:
            ug_pg_options = ["All"] + sorted(df[ug_pg_col].dropna().unique().tolist()) if ug_pg_col and ug_pg_col in df.columns else ["All"]
            selected_ug_pg = st.selectbox("UG / PG", ug_pg_options)

        with f_col5:
            ccf_cbcs_options = ["All"] + sorted(df[ccf_cbcs_col].dropna().unique().tolist()) if ccf_cbcs_col and ccf_cbcs_col in df.columns else ["All"]
            selected_ccf_cbcs = st.selectbox("CCF / CBCS", ccf_cbcs_options)

        with f_col6:
            struct_options = ["All"] + sorted(df[course_struct_col].dropna().unique().tolist()) if course_struct_col and course_struct_col in df.columns else ["All"]
            selected_struct = st.selectbox("Course Structure", struct_options)

        with f_col7:
            search_text = st.text_input("Keyword Search", placeholder="Paper code or text...")
            
        # Apply filters safely (Exclude syllabi)
        filtered_df = df.copy()
        if doc_type_col and doc_type_col in filtered_df.columns:
            filtered_df = filtered_df[~filtered_df[doc_type_col].astype(str).str.contains("syllabus", case=False, na=False)]
            
        if selected_dept != "All" and dept_col and dept_col in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[dept_col] == selected_dept]
        if selected_sem != "All" and sem_col and sem_col in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[sem_col] == selected_sem]
        if selected_year != "All" and year_col and year_col in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[year_col].astype(str).str.contains(selected_year, na=False)]
        if selected_ug_pg != "All" and ug_pg_col and ug_pg_col in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[ug_pg_col] == selected_ug_pg]
        if selected_ccf_cbcs != "All" and ccf_cbcs_col and ccf_cbcs_col in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[ccf_cbcs_col] == selected_ccf_cbcs]
        if selected_struct != "All" and course_struct_col and course_struct_col in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[course_struct_col] == selected_struct]
        if search_text:
            mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_text, case=False)).any(axis=1)
            filtered_df = filtered_df[mask]
            
        st.markdown("---")
        
        # Results header & CSV Export button row
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
                    dept_val = row[dept_col] if dept_col and dept_col in row and pd.notna(row[dept_col]) else "N/A"
                    sem_val = row[sem_col] if sem_col and sem_col in row and pd.notna(row[sem_col]) else "N/A"
                    year_val = row[year_col] if year_col and year_col in row and pd.notna(row[year_col]) else "N/A"
                    
                    paper_info = row.iloc[2] if len(row) > 2 else "Question Paper"
                    
                    file_link = ""
                    for col in df.columns:
                        val = str(row[col])
                        if val.startswith("http"):
                            file_link = val
                            break
                    
                    st.markdown(f"**Paper Details:** {paper_info}")
                    
                    caption_parts = [f"📂 **Dept:** {dept_val}", f"📚 **Semester:** {sem_val}", f"📅 **Year:** `{year_val}`"]
                    if ug_pg_col and ug_pg_col in row and pd.notna(row[ug_pg_col]):
                        caption_parts.append(f"🎓 **Level:** {row[ug_pg_col]}")
                    if ccf_cbcs_col and ccf_cbcs_col in row and pd.notna(row[ccf_cbcs_col]):
                        caption_parts.append(f"⚙️ **System:** {row[ccf_cbcs_col]}")
                    if course_struct_col and course_struct_col in row and pd.notna(row[course_struct_col]):
                        caption_parts.append(f"📖 **Structure:** {row[course_struct_col]}")
                    st.caption(" | ".join(caption_parts))
                    
                    if pd.notna(file_link) and file_link.startswith("http"):
                        urls = [u.strip() for u in file_link.split(",")]
                        for i, url in enumerate(urls):
                            st.markdown(f"🔗 [📥 Open External Link {i+1}]({url})")
                    else:
                        st.warning("⚠️ No file link available for this submission.")

                    # Direct Document Preview Expander
                    if pd.notna(file_link) and file_link.startswith("http"):
                        with st.expander("👁️ Preview Document Inside App"):
                            embed_url = get_embeddable_url(file_link.split(",")[0])
                            st.markdown(
                                f'<iframe src="{embed_url}" width="100%" height="550px" style="border: none; border-radius: 8px;"></iframe>',
                                unsafe_allow_html=True
                            )

# ==========================================
# 2. SYLLABI ARCHIVE (CBCS & CCF - Department Only)
# ==========================================
elif app_mode == "📚 Syllabi Archive (CBCS & CCF)":
    st.markdown("<h3 style='color: #1E3A8A;'>Department Syllabi Archive (CBCS & CCF)</h3>", unsafe_allow_html=True)
    st.markdown("Access official curriculum and syllabi structured strictly by department, curriculum system (CBCS / CCF), and level.")
    
    if df.empty:
        st.warning("⚠️ Google Sheet URL is not configured yet or no submissions have been made.")
    else:
        ug_pg_col = next((col for col in df.columns if any(k in col.lower() for k in ['ug', 'pg', 'level', 'undergraduate'])), None)
        ccf_cbcs_col = next((col for col in df.columns if any(k in col.lower() for k in ['ccf', 'cbcs', 'system', 'curriculum'])), None)
        
        # Filter controls for Syllabi
        s_col1, s_col2, s_col3 = st.columns(3)
        with s_col1:
            dept_options = ["All"] + sorted(df[dept_col].dropna().unique().tolist()) if dept_col and dept_col in df.columns else ["All"]
            selected_syllabus_dept = st.selectbox("Department", dept_options, key="syl_dept")
            
        with s_col2:
            ccf_cbcs_options = ["All"] + sorted(df[ccf_cbcs_col].dropna().unique().tolist()) if ccf_cbcs_col and ccf_cbcs_col in df.columns else ["All"]
            selected_syllabus_system = st.selectbox("Curriculum System", ccf_cbcs_options, key="syl_sys")

        with s_col3:
            ug_pg_options = ["All"] + sorted(df[ug_pg_col].dropna().unique().tolist()) if ug_pg_col and ug_pg_col in df.columns else ["All"]
            selected_syllabus_level = st.selectbox("Level / Program", ug_pg_options, key="syl_lvl")
            
        # Filter dataframe specifically for Syllabi
        filtered_syl_df = df.copy()
        if doc_type_col and doc_type_col in filtered_syl_df.columns:
            filtered_syl_df = filtered_syl_df[filtered_syl_df[doc_type_col].astype(str).str.contains("syllabus", case=False, na=False)]
        
        if selected_syllabus_dept != "All" and dept_col and dept_col in filtered_syl_df.columns:
            filtered_syl_df = filtered_syl_df[filtered_syl_df[dept_col] == selected_syllabus_dept]
        if selected_syllabus_system != "All" and ccf_cbcs_col and ccf_cbcs_col in filtered_syl_df.columns:
            filtered_syl_df = filtered_syl_df[filtered_syl_df[ccf_cbcs_col] == selected_syllabus_system]
        if selected_syllabus_level != "All" and ug_pg_col and ug_pg_col in filtered_syl_df.columns:
            filtered_syl_df = filtered_syl_df[filtered_syl_df[ug_pg_col] == selected_syllabus_level]
            
        st.markdown("---")
        
        # Syllabi header & CSV Export button row
        s_res1, s_res2 = st.columns([7, 3], vertical_alignment="center")
        with s_res1:
            st.subheader(f"Syllabi Found: {len(filtered_syl_df)}")
        with s_res2:
            if not filtered_syl_df.empty:
                syl_csv
