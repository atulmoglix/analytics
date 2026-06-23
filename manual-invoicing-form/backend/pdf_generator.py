import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_pdf(doc_data: dict, filepath: str):
    """
    Generates a professional PDF for Invoice, Credit Note, or Debit Note using ReportLab.
    """
    # Create the document template
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        textColor=colors.HexColor('#475569'),
        spaceAfter=8
    )
    
    label_style = ParagraphStyle(
        'DocLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#64748b')
    )
    
    value_style = ParagraphStyle(
        'DocValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#0f172a')
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#334155')
    )

    table_cell_bold_style = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#0f172a')
    )

    doc_type = doc_data.get("doc_type", "invoice").lower()
    
    # 1. Header Section: Title & Company Identity
    title_text = "TAX INVOICE"
    primary_color = colors.HexColor('#de1c24') # Moglix Red accent
    
    if doc_type == "credit_note":
        title_text = "CREDIT NOTE"
        primary_color = colors.HexColor('#0d9488') # Teal/Green for CN
    elif doc_type == "debit_note":
        title_text = "DEBIT NOTE"
        primary_color = colors.HexColor('#d97706') # Amber/Orange for DN
        
    title_style.textColor = primary_color
    
    header_data = [
        [
            Paragraph(title_text, title_style),
            Paragraph("<b>MOGLIX</b><br/><font size=8 color='#64748b'>Mogli Labs (India) Pvt. Ltd.</font>", ParagraphStyle('Brand', parent=styles['Normal'], alignment=2, leading=10))
        ]
    ]
    header_table = Table(header_data, colWidths=[3.5 * inch, 4.0 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(header_table)
    
    # Colored horizontal rule line
    rule_table = Table([[""]], colWidths=[7.5 * inch])
    rule_table.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 2.5, primary_color),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
    ]))
    story.append(rule_table)
    story.append(Spacer(1, 10))
    
    # 2. Meta Details (Invoice Numbers, Dates, Plant ID, etc.)
    # Build details depending on the doc_type
    left_meta = []
    right_meta = []
    
    # Standard Metadata
    left_meta.append([Paragraph("Company ID:", label_style), Paragraph(doc_data.get("id_company", "N/A"), value_style)])
    left_meta.append([Paragraph("Plant ID:", label_style), Paragraph(doc_data.get("plant_id", "N/A"), value_style)])
    left_meta.append([Paragraph("Plant Name:", label_style), Paragraph(doc_data.get("plant_name", "N/A"), value_style)])
    
    if doc_type == "credit_note":
        right_meta.append([Paragraph("CN Note No:", label_style), Paragraph(doc_data.get("note_no", "N/A"), value_style)])
        right_meta.append([Paragraph("Return Date:", label_style), Paragraph(str(doc_data.get("return_date", "N/A")), value_style)])
        right_meta.append([Paragraph("Ref Invoice No:", label_style), Paragraph(doc_data.get("invoice_number", "N/A"), value_style)])
    else:
        # Invoice or Debit Note
        right_meta.append([Paragraph("Invoice No:", label_style), Paragraph(doc_data.get("invoice_number", "N/A"), value_style)])
        right_meta.append([Paragraph("Invoice Date:", label_style), Paragraph(str(doc_data.get("invoice_date", "N/A")), value_style)])
        right_meta.append([Paragraph("Sale Type:", label_style), Paragraph(doc_data.get("sale_type", "N/A"), value_style)])
        
    # Supplier metadata if present
    if doc_data.get("supplier_id") or doc_data.get("supplier_name"):
        left_meta.append([Paragraph("Supplier ID:", label_style), Paragraph(doc_data.get("supplier_id", "N/A"), value_style)])
        left_meta.append([Paragraph("Supplier Name:", label_style), Paragraph(doc_data.get("supplier_name", "N/A"), value_style)])
    if doc_data.get("msn"):
        right_meta.append([Paragraph("MSN Code:", label_style), Paragraph(doc_data.get("msn", "N/A"), value_style)])
        
    left_table = Table(left_meta, colWidths=[1.2 * inch, 2.3 * inch])
    left_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    
    right_table = Table(right_meta, colWidths=[1.2 * inch, 2.3 * inch])
    right_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    
    meta_columns = Table([[left_table, right_table]], colWidths=[3.75 * inch, 3.75 * inch])
    meta_columns.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 15),
    ]))
    
    story.append(meta_columns)
    
    # 3. Specific Remarks for Credit Notes
    if doc_type == "credit_note" and doc_data.get("return_remark"):
        remark_table = Table([
            [Paragraph("Return Remark:", label_style), Paragraph(doc_data.get("return_remark"), value_style)]
        ], colWidths=[1.2 * inch, 6.3 * inch])
        remark_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 15),
        ]))
        story.append(remark_table)
        
    story.append(Spacer(1, 10))
    story.append(Paragraph("Financial Summary", subtitle_style))
    
    # 4. Measures Grid Table
    # Build list of fields based on the doc type
    measures_data = []
    
    if doc_type == "credit_note":
        # CN Measures
        measures_headers = [
            Paragraph("Measure Field", table_header_style),
            Paragraph("Value (INR)", table_header_style)
        ]
        measures_data.append(measures_headers)
        
        cn_fields = [
            ("Return Sales", doc_data.get("return_sales")),
            ("Return Tax", doc_data.get("return_tax")),
            ("Return COGS", doc_data.get("return_cogs")),
        ]
        
        for label, val in cn_fields:
            if val is not None:
                measures_data.append([
                    Paragraph(label, table_cell_bold_style),
                    Paragraph(f"₹{val:,.2f}" if isinstance(val, (int, float)) else str(val), table_cell_style)
                ])
    else:
        # Invoice or DN Measures
        measures_headers = [
            Paragraph("Measure Field", table_header_style),
            Paragraph("Value (INR)", table_header_style)
        ]
        measures_data.append(measures_headers)
        
        inv_fields = [
            ("Value SP (Selling Price) *", doc_data.get("value_sp")),
            ("Quantity", doc_data.get("qty")),
            ("Sales Without Tax *", doc_data.get("sales_wo_tax")),
            ("Tax Amount", doc_data.get("tax")),
            ("Sales With Tax", doc_data.get("sales_with_tax")),
            ("GMV (Gross Merchandise Value)", doc_data.get("gmv")),
            ("COGS (Cost of Goods Sold)", doc_data.get("cogs")),
            ("Effective COGS", doc_data.get("eff_cogs")),
        ]
        
        for label, val in inv_fields:
            if val is not None:
                # Highlight mandatory fields with *
                is_mandatory = "*" in label
                cell_style = table_cell_bold_style if is_mandatory else table_cell_style
                measures_data.append([
                    Paragraph(label, cell_style),
                    Paragraph(f"₹{val:,.2f}" if isinstance(val, (int, float)) else str(val), table_cell_style)
                ])
                
    measures_table = Table(measures_data, colWidths=[4.5 * inch, 3.0 * inch])
    measures_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    
    story.append(measures_table)
    
    story.append(Spacer(1, 40))
    
    # 5. Signatures and Declarations
    sig_data = [
        [
            Paragraph("<b>Terms & Conditions:</b><br/><font size=7 color='#64748b'>1. This is a computer generated document.<br/>2. Discrepancies if any should be reported immediately.<br/>3. Subject to jurisdiction of local courts.</font>", ParagraphStyle('Terms', parent=styles['Normal'], leading=9)),
            Paragraph("<br/><br/>___________________________<br/><b>Authorized Signatory</b>", ParagraphStyle('Sig', parent=styles['Normal'], alignment=2, leading=12))
        ]
    ]
    sig_table = Table(sig_data, colWidths=[4.2 * inch, 3.3 * inch])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(sig_table)
    
    # Build Document
    doc.build(story)
