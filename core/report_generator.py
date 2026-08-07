import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class ComplianceReportGenerator:
    @staticmethod
    def generate_pdf(account_id, pd_val, provision_val, risk_tag, feature_weights):
        """
        Generates an official, professionally styled RBI Statutory Inspection Form 
        using strict ReportLab elements to track compliance details.
        """
        filename = f"Credit_Audit_Report_{account_id}.pdf"
        
        # Initialize Document
        doc = SimpleDocTemplate(
            filename,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        
        styles = getSampleStyleSheet()
        story = []
        
        # Define Custom Corporate Banking Color Palette Styles
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            textColor=colors.HexColor('#1E3A8A'),
            spaceAfter=15
        )
        
        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=colors.HexColor('#0F172A'),
            spaceBefore=12,
            spaceAfter=8
        )
        
        body_style = ParagraphStyle(
            'BodyTextCustom',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#334155')
        )
        
        # 1. Document Header Block
        story.append(Paragraph("CREDITPULSE-AI | RBI STATUTORY AUDIT REPORT", title_style))
        story.append(Paragraph("Issued in accordance with the RBI Income Recognition, Asset Classification and Provisioning (IRACP) Directions.", body_style))
        story.append(Spacer(1, 15))
        
        # 2. Summary Grid Block (Dynamic Core Metrics Data Matrix Table)
        story.append(Paragraph("I. Regulatory Account Metric Snapshot", section_style))
        
        summary_data = [
            [Paragraph("<b>Statutory Audit Parameter</b>", body_style), Paragraph("<b>Assessed Portfolio Record</b>", body_style)],
            [Paragraph("Target Account Identifier", body_style), Paragraph(str(account_id), body_style)],
            [Paragraph("RBI IRACP Asset Classification", body_style), Paragraph(str(risk_tag), body_style)],
            [Paragraph("Statutory Provision Pool Allocation", body_style), Paragraph(f"INR {provision_val:,.2f}", body_style)],
            [Paragraph("Assessed Probability of Default (PD)", body_style), Paragraph(f"{pd_score_label(pd_val)}", body_style)]
        ]
        
        summary_table = Table(summary_data, colWidths=[250, 250])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#F1F5F9')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.HexColor('#1E3A8A')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 15))
        
        # 3. Explainable AI (XAI) Attribution Table Block (RBI Transparency Mandate)
        story.append(Paragraph("II. Key Fact Statement (KFS) - Scorecard Attribution Weights", section_style))
        story.append(Paragraph("Programmatic reason code weights driving asset evaluation and underwriting actions:", body_style))
        story.append(Spacer(1, 8))
        
        xai_data = [[Paragraph("<b>Underwriting Risk Metric Parameter</b>", body_style), Paragraph("<b>Attribution Weight Impact Code</b>", body_style)]]
        for key, val in feature_weights.items():
            color_hex = '#EF4444' if val > 0 else '#10B981' # Color maps positive/negative risks
            weight_p = Paragraph(f"<font color='{color_hex}'>{val:+.4f}</font>", body_style)
            xai_data.append([Paragraph(str(key), body_style), weight_p])
            
        xai_table = Table(xai_data, colWidths=[250, 250])
        xai_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#F8FAFC')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ]))
        story.append(xai_table)
        story.append(Spacer(1, 20))
        
        # 4. Regulatory Audit Footnote Declaration Statement
        story.append(Paragraph("<i>Disclaimer: This document constitutes a certified systemic audit record frozen for internal ledger verification and statutory compliance reporting. All Rights Reserved © 2026 T A Srinivas.</i>", body_style))
        
        # Build Document Template Canvas Object
        doc.build(story)
        return filename

def pd_score_label(val):
    try:
        return f"{float(val)*100:.2f}%"
    except (ValueError, TypeError):
        return str(val)
