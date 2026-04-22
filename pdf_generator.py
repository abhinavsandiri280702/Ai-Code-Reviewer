# pdf_generator.py
import markdown
import html
import re
from fpdf import FPDF

class CodeReviewPDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(44, 62, 80)
        self.cell(0, 10, 'AI Code Review Report', border=0, align='C')
        self.ln(15)

# ADDED exec_result to parameters
def generate_pdf(code, language, review_md, chat_history=None, exec_result=None):
    try:
        safe_code = html.escape(code)
        safe_review_md = re.sub(r'[^\x00-\x7F]+', ' ', review_md)

        review_html = markdown.markdown(safe_review_md, extensions=['fenced_code', 'tables', 'sane_lists'])
        
        # Build Execution HTML
        exec_html = ""
        if exec_result:
            color = "#c0392b" if exec_result['status'] == 'error' else "#27ae60"
            safe_exec_text = html.escape(exec_result['text'])
            exec_html = f"""
            <h2 color="{color}">Execution Results ({exec_result['status'].upper()})</h2>
            <pre><code>{safe_exec_text}</code></pre>
            <br>
            """
        
        chat_html = ""
        if chat_history and len(chat_history) > 1:
            chat_html += '<br><hr><br><h2 color="#2980b9">Follow-up Q&A</h2>'
            for msg in chat_history[1:]:
                role = "You (User)" if msg["role"] == "user" else "AI Reviewer"
                color = "#d35400" if msg["role"] == "user" else "#27ae60"
                safe_msg = re.sub(r'[^\x00-\x7F]+', ' ', msg["content"])
                msg_html = markdown.markdown(safe_msg, extensions=['fenced_code', 'tables'])
                chat_html += f'<h3 color="{color}">{role}:</h3>{msg_html}<br>'

        full_html = f"""
        <h2 color="#2980b9">Original Code ({language})</h2>
        <pre><code>{safe_code}</code></pre>
        <br>
        {exec_html}
        <h2 color="#2980b9">AI Review Report</h2>
        {review_html}
        {chat_html}
        """

        pdf = CodeReviewPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("helvetica", size=11)
        pdf.write_html(full_html)
        
        return bytes(pdf.output())
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None