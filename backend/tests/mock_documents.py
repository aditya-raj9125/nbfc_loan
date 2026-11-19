"""
Mock Document Generator for Testing
Generates realistic synthetic PDFs for testing multimodal OCR and document ingestion:
- Salary Slip (Standard high salary - Rs. 85,000/mo)
- Salary Slip (Low salary - Rs. 20,000/mo for FOIR rejection tests)
- PAN Card document
- Aadhaar Card document
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

MOCK_DOCS_DIR = os.path.join(os.path.dirname(__file__), "mock_files")
os.makedirs(MOCK_DOCS_DIR, exist_ok=True)


def create_mock_salary_slip(
    filename: str = "mock_salary_slip.pdf",
    employee_name: str = "Rahul Sharma",
    monthly_salary: float = 85000.0,
    employer: str = "Tata Consultancy Services Ltd",
    pan: str = "ABCDE1234F"
) -> str:
    """Generate a synthetic salary slip PDF using ReportLab"""
    file_path = os.path.join(MOCK_DOCS_DIR, filename)
    doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    elements = []

    # Header
    title_style = ParagraphStyle(
        "CompanyHeader",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        alignment=1,
        textColor=colors.HexColor("#1A365D")
    )
    elements.append(Paragraph(employer, title_style))
    elements.append(Paragraph("<font size=10 color='#4A5568'>PAYSLIP FOR THE MONTH OF OCTOBER 2026</font>", ParagraphStyle("SubHeader", alignment=1, leading=14)))
    elements.append(Spacer(1, 15))

    # Employee Details Table
    emp_data = [
        ["Employee Name:", employee_name, "Designation:", "Lead Software Engineer"],
        ["Employee ID:", "EMP98214", "PAN Number:", pan],
        ["Bank A/C No:", "XXXXXXXX4321", "Pay Period:", "01-Oct-2026 to 31-Oct-2026"],
        ["Working Days:", "31", "Paid Days:", "31"]
    ]
    t1 = Table(emp_data, colWidths=[110, 150, 110, 150])
    t1.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LINEBELOW', (0,-1), (-1,-1), 1, colors.HexColor("#E2E8F0")),
    ]))
    elements.append(t1)
    elements.append(Spacer(1, 15))

    # Earnings & Deductions Breakdown
    basic = round(monthly_salary * 0.50, 2)
    hra = round(monthly_salary * 0.30, 2)
    allowance = round(monthly_salary * 0.20, 2)
    pf = 1800.0
    tax = round(monthly_salary * 0.08, 2)
    total_deductions = pf + tax
    net_pay = monthly_salary - total_deductions

    salary_data = [
        ["EARNINGS", "AMOUNT (Rs.)", "DEDUCTIONS", "AMOUNT (Rs.)"],
        ["Basic Salary", f"{basic:,.2f}", "Provident Fund (PF)", f"{pf:,.2f}"],
        ["House Rent Allowance", f"{hra:,.2f}", "Professional Tax", f"{tax:,.2f}"],
        ["Special Allowance", f"{allowance:,.2f}", "", ""],
        ["Gross Earnings", f"{monthly_salary:,.2f}", "Total Deductions", f"{total_deductions:,.2f}"],
        ["NET SALARY PAYABLE", f"Rs. {net_pay:,.2f}", "", ""]
    ]
    t2 = Table(salary_data, colWidths=[170, 90, 170, 90])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2B6CB0")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('ALIGN', (3,0), (3,-1), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#EDF2F7")),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 15))

    footer_style = ParagraphStyle("Footer", fontName="Helvetica-Oblique", fontSize=8, textColor=colors.gray, alignment=1)
    elements.append(Paragraph("This is a computer-generated salary slip and does not require a physical signature.", footer_style))

    doc.build(elements)
    return file_path


def create_mock_pan_card(
    filename: str = "mock_pan_card.pdf",
    name: str = "RAHUL SHARMA",
    pan: str = "ABCDE1234F",
    father_name: str = "SURESH SHARMA",
    dob: str = "15/08/1992"
) -> str:
    """Generate a synthetic PAN Card PDF"""
    file_path = os.path.join(MOCK_DOCS_DIR, filename)
    doc = SimpleDocTemplate(file_path, pagesize=(400, 250), rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    styles = getSampleStyleSheet()

    elements = []
    header = ParagraphStyle("GovHeader", fontName="Helvetica-Bold", fontSize=12, alignment=1, textColor=colors.HexColor("#1A365D"))
    elements.append(Paragraph("INCOME TAX DEPARTMENT", header))
    elements.append(Paragraph("<font size=8>GOVT. OF INDIA</font>", ParagraphStyle("GovSub", alignment=1, fontSize=8)))
    elements.append(Spacer(1, 10))

    pan_data = [
        ["Name:", name],
        ["Father's Name:", father_name],
        ["Date of Birth:", dob],
        ["Permanent Account Number:", f"<b>{pan}</b>"]
    ]
    t = Table(pan_data, colWidths=[150, 200])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t)
    doc.build(elements)
    return file_path


def create_mock_aadhaar_card(
    filename: str = "mock_aadhaar_card.pdf",
    name: str = "Anjali Verma",
    aadhaar: str = "XXXX XXXX 9012",
    address: str = "987 T Nagar, Chennai 600017",
    dob: str = "24/11/1998"
) -> str:
    """Generate a synthetic Aadhaar Card PDF"""
    file_path = os.path.join(MOCK_DOCS_DIR, filename)
    doc = SimpleDocTemplate(file_path, pagesize=(400, 250), rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    styles = getSampleStyleSheet()

    elements = []
    header = ParagraphStyle("UidaiHeader", fontName="Helvetica-Bold", fontSize=12, alignment=1, textColor=colors.HexColor("#C53030"))
    elements.append(Paragraph("Unique Identification Authority of India", header))
    elements.append(Paragraph("<font size=8>Government of India</font>", ParagraphStyle("UidaiSub", alignment=1, fontSize=8)))
    elements.append(Spacer(1, 10))

    aadhaar_data = [
        ["Name:", name],
        ["DOB:", dob],
        ["Address:", address],
        ["Aadhaar Number:", f"<b>{aadhaar}</b>"]
    ]
    t = Table(aadhaar_data, colWidths=[110, 240])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t)
    doc.build(elements)
    return file_path
