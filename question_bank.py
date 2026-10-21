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
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTmVbhktPZiOsXXra7mqjElbUVxybeBGAMSqloH3kTrjXe0nziwqfYMf-gU7AjNDI_inkHQHLgZ61ki/pub?output=csv"
GOOGLE_FORM_URL = "https://docs.google.com/forms/d/19b_w04j5vIQl1U2SvAfzcqhcVwW_cU6FlYGL5d4qk9U/viewform"
FACULTY_PASSWORD = "PJC_Faculty@2026"

@st.cache_data(ttl=30)
def load_sheet_data():
    if not SHEET_CSV_URL:
        return pd.DataFrame()
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        # Drop completely empty rows or rows where all entries are NaN
        df = df.dropna(how='all')
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
    st.markdown("<p style='color: #1E3A8A; font-size: 16px; font-weight: 500; margin-top: 5px;'>Centralized repository featuring University Question Papers (PYQs) and Departmental Syllabi (CBCS & CCF).</p>", unsafe_allow_html=True)

st.markdown("---")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Select View:", [
    "🏠 Home & Overview",
    "🔍 Search & Browse Question Bank", 
    "📚 Syllabi Archive (CBCS & CCF)", 
    "🔒 Faculty Upload Portal", 
    "❓ FAQs"
], index=0)

st.sidebar.markdown("---")
st.sidebar.subheader("📖 Quick Guide")
st.sidebar.markdown("""
1. **Explore Home**: Check live repository metrics and recent additions.
2. **Search**: Filter question papers or syllabi by department and curriculum.
3. **Faculty Upload**: Secure login required to upload verified documents.
""")

