import streamlit as st
import pandas as pd

# --- GOOGLE SHEET CONFIGURATION ---
# Paste your published Google Sheet CSV URL inside the quotes below:
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTk76nAKx8YLKPJ7O9fqdsupi5ULuxe8RjJhIPv4GpUNUjmQkwEv6NlydEZuAA9nzHe04Dzq16cMTfj/pub?output=csv"

@st.cache_data(ttl=30)
def load_sheet_data():
    """Fetches live student submissions directly from the Google Sheet response backend."""
    if not SHEET_CSV_URL or "YOUR_PUBLISHED" in SHEET_CSV_URL:
        return pd.DataFrame()
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        return df
    except Exception as e:
        return pd.DataFrame()

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Prabhu Jagatbandhu College - Question Bank",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Prabhu Jagatbandhu College Question Bank & Archive")
st.markdown("Centralized repository featuring Major, MDC, and University Previous Years' Questions (PYQs).")

PJC_DEPARTMENTS = [
    "Bengali", "English", "Sanskrit", "History", "Political Science", 
    "Philosophy", "Education", "Sociology", "Economics", "Geography", 
    "Mathematics", "Computer Science", "Physics", "Chemistry", "Botany", 
    "Zoology", "Electronics", "Food & Nutrition", "Physical Education", 
    "Commerce (Accounting & Finance)"
]

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Select View:", ["🔍 Search & Browse Bank", "✍️ Submit Question / PYQ (Google Form)"])

# ==========================================
# 1. SEARCH & BROWSE QUESTION BANK
# ==========================================
if app_mode == "🔍 Search & Browse Bank":
    st.header("Search & Filter Question Bank")
    
    df = load_sheet_data()
    
    if df.empty:
        st.warning("⚠️ Google Sheet URL is not configured yet or no submissions have been made. Please publish your Google Sheet as a CSV and update `SHEET_CSV_URL` in the code.")
    else:
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Filter controls layout
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            # Look for Department column dynamically
            dept_col = next((col for col in df.columns if 'department' in col.lower()), df.columns[1] if len(df.columns) > 1 else None)
            dept_options = ["All"] + list(df[dept_col].dropna().unique()) if dept_col else ["All"]
            selected_dept = st.selectbox("Department", dept_options)
            
        with f_col2:
            # Look for Semester column dynamically
            sem_col = next((col for col in df.columns if 'semester' in col.lower()), df.columns[3] if len(df.columns) > 3 else None)
            sem_options = ["All"] + list(df[sem_col].dropna().unique()) if sem_col else ["All"]
            selected_sem = st.selectbox("Semester", sem_options)
            
        with f_col3:
            search_text = st.text_input("Keyword Search", placeholder="Paper code or text...")
            
        # Apply filters
        filtered_df = df.copy()
        if selected_dept != "All" and dept_col:
            filtered_df = filtered_df[filtered_df[dept_col] == selected_dept]
        if selected_sem != "All" and sem_col:
            filtered_df = filtered_df[filtered_df[sem_col] == selected_sem]
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
                    # Extract values safely
                    timestamp = row.iloc[0] if len(row) > 0 else ""
                    dept_val = row[dept_col] if dept_col in row else "N/A"
                    sem_val = row[sem_col] if sem_col in row else "N/A"
                    
                    # Assume second or third column holds paper info/code
                    paper_info = row.iloc[2] if len(row) > 2 else "Question Paper"
                    file_link = row.iloc[-1] if len(row) > 0 else ""
                    
                    st.markdown(f"**Paper Details:** {paper_info}")
                    st.caption(f"📂 **Dept:** {dept_val} | 📚 **Semester:** {sem_val} | 🕒 **Submitted:** {timestamp}")
                    
                    if pd.notna(file_link) and str(file_link).startswith("http"):
                        st.markdown(f"🔗 [📥 View / Download Document from Drive]({file_link})")
                    else:
                        st.warning("⚠️ No file link available for this submission.")

# ==========================================
# 2. SUBMIT QUESTION VIA GOOGLE FORM LINK
# ==========================================
elif app_mode == "✍️ Submit Question / PYQ (Google Form)":
    st.header("Upload Question Paper via Secure Google Form")
    st.markdown("""
    To ensure seamless file uploads and avoid permission restrictions, question paper submissions are managed through our official Google Form portal.
    """)
    
    GOOGLE_FORM_URL = "https://forms.gle/ukm1N3SyHaVdNmi3A"
    st.link_button("📤 Open PJC Question Submission Form", GOOGLE_FORM_URL, use_container_width=True)
    
    st.info("💡 **Tip:** Submitted papers are automatically sorted into departmental folders and instantly populate this search archive.")
