"""
PDF Generation Service
Generates official sanction and status letters for NBFC personal loans.
Uses ReportLab with Latin-1 compatible currency formatting (Rs.) to avoid font encoding errors.
"""
import os
import asyncio
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class PDFGeneratorService:
    """Service for generating loan sanction letters and official documentation"""

    def __init__(self, output_dir: str = "./uploads/sanction_letters"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    async def generate_sanction_letter(
        self,
        customer_name: str,
        customer_address: str,
        loan_amount: float,
        tenure_months: int,
        interest_rate: float,
        emi_amount: float,
        loan_id: str,
    ) -> str:
        """
        Generate PDF sanction letter.
        Returns: File path of generated PDF.
        """
        await asyncio.sleep(0.3)

        clean_customer_name = customer_name or "Valued Customer"
        clean_address = customer_address or "Address on file"
        first_name = clean_customer_name.split()[0]

        safe_loan_id = str(loan_id).replace("-", "").upper()[:12]
        filename = f"sanction_letter_{safe_loan_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )
        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "CompanyTitle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#1e3a8a"),
            alignment=TA_CENTER,
            spaceAfter=4,
        )

        subtitle_style = ParagraphStyle(
            "SubTitle",
            parent=styles["Normal"],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#475569"),
            alignment=TA_CENTER,
            spaceAfter=15,
        )

        heading_style = ParagraphStyle(
            "DocHeading",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1e3a8a"),
            spaceBefore=10,
            spaceAfter=8,
        )

        # Header Banner
        story.append(Paragraph("NBFC FINANCE LIMITED", title_style))
        story.append(
            Paragraph("Digital Lending Division | Reg. NBFC-ND-SI | RBI Approved", subtitle_style)
        )
        story.append(Spacer(1, 0.15 * inch))

        # Letter Type
        sanction_banner = ParagraphStyle(
            "Banner",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#0f766e"),
            alignment=TA_CENTER,
            spaceAfter=15,
        )
        story.append(Paragraph("OFFICIAL IN-PRINCIPLE LOAN SANCTION LETTER", sanction_banner))
        story.append(Spacer(1, 0.1 * inch))

        # Date and Reference Table
        date_str = datetime.now().strftime("%d %B %Y")
        meta_data = [
            [f"Date: {date_str}", f"Reference No: NBFC-{safe_loan_id}"],
            [f"Applicant: {clean_customer_name}", f"City / Address: {clean_address}"],
        ]
        meta_table = Table(meta_data, colWidths=[3.5 * inch, 3.5 * inch])
        meta_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#334155")),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(meta_table)
        story.append(Spacer(1, 0.2 * inch))

        # Salutation & Body
        story.append(Paragraph(f"Dear {first_name},", styles["Normal"]))
        story.append(Spacer(1, 0.08 * inch))

        body_text = (
            "We are delighted to convey our in-principle sanction for your <b>Personal Loan</b> "
            "application processed via our Agentic AI digital sales platform. Based on your credit "
            "evaluation, KYC verification, and risk assessment, the key loan sanction parameters "
            "are approved as detailed below:"
        )
        story.append(Paragraph(body_text, styles["Normal"]))
        story.append(Spacer(1, 0.15 * inch))

        # Loan Details Table (Using Rs. instead of Unicode ₹ to ensure PDF rendering)
        loan_details = [
            ["Facility Type", "Unsecured Personal Term Loan"],
            ["Sanctioned Amount", f"Rs. {loan_amount:,.2f}"],
            ["Annualized Rate of Interest (ROI)", f"{interest_rate:.2f}% per annum (Reducing)"],
            ["Tenure (Months)", f"{int(tenure_months)} Months"],
            ["Equated Monthly Installment (EMI)", f"Rs. {emi_amount:,.2f}"],
            ["Processing Fee & Documentation", "Rs. 0.00 (Special Campaign Waiver)"],
            [
                "Estimated Disbursement Timeline",
                (datetime.now() + timedelta(days=1)).strftime("%d %B %Y"),
            ],
            ["Repayment Mode", "NACH / e-Mandate auto-debit"],
        ]

        table = Table(loan_details, colWidths=[3.2 * inch, 3.8 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                    ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#f8fafc"), colors.HexColor("#ffffff")]),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0f172a")),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ]
            )
        )
        story.append(table)
        story.append(Spacer(1, 0.2 * inch))

        # Terms & Conditions
        story.append(Paragraph("Key Terms & Conditions:", heading_style))
        terms = [
            "1. Disbursement is subject to final e-sign of the digital loan agreement and bank mandate registration.",
            "2. Monthly installments shall be debited on the 5th day of every calendar month.",
            "3. Zero prepayment or foreclosure charges apply after completion of 6 active EMIs.",
            "4. This sanction letter is valid for 30 calendar days from the date of issue.",
        ]
        for term in terms:
            story.append(Paragraph(term, styles["Normal"]))
            story.append(Spacer(1, 0.04 * inch))

        story.append(Spacer(1, 0.25 * inch))

        # Signatures
        story.append(Paragraph("<b>For NBFC Finance Limited</b>", styles["Normal"]))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph("<b>Authorized Digital Officer</b>", styles["Normal"]))
        story.append(
            Paragraph("Automated Credit & Sanction Desk (Agentic Workflow System)", styles["Normal"])
        )

        doc.build(story)
        return filepath

    async def generate_rejection_letter(
        self,
        customer_name: str,
        customer_address: str,
        reason: str,
        loan_id: str,
    ) -> str:
        """Generate official communication regarding application status"""
        await asyncio.sleep(0.2)

        safe_loan_id = str(loan_id).replace("-", "").upper()[:12]
        filename = f"application_status_{safe_loan_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(filepath, pagesize=A4, margin=36)
        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "Title",
            parent=styles["Heading1"],
            fontSize=18,
            textColor=colors.HexColor("#1e3a8a"),
            alignment=TA_CENTER,
        )
        story.append(Paragraph("NBFC FINANCE LIMITED", title_style))
        story.append(Spacer(1, 0.2 * inch))

        date_str = datetime.now().strftime("%d %B %Y")
        story.append(Paragraph(f"Date: {date_str}", styles["Normal"]))
        story.append(Paragraph(f"Application Ref: NBFC-{safe_loan_id}", styles["Normal"]))
        story.append(Paragraph(f"Applicant: {customer_name or 'Applicant'}", styles["Normal"]))
        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph("Dear Customer,", styles["Normal"]))
        story.append(Spacer(1, 0.1 * inch))
        msg = (
            f"Thank you for your interest in a Personal Loan from NBFC Finance. "
            f"After reviewing your application against our risk underwriting guidelines, "
            f"we are unable to approve the requested terms at this moment. Reason: {reason}. "
            f"We invite you to re-apply after 90 days or explore alternative tenure options."
        )
        story.append(Paragraph(msg, styles["Normal"]))
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph("Sincerely,", styles["Normal"]))
        story.append(Paragraph("Credit Underwriting Team, NBFC Finance Limited", styles["Normal"]))

        doc.build(story)
        return filepath


pdf_generator = PDFGeneratorService()