# Load and clean data globally
df = load_sheet_data()
if not df.empty:
    df.columns = df.columns.str.strip()
    dept_col = next((col for col in df.columns if any(k in col.lower() for k in ['dept', 'department'])), None)
    doc_type_col = next((col for col in df.columns if any(k in col.lower() for k in ['doc', 'type', 'document'])), None)
    
    # Filter out rows missing essential department info to prevent 'nan' cards
    if dept_col and dept_col in df.columns:
        df = df[df[dept_col].notna() & (df[dept_col].astype(str).str.strip() != "")]

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
# 0. HOME & DYNAMIC FRONTAL OVERVIEW
# ==========================================
if app_mode == "🏠 Home & Overview":
    
    # 1. Stunning Hero Banner
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); padding: 35px; border-radius: 15px; color: white; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h1 style="color: white; margin-bottom: 10px; font-size: 32px;">Welcome to PJC Academic Repository 🎓</h1>
        <p style="font-size: 16px; opacity: 0.9; margin-bottom: 10px;">
            Your centralized institutional gateway for Prabhu Jagatbandhu College University Question Papers (PYQs) and Departmental Syllabi (CBCS & CCF).
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 2. Metric Cards
    st.markdown(f"""
    <div style="display: flex; gap: 15px; margin-bottom: 30px;">
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

    # 3. Quick Action Hub
    st.subheader("⚡ Quick Portal Navigation")
    q_col1, q_col2, q_col3 = st.columns(3)
    
    with q_col1:
        with st.container(border=True):
            st.markdown("### 🔍 Question Bank")
            st.write("Browse and filter past university question papers by semester, year, and department.")
            st.info("👈 Select **Search & Browse** in the sidebar to begin.")
                
    with q_col2:
        with st.container(border=True):
            st.markdown("### 📚 Syllabi Archive")
            st.write("Access official curriculum and syllabi structured by CBCS and CCF frameworks.")
            st.info("👈 Select **Syllabi Archive** in the sidebar.")
                
    with q_col3:
        with st.container(border=True):
            st.markdown("### 🔒 Faculty Portal")
            st.write("Secure, password-protected upload gateway for authorized department faculty.")
            st.info("👈 Select **Faculty Upload Portal** in the sidebar.")

    # 4. Department Distribution Chart & Recent Additions
    if not df.empty and dept_col and dept_col in df.columns:
        st.markdown("---")
        chart_col1, chart_col2 = st.columns([1, 1], vertical_alignment="top")
        
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
            year_options = ["All"] + sorted(df[year_col].dropna().unique().astype(str).tolist()) if year_col and year_col in df.columns else ["All"]
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
            
        # Apply filters (exclude syllabi)
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
                    dept_val = row[dept_col] if dept_col and dept_col in row and pd.notna(row[dept_col]) else "N/A"
                    sem_val = row[sem_col] if sem_col and sem_col in row and pd.notna(row[sem_col]) else "N/A"
                    year_val = str(row[year_col]) if year_col and year_col in row and pd.notna(row[year_col]) else "N/A"
                    
                    paper_code_col = next((c for c in df.columns if 'code' in c.lower()), None)
                    paper_code = row[paper_code_col] if paper_code_col and pd.notna(row[paper_code_col]) else (row.iloc[2] if len(row) > 2 else "Question Paper")
                    
                    file_link = ""
                    for col in df.columns:
                        val = str(row[col])
                        if val.startswith("http"):
                            file_link = val
                            break
                    
                    st.markdown(f"**Paper Details:** `{paper_code}`")
                    
                    caption_parts = [f"📂 **Dept:** {dept_val}", f"📚 **Semester:** {sem_val}", f"📅 **Year:** `{year_val}`"]
                    if ug_pg_col and ug_pg_col in row and pd.notna(row[ug_pg_col]):
                        caption_parts.append(f"🎓 **Level:** {row[ug_pg_col]}")
                    if ccf_cbcs_col and ccf_cbcs_col in row and pd.notna(row[ccf_cbcs_col]):
                        caption_parts.append(f"⚙️ **System:** {row[ccf_cbcs_col]}")
                    if course_struct_col and course_struct_col in row and pd.notna(row[course_struct_col]):
                        caption_parts.append(f"📖 **Structure:** {row[course_struct_col]}")
                    st.caption(" | ".join(caption_parts))
                    
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
    st.markdown("Access official curriculum and syllabi structured strictly by department, curriculum system, and level.")
    
    if df.empty:
        st.warning("⚠️ No data available.")
    else:
        ccf_cbcs_col = next((col for col in df.columns if any(k in col.lower() for k in ['ccf', 'cbcs', 'system', 'curriculum'])), None)
        ug_pg_col = next((col for col in df.columns if any(k in col.lower() for k in ['ug', 'pg', 'level', 'undergraduate'])), None)

        s_col1, s_col2, s_col3 = st.columns(3)
        with s_col1:
            dept_opts = ["All"] + sorted(df[dept_col].dropna().unique().tolist()) if dept_col and dept_col in df.columns else ["All"]
            selected_syl_dept = st.selectbox("Department", dept_opts, key="syl_dept")
        with s_col2:
            sys_opts = ["All"] + sorted(df[ccf_cbcs_col].dropna().unique().tolist()) if ccf_cbcs_col and ccf_cbcs_col in df.columns else ["All"]
            selected_syl_sys = st.selectbox("Curriculum System", sys_opts, key="syl_sys")
        with s_col3:
            lvl_opts = ["All"] + sorted(df[ug_pg_col].dropna().unique().tolist()) if ug_pg_col and ug_pg_col in df.columns else ["All"]
            selected_syl_lvl = st.selectbox("Level / Program", lvl_opts, key="syl_lvl")
            
        filtered_syl = df.copy()
        if doc_type_col and doc_type_col in filtered_syl.columns:
            filtered_syl = filtered_syl[filtered_syl[doc_type_col].astype(str).str.contains("syllabus", case=False, na=False)]
        if selected_syl_dept != "All" and dept_col and dept_col in filtered_syl.columns:
            filtered_syl = filtered_syl[filtered_syl[dept_col] == selected_syl_dept]
        if selected_syl_sys != "All" and ccf_cbcs_col and ccf_cbcs_col in filtered_syl.columns:
            filtered_syl = filtered_syl[filtered_syl[ccf_cbcs_col] == selected_syl_sys]
        if selected_syl_lvl != "All" and ug_pg_col and ug_pg_col in filtered_syl.columns:
            filtered_syl = filtered_syl[filtered_syl[ug_pg_col] == selected_syl_lvl]
            
        st.markdown("---")
        
        s_res1, s_res2 = st.columns([7, 3], vertical_alignment="center")
        with s_res1:
            st.subheader(f"Syllabi Found: {len(filtered_syl)}")
        with s_res2:
            if not filtered_syl.empty:
                syl_csv_data = filtered_syl.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Export Filtered CSV",
                    data=syl_csv_data,
                    file_name="pjc_syllabi_export.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="syl_csv_btn"
                )
        
        if filtered_syl.empty:
            st.info("No syllabi found matching your criteria.")
        else:
            for index, row in filtered_syl.iterrows():
                with st.container(border=True):
                    dept = row.get(dept_col, "N/A") if dept_col else "N/A"
                    system = row.get(ccf_cbcs_col, "N/A") if ccf_cbcs_col else "N/A"
                    level = row.get(ug_pg_col, "N/A") if ug_pg_col else "N/A"
                    doc_title = row.iloc[2] if len(row) > 2 else "Department Syllabus"
                    
                    file_link = ""
                    for col in df.columns:
                        val = str(row[col])
                        if val.startswith("http"):
                            file_link = val
                            break
                            
                    st.markdown(f"**Document Title:** {doc_title}")
                    st.caption(f"📂 **Dept:** {dept} | ⚙️ **System:** {system} | 🎓 **Level:** {level}")
                    
                    if pd.notna(file_link) and str(file_link).startswith("http"):
                        st.markdown(f"🔗 [📥 Open External Syllabus Link]({file_link})")
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
    st.markdown("<h3 style='color: #1E3A8A;'>Frequently Asked Questions (FAQs)</h3>", unsafe_allow_html=True)
    
    with st.expander("1. How can I search for a specific question paper?"):
        st.write("Use the multi-row filters in the **Search & Browse Question Bank** tab to filter by Department, Semester, Year, UG/PG, CCF/CBCS, and Course Structure.")
    
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
