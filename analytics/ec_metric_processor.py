import pandas as pd
import numpy as np

from data.models.fundamental_data import FundamentalData


class FundamentalProcessor:  # Raw financial statement conversion to econ. metrics using the McKinsey Valuation framework (Valuation - measuring and managing the value of companies 8th ed.)
    def __init__(self, data: FundamentalData, tax_rate: float = 0.21): # 21% - https://en.wikipedia.org/wiki/Corporate_tax_in_the_United_States
        """
       Parameters
       ----------
       data : FundamentalData
           Data containing info about instrument and potentially financial statements
       tax_rate : float, optional
           Used corporate tax_rate
       """
        self._data = data
        self._tax_rate = tax_rate
        self._output: pd.DataFrame | None = None

    def get_metrics(self) -> pd.DataFrame | None:
        """
        Run FundamentalProcessor.
        Returns metrics DataFrame if successful, else None.
        """
        if self._data.quote_type != "EQUITY":
            print(f"{self._data.ticker}: QuoteType={self._data.quote_type} Not Supported."
                  f" FundamentalProcessor only supports EQUITIES.")
            return None

        if self._output is not None:
            return self._output.copy()

        try:
            self._output = self._process_metrics()
            return self._output.copy()
        except Exception as e:
            print(e)
            return None
        
    # Processes financial statements  (Private method)
    def _process_metrics(self) -> pd.DataFrame:
        dfs = []
        for key, df in self._data.statements.items():
            if not df.empty:
                dfs.append(df.T)
    
        full_df = pd.concat(dfs, axis=1)
        full_df.index = pd.to_datetime(full_df.index)
        full_df = full_df.sort_index()
        economic_df = pd.DataFrame(index=full_df.index)

        # NOPAT (Net Operating Profit Less Adjusted Taxes) = EBIT * (1 - Tax Rate)

        if "EBIT" in full_df.columns:
            ebit = full_df["EBIT"]
        elif "Pretax Income" in full_df.columns and "Interest Expense" in full_df.columns:
            ebit = full_df["Pretax Income"] + full_df["Interest Expense"].fillna(0)
        else:
            ebit = full_df.get("Operating Income", 0)
        
        tax_provision = full_df.get("Tax Provision", 0)
        pretax_income = full_df.get("Pretax Income", 1)
        
        effective_tax_rate = (tax_provision/pretax_income).clip(0, 0.4)
        economic_df["NOPAT"] = ebit - tax_provision

        # Invested Capital = Operating Working Cash + Net Fixed Assets

        cur_assets = full_df.get("Current Assets", 0)
        cash = full_df.get("Cash And Cash Equivalents", 0)
        cur_lia = full_df.get("Current Liabilities", 0)

        op_work_cap = (cur_assets - cash) - cur_lia

        net_ppe = full_df.get("Net PPE", 0)
        if "Net PPE" not in full_df.columns:
            net_ppe = full_df.get("Gross PPE", 0) - full_df.get("Accumulated Depreciation", 0)

        other_assets = full_df.get("Total Non Current Assets", 0) - net_ppe

        economic_df["Invested_Capital"] = op_work_cap + net_ppe + other_assets

        # ROIC (Return On Invested Capital) = NOPAT / Invested Capital

        economic_df["ROIC"] = economic_df["NOPAT"] / economic_df["Invested_Capital"].replace(0, np.nan)

        # Free Cash Flow = Nopat / Invested Capital Change

        economic_df["Change_in_IC"] = economic_df["Invested_Capital"].diff()
        economic_df["FCF"] = economic_df["NOPAT"] - economic_df["Change_in_IC"]

        # Revenue Growth = Revenue Growth Year X - Revenue Growth Year (X - 1)

        economic_df["Revenue"] = full_df.get("Total Revenue", 0)
        economic_df["Growth"] = economic_df["Revenue"].pct_change()

        return economic_df