import yfinance as yf
import pandas as pd
import time

from .base import BaseConnector
from typing import Dict

from ..models.fundamental_data import FundamentalData


class YahooFundamentalsConnector(BaseConnector):
    """Fetch financial statements from Yahoo Finance."""

    def fetch(self, ticker: str) -> FundamentalData:
        stock = yf.Ticker(ticker)
        # To prevent API rate limit, potentially due to calling fetch method in loop
        time.sleep(1)

        return FundamentalData(stock.info, stock.income_stmt, stock.balance_sheet, stock.cash_flow)
