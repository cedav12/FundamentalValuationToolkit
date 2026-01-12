import yfinance as yf
import pandas as pd
import time

from .base import BaseConnector


class YahooPriceConnector(BaseConnector):
    """Fetch historical price data from Yahoo Finance."""

    def fetch(
        self,
        ticker: str,
        start: str = "2015-01-01", # We need to specify default start, otherwise with start=None, the method returns
            # only small sample
        end: str | None = None,
        interval: str = "1d"
    ) -> pd.DataFrame:
        data = yf.download(
            ticker,
            start=start,
            end=end,
            interval=interval,
            auto_adjust=True, # ALL OHLC automatically adjusted
            progress=False # No progress printed
        )

        if data.empty:
            raise ValueError(f"No price data returned for {ticker}")
        # Remove multicolumn index with simple index
        data.columns = [c[0] for c in data.columns]
        data.reset_index(inplace=True)
        data["Ticker"] = ticker.upper()

        # To prevent API rate limit, potentially due to calling fetch method in loop
        time.sleep(1)

        return data
