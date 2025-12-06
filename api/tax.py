"""
Tax API
Handles all tax calculation operations
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import pandas as pd

from api.base import BaseAPI, APIResponse
from models.transaction import Transaction
from services.excel_generator import ExcelGenerator


@dataclass
class TaxSummary:
    """Tax calculation summary"""

    total_transactions: int
    total_transfer_tax: float
    total_other_income_tax: float
    total_tax: float
    total_profit_loss: float
    by_token: Dict[str, float]


@dataclass
class TaxPeriodData:
    """Tax data for a period"""

    period: str
    tax_amount: float
    profit_loss: float


class TaxAPI(BaseAPI):
    """
    API for tax calculations.
    Independent of any UI framework.
    """

    def calculate_summary(
        self, transactions: List[Transaction] = None
    ) -> APIResponse[TaxSummary]:
        """
        Calculate tax summary for transactions.

        Args:
            transactions: List of transactions. If None, uses all transactions.
        """
        if transactions is None:
            result = self.container.transactions.get_all()
            if not result.success:
                return APIResponse.error("Failed to get transactions")
            transactions = result.data

        if not transactions:
            return APIResponse.ok(
                TaxSummary(
                    total_transactions=0,
                    total_transfer_tax=0.0,
                    total_other_income_tax=0.0,
                    total_tax=0.0,
                    total_profit_loss=0.0,
                    by_token={},
                )
            )

        try:
            calculator = self.container.tax_calculator
            summary = calculator.get_tax_summary(transactions)

            return APIResponse.ok(
                TaxSummary(
                    total_transactions=summary.get("total_transactions", 0),
                    total_transfer_tax=summary.get("total_transfer_tax", 0.0),
                    total_other_income_tax=summary.get("total_other_income_tax", 0.0),
                    total_tax=summary.get("total_tax", 0.0),
                    total_profit_loss=summary.get("total_profit_loss", 0.0),
                    by_token=summary.get("by_token", {}),
                )
            )
        except Exception as e:
            return APIResponse.error(f"Tax calculation failed: {str(e)}")

    def calculate_by_period(
        self, transactions: List[Transaction] = None, period: str = "month"
    ) -> APIResponse[List[TaxPeriodData]]:
        """
        Calculate tax grouped by period.

        Args:
            transactions: List of transactions. If None, uses all transactions.
            period: 'month', 'quarter', or 'year'
        """
        if transactions is None:
            result = self.container.transactions.get_all()
            if not result.success:
                return APIResponse.error("Failed to get transactions")
            transactions = result.data

        if not transactions:
            return APIResponse.ok([])

        try:
            calculator = self.container.tax_calculator
            df = calculator.get_tax_by_period(transactions, period)

            if df.empty:
                return APIResponse.ok([])

            period_data = []
            for _, row in df.iterrows():
                period_data.append(
                    TaxPeriodData(
                        period=row["period"],
                        tax_amount=row["tax_amount"],
                        profit_loss=row["profit_loss"],
                    )
                )

            return APIResponse.ok(period_data)
        except Exception as e:
            return APIResponse.error(f"Period calculation failed: {str(e)}")

    def calculate_detailed(
        self, transactions: List[Transaction] = None
    ) -> APIResponse[pd.DataFrame]:
        """
        Get detailed tax calculation for each transaction.

        Returns DataFrame with columns: transaction, cost_basis, profit_loss, tax_amount, tax_type
        """
        if transactions is None:
            result = self.container.transactions.get_all()
            if not result.success:
                return APIResponse.error("Failed to get transactions")
            transactions = result.data

        if not transactions:
            return APIResponse.ok(pd.DataFrame())

        try:
            calculator = self.container.tax_calculator
            df = calculator.calculate_taxes(transactions)
            return APIResponse.ok(df)
        except Exception as e:
            return APIResponse.error(f"Detailed calculation failed: {str(e)}")

    def generate_pdf_report(
        self,
        transactions: List[Transaction] = None,
        output_path: str = "tax_report.pdf",
        personal_info: Dict = None,
    ) -> APIResponse[str]:
        """
        Generate PDF tax report.

        Returns path to generated PDF.
        """
        if transactions is None:
            result = self.container.transactions.get_all()
            if not result.success:
                return APIResponse.error("Failed to get transactions")
            transactions = result.data

        if not transactions:
            return APIResponse.error("No transactions to generate report")

        try:
            from services.pdf_generator import PDFGenerator

            generator = PDFGenerator()
            generator.generate_tax_report(
                transactions, output_path, personal_info or {}
            )
            return APIResponse.ok(output_path, "PDF report generated")
        except Exception as e:
            return APIResponse.error(f"PDF generation failed: {str(e)}")

    def generate_excel_report(
        self,
        transactions: List[Transaction] = None,
        output_path: str = "tax_report.xlsx",
        personal_info: Dict = None,
    ) -> APIResponse[str]:
        """
        Generate Excel tax report.

        Returns path to generated Excel file.
        """
        if transactions is None:
            result = self.container.transactions.get_all()
            if not result.success:
                return APIResponse.error("Failed to get transactions")
            transactions = result.data

        if not transactions:
            return APIResponse.error("No transactions to generate report")

        try:

            # Get tax summary
            tax_summary = None
            summary_result = self.calculate_summary(transactions)
            if summary_result.success:
                tax = summary_result.data
                tax_summary = {
                    "total_transactions": tax.total_transactions,
                    "total_transfer_tax": tax.total_transfer_tax,
                    "total_other_income_tax": tax.total_other_income_tax,
                    "total_tax": tax.total_tax,
                    "total_profit_loss": tax.total_profit_loss,
                    "by_token": tax.by_token,
                }

            # Get detailed tax calculations
            tax_details = None
            details_result = self.calculate_detailed(transactions)
            if details_result.success:
                tax_details = details_result.data

            # Generate Excel
            generator = ExcelGenerator()
            generator.generate_tax_report(
                transactions, output_path, personal_info or {}, tax_summary, tax_details
            )
            return APIResponse.ok(output_path, "Excel report generated")
        except Exception as e:
            return APIResponse.error(f"Excel generation failed: {str(e)}")
