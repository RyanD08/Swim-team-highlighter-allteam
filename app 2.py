
import streamlit as st
import fitz  # PyMuPDF
import io
from collections import defaultdict

st.title("🏊 Swim Team Highlighter for Psych/Heat Sheets")

uploaded_file = st.file_uploader("Upload Psych/Heat Sheet PDF", type="pdf")
team_code = st.text_input("Enter Team Code (e.g. MAC-MA, NPAC-MA, UDAC-MA)")
all_teams = st.checkbox("All teams")

def highlight_pdf_by_team(input_pdf, team_codes):
    highlighted_pdfs = {}
    doc = fitz.open(stream=input_pdf.read(), filetype="pdf")
    
    for code in team_codes:
        doc_copy = fitz.open(stream=doc.write(), filetype="pdf")
        num_highlights = 0
        for page in doc_copy:
            blocks = page.get_text("blocks")
            for block in blocks:
                text = block[4]
                if code in text:
                    matches = page.search_for(text.strip())
                    for inst in matches:
                        highlight_rect = fitz.Rect(inst.x0, inst.y0, inst.x1, inst.y1)
                        # No black box, slightly darker highlight (opacity higher)
                        page.draw_rect(highlight_rect, fill=(1, 1, 0), overlay=True, fill_opacity=0.6)
                        num_highlights += 1
        output = io.BytesIO()
        doc_copy.save(output)
        doc_copy.close()
        highlighted_pdfs[code] = output.getvalue()
    doc.close()
    return highlighted_pdfs

if uploaded_file:
    if all_teams:
        # Extract all team codes by scanning the PDF text blocks
        doc_temp = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        team_set = set()
        for page in doc_temp:
            blocks = page.get_text("blocks")
            for block in blocks:
                text = block[4]
                if "-" in text:
                    fragments = text.split()
                    for frag in fragments:
                        if "-" in frag and len(frag) <= 10:
                            team_set.add(frag.strip(",:;()"))
        doc_temp.close()
        
        st.write(f"📋 Found {len(team_set)} unique team codes")
        highlighted = highlight_pdf_by_team(uploaded_file, list(team_set))
        
        for code, pdf_data in highlighted.items():
            st.download_button(
                label=f"📥 Download Highlighted PDF for {code}",
                data=pdf_data,
                file_name=f"{code}_highlighted.pdf",
                mime="application/pdf"
            )
    elif team_code:
        highlighted = highlight_pdf_by_team(uploaded_file, [team_code])
        pdf_data = highlighted[team_code]
        st.success(f"✅ Highlighted swimmers from {team_code} with visible highlights!")
        st.download_button(
            label="📥 Download Highlighted PDF",
            data=pdf_data,
            file_name=f"{team_code}_highlighted.pdf",
            mime="application/pdf"
        )
