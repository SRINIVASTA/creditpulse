import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class ComplianceReportGenerator:
    @staticmethod
    def generate_pdf(account_id: str, pd_val: float, ecl_val: float, risk_tag: str, feature_weights: dict) -> str:
        """Generates a secure, audit-ready PDF underwriting report for an individual applicant."""
        output_dir = "data/reports"
        os.makedirs(output_dir, exist_ok=True)
        file_path = f"{output_dir}/Credit_Audit_{account_id}.pdf"
        
        # Initialize Document setup
        doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []
        
        # Styles Setup
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'ReportTitle', parent=styles['Heading1'], fontSize=22, textColor=colors.HexColor('#1E3A8A'), spaceAfter=15
        )
        section_style = ParagraphStyle(
            'SectionHeader', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#0F172A'), spaceBefore=10, spaceAfter=8
        )
        body_style = ParagraphStyle('BodyTextCustom', parent=styles['BodyText'], fontSize=10, leading=14)
        
        # Document Header
        story.append(Paragraph("CreditPulse-AI Compliance & Underwriting Audit", title_style))
        story.append(Paragraph(f"<b>Account Identification Number:</b> {account_id}", body_style))
        story.append(Paragraph(f"<b>Regulatory Evaluation Framework:</b> RBI/NBFC Internal AI Governance Policy", body_style))
        story.append(Spacer(1, 15))
        
        # Financial Risk Metrics Table
        story.append(Paragraph("1. Core Risk Assessment Metrics", section_style))
        metric_data = [
            ['Metric Parameter', 'Evaluated Value', 'Compliance Definition'],
            ['Probability of Default (PD)', f"{pd_val * 100:.2f}%", 'Statistical default probability output by core ML model'],
            ['Expected Credit Loss (ECL)', f"INR {ecl_val:,.2f}", 'Ind AS 104 formula based balance sheet impairment value'],
            ['Regulatory Risk Tier', risk_tag, 'Action tier dictated by systemic portfolio limits']
        ]
        
        t1 = Table(metric_data, colWidths=[160, 120, 240])
        t1.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F8FAFC')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
        ]))
        story.append(t1)
        story.append(Spacer(1, 15))
        
        # Model Explainability Feature Importance Table
        story.append(Paragraph("2. Algorithmic Attribution Analysis (Explainable AI - XAI)", section_style))
        story.append(Paragraph("The values below show the exact numeric impact each internal metric had on the applicant's default classification:", body_style))
        story.append(Spacer(1, 5))
        
        explain_data = [['Underwriting Parameter Column Name', 'Feature Importance Score (SHAP Valuation)']]
        for feature, weight in feature_weights.items():
            explain_data.append([str(feature), f"{weight:+.4f}"])
            
        t2 = Table(explain_data, colWidths=[280, 240])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#334155')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 5),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('FONTSIZE', (0,0), (-1,-1), 9),
        ]))
        story.append(t2)
        
        # Build Document
        doc.build(story)
        return file_path
