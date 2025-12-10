"""
PDF Report Generator Module
Handles PDF generation for CV evaluation reports
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from datetime import datetime
import os
from PIL import Image as PILImage


class PDFReportGenerator:
    def __init__(self, logo_path="logo.png"):
        """
        Initialize PDF Report Generator

        Args:
            logo_path: Path to company logo (default: logo.png)
        """
        self.logo_path = logo_path
        self.primary_blue = "#000435"  # Brand blue
        self.secondary_color = "#666666"
        self.page_width, self.page_height = A4

    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def create_logo_header(self):
        """Create centered logo image for page header - compact size"""
        try:
            if os.path.exists(self.logo_path):
                # Get logo dimensions to maintain aspect ratio
                img = PILImage.open(self.logo_path)
                original_width, original_height = img.size
                aspect_ratio = original_height / original_width

                # Set smaller width for compact header
                logo_width = 0.8 * inch  # Reduced from 1.2 inches
                logo_height = logo_width * aspect_ratio

                # Create centered image table
                logo_img = Image(self.logo_path, width=logo_width, height=logo_height)

                # Create a table with centered logo
                logo_table = Table([[logo_img]], colWidths=[7.5*inch])
                logo_table_style = TableStyle([
                    ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                    ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (0, 0), 0),
                    ('RIGHTPADDING', (0, 0), (0, 0), 0),
                    ('TOPPADDING', (0, 0), (0, 0), 0),
                    ('BOTTOMPADDING', (0, 0), (0, 0), 0),
                ])
                logo_table.setStyle(logo_table_style)
                return [logo_table, Spacer(1, 0.05*inch)]  # Reduced spacing from 0.2 to 0.05
            else:
                # If logo not found, just return spacer
                return [Spacer(1, 0.05*inch)]
        except Exception as e:
            print(f"Warning: Could not load logo - {e}")
            return [Spacer(1, 0.05*inch)]

    def create_header(self):
        """Create fixed header section"""
        blue_rgb = self.hex_to_rgb(self.primary_blue)

        # Header text - INCREASED font size
        header_style = ParagraphStyle(
            'CustomHeader',
            fontName='Helvetica-Bold',
            fontSize=15,  # Increased from 13 to 15
            textColor=colors.HexColor(self.primary_blue),
            spaceAfter=12,
            alignment=TA_LEFT
        )

        header_text = "Bottomline Assist Fusion – Powered by a multi dimensional talent evaluation framework"
        return Paragraph(header_text, header_style)

    def create_report_info_section(self, report_header):
        """Create report information section with proper left alignment"""
        elements = []

        # Style for labels and values - left aligned, bigger font
        info_style = ParagraphStyle(
            'ReportInfo',
            fontName='Helvetica',
            fontSize=11,  # Increased from 10
            textColor=colors.black,
            spaceAfter=3,
            alignment=TA_LEFT,
            leading=14
        )

        # Bold style for labels
        label_style = ParagraphStyle(
            'ReportInfoLabel',
            fontName='Helvetica-Bold',
            fontSize=11,  # Increased from 10
            textColor=colors.black,
            spaceAfter=3,
            alignment=TA_LEFT,
            leading=14
        )

        # Create each line as separate paragraph
        elements.append(Paragraph(f"<b>Role:</b> {report_header.get('role', '')}", info_style))
        elements.append(Paragraph(f"<b>Department:</b> {report_header.get('department', '')}", info_style))
        elements.append(Paragraph(f"<b>Company:</b> {report_header.get('company', '')}", info_style))
        elements.append(Paragraph(f"<b>Work Mode:</b> {report_header.get('work_mode', '')}", info_style))
        elements.append(Paragraph(f"<b>Report Date:</b> {report_header.get('report_date', '')}", info_style))

        return elements

    def create_assessment_method(self, method_text):
        """Create assessment method section"""
        style = ParagraphStyle(
            'AssessmentMethod',
            fontName='Helvetica',
            fontSize=11,  # Increased from 9
            textColor=colors.black,
            spaceAfter=14,
            spaceBefore=6,
            alignment=TA_JUSTIFY,
            leading=14
        )

        return Paragraph(f"<b>Assessment Method:</b> {method_text}", style)

    def create_candidate_section(self, candidate):
        """Create individual candidate section with proper left alignment"""
        elements = []

        # Candidate heading - bigger font
        heading_style = ParagraphStyle(
            'CandidateHeading',
            fontName='Helvetica-Bold',
            fontSize=16,  # Increased from 12
            textColor=colors.black,
            spaceAfter=12,
            spaceBefore=16,
            alignment=TA_LEFT
        )

        candidate_num = candidate.get('candidate_number', '')
        elements.append(Paragraph(f"Candidate {candidate_num}", heading_style))

        # Candidate info - left aligned, bigger font
        info_style = ParagraphStyle(
            'CandidateInfo',
            fontName='Helvetica',
            fontSize=11,  # Increased from 10
            textColor=colors.black,
            spaceAfter=3,
            alignment=TA_LEFT,
            leading=14
        )

        elements.append(Paragraph(f"<b>Candidate Name:</b> {candidate.get('candidate_name', '')}", info_style))
        elements.append(Paragraph(f"<b>Match Score:</b> {candidate.get('match_score', 0)}/100", info_style))
        elements.append(Spacer(1, 0.15*inch))

        # Rating Summary heading
        summary_heading_style = ParagraphStyle(
            'SummaryHeading',
            fontName='Helvetica-Bold',
            fontSize=12,  # Increased from 10
            textColor=colors.black,
            spaceAfter=8,
            spaceBefore=4,
            alignment=TA_LEFT
        )

        elements.append(Paragraph("Rating Summary", summary_heading_style))

        # Rating Summary text
        rating_style = ParagraphStyle(
            'RatingSummary',
            fontName='Helvetica',
            fontSize=11,  # Increased from 9
            textColor=colors.black,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            leading=14
        )

        rating_text = candidate.get('rating_summary', '')
        elements.append(Paragraph(rating_text, rating_style))

        # Strengths heading
        strengths_heading = ParagraphStyle(
            'SubHeading',
            fontName='Helvetica-Bold',
            fontSize=12,  # Increased from 10
            textColor=colors.black,
            spaceAfter=8,
            spaceBefore=6,
            alignment=TA_LEFT
        )

        elements.append(Paragraph("Strengths", strengths_heading))

        # Strengths items
        strengths_style = ParagraphStyle(
            'Strengths',
            fontName='Helvetica',
            fontSize=11,  # Increased from 9
            textColor=colors.black,
            leftIndent=0,
            spaceAfter=3,
            alignment=TA_LEFT,
            leading=14
        )

        for strength in candidate.get('strengths', []):
            elements.append(Paragraph(f"• {strength}", strengths_style))

        elements.append(Spacer(1, 0.08*inch))

        # Potential Gaps heading
        gaps_heading = ParagraphStyle(
            'GapsHeading',
            fontName='Helvetica-Bold',
            fontSize=12,  # Increased from 10
            textColor=colors.black,
            spaceAfter=8,
            spaceBefore=6,
            alignment=TA_LEFT
        )

        elements.append(Paragraph("Potential Gaps", gaps_heading))

        # Gaps items
        gaps_style = ParagraphStyle(
            'Gaps',
            fontName='Helvetica',
            fontSize=11,  # Increased from 9
            textColor=colors.black,
            leftIndent=0,
            spaceAfter=3,
            alignment=TA_LEFT,
            leading=14
        )

        for gap in candidate.get('potential_gaps', []):
            elements.append(Paragraph(f"• {gap}", gaps_style))

        return elements

    def create_overall_summary_section(self, overall_summary):
        """Create overall comparative summary section"""
        elements = []

        # Overall section heading - bigger font
        heading_style = ParagraphStyle(
            'OverallHeading',
            fontName='Helvetica-Bold',
            fontSize=16,  # Increased from 12
            textColor=colors.black,
            spaceAfter=12,
            spaceBefore=18,
            alignment=TA_LEFT
        )

        elements.append(Paragraph("Overall Comparative Insight", heading_style))

        # Summary text
        summary_style = ParagraphStyle(
            'OverallSummary',
            fontName='Helvetica',
            fontSize=11,  # Increased from 9
            textColor=colors.black,
            alignment=TA_JUSTIFY,
            leading=14,
            spaceAfter=12
        )

        elements.append(Paragraph(overall_summary, summary_style))

        return elements

    def generate_pdf(self, report_data, output_file="evaluation_report.pdf"):
        """
        Generate PDF report from evaluation data

        Args:
            report_data: Dictionary with report data structure
            output_file: Output PDF filename
        """
        print(f"\n→ Generating PDF report: {output_file}")

        # Create PDF document
        doc = SimpleDocTemplate(
            output_file,
            pagesize=A4,
            rightMargin=0.7*inch,
            leftMargin=0.7*inch,
            topMargin=0.8*inch,  # Reduced from 1.2 inches
            bottomMargin=0.7*inch,
            title="CV Evaluation Report"
        )

        # Build story
        story = []

        # Add logo header
        logo_elements = self.create_logo_header()
        story.extend(logo_elements)

        # Add header
        story.append(self.create_header())
        story.append(Spacer(1, 0.15*inch))

        # Add report info
        report_header = report_data.get('report_header', {})
        info_elements = self.create_report_info_section(report_header)
        story.extend(info_elements)
        story.append(Spacer(1, 0.15*inch))

        # Add assessment method
        assessment_method = report_header.get('assessment_method', '')
        story.append(self.create_assessment_method(assessment_method))

        # Add candidates
        candidates = report_data.get('candidates', [])
        for idx, candidate in enumerate(candidates, 1):
            candidate['candidate_number'] = idx
            candidate_elements = self.create_candidate_section(candidate)
            story.extend(candidate_elements)

            # Add spacer between candidates
            if idx < len(candidates):
                story.append(Spacer(1, 0.3*inch))

        # Add overall summary
        overall_summary = report_data.get('overall_summary', '')
        if overall_summary:
            story.extend(self.create_overall_summary_section(overall_summary))

        # Build PDF
        try:
            doc.build(story)
            print(f"✅ PDF report generated successfully: {output_file}")
            return output_file
        except Exception as e:
            print(f"❌ Error generating PDF: {e}")
            raise
