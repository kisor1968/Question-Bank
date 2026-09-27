import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

# --- DATABASE & STORAGE CONFIGURATION ---
DB_NAME = "pjc_question_bank.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_text TEXT NOT NULL,
            course_type TEXT,
            department TEXT,
            semester TEXT,
            paper_code TEXT,
            unit_module TEXT,
            marks INTEGER,
            difficulty TEXT,
            source_tag TEXT,
            file_link TEXT,
            date_added TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def fetch_questions(course_type="All", dept="All", sem="All", diff="All", search_query=""):
    conn = sqlite3.connect(DB_NAME)
    query = "SELECT * FROM questions WHERE 1=1"
    params = []
    
    if course_type != "All":
        query += " AND course_type = ?"
        params.append(course_type)
    if dept != "All":
        query += " AND department = ?"
        params.append(dept)
    if sem != "All":
        query += " AND semester = ?"
        params.append(sem)
    if diff != "All":
        query += " AND difficulty = ?"
        params.append(diff)
    if search_query:
        query += " AND (question_text LIKE ? OR paper_code LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])
        
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

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
    
    f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)
    
    with f_col1:
        selected_course_type = st.selectbox("Course Type", ["All", "Major", "MDC (Multidisciplinary)"])
    with f_col2:
        selected_dept = st.selectbox("Department", ["All"] + PJC_DEPARTMENTS)
    with f_col3:
        selected_sem = st.selectbox("Semester", ["All", "Semester I", "Semester II", "Semester III", "Semester IV", "Semester V", "Semester VI"])
    with f_col4:
        selected_diff = st.selectbox("Difficulty", ["All", "Easy", "Medium", "Hard"])
    with f_col5:
        search_text = st.text_input("Keyword Search", placeholder="Paper code or text...")
        
    filtered_df = fetch_questions(
        course_type=selected_course_type, 
        dept=selected_dept, 
        sem=selected_sem, 
        diff=selected_diff, 
        search_query=search_text
    )
    
    st.markdown("---")
    st.subheader(f"Results Found: {len(filtered_df)}")
    
    if filtered_df.empty:
        st.info("No questions found matching your criteria yet.")
    else:
        for index, row in filtered_df.iterrows():
            with st.container(border=True):
                col_q1, col_q2 = st.columns([4, 1])
                with col_q1:
                    st.markdown(f"**Paper / Title:** {row['question_text']}")
                    st.caption(f"🎓 **Type:** `{row['course_type']}` | 📂 **Dept:** {row['department']} | **Paper Code:** `{row['paper_code']}` | **Semester:** {row['semester']} | **Unit:** {row['unit_module']} | **Source:** {row['source_tag']}")
                    
                    if row['file_link']:
                        st.markdown(f"🔗 [📥 View / Download Document]({row['file_link']})")
                    else:
                        st.warning("⚠️ No file link attached to this entry.")
                with col_q2:
                    st.markdown(f"**Marks:** {row['marks']}")
                    st.markdown(f"`{row['difficulty']}`")

# ==========================================
# 2. SUBMIT QUESTION VIA GOOGLE FORM LINK
# ==========================================
elif app_mode == "✍️ Submit Question / PYQ (Google Form)":
    st.header("Upload Question Paper via Secure Google Form")
    st.markdown("""
    To ensure seamless file uploads and avoid permission restrictions, question paper submissions are securely managed through our official Google Form portal. 
    
    Click the button below to open the submission form in a new tab:
    """)
    
    # Replace with your actual Google Form shareable link (e.g., https://forms.gle/xxxxx)
    GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/YOUR_FORM_ID_HERE/viewform"
    
    st.link_button("📤 Open PJC Question Submission Form", GOOGLE_FORM_URL, use_container_width=True)
    
    st.info("💡 **Tip:** After submitting your question paper through the form, it will be routed to the departmental folder and updated in the archive.")
