import pandas as pd
import numpy as np


class PriceAnalytics:
    """
        Analytics for price-based risk and performance metrics.
    """

    def __init__(self, data: pd.DataFrame, periods: int = 252):
        """
        Parameters
        ----------
        data : pd.DataFrame
            OHLC price data from yfinance.
            Must contain 'Date' and 'Close'.
        periods : int
            Number of trading days in the year
        """
        required_cols = {"Date", "Close"}
        missing = required_cols - set(data.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # To want to copy the value of object not the reference
        self.data = data.copy()
        self.periods = periods

        # Ensure Date column is datetime
        self.data["Date"] = pd.to_datetime(self.data["Date"], errors="raise")

        self._prepare_returns()

    # -------------------------
    # Internal helpers
    # -------------------------
    def _prepare_returns(self):
        self.data["returns"] = self.data["Close"].pct_change()
        self.data["log_returns"] = np.log(self.data["Close"] / self.data["Close"].shift(1))
        self.returns = self.data["returns"].dropna()

    # -------------------------
    # Performance metrics
    # -------------------------
    def sharpe_ratio(self, risk_free_rate: float = 0.0) -> float:
        """
        Annualized Sharpe Ratio
        """
        excess_returns = self.returns - risk_free_rate / self.periods
        return np.sqrt(self.periods) * excess_returns.mean() / excess_returns.std()

    def sortino_ratio(self, risk_free_rate: float = 0.0) -> float:
        """
        Annualized Sortino Ratio
        """
        downside = self.returns[self.returns < 0]
        downside_std = downside.std()

        if downside_std == 0 or pd.isna(downside_std):
            return np.nan

        excess_returns = self.returns.mean() - risk_free_rate / self.periods
        return np.sqrt(self.periods) * excess_returns / downside_std

    def annualized_return(self) -> float:
        """
        Annualized arithmetic mean return
        """
        return self.returns.mean() * self.periods

    # -------------------------
    # Risk metrics
    # -------------------------
    def volatility(self) -> float:
        """
        Annualized volatility
        """
        return self.returns.std() * np.sqrt(self.periods)

    def max_drawdown(self) -> float:
        """
        Maximum drawdown
        """
        cumulative = (1 + self.returns).cumprod() # portfolio multiplier in time
        peak = cumulative.cummax() # de facto High Watermark - highest reached value in time
        drawdown = cumulative / peak - 1 # Reached relative downfall from High Watermark in time
        return drawdown.min() # Drawdown is the largest fall from high watermark recorded

    def cvar(self, alpha: float = 0.05) -> float:
        """
        Conditional Value at Risk (Expected Shortfall)
        """
        var = self.returns.quantile(alpha)
        return self.returns[self.returns <= var].mean()

    # -------------------------
    # Summary
    # -------------------------
    def summary(self, risk_free_rate: float = 0.0) -> pd.Series:
        """
        Summary of key metrics
        """
        return pd.Series({
            "Annualized Return": self.annualized_return(),
            "Sharpe Ratio": self.sharpe_ratio(risk_free_rate),
            "Sortino Ratio": self.sortino_ratio(risk_free_rate),
            "Volatility": self.volatility(),
            "Max Drawdown": self.max_drawdown(),
            "CVaR (5%)": self.cvar(0.05)
        })