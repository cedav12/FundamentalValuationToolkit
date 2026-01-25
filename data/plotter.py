import os
import matplotlib.pyplot as plt
import pandas as pd


class Plotter:
    """
    Generates key plots for equity analysis:
    - Price with Moving Averages
    - Price vs DCF Value
    - Revenue / FCF over time
    - ROIC vs WACC
    """

    @staticmethod
    def _save_or_show(fig, output_path: str | None, filename: str, show: bool = False):
        if output_path:
            os.makedirs(output_path, exist_ok=True)
            fig.savefig(os.path.join(output_path, filename), bbox_inches="tight")
        if show:
            plt.show()
        plt.close(fig)

    # =====================================================
    # Price + Moving Averages
    # =====================================================
    @staticmethod
    def plot_price_ma(prices: pd.DataFrame, output_path: str | None, ticker: str, show: bool = False):
        """
        Plots closing price + 50 & 200-day moving averages
        """
        fig, ax = plt.subplots(figsize=(10, 5))

        ax.plot(prices.index, prices["Close"], label="Close Price", color="blue")
        ax.plot(prices["Close"].rolling(50).mean(), label="MA 50", color="orange")
        ax.plot(prices["Close"].rolling(200).mean(), label="MA 200", color="green")

        ax.set_title(f"{ticker} Price Trend")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price ($)")
        ax.legend()
        ax.grid(True)

        Plotter._save_or_show(fig, output_path, f"{ticker}_price_ma.png", show)

    # =====================================================
    # Price vs DCF Value
    # =====================================================
    @staticmethod
    def plot_price_vs_dcf(prices: pd.DataFrame, dcf_value: float, output_path: str | None, ticker: str,
                          show: bool = False):
        fig, ax = plt.subplots(figsize=(10, 5))

        ax.plot(prices.index, prices["Close"], label="Market Price", color="blue")
        ax.axhline(y=dcf_value, color="red", linestyle="--", label="DCF Value")

        ax.set_title(f"{ticker} Market Price vs DCF")
        ax.set_xlabel("Date")
        ax.set_ylabel("Price ($)")
        ax.legend()
        ax.grid(True)

        Plotter._save_or_show(fig, output_path, f"{ticker}_price_vs_dcf.png", show)

    # =====================================================
    # Revenue & FCF
    # =====================================================
    @staticmethod
    def plot_revenue_fcf(metrics: pd.DataFrame, output_path: str | None, ticker: str, show: bool = False):
        fig, ax = plt.subplots(figsize=(10, 5))

        ax.plot(metrics.index, metrics["Revenue"], marker="o", label="Revenue")
        ax.plot(metrics.index, metrics["FCF"], marker="o", label="FCF")

        ax.set_title(f"{ticker} Revenue & Free Cash Flow")
        ax.set_xlabel("Date")
        ax.set_ylabel("USD")
        ax.legend()
        ax.grid(True)

        Plotter._save_or_show(fig, output_path, f"{ticker}_revenue_fcf.png", show)

    # =====================================================
    # ROIC vs WACC
    # =====================================================
    @staticmethod
    def plot_roic_vs_wacc(metrics: pd.DataFrame, wacc: float, output_path: str | None, ticker: str, show: bool = False):
        fig, ax = plt.subplots(figsize=(10, 5))

        ax.plot(metrics.index, metrics["ROIC"], marker="o", label="ROIC")
        ax.axhline(y=wacc, color="red", linestyle="--", label="WACC")

        ax.set_title(f"{ticker} ROIC vs WACC")
        ax.set_xlabel("Date")
        ax.set_ylabel("Rate")
        ax.legend()
        ax.grid(True)

        Plotter._save_or_show(fig, output_path, f"{ticker}_roic_vs_wacc.png", show)
