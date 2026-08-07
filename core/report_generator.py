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
        safely processing both pandas core types and strings.
        """
        filename = f"Credit_Audit_Report_{str(account_id)}.pdf"
        
        # Safe string & float format parsing
        try:
            clean_provision = f"INR {float(provision_val):,.2f}"
        except (ValueError, TypeError):
            clean_provision = f"INR {str(provision_val)}"
            
        try:
            clean_pd = f"{float(pd_val) * 100:.2f}%" if float(pd_val) <= 1.0 else f"{float(pd_val):.2f}%"
        except (ValueError, TypeError):
            clean_pd = str(pd_val)

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
        
        title_style = ParagraphStyle(
            'DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold',
            fontSize=22, textColor=colors.HexColor('#1E3A8A'), spaceAfter=15
        )
        section_style = ParagraphStyle(
            'SectionHeader', parent=styles['Heading2'], fontName='Helvetica-Bold',
            fontSize=14, textColor=colors.HexColor('#0F172A'), spaceBefore=12, spaceAfter=8
        )
        body_style = ParagraphStyle(
            'BodyTextCustom', parent=styles['Normal'], fontName='Helvetica',
            fontSize=10, leading=14, textColor=colors.HexColor('#334155')
        )
        
        # Title Block
        story.append(Paragraph("CREDITPULSE-AI | RBI STATUTORY AUDIT REPORT", title_style))
        story.append(Paragraph("Issued in accordance with the RBI Income Recognition, Asset Classification and Provisioning (IRACP) Directions.", body_style))
        story.append(Spacer(1, 15))
        
        # Summary Data Matrix Table
        story.append(Paragraph("I. Regulatory Account Metric Snapshot", section_style))
        summary_data = [
            [Paragraph("<b>Statutory Audit Parameter</b>", body_style), Paragraph("<b>Assessed Portfolio Record</b>", body_style)],
            [Paragraph("Target Account Identifier", body_style), Paragraph(str(account_id), body_style)],
            [Paragraph("RBI IRACP Asset Classification", body_style), Paragraph(str(risk_tag), body_style)],
            [Paragraph("Statutory Provision Pool Allocation", body_style), Paragraph(clean_provision, body_style)],
            [Paragraph("Assessed Probability of Default (PD)", body_style), Paragraph(clean_pd, body_style)]
        ]
        
        summary_table = Table(summary_data, colWidths=[250, 250])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#F1F5F9')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.HexColor('#1E3A8A')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 15))
        
        # XAI Feature Table
        story.append(Paragraph("II. Key Fact Statement (KFS) - Scorecard Attribution Weights", section_style))
        xai_data = [[Paragraph("<b>Underwriting Risk Metric Parameter</b>", body_style), Paragraph("<b>Attribution Weight Impact Code</b>", body_style)]]
        
        if isinstance(feature_weights, dict):
            for key, val in feature_weights.items():
                try:
                    num_val = float(val)
                    color_hex = '#EF4444' if num_val > 0 else '#10B981'
                    weight_p = Paragraph(f"<font color='{color_hex}'>{num_val:+.4f}</font>", body_style)
                except (ValueError, TypeError):
                    weight_p = Paragraph(str(val), body_style)
                xai_data.append([Paragraph(str(key), body_style), weight_p])
        else:
            xai_data.append([Paragraph("No features extracted", body_style), Paragraph("0.00", body_style)])
            
        xai_table = Table(xai_data, colWidths=[250, 250])
        xai_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#F8FAFC')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(xai_table)
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("<i>Disclaimer: This document constitutes a certified systemic audit record frozen for internal ledger verification and statutory compliance reporting. All Rights Reserved © 2026 T A Srinivas.</i>", body_style))
        
        doc.build(story)
        return filename
