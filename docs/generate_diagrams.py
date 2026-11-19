"""
Generate diagram images from ASCII art and Mermaid diagrams.
Uses matplotlib for ASCII art rendering and requests for Mermaid.
"""

import os
import base64
import urllib.parse

# Try to import required libraries
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("matplotlib not installed. Run: pip install matplotlib")

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Pillow not installed. Run: pip install Pillow")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("requests not installed. Run: pip install requests")


# Output directory
OUTPUT_DIR = "diagrams"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_mermaid_image(mermaid_code: str, filename: str) -> bool:
    """Generate image from Mermaid code using mermaid.ink API"""
    if not REQUESTS_AVAILABLE:
        print(f"Cannot generate {filename}: requests library not available")
        return False
    
    try:
        # Encode mermaid code for URL
        graphbytes = mermaid_code.encode("utf-8")
        base64_bytes = base64.b64encode(graphbytes)
        base64_string = base64_bytes.decode("ascii")
        
        # Use mermaid.ink service
        url = f"https://mermaid.ink/img/{base64_string}"
        
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            filepath = os.path.join(OUTPUT_DIR, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"✅ Generated: {filepath}")
            return True
        else:
            print(f"❌ Failed to generate {filename}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error generating {filename}: {e}")
        return False


def create_architecture_diagram():
    """Create system architecture diagram using matplotlib"""
    if not MATPLOTLIB_AVAILABLE:
        print("Cannot create architecture diagram: matplotlib not available")
        return False
    
    fig, ax = plt.subplots(1, 1, figsize=(20, 16))
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 16)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Colors
    colors = {
        'client': '#3498db',
        'api': '#2ecc71',
        'agents': '#9b59b6',
        'services': '#e74c3c',
        'data': '#f39c12',
        'external': '#1abc9c',
        'text': 'white',
        'arrow': '#34495e'
    }
    
    def draw_box(x, y, w, h, color, label, sublabels=None):
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                            facecolor=color, edgecolor='white', linewidth=2, alpha=0.9)
        ax.add_patch(box)
        ax.text(x + w/2, y + h - 0.3, label, ha='center', va='top',
               fontsize=10, fontweight='bold', color='white')
        if sublabels:
            for i, sub in enumerate(sublabels):
                ax.text(x + w/2, y + h - 0.7 - i*0.35, sub, ha='center', va='top',
                       fontsize=7, color='white', alpha=0.9)
    
    def draw_layer_label(y, label):
        ax.text(0.5, y + 0.5, label, ha='left', va='center',
               fontsize=12, fontweight='bold', color='#2c3e50')
    
    # Layer 1: Client Layer
    draw_layer_label(14.5, "CLIENT LAYER")
    draw_box(1, 13, 3, 1.5, colors['client'], "Chat UI", ["React Components", "WebSocket Client"])
    draw_box(4.5, 13, 3, 1.5, colors['client'], "Voice I/O", ["Web Speech API", "TTS/STT"])
    draw_box(8, 13, 3, 1.5, colors['client'], "Language", ["EN/HI Toggle", "Auto-detect"])
    draw_box(11.5, 13, 3.5, 1.5, colors['client'], "Dashboard", ["Analytics", "Conversion Funnel"])
    draw_box(15.5, 13, 3.5, 1.5, colors['client'], "Auth", ["Google OAuth", "NextAuth.js"])
    
    # Layer 2: API Gateway
    draw_layer_label(11.5, "API GATEWAY")
    draw_box(1, 10, 4, 1.5, colors['api'], "WebSocket", ["/ws/chat/{id}", "Real-time"])
    draw_box(5.5, 10, 4, 1.5, colors['api'], "REST APIs", ["Customers", "Documents"])
    draw_box(10, 10, 4, 1.5, colors['api'], "Upload API", ["OCR Trigger", "File Storage"])
    draw_box(14.5, 10, 4.5, 1.5, colors['api'], "Analytics API", ["Funnel", "A/B Test"])
    
    # Layer 3: Multi-Agent System
    draw_layer_label(8.5, "MULTI-AGENT ORCHESTRATION (LangGraph)")
    draw_box(8, 7, 4, 1.5, colors['agents'], "MASTER AGENT", ["Intent Analysis", "Sentiment", "Routing"])
    
    draw_box(1, 5, 3, 1.5, colors['agents'], "Sales Agent", ["A/B Testing", "EMI Calc"])
    draw_box(4.5, 5, 3, 1.5, colors['agents'], "Verification", ["KYC Check", "CRM Lookup"])
    draw_box(8, 5, 3, 1.5, colors['agents'], "Underwriting", ["Credit Score", "XAI Decision"])
    draw_box(11.5, 5, 3, 1.5, colors['agents'], "Document", ["OCR Process", "Validation"])
    draw_box(15, 5, 3.5, 1.5, colors['agents'], "Sanction", ["PDF Gen", "Multilingual"])
    
    # Layer 4: Services
    draw_layer_label(3.5, "SERVICES LAYER")
    draw_box(1, 2, 2.5, 1.5, colors['services'], "OCR", ["Tesseract", "Vision API"])
    draw_box(4, 2, 2.5, 1.5, colors['services'], "Credit", ["Bureau API", "Scoring"])
    draw_box(7, 2, 2.5, 1.5, colors['services'], "CRM", ["Customer", "Profile"])
    draw_box(10, 2, 2.5, 1.5, colors['services'], "PDF", ["ReportLab", "Letters"])
    draw_box(13, 2, 2.5, 1.5, colors['services'], "Sentiment", ["LLM-based", "Emotion"])
    draw_box(16, 2, 2.5, 1.5, colors['services'], "Analytics", ["Tracking", "Metrics"])
    
    # Layer 5: Data & External
    draw_layer_label(0.5, "DATA & EXTERNAL")
    draw_box(1, -0.5, 3, 1, colors['data'], "PostgreSQL", ["SQLAlchemy"])
    draw_box(4.5, -0.5, 2.5, 1, colors['data'], "Redis", ["Cache"])
    draw_box(7.5, -0.5, 2.5, 1, colors['data'], "Files", ["Uploads"])
    draw_box(10.5, -0.5, 2.5, 1, colors['external'], "OpenAI", ["GPT-3.5/4"])
    draw_box(13.5, -0.5, 2.5, 1, colors['external'], "Google", ["Vision/Speech"])
    draw_box(16.5, -0.5, 2.5, 1, colors['external'], "OAuth", ["Google"])
    
    # Arrows (simplified)
    arrow_style = dict(arrowstyle='->', color=colors['arrow'], lw=1.5)
    
    # Client to API
    ax.annotate('', xy=(10, 11.5), xytext=(10, 13), arrowprops=arrow_style)
    
    # API to Master
    ax.annotate('', xy=(10, 8.5), xytext=(10, 10), arrowprops=arrow_style)
    
    # Master to Workers
    for x in [2.5, 6, 9.5, 13, 16.75]:
        ax.annotate('', xy=(x, 6.5), xytext=(10, 7), arrowprops=arrow_style)
    
    # Workers to Services
    ax.annotate('', xy=(10, 3.5), xytext=(10, 5), arrowprops=arrow_style)
    
    # Services to Data
    ax.annotate('', xy=(10, 0.5), xytext=(10, 2), arrowprops=arrow_style)
    
    # Title
    ax.text(10, 15.5, "NBFC Loan Chatbot - System Architecture", 
           ha='center', va='center', fontsize=16, fontweight='bold', color='#2c3e50')
    
    plt.tight_layout()
    filepath = os.path.join(OUTPUT_DIR, "architecture_diagram.png")
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print(f"✅ Generated: {filepath}")
    return True


