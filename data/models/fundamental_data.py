from typing import Any, Dict

import pandas as pd


class FundamentalData:
    """Data model for fundamentals."""
    def __init__(
            self,
            info: Dict[str, Any],
            income_stmt: pd.DataFrame,
            balance_sheet: pd.DataFrame,
            cashflow: pd.DataFrame
    ):
        self.info = info
        self.statements: Dict[str, pd.DataFrame] = {
            "income_statement": income_stmt,
            "balance_sheet": balance_sheet,
            "cash_flow": cashflow
        }
        self.ticker: str = self.info.get("symbol")
        self.quote_type: str = self.info.get("quoteType")