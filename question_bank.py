import streamlit as st
import pandas as pd

# 1. Page Configuration and Styling
st.set_page_config(
    page_title="PJC Question Bank & Archive",
    page_icon="📚",
    layout="wide"
)

# Light-blue professional theme styling
st.markdown("""
    <style>
    .main {
        background-color: #f4f8fb;
    }
    .stButton>button {
        background-color: #004b87;
        color: white;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #00335c;
        color: white;
    }
    h1, h2, h3 {
        color: #004b87;
    }
    </style>
""", unsafe_allow_html=True)

# 2. App Header
st.title("Prabhu Jagatbandhu College")
st.subheader("📖 Question Bank & Academic Archive")
st.markdown("Welcome to the official repository for departmental question papers. Use the filters below to search and download papers for study or NAAC preparation.")

st.markdown("---")

# 3. Load Data from Google Sheets CSV Link
# (Replace the URL below with your actual published Google Sheet CSV link)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR-_lVqargGK2c_8W-U9_orAY62PvBY8qPJuj9XC45p68CCmGZg1qaSnNVRPsPowdBbxQMQ-7Qfx3Eu/pub?output=csv"

@st.cache_data(ttl=60)
def load_data(url):
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data(SHEET_URL)

if df.empty:
    st.info("📌 Database is currently empty or loading. Please ensure your Google Sheet link is configured correctly.")
else:
    # 4. Filtering Section
    st.sidebar.header("🔍 Filter Question Papers")
    
    departments = ["All"] + sorted(df["Department"].dropna().unique().tolist()) if "Department" in df.columns else ["All"]
    selected_dept = st.sidebar.selectbox("Select Department", departments)
    
    semesters = ["All"] + sorted(df["Semester"].dropna().unique().tolist()) if "Semester" in df.columns else ["All"]
    selected_sem = st.sidebar.selectbox("Select Semester", semesters)
    
    # Apply Filters
    filtered_df = df.copy()
    if selected_dept != "All":
        filtered_df = filtered_df[filtered_df["Department"] == selected_dept]
    if selected_sem != "All":
        filtered_df = filtered_df[filtered_df["Semester"] == selected_sem]
        
    # 5. Display Records
    st.markdown(f"### Found **{len(filtered_df)}** Question Papers")
    
    if filtered_df.empty:
        st.warning("No question papers match your selected filters.")
    else:
        for index, row in filtered_df.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    st.write(f"**Paper Code/Name:** {row.get('Paper Code', 'N/A')}")
                    st.caption(f"Department: {row.get('Department', 'N/A')} | Semester: {row.get('Semester', 'N/A')}")
                with col2:
                    st.write(f"**Exam Year:** {row.get('Year', 'N/A')}")
                with col3:
                    file_links = str(row.get('Question Paper file', ''))
                    if file_links and "http" in file_links:
                        # Handle multiple links if separated by comma
                        urls = [u.strip() for u in file_links.split(",")]
                        for i, url in enumerate(urls):
                            st.markdown(f"[📥 Download File {i+1}]({url})", unsafe_allow_html=True)
                    else:
                        st.write("File unavailable")
                st.divider()

# 6. Faculty Upload Portal Section (Password Protected)
with st.expander("🔒 Faculty Upload Portal (Restricted)"):
    st.markdown("Faculty members can upload new question papers using the secure portal link below:")
    st.markdown("[🔗 Open Faculty Upload Google Form](https://forms.gle/YOUR_GOOGLE_FORM_LINK)")
    st.caption("Note: Uploading requires the shared faculty password.")

# 7. Copyright & Footer Section
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666666; font-size: 14px;'>"
    "© 2026 Prabhu Jagatbandhu College &nbsp;|&nbsp; Developed & Maintained by <b>Dr. Kisor Mukhopadhyay</b>"
    "</div>", 
    unsafe_allow_html=True
)
