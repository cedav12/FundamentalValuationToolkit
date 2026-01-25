import os
import datetime
import json

import pandas as pd

from data.logger import Logger
from data.connector.price import YahooPriceConnector
from data.connector.fundamental import YahooFundamentalsConnector
from analytics.ec_metric_processor import FundamentalProcessor
from analytics.price_analytics import PriceAnalytics
from analytics.valuation import DCFModel, DCFAssumptions
from data.models.fundamental_data import FundamentalData
from data.plotter import Plotter


class AnalysisPipeline:
    """
    Orchestrates full equity analysis in small, testable steps.
    """
    def __init__(self, output_path: str | None = None, show_plt: bool = False, config_path: str="config.json", overrides: dict = None):
        self.show_plt = show_plt
        self.output_path = output_path
        self.config = self._load_config(config_path)
        self.overrides = overrides or {}
        # Shared services
        self.price_connector = YahooPriceConnector()
        self.fundamental_connector = YahooFundamentalsConnector()
        self.dcf_model = DCFModel()

    def _load_config(self, path: str) -> dict:
        try:
            with open(path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"{path} not found. Using defaults.")
            return {}

    # =====================================================
    # Public API
    # =====================================================
    def run(self, tickers: list[str]):
        print("ANALYSIS STARTED:")
        for ticker in tickers:
            self._analyze_ticker(ticker.upper())
        print("\nANALYSIS FINISHED.")
        if self.output_path is not None:
            print(f"Reports saved in: ./{self.output_path}/")

    # =====================================================
    # Per-ticker pipeline
    # =====================================================
    def _analyze_ticker(self, ticker: str):
        logger = self._create_logger(ticker)
        try:
            self._write_header(logger, ticker)
            prices = self._run_price_analysis(logger, ticker)
            self._run_fundamental_analysis(prices, logger, ticker)
        except Exception as e:
            logger.log(f"Unexpected pipeline failure: {e}")
        finally:
            logger.close()

    # =====================================================
    # Setup
    # =====================================================
    def _create_logger(self, ticker: str) -> Logger:
        path = os.path.join(self.output_path, ticker, f"{ticker}_report.txt") if self.output_path else None
        return Logger(path)

    @staticmethod
    def _write_header(logger: Logger, ticker: str):

        logger.section(
            f"Ticker: {ticker}\nRun Time: {datetime.datetime.now()}"
        )

    # =====================================================
    # Price Analysis
    # =====================================================
    def _run_price_analysis(self, logger: Logger, ticker: str) -> pd.DataFrame | None:
        logger.subsection("Risk and Performance Metrics")
        try:
            prices = self.price_connector.fetch(ticker)
            analysis = PriceAnalytics(prices)
            summary = analysis.summary()
            logger.log(summary)
            # Price MA plot
            Plotter.plot_price_ma(prices, logger.log_dir, ticker, self.show_plt)
            return prices

        except Exception as e:

            logger.log(f"Price analysis failed {e}")
            return None

    # =====================================================
    # Fundamental Analysis
    # =====================================================
    def _run_fundamental_analysis(
        self,
        prices: pd.DataFrame,
        logger: Logger,
        ticker: str
    ) -> None:
        logger.subsection("\nFundamental Analysis:")
        fundamentals: FundamentalData = self.fundamental_connector.fetch(ticker)
        processor = FundamentalProcessor(fundamentals, logger)
        metrics = processor.get_metrics()
        if metrics is not None:
            logger.subsection(f"Key Metrics for {ticker} (Last 5 years)")
            logger.log(metrics[["Revenue", "NOPAT", "ROIC", "FCF"]].tail(5))
            latest = processor.get_latest_data()
            sector = fundamentals.info.get("sector", "Unknown")
            final_dcf_cfg = self._resolve_dcf_config(sector)
            logger.subsection("\nValuation Model (DCF)")
            logger.log(f"Sector Detected: {sector}")
            logger.log(f"Assumptions Used: Growth={final_dcf_cfg['revenue_growth_5y']:.1%}, WACC={final_dcf_cfg['wacc']:.1%}, Margin={final_dcf_cfg['operating_margin_target']:.1%}")
            base_assumptions = DCFAssumptions(
                name=f"Sector: {sector} + Overrides",
                gr_next5y=final_dcf_cfg["revenue_growth_5y"],
                operating_margin_target=final_dcf_cfg["operating_margin_target"],
                tax_rate=final_dcf_cfg["tax_rate"],
                wacc=final_dcf_cfg["wacc"],
                terminal_gr=final_dcf_cfg["terminal_growth"],
                roic_target=latest["roic"],
                shares_outst=latest["shares"],
                net_debt=latest["net_debt"],
            )
            try:
                result = self.dcf_model.run_dcf(latest["rev"], base_assumptions)
                logger.log(f"Scenario: {result['scenario']}")
                logger.log(f"Estimated fair value per share: ${result['share_price']:.2f}")
                intr_val = result['share_price']
                curr_price = prices['Close'].iloc[-1]
                logger.log(f"Current Market Price: ${curr_price:.2f}")
                upside = (intr_val - curr_price) / curr_price
                logger.log(f"Implied Upside: {upside:.1%}")
                # Revenue / FCF plot
                Plotter.plot_revenue_fcf(metrics, logger.log_dir, ticker, self.show_plt)
                # ROIC vs WACC
                Plotter.plot_roic_vs_wacc(metrics, base_assumptions.wacc, logger.log_dir, ticker, self.show_plt)
                # Price vs DCF (after DCF calculated)
                Plotter.plot_price_vs_dcf(prices, intr_val, logger.log_dir, ticker, self.show_plt)
            except Exception as e:
                logger.log(f"DCF analysis failed: {e}")

    def _resolve_dcf_config(self, sector: str) -> dict:
        base = self.config.get("dcf", {
            "revenue_growth_5y": 0.05,
            "operating_margin_target": 0.20,
            "tax_rate": 0.21,
            "wacc": 0.08,
            "terminal_growth": 0.03
        }).copy()

        sector_map = {
            "Technology": {"revenue_growth_5y": 0.15, "operating_margin_target": 0.30, "wacc": 0.10},
            "Consumer Defensive": {"revenue_growth_5y": 0.04, "operating_margin_target": 0.20, "wacc": 0.065},
            "Healthcare": {"revenue_growth_5y": 0.06, "operating_margin_target": 0.25, "wacc": 0.08},
            "Energy": {"revenue_growth_5y": 0.03, "operating_margin_target": 0.15, "wacc": 0.09},
        }   
        if sector in sector_map:
            base.update(sector_map[sector])
        base.update(self.overrides)
        
        return base
