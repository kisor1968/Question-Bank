import streamlit as st
import sqlite3
import pandas as pd
import os
import json
import tempfile
from datetime import datetime

# --- GOOGLE DRIVE API IMPORTS ---
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- DATABASE & STORAGE CONFIGURATION ---
DB_NAME = "pjc_question_bank.db"
TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

# --- GOOGLE DRIVE SCOPES ---
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    """Initializes Google Drive service using Streamlit Secrets with strict PEM normalization and a secure temp file bridge."""
    try:
        if "gcp_service_account" in st.secrets:
            sec = st.secrets["gcp_service_account"]
            
            # Extract and clean the private key line by line to eliminate stray characters/padding errors
            raw_key = str(sec.get("private_key", ""))
            if "\\n" in raw_key:
                raw_key = raw_key.replace("\\n", "\n")
                
            lines = raw_key.splitlines()
            cleaned_lines = [line.strip() for line in lines if line.strip()]
            cleaned_key = "\n".join(cleaned_lines)
            
            # Ensure correct PEM header and footer wrapping
            if not cleaned_key.startswith("-----BEGIN PRIVATE KEY-----"):
                start = cleaned_key.find("-----BEGIN PRIVATE KEY-----")
                end = cleaned_key.find("-----END PRIVATE KEY-----") + len("-----END PRIVATE KEY-----")
                if start != -1 and end != -1:
                    cleaned_key = cleaned_key[start:end]

            service_account_info = {
                "type": "service_account",
                "project_id": str(sec.get("project_id", "")),
                "private_key_id": str(sec.get("private_key_id", "")),
                "private_key": cleaned_key,
                "client_email": str(sec.get("client_email", "")),
                "client_id": str(sec.get("client_id", "")),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": str(sec.get("client_x509_cert_url", ""))
            }
            
            # Write to a secure temporary file to let Google's library load it natively without crypto edge cases
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_cred:
                json.dump(service_account_info, temp_cred)
                temp_cred_path = temp_cred.name

            creds = service_account.Credentials.from_service_account_file(
                temp_cred_path, scopes=SCOPES
            )
            
            # Clean up temp file immediately after loading
            if os.path.exists(temp_cred_path):
                os.remove(temp_cred_path)
                
        elif os.path.exists('credentials.json'):
            creds = service_account.Credentials.from_service_account_file(
                'credentials.json', scopes=SCOPES
            )
        else:
            return None
            
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        st.error(f"Google Drive Authentication Error: {e}")
        return None

def upload_to_google_drive(file_path, file_name):
    """Uploads file to the college Google Drive folder and returns public link."""
    service = get_drive_service()
    if not service:
        st.error("Google Drive service could not be initialized. Check secrets configuration.")
        return None
        
    try:
        folder_id = st.secrets.get("google_drive", {}).get("folder_id", "")
        file_metadata = {
            'name': file_name,
            'parents': [folder_id] if folder_id else []
        }
        media = MediaFileUpload(file_path, resumable=True)
        
        file = service.files().create(
            body=file_metadata, media_body=media, fields='id, webViewLink'
        ).execute()
        
        file_id = file.get('id')
        service.permissions().create(
            fileId=file_id,
            body={'role': 'reader', 'type': 'anyone'}
        ).execute()

        return file.get('webViewLink')
    except Exception as e:
        st.error(f"Google Drive Upload Error: {e}")
        return None

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

def insert_question(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO questions (
            question_text, course_type, department, semester, 
            paper_code, unit_module, marks, difficulty, source_tag, file_link, date_added
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()
    conn.close()

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
st.markdown("Centralized repository featuring Major, MDC, and University Previous Years' Questions (PYQs) stored in official Google Drive.")

PJC_DEPARTMENTS = [
    "Bengali", "English", "Sanskrit", "History", "Political Science", 
    "Philosophy", "Education", "Sociology", "Economics", "Geography", 
    "Mathematics", "Computer Science", "Physics", "Chemistry", "Botany", 
    "Zoology", "Electronics", "Food & Nutrition", "Physical Education", 
    "Commerce (Accounting & Finance)"
]

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Select View:", ["🔍 Search & Browse Bank", "✍️ Add Question / PYQ"])

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
        st.info("No questions found matching your criteria.")
    else:
        for index, row in filtered_df.iterrows():
            with st.container(border=True):
                col_q1, col_q2 = st.columns([4, 1])
                with col_q1:
                    st.markdown(f"**Paper / Title:** {row['question_text']}")
                    st.caption(f"🎓 **Type:** `{row['course_type']}` | 📂 **Dept:** {row['department']} | **Paper Code:** `{row['paper_code']}` | **Semester:** {row['semester']} | **Unit:** {row['unit_module']} | **Source:** {row['source_tag']}")
                    
                    if row['file_link']:
                        st.markdown(f"🔗 [📥 Download / View Document from Google Drive]({row['file_link']})")
                    else:
                        st.warning("⚠️ No file link attached to this entry.")
                with col_q2:
                    st.markdown(f"**Marks:** {row['marks']}")
                    st.markdown(f"`{row['difficulty']}`")

# ==========================================
# 2. ADD QUESTION / PYQ PORTAL
# ==========================================
elif app_mode == "✍️ Add Question / PYQ":
    st.header("Upload Question Paper / PYQ")
    st.markdown("Uploaded documents will be safely routed directly into your official Google Drive repository.")

    with st.form("add_question_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            course_type = st.selectbox("Course Structure", ["Major", "MDC (Multidisciplinary)"])
            department = st.selectbox("Department", PJC_DEPARTMENTS)
        with col2:
            semester = st.selectbox("Semester", ["Semester I", "Semester II", "Semester III", "Semester IV", "Semester V", "Semester VI"])
            paper_code = st.text_input("Paper Code & Name", placeholder="e.g., BNGR-CC-1")
        with col3:
            unit_module = st.text_input("Unit / Module", placeholder="e.g., Unit 2")
            marks = st.number_input("Marks Allocated", min_value=1, max_value=100, value=50)
            
        col4, col5, col6 = st.columns(3)
        with col4:
            difficulty = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"])
        with col5:
            source_tag = st.text_input("Source Tag", value="University PYQ", placeholder="e.g., Mid-Sem 2026")
        with col6:
            uploaded_file = st.file_uploader("Upload Document (PDF, PNG, JPEG)", type=["pdf", "png", "jpg", "jpeg"])
            
        submitted = st.form_submit_button("Upload & Save to Google Drive")
        
        if submitted:
            if not paper_code:
                st.error("Please fill out at least the Paper Code & Name.")
            elif not uploaded_file:
                st.error("Please attach a document file (PDF, PNG, JPEG) to upload.")
            else:
                file_label = uploaded_file.name
                question_text = f"{department} - {paper_code} ({semester}) [{file_label}]"
                
                with st.spinner("Syncing file with Google Drive..."):
                    temp_path = os.path.join(TEMP_DIR, uploaded_file.name)
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    drive_file_link = upload_to_google_drive(temp_path, uploaded_file.name)
                    
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                
                if drive_file_link:
                    data_tuple = (
                        question_text,
                        course_type,
                        department,
                        semester,
                        paper_code,
                        unit_module,
                        marks,
                        difficulty,
                        source_tag,
                        drive_file_link,
                        datetime.now().strftime("%Y-%m-%d")
                    )
                    insert_question(data_tuple)
                    st.success("Successfully uploaded to Google Drive and added to the question bank!")
                else:
                    st.error("Upload failed. Please check your Google Drive API and permissions.")
