import io
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from typing import Dict, Any

class PDFService:
    def generate_quote_pdf(self, quote: Dict[str, Any]) -> bytes:
        """
        Generates an enterprise-grade PDF quotation for Accel Business / UdyamOne.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom styles
        primary_color = colors.HexColor("#E11D48") # Airtel Crimson
        slate_dark = colors.HexColor("#0F172A")
        slate_muted = colors.HexColor("#64748B")
        table_header_bg = colors.HexColor("#F8FAFC")
        
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=20,
            leading=24,
            textColor=primary_color
        )
        subtitle_style = ParagraphStyle(
            'SubTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            textColor=slate_dark
        )
        meta_label_style = ParagraphStyle(
            'MetaLabel',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10,
            textColor=slate_muted
        )
        meta_val_style = ParagraphStyle(
            'MetaValue',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=slate_dark
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=slate_dark
        )
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=7.5,
            leading=10,
            textColor=slate_muted
        )

        story = []

        # 1. Header Banner
        qid = quote.get('quote_id') or quote.get('id', 'QUO-2026-DRAFT')
        c_date = quote.get('created_at', '2026-07-15')[:10]
        header_data = [
            [
                Paragraph("<b>ACCEL BUSINESS</b><br/><font size=9 color='#64748B'>UdyamOne Digital Acquisition Platform · Enterprise B2B</font>", title_style),
                Paragraph(f"<b>OFFICIAL QUOTATION</b><br/><font size=8 color='#E11D48'>Ref: {qid}</font><br/><font size=7.5 color='#64748B'>Date: {c_date} | Valid 14 Days Price-Lock</font>", subtitle_style)
            ]
        ]
        header_table = Table(header_data, colWidths=[3.8 * inch, 3.8 * inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceAfter=12))

        # 2. Client & Account Metadata Box
        biz = quote.get("business", {})
        b_name = quote.get("business_name") or biz.get("business_name", "Valued Enterprise")
        b_seg = quote.get("segment") or biz.get("segment", "Micro Retail")
        b_city = quote.get("city") or biz.get("city", "Bengaluru")
        b_tier = quote.get("city_tier") or biz.get("city_tier", 1)
        b_gstin = quote.get("gstin") or biz.get("gstin") or "Not Registered / Micro Exemption"

        client_data = [
            [
                Paragraph("CLIENT INFORMATION", meta_label_style),
                Paragraph("SERVICE SPECIFICATIONS", meta_label_style)
            ],
            [
                Paragraph(f"<b>Business Name:</b> {b_name}<br/>"
                          f"<b>Segment:</b> {str(b_seg).title()}<br/>"
                          f"<b>Location:</b> {b_city} (Tier {b_tier})<br/>"
                          f"<b>GSTIN:</b> {b_gstin}", meta_val_style),
                Paragraph(f"<b>Recommended Tier:</b> {quote.get('tier_name', 'Growth Plus')}<br/>"
                          f"<b>Connected Sites:</b> {biz.get('num_sites') or quote.get('num_sites', 1)} Site(s)<br/>"
                          f"<b>Employees Supported:</b> {biz.get('employee_count') or quote.get('employee_count', 5)} Users<br/>"
                          f"<b>Contract Term:</b> {quote.get('contract_months', 12)} Months (Guaranteed SLA)", meta_val_style)
            ]
        ]
        client_table = Table(client_data, colWidths=[3.8 * inch, 3.8 * inch])
        client_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.HexColor("#E2E8F0")),
        ]))
        story.append(client_table)
        story.append(Spacer(1, 14))

        # 3. Itemized Bundle Table
        story.append(Paragraph("<b>SELECTED PRODUCTS & SERVICES (OFFICIAL CATALOGUE INGESTION)</b>", subtitle_style))
        story.append(Spacer(1, 6))

        items = quote.get("items", [])
        table_rows = [
            [
                Paragraph("<b>SKU</b>", meta_label_style),
                Paragraph("<b>Product / Service Name</b>", meta_label_style),
                Paragraph("<b>Category</b>", meta_label_style),
                Paragraph("<b>Qty</b>", meta_label_style),
                Paragraph("<b>Monthly (INR)</b>", meta_label_style),
                Paragraph("<b>Setup (INR)</b>", meta_label_style)
            ]
        ]

        for it in items:
            m_rate = it.get('total_monthly_inr') if it.get('total_monthly_inr') is not None else (it.get('monthly_rate_inr') or it.get('unit_price_monthly_inr', 0.0))
            s_rate = it.get('total_setup_inr') if it.get('total_setup_inr') is not None else (it.get('setup_charge_inr') or it.get('unit_setup_inr', 0.0))
            table_rows.append([
                Paragraph(it.get("product_id", "-"), meta_val_style),
                Paragraph(f"<b>{it.get('product_name', '-')}</b>", meta_val_style),
                Paragraph(it.get("category", "-").title(), meta_val_style),
                Paragraph(str(it.get("quantity", 1)), meta_val_style),
                Paragraph(f"₹{m_rate:,.2f}", meta_val_style),
                Paragraph(f"₹{s_rate:,.2f}", meta_val_style)
            ])

        if not items:
            table_rows.append([Paragraph("No items configured", meta_val_style)] * 6)

        col_widths = [0.8 * inch, 2.7 * inch, 1.3 * inch, 0.5 * inch, 1.1 * inch, 1.2 * inch]
        items_table = Table(table_rows, colWidths=col_widths)
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), table_header_bg),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 12))

        # 4. Financial Calculation & Tax Disclosure
        pricing = quote.get("pricing", {})
        subtotal = quote.get("monthly_recurring_inr", 0.0) or pricing.get("subtotal_monthly_inr", 0.0)
        gst_rate = quote.get("applicable_gst_percent", 18.0)
        gst_amount = quote.get("applicable_gst_amount_monthly", round(subtotal * (gst_rate / 100.0), 2))
        setup_total = quote.get("one_time_setup_inr", 0.0) or pricing.get("total_setup_charges_inr", 0.0)
        setup_gst = round((setup_total * gst_rate) / 100.0, 2)
        total_monthly_post_tax = round(subtotal + gst_amount, 2)
        total_first_month = quote.get("total_first_month_inr", round(subtotal + gst_amount + setup_total + setup_gst, 2))
        annual_savings = quote.get("calculated_savings_inr", 0.0)

        calc_rows = [
            [Paragraph("Subtotal Monthly Recurring Charges (MRC):", meta_val_style), Paragraph(f"₹{subtotal:,.2f}", meta_val_style)],
            [Paragraph(f"Applicable GST ({gst_rate:.0f}% SAC 9984 / 9983 Assumption):", meta_val_style), Paragraph(f"₹{gst_amount:,.2f}", meta_val_style)],
            [Paragraph("<b>Net Monthly Ongoing Outlay (MRC + GST):</b>", subtitle_style), Paragraph(f"<b>₹{total_monthly_post_tax:,.2f} / mo</b>", subtitle_style)],
            [Paragraph("One-Time Deployment / Installation Setup Fee:", meta_val_style), Paragraph(f"₹{setup_total:,.2f}", meta_val_style)],
            [Paragraph(f"Setup Fee GST ({gst_rate:.0f}% Installation):", meta_val_style), Paragraph(f"₹{setup_gst:,.2f}", meta_val_style)],
            [Paragraph("<b>TOTAL 1ST MONTH PAYABLE OUTLAY:</b>", ParagraphStyle('RedTitle', parent=subtitle_style, textColor=primary_color)),
             Paragraph(f"<b>₹{total_first_month:,.2f}</b>", ParagraphStyle('RedVal', parent=subtitle_style, textColor=primary_color))],
            [Paragraph("<b>Estimated Multi-Product Bundle Discount Savings:</b>", ParagraphStyle('GreenText', parent=meta_val_style, textColor=colors.HexColor("#059669"))),
             Paragraph(f"<b>Save ₹{annual_savings:,.2f} / month</b>", ParagraphStyle('GreenVal', parent=meta_val_style, textColor=colors.HexColor("#059669")))]
        ]
        calc_table = Table(calc_rows, colWidths=[5.5 * inch, 2.1 * inch])
        calc_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('LINEABOVE', (0, 2), (-1, 2), 0.5, colors.HexColor("#CBD5E1")),
            ('LINEBELOW', (0, 2), (-1, 2), 0.5, colors.HexColor("#CBD5E1")),
            ('LINEABOVE', (0, 5), (-1, 5), 1, primary_color),
            ('LINEBELOW', (0, 5), (-1, 5), 1, primary_color),
            ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor("#FFF1F2")),
        ]))
        story.append(calc_table)
        story.append(Spacer(1, 14))

        # 5. Terms & Compliance Note
        story.append(KeepTogether([
            Paragraph("<b>TERMS, SLA & REGULATORY COMPLIANCE</b>", subtitle_style),
            Spacer(1, 4),
            Paragraph("1. <b>Service SLA:</b> 99.9% uptime for Biz Fibre / ILL with committed 4-hour restoration in Tier-1/2 cities.<br/>"
                      "2. <b>Tax Treatment & Jurisdiction:</b> Modeled at an assumed statutory baseline of 18% GST under SAC 9984 (Telecommunications) and SAC 9983 (Cloud/IT). Intra-state transactions attract 9% CGST + 9% SGST; inter-state transactions attract 18% IGST. Physical equipment bundled within managed connectivity is billed as composite supply; final ERP tax invoices reflect jurisdictional HSN/SAC breakdowns.<br/>"
                      "3. <b>Privacy & Regulatory Compliance:</b> Customer data is processed under prototype controls aligned with the Digital Personal Data Protection (DPDP) Act, 2023 under Consent Template <code>DPDP-2026-V1.0</code>. Customer Application Form (CAF) records are maintained subject to Department of Telecommunications (DoT) licensing directives.<br/>"
                      "4. <b>Hackathon Disclaimer:</b> This document was generated automatically by Project UdyamOne for Airtel SYNC / YTL Hackathon 2026 demonstration purposes.", disclaimer_style)
        ]))

        doc.build(story)
        return buffer.getvalue()

pdf_service = PDFService()

