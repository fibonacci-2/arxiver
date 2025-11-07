from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

def generate_pdf(summary, metadata, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor='#1a1a1a',
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph(metadata['title'], title_style))
    story.append(Spacer(1, 0.2*inch))
    
    authors_text = ", ".join(metadata['authors'][:3])
    if len(metadata['authors']) > 3:
        authors_text += " et al."
    
    story.append(Paragraph(f"<b>Authors:</b> {authors_text}", styles['Normal']))
    story.append(Paragraph(f"<b>ArXiv ID:</b> {metadata['arxiv_id']}", styles['Normal']))
    story.append(Paragraph(f"<b>Published:</b> {metadata['published']}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("<b>Summary</b>", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    
    summary_style = ParagraphStyle(
        'Summary',
        parent=styles['Normal'],
        alignment=TA_JUSTIFY,
        fontSize=11
    )
    
    for para in summary.split('\n\n'):
        if para.strip():
            story.append(Paragraph(para, summary_style))
            story.append(Spacer(1, 0.15*inch))
    
    doc.build(story)
