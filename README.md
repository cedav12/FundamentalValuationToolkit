# Fundamental Valuation Toolkit
Our project is a comprehensive financial research engine designed to automate the transition from raw accounting data into actionable investment insights. We use the **McKinsey Valuation Framework**, where raw financial statements are translated into economic metrics (specifically **NOPAT** and **Invested Capital**) to calculate **Return on Invested Capital** ("ROIC"). This data is used to calculate an enhanced 5-year ****Discounted Cash Flow** ("DCF") model with embedded risk analytics, all orchestrated through an automated, object-oriented pipeline.

## Features
* **McKinsey Framework Implementation:** Automatically converts standard balance sheet and income statement items into **Invested Capital** and **NOPAT** (Net Operating Profit less Adjusted Taxes) to calculate **ROIC** (Return on invested capital).
* **Automated DCF Valuation:** Projects Free Cash Flow for 5 years and calculates terminal value to find an intrinsic value per share.
* **Risk Analytics:** Returns annualized volatility, Sharpe Ratio, Sortino Ratio, Maximum Drawdown, and Value at Risk (CVaR).
* **Modular Pipeline:** A clear process separating data fetching, processing, and visualization.
* **Visualizations:** Automatically generates charts for price trends, ROIC vs. WACC, and Revenue/FCF trajectories.

## Installation
1. **Clone repository**
```
git clone <https://github.com/cedav12/FundamentalValuationToolkit.git>
cd EquityVal
```
2. **Install dependencies**
```
pip install -r requirements.txt
```

## Usage manual

**Configuration**

The project uses a config.json file for users to be able to change the assumptions. What can be modified are the default growth rates, margins, and discount rates (WACC). This is done by editing this file in the root directory:
```
{
    "dcf": {
        "revenue_growth_5y": 0.05,
        "operating_margin_target": 0.20,
        "tax_rate": 0.21,
        "wacc": 0.08,
        "terminal_growth": 0.03
    }
}
```
The user may then proceedto run the project via the command line.
**Basic run**
```
python main.py --tickers KO PLTR NVDA
```
**Run with interactive plots**
```
python main.py --tickers NVDA --show_plt
```
**Custom Output Directory**
```
python main.py --tickers NVDA --output_path ./my_research
```

## Methodology
### 1. Economic metrics
Net income is often not the best metric to count a company's true performance due to non-cash items and leverage. We calculate **Economic Profit**:
If ROIC > WACC, the company is creating value.
### 2. Valuation
We use a 5-year DCF model:
$$\text{Enterprise Value} = \sum_{t=1}^{5} \frac{\text{FCF}_t}{(1+WACC)^t} + \frac{\text{Terminal Value}}{(1+WACC)^5}$$
