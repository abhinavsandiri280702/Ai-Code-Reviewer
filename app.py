import streamlit as st
import streamlit.components.v1 as components
import os
from analyzer import run_static_analysis
from ai_reviewer import generate_review, chat_with_code
from pdf_generator import generate_pdf
from code_executor import execute_code
import database

# Initialize Database
database.init_db()

LANGUAGE_MAP = {
    '.py': 'Python', '.js': 'JavaScript', '.java': 'Java',
    '.c': 'C', '.cpp': 'C++', '.html': 'HTML'
}

REVERSE_EXT_MAP = {
    'Python': '.py', 'JavaScript': '.js', 'Java': '.java',
    'C': '.c', 'C++': '.cpp', 'HTML': '.html'
}

st.set_page_config(page_title="Advanced AI Code Reviewer", page_icon="💻", layout="wide")

# --- INITIALIZE SESSION STATE ---
if "current_review_id" not in st.session_state: st.session_state.current_review_id = None
if "review_report" not in st.session_state: st.session_state.review_report = None
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "code_content" not in st.session_state: st.session_state.code_content = ""
if "language" not in st.session_state: st.session_state.language = "Unknown"
if "pdf_data" not in st.session_state: st.session_state.pdf_data = None
if "exec_result" not in st.session_state: st.session_state.exec_result = None

# --- SIDEBAR: HISTORY ---
with st.sidebar:
    st.header("📚 Review History")
    if st.button("➕ Start New Review", use_container_width=True):
        st.session_state.current_review_id = None
        st.session_state.review_report = None
        st.session_state.chat_history = []
        st.session_state.code_content = ""
        st.session_state.language = "Unknown"
        st.session_state.pdf_data = None
        st.session_state.exec_result = None
        st.rerun()
        
    st.divider()
    
    history = database.get_all_reviews_summary()
    if not history:
        st.info("No past reviews yet.")
    else:
        for rev_id, timestamp, lang in history:
            if st.button(f"📄 {lang} | {timestamp[:16]}", key=f"hist_{rev_id}", use_container_width=True):
                data = database.get_review_by_id(rev_id)
                if data:
                    st.session_state.current_review_id = rev_id
                    st.session_state.language = data["language"]
                    st.session_state.code_content = data["code"]
                    st.session_state.exec_result = data["exec_result"]
                    st.session_state.review_report = data["ai_report"]
                    st.session_state.chat_history = data["chat_history"]
                    
                    st.session_state.pdf_data = generate_pdf(
                        data["code"], data["language"], data["ai_report"], data["chat_history"], data["exec_result"]
                    )
                    st.rerun()

# --- MAIN UI ---
st.title("💻 Advanced AI Assisted Code Reviewer")

# Only show upload/paste boxes if we are starting a NEW review
if st.session_state.current_review_id is None and st.session_state.review_report is None:
    tab1, tab2 = st.tabs(["📂 Upload File", "📝 Paste Code Directly"])

    code = None
    language = "Unknown"
    file_extension = ".txt"

    with tab1:
        uploaded_file = st.file_uploader("Upload a code file", type=["py", "js", "java", "c", "cpp", "html"])
        if uploaded_file:
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            language = LANGUAGE_MAP.get(file_extension, "Unknown")
            code = uploaded_file.getvalue().decode("utf-8")

    with tab2:
        pasted_code = st.text_area("Paste your source code here:", height=300)
        selected_language = st.selectbox("Select Programming Language", ["Python", "JavaScript", "Java", "C", "C++", "HTML"])
        if pasted_code.strip():
            code = pasted_code
            language = selected_language
            file_extension = REVERSE_EXT_MAP.get(language, ".txt")

    if code:
        st.info(f"Detected/Selected Language: **{language}**")
        
        with st.expander("View Code to be Reviewed"):
            st.code(code, language=language.lower() if language != "Unknown" else None)
            
        if st.button("🚀 Run Advanced Code Review", type="primary"):
            with st.spinner("Executing code and generating AI report..."):
                
                temp_file_path = f"temp_code{file_extension}"
                with open(temp_file_path, "w", encoding="utf-8") as f:
                    f.write(code)
                
                exec_res = execute_code(temp_file_path, language)
                sa_results = run_static_analysis(temp_file_path, language)
                ai_report = generate_review(code, language, sa_results, exec_res['text'])
                
                if os.path.exists(temp_file_path): os.remove(temp_file_path)
                
                chat_hist = [{"role": "system", "content": f"You are reviewing this code:\n\n{code}\n\nExecution Output:\n{exec_res['text']}\n\nInitial review:\n{ai_report}"}]
                
                rev_id = database.save_review(language, code, exec_res, ai_report, chat_hist)
                
                st.session_state.current_review_id = rev_id
                st.session_state.exec_result = exec_res
                st.session_state.review_report = ai_report
                st.session_state.code_content = code
                st.session_state.language = language
                st.session_state.chat_history = chat_hist
                
                st.session_state.pdf_data = generate_pdf(code, language, ai_report, chat_hist, exec_res)
                st.rerun()

# --- RESULTS SECTION ---
if st.session_state.review_report:
    st.divider()
    
    # NEW FEATURE: Show original code at the top of the results!
    st.markdown(f"### 📄 Original Source Code ({st.session_state.language})")
    with st.expander("View Code", expanded=False):
        st.code(st.session_state.code_content, language=st.session_state.language.lower() if st.session_state.language != "Unknown" else None)
    
    st.markdown("### 🖥️ Code Execution Results")
    res = st.session_state.exec_result
    
    if st.session_state.language == 'HTML':
        st.success("**Live Webpage Preview:**")
        components.html(st.session_state.code_content, height=400, scrolling=True)
    elif res['status'] == 'error':
        st.error(f"**Runtime/Compilation Error:**\n\n```text\n{res['text']}\n```")
    elif res['status'] == 'success':
        st.success(f"**Output:**\n\n```text\n{res['text']}\n```")
    else:
        st.warning(f"**Status:** {res['text']}")
        
    st.divider()
    
    col1, col2 = st.columns([0.8, 0.2])
    with col1: st.markdown("### 🧠 AI Code Review Report")
    with col2:
        if st.session_state.pdf_data:
            st.download_button("📥 Download as PDF", data=st.session_state.pdf_data, file_name=f"Code_Review_{st.session_state.current_review_id}.pdf", mime="application/pdf", type="primary")
        
    st.markdown(st.session_state.review_report)
    st.divider()
    
    st.markdown("### 💬 Ask Follow-up Questions")
    for msg in st.session_state.chat_history[1:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if user_question := st.chat_input("Ask a question about the code or the review..."):
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        with st.chat_message("user"): st.markdown(user_question)
            
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = chat_with_code(st.session_state.chat_history)
                st.markdown(answer)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                
        database.update_chat_history(st.session_state.current_review_id, st.session_state.chat_history)
                
        with st.spinner("Updating PDF..."):
            st.session_state.pdf_data = generate_pdf(
                st.session_state.code_content, st.session_state.language, 
                st.session_state.review_report, st.session_state.chat_history, st.session_state.exec_result
            )
        st.rerun()