def create_flowchart_loan_application():
    """Create loan application flowchart using matplotlib"""
    if not MATPLOTLIB_AVAILABLE:
        print("Cannot create flowchart: matplotlib not available")
        return False
    
    fig, ax = plt.subplots(1, 1, figsize=(16, 24))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 24)
    ax.axis('off')
    
    colors = {
        'start': '#27ae60',
        'process': '#3498db',
        'decision': '#f39c12',
        'agent': '#9b59b6',
        'end': '#e74c3c',
        'arrow': '#34495e'
    }
    
    def draw_box(x, y, w, h, color, label, shape='rect'):
        if shape == 'diamond':
            diamond = plt.Polygon([(x, y+h/2), (x+w/2, y+h), (x+w, y+h/2), (x+w/2, y)],
                                 facecolor=color, edgecolor='white', linewidth=2)
            ax.add_patch(diamond)
        elif shape == 'oval':
            ellipse = mpatches.Ellipse((x+w/2, y+h/2), w, h, 
                                       facecolor=color, edgecolor='white', linewidth=2)
            ax.add_patch(ellipse)
        else:
            box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                                facecolor=color, edgecolor='white', linewidth=2)
            ax.add_patch(box)
        
        ax.text(x + w/2, y + h/2, label, ha='center', va='center',
               fontsize=8, fontweight='bold', color='white', wrap=True)
    
    arrow_style = dict(arrowstyle='->', color=colors['arrow'], lw=1.5)
    
    # Start
    draw_box(6.5, 22.5, 3, 1, colors['start'], "START", 'oval')
    
    # User opens chatbot
    draw_box(5.5, 20.5, 5, 1, colors['process'], "User Opens Chatbot\n(Web/Voice)")
    ax.annotate('', xy=(8, 21.5), xytext=(8, 22.5), arrowprops=arrow_style)
    
    # Language detection
    draw_box(5.5, 18.5, 5, 1, colors['process'], "Language Detection\n(EN/HI)")
    ax.annotate('', xy=(8, 19.5), xytext=(8, 20.5), arrowprops=arrow_style)
    
    # Auth check
    draw_box(5.5, 16.5, 5, 1.2, colors['decision'], "Authenticated?", 'diamond')
    ax.annotate('', xy=(8, 17.7), xytext=(8, 18.5), arrowprops=arrow_style)
    
    # Google OAuth
    draw_box(2, 16.5, 3, 1, colors['process'], "Google\nOAuth")
    ax.annotate('', xy=(5, 17), xytext=(5.5, 17), arrowprops=arrow_style)
    ax.text(4.5, 17.5, "No", fontsize=7, color=colors['arrow'])
    
    # Guest mode
    draw_box(11, 16.5, 3, 1, colors['process'], "Guest\nMode")
    ax.annotate('', xy=(11, 17), xytext=(10.5, 17), arrowprops=arrow_style)
    ax.text(10.7, 17.5, "Yes", fontsize=7, color=colors['arrow'])
    
    # Welcome
    draw_box(5.5, 14.5, 5, 1, colors['agent'], "Shruti Welcomes User\n(Personalized)")
    ax.annotate('', xy=(8, 15.5), xytext=(8, 16.5), arrowprops=arrow_style)
    ax.annotate('', xy=(8, 15.5), xytext=(3.5, 16.5), arrowprops=arrow_style)
    ax.annotate('', xy=(8, 15.5), xytext=(12.5, 16.5), arrowprops=arrow_style)
    
    # Master Agent
    draw_box(5.5, 12.5, 5, 1, colors['agent'], "Master Agent\nIntent + Sentiment")
    ax.annotate('', xy=(8, 13.5), xytext=(8, 14.5), arrowprops=arrow_style)
    
    # Intent classification
    draw_box(5.5, 10.5, 5, 1.2, colors['decision'], "User Intent?", 'diamond')
    ax.annotate('', xy=(8, 11.7), xytext=(8, 12.5), arrowprops=arrow_style)
    
    # Sales Agent path
    draw_box(1, 8.5, 3, 1, colors['agent'], "Sales Agent\n(A/B Test)")
    ax.annotate('', xy=(2.5, 9.5), xytext=(5.5, 11), arrowprops=arrow_style)
    ax.text(3.5, 10.5, "Loan", fontsize=7, color=colors['arrow'])
    
    # Collect requirements
    draw_box(1, 6.5, 3, 1, colors['process'], "Collect\nRequirements")
    ax.annotate('', xy=(2.5, 7.5), xytext=(2.5, 8.5), arrowprops=arrow_style)
    
    # Calculate EMI
    draw_box(1, 4.5, 3, 1, colors['process'], "Calculate EMI\nPresent Offer")
    ax.annotate('', xy=(2.5, 5.5), xytext=(2.5, 6.5), arrowprops=arrow_style)
    
    # Amount check
    draw_box(5, 4.5, 3.5, 1.2, colors['decision'], "≤ Pre-approved?", 'diamond')
    ax.annotate('', xy=(5, 5), xytext=(4, 5), arrowprops=arrow_style)
    
    # Document Agent
    draw_box(9, 4.5, 3, 1, colors['agent'], "Document\nAgent (OCR)")
    ax.annotate('', xy=(9, 5), xytext=(8.5, 5), arrowprops=arrow_style)
    ax.text(8.7, 5.5, "No", fontsize=7, color=colors['arrow'])
    
    # Verification
    draw_box(5.5, 2.5, 5, 1, colors['agent'], "Verification Agent\nKYC + CRM")
    ax.annotate('', xy=(8, 3.5), xytext=(6.75, 4.5), arrowprops=arrow_style)
    ax.annotate('', xy=(8, 3.5), xytext=(10.5, 4.5), arrowprops=arrow_style)
    ax.text(5.5, 4.2, "Yes", fontsize=7, color=colors['arrow'])
    
    # Underwriting
    draw_box(5.5, 0.5, 5, 1, colors['agent'], "Underwriting Agent\nCredit + XAI Decision")
    ax.annotate('', xy=(8, 1.5), xytext=(8, 2.5), arrowprops=arrow_style)
    
    # Decision
    draw_box(12, 2.5, 3, 1.2, colors['decision'], "Approved?", 'diamond')
    ax.annotate('', xy=(12, 3), xytext=(10.5, 1), arrowprops=arrow_style)
    
    # Sanction
    draw_box(12, 0.5, 3, 1, colors['agent'], "Sanction Agent\nPDF Gen")
    ax.annotate('', xy=(13.5, 1.5), xytext=(13.5, 2.5), arrowprops=arrow_style)
    ax.text(13.7, 2.2, "Yes", fontsize=7, color=colors['arrow'])
    
    # End
    draw_box(12, -1, 3, 0.8, colors['end'], "END", 'oval')
    ax.annotate('', xy=(13.5, -0.2), xytext=(13.5, 0.5), arrowprops=arrow_style)
    
    # Title
    ax.text(8, 23.5, "Loan Application Flowchart", 
           ha='center', va='center', fontsize=14, fontweight='bold', color='#2c3e50')
    
    plt.tight_layout()
    filepath = os.path.join(OUTPUT_DIR, "flowchart_loan_application.png")
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print(f"✅ Generated: {filepath}")
    return True


