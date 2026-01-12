import yfinance as yf
import pandas as pd
import time

from .base import BaseConnector


class YahooFundamentalsConnector(BaseConnector):
    """Fetch financial statements from Yahoo Finance."""

    def fetch(self, ticker: str) -> dict[str, pd.DataFrame]:
        stock = yf.Ticker(ticker)
        # To prevent API rate limit, potentially due to calling fetch method in loop
        time.sleep(1)

        return {
            "income_statement": stock.income_stmt,
            "balance_sheet": stock.balance_sheet,
            "cash_flow": stock.cashflow,
        }