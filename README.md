# Fundamental Valuation Toolkit

**[David Černý](https://www.linkedin.com/in/david-%C4%8Dern%C3%BD-568a30131/)**, **[Simon Martinek](https://www.linkedin.com/in/simon-martinek-8b4524301/)**

Our project is a comprehensive financial research engine designed to automate the transition from raw accounting data into actionable investment insights. We use the **[McKinsey Valuation Framework](https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights/valuation-measuring-and-managing-the-value-of-companies)**, where raw financial statements are translated into economic metrics (specifically **NOPAT** and **Invested Capital**) to calculate **Return on Invested Capital** ("ROIC"). This data is used to calculate an enhanced 5-year ****Discounted Cash Flow** ("DCF") model with embedded risk analytics, all orchestrated through an automated, object-oriented pipeline.

## Features

* **McKinsey Framework Implementation:** Automatically converts standard balance sheet and income statement items into **Invested Capital** and **NOPAT** (Net Operating Profit less Adjusted Taxes) to calculate **ROIC** (Return on invested capital).

* **Automated DCF Valuation:** Projects Free Cash Flow for 5 years and calculates terminal value to find an intrinsic value per share.

* **Smart Sector Detection:** Automatically detects the sector and applies appropriate growth and margin assumptions.

* **Risk Analytics:** Returns annualized volatility, Sharpe Ratio, Sortino Ratio, Maximum Drawdown, and Value at Risk (CVaR).

* **Modular Pipeline:** A clear process separating data fetching, processing, and visualization.

* **Visualizations:** Automatically generates charts for price trends, ROIC vs. WACC, and Revenue/FCF trajectories.

## Installation

1. **Clone repository**

```

git clone <https://github.com/cedav12/FundamentalValuationToolkit.git>

cd FundamentalValuationToolkit

```

2. **Install dependencies**

```

pip install -r requirements.txt

```

## Usage manual

**Configuration** 

The project uses a cascading configuration system:

* CLI overrides (Highest priority - manually specified assumptions)

* Sector detection (Middle priority - adjusts based on industry)

* config.json defaults (Lowest priority - as specified in config.json)

To change the default assumptions, edit config.json in the root directory:

```

{

  "dcf":{

    "revenue_growth_5y": 0.05,

    "operating_margin_target": 0.20,

    "tax_rate": 0.21,

    "wacc": 0.08,

    "terminal_growth": 0.03

  },

  "market":{

    "risk_free_rate": 0.04

  }

}

```

The user may then proceed to run the project via the command line.

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

**Overriding Assumptions**

* (Available overrides: --growth, --margin, --wacc, --terminal_growth)

```

python main.py --tickers TSLA --wacc 0.15 --growth 0.30

```

## Methodology

### 1. Economic metrics

Net income is often not the best metric to count a company's true performance due to non-cash items and leverage. We calculate the **[Return On Invested Capital](https://www.investopedia.com/terms/r/returnoninvestmentcapital.asp)**:

$$\text{ROIC} = \frac{\text{NOPAT}}{\text{Invested Capital}}$$

If ROIC > WACC, the company is creating value.

### 2. Valuation

We use a 5-year Discounted Cash Flow (DCF) model to determine intrinsic value:

$$\text{Enterprise Value} = \sum_{t=1}^{5} \frac{\text{FCF}_t}{(1+WACC)^t} + \frac{\text{Terminal Value}}{(1+WACC)^5}$$

Where Terminal Value is calculated using the Gordon Growth Model:

$$\text{Terminal Value} = \frac{\text{NOPAT}_{t=5} \times (1 + g) \times (1 - \frac{g}{\text{ROIC}})}{WACC - g}$$
