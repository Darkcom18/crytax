"""
PDF generator for tax reports
Creates tax reports in Vietnamese format
"""

from typing import List, Dict, Optional
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from models.transaction import Transaction
from services.tax_calculator import TaxCalculator
from utils.formatters import format_vnd, format_date
import config


class PDFGenerator:
    """Generate PDF tax reports"""
    
    def __init__(self):
        self.tax_calculator = TaxCalculator()
        # Try to register Vietnamese font (if available)
        # For MVP, use default fonts
        try:
            # You can add Vietnamese font support here
            pass
        except:
            pass
    
    def generate_tax_report(self, transactions: List[Transaction], 
                           output_path: str,
                           personal_info: Optional[Dict] = None) -> str:
        """
        Generate tax report PDF
        
        Args:
            transactions: List of transactions
            output_path: Output file path
            personal_info: Personal information dict with keys:
                - name: Full name
                - id_number: CMND/CCCD
                - address: Address
                - phone: Phone number (optional)
                - email: Email (optional)
                
        Returns:
            Path to generated PDF
        """
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=1,  # Center
        )
        story.append(Paragraph("BÁO CÁO KHAI THUẾ GIAO DỊCH TIỀN ĐIỆN TỬ", title_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Personal Information
        if personal_info:
            story.append(Paragraph("THÔNG TIN CÁ NHÂN", styles['Heading2']))
            info_data = [
                ["Họ và tên:", personal_info.get("name", "")],
                ["CMND/CCCD:", personal_info.get("id_number", "")],
                ["Địa chỉ:", personal_info.get("address", "")],
            ]
            if personal_info.get("phone"):
                info_data.append(["Số điện thoại:", personal_info.get("phone", "")])
            if personal_info.get("email"):
                info_data.append(["Email:", personal_info.get("email", "")])
            
            info_table = Table(info_data, colWidths=[4*cm, 12*cm])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(info_table)
            story.append(Spacer(1, 0.5*cm))
        
        # Tax Summary
        tax_summary = self.tax_calculator.get_tax_summary(transactions)
        
        story.append(Paragraph("TỔNG HỢP THUẾ", styles['Heading2']))
        summary_data = [
            ["Chỉ tiêu", "Giá trị"],
            ["Tổng số giao dịch", str(tax_summary["total_transactions"])],
            ["Thuế chuyển nhượng (0.1%)", format_vnd(tax_summary["total_transfer_tax"])],
            ["Thuế thu nhập khác (10%)", format_vnd(tax_summary["total_other_income_tax"])],
            ["<b>Tổng thuế phải nộp</b>", f"<b>{format_vnd(tax_summary['total_tax'])}</b>"],
            ["Tổng lãi/lỗ", format_vnd(tax_summary["total_profit_loss"])],
        ]
        
        summary_table = Table(summary_data, colWidths=[10*cm, 6*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Tax by Period
        tax_by_month = self.tax_calculator.get_tax_by_period(transactions, "month")
        if not tax_by_month.empty:
            story.append(Paragraph("THUẾ THEO TỪNG THÁNG", styles['Heading2']))
            
            period_data = [["Tháng", "Thuế phải nộp", "Lãi/Lỗ"]]
            for _, row in tax_by_month.iterrows():
                period_data.append([
                    row["period"],
                    format_vnd(row["tax_amount"]),
                    format_vnd(row["profit_loss"]),
                ])
            
            period_table = Table(period_data, colWidths=[5*cm, 5.5*cm, 5.5*cm])
            period_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            story.append(period_table)
            story.append(Spacer(1, 0.5*cm))
        
        # Transaction Details (optional, can be long)
        story.append(Paragraph("CHI TIẾT GIAO DỊCH", styles['Heading2']))
        
        # Calculate taxes for display
        tax_df = self.tax_calculator.calculate_taxes(transactions)
        
        if not tax_df.empty:
            # Limit to first 50 transactions for PDF (to avoid too long)
            display_df = tax_df.head(50)
            
            detail_data = [["Ngày", "Loại", "Token", "Số lượng", "Giá trị (VND)", "Thuế (VND)"]]
            
            for _, row in display_df.iterrows():
                tx = row["transaction"]
                detail_data.append([
                    format_date(tx.date),
                    tx.type.value,
                    tx.token,
                    f"{tx.amount:.6f}",
                    format_vnd(tx.value_vnd),
                    format_vnd(row["tax_amount"]),
                ])
            
            detail_table = Table(detail_data, colWidths=[3*cm, 2*cm, 2*cm, 2.5*cm, 3.5*cm, 3*cm])
            detail_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            story.append(detail_table)
            
            if len(tax_df) > 50:
                story.append(Spacer(1, 0.3*cm))
                story.append(Paragraph(
                    f"<i>Lưu ý: Chỉ hiển thị 50 giao dịch đầu tiên. Tổng cộng {len(tax_df)} giao dịch.</i>",
                    styles['Normal']
                ))
        
        # Footer
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(
            f"Báo cáo được tạo vào: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            styles['Normal']
        ))
        story.append(Paragraph(
            "<i>Báo cáo này được tạo tự động. Vui lòng kiểm tra lại thông tin trước khi nộp thuế.</i>",
            styles['Normal']
        ))
        
        # Build PDF
        doc.build(story)
        return output_path