def create_agent_routing_diagram():
    """Create agent routing diagram using Mermaid"""
    mermaid_code = """
flowchart TD
    A[User Message] --> B[Master Agent]
    
    B --> C{Detect Language}
    C -->|English| D[Set EN]
    C -->|Hindi| E[Set HI]
    
    D --> F{Analyze Sentiment}
    E --> F
    
    F -->|Positive| G[Normal Flow]
    F -->|Hesitant| H[Reassuring Tone]
    F -->|Frustrated| I[Apologetic Tone]
    
    G --> K{Classify Intent}
    H --> K
    I --> K
    
    K -->|Loan Inquiry| L[Sales Agent]
    K -->|Document Upload| M[Document Agent]
    K -->|KYC Check| N[Verification Agent]
    K -->|Credit Check| O[Underwriting Agent]
    K -->|Approval| P[Sanction Agent]
    
    L --> R{A/B Variant}
    R -->|A| S[Friendly Style]
    R -->|B| T[Expert Style]
    
    S --> U[Generate Response]
    T --> U
    M --> U
    N --> U
    O --> U
    P --> U
    
    U --> V[Localize Language]
    V --> W[Send Response]
"""
    return generate_mermaid_image(mermaid_code, "flowchart_agent_routing.png")


def create_ocr_flow_diagram():
    """Create OCR processing flow diagram using Mermaid"""
    mermaid_code = """
flowchart TD
    A[User Uploads Document] --> B{Validate File}
    B -->|Invalid| C[Return Error]
    B -->|Valid| D{Identify Doc Type}
    
    D -->|Aadhaar| E[Aadhaar Parser]
    D -->|PAN| F[PAN Parser]
    D -->|Salary Slip| G[Salary Parser]
    
    E --> H{Select OCR Engine}
    F --> H
    G --> H
    
    H -->|Available| I[Google Cloud Vision]
    H -->|Fallback| J[Tesseract OCR]
    
    I --> K[Extract Raw Text]
    J --> K
    
    K --> L[Apply Regex Patterns]
    L --> M[Validate Extracted Data]
    M --> N[Calculate Confidence]
    N --> O[Update Customer Profile]
    O --> P[Return to Agent]
"""
    return generate_mermaid_image(mermaid_code, "flowchart_ocr_processing.png")


