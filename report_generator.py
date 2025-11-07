from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from datetime import datetime

def generate_report_pdf(report_content, papers, topic, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor='#1a1a1a',
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph(f"Research Report: {topic}", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    date_text = f"Generated on {datetime.now().strftime('%Y-%m-%d')}"
    story.append(Paragraph(date_text, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("<b>Source Papers</b>", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    
    for i, paper in enumerate(papers, 1):
        paper_info = f"{i}. <b>{paper['title']}</b><br/>"
        paper_info += f"   Authors: {', '.join(paper['authors'][:3])}"
        if len(paper['authors']) > 3:
            paper_info += " et al."
        paper_info += f"<br/>   arXiv:{paper['arxiv_id']} | Published: {paper['published']}"
        
        story.append(Paragraph(paper_info, styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(PageBreak())
    
    story.append(Paragraph("<b>Report</b>", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    
    report_style = ParagraphStyle(
        'Report',
        parent=styles['Normal'],
        alignment=TA_JUSTIFY,
        fontSize=11
    )
    
    for para in report_content.split('\n\n'):
        if para.strip():
            story.append(Paragraph(para, report_style))
            story.append(Spacer(1, 0.15*inch))
    
    doc.build(story)