def create_underwriting_flow():
    """Create underwriting decision flow using Mermaid"""
    mermaid_code = """
flowchart TD
    A[Receive Application] --> B[Gather Decision Factors]
    
    B --> C[Fetch Credit Score]
    B --> D[Get Income Data]
    B --> E[Get Loan Details]
    
    C --> F[Calculate Metrics]
    D --> F
    E --> F
    
    F --> G{Credit Score >= 700?}
    
    G -->|No| H[REJECT: Low Credit]
    G -->|Yes| I{Amount <= Pre-approved?}
    
    I -->|Yes| J[INSTANT APPROVE]
    I -->|No| K{Amount <= 2x Limit?}
    
    K -->|No| L[REJECT: Too High]
    K -->|Yes| M{EMI <= 50% Income?}
    
    M -->|Yes| N[APPROVE with Docs]
    M -->|No| O[REJECT: High EMI]
    
    J --> P[Generate XAI Explanation]
    N --> P
    H --> Q[Offer Alternative]
    L --> Q
    O --> Q
    
    P --> R[Communicate Decision]
    Q --> R
"""
    return generate_mermaid_image(mermaid_code, "flowchart_underwriting.png")


def create_conversion_funnel():
    """Create conversion funnel diagram using matplotlib"""
    if not MATPLOTLIB_AVAILABLE:
        print("Cannot create funnel: matplotlib not available")
        return False
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    stages = ['Greeting', 'Sales', 'Verification', 'Underwriting', 'Sanction']
    values = [100, 75, 60, 50, 45]
    colors = ['#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#e74c3c']
    
    # Create funnel
    for i, (stage, value, color) in enumerate(zip(stages, values, colors)):
        left = (100 - value) / 2
        ax.barh(i, value, left=left, height=0.7, color=color, edgecolor='white', linewidth=2)
        ax.text(50, i, f"{stage}\n{value}%", ha='center', va='center', 
               fontsize=12, fontweight='bold', color='white')
    
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.5, len(stages) - 0.5)
    ax.invert_yaxis()
    ax.axis('off')
    
    ax.set_title("Conversion Funnel Analytics", fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    filepath = os.path.join(OUTPUT_DIR, "conversion_funnel.png")
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    print(f"✅ Generated: {filepath}")
    return True


def main():
    """Generate all diagrams"""
    print("\n" + "="*60)
    print("NBFC Loan Chatbot - Diagram Generator")
    print("="*60 + "\n")
    
    results = []
    
    # Generate matplotlib-based diagrams
    print("📊 Generating Architecture Diagram...")
    results.append(("Architecture Diagram", create_architecture_diagram()))
    
    print("\n📊 Generating Loan Application Flowchart...")
    results.append(("Loan Application Flowchart", create_flowchart_loan_application()))
    
    print("\n📊 Generating Conversion Funnel...")
    results.append(("Conversion Funnel", create_conversion_funnel()))
    
    # Generate Mermaid-based diagrams
    print("\n📊 Generating Agent Routing Diagram (Mermaid)...")
    results.append(("Agent Routing", create_agent_routing_diagram()))
    
    print("\n📊 Generating OCR Flow Diagram (Mermaid)...")
    results.append(("OCR Flow", create_ocr_flow_diagram()))
    
    print("\n📊 Generating Underwriting Flow (Mermaid)...")
    results.append(("Underwriting Flow", create_underwriting_flow()))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for name, success in results:
        status = "✅ Success" if success else "❌ Failed"
        print(f"  {name}: {status}")
    
    print(f"\n📁 Output directory: {os.path.abspath(OUTPUT_DIR)}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
