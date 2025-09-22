# Portfolio Analysis Tool

A comprehensive portfolio analysis tool that integrates with Interactive Brokers data and leverages Gemini AI for intelligent investment insights.

## Features

- 📊 **Portfolio Data Processing**: Parse Interactive Brokers Flex XML reports
- 📈 **Monte Carlo Optimization**: Find optimal portfolio allocation using modern portfolio theory
- 🤖 **AI-Powered Analysis**: Generate detailed investment recommendations using Gemini AI
- 📋 **Comprehensive Reports**: Export detailed CSV reports and markdown summaries
- 🔄 **Interactive Mode**: Engage in follow-up conversations with AI for deeper insights
- 🛠 **Flexible Configuration**: Customizable source paths, output directories, and AI models

## Quick Start

### Prerequisites

1. **Python Environment**: Python 3.8+ with required packages
   ```bash
   pip install -r requirements.txt
   ```

2. **Gemini CLI**: Install Google's [Gemini CLI tool](https://github.com/google-gemini/gemini-cli)
   ```bash
   npm install -g @google-cloud/gemini-cli
   ```

3. **Portfolio Data**: Interactive Brokers Flex Query XML file (see [Data Sources](#data-sources))

### Basic Usage

#### Option 1: Direct Execution
```bash
# Basic analysis with AI insights
python main.py

# Custom source and output
python main.py --source "path/to/portfolio_data.json" --output "path/to/results"

# Skip AI analysis (faster)
python main.py --skip-gemini

# Use different AI model
python main.py --model "gemini-2.5-flash"

# Custom prompt file for AI analysis
python main.py --prompt-file "custom_prompt.txt"

# Adjust Monte Carlo simulations for faster/more accurate results
python main.py --simulations 10000

# Combined options
python main.py --source "data.json" --simulations 3000 --model "gemini-2.5-flash"

```

#### Option 2: Interactive Mode
```bash
# Run with defaults
python main.py --interactive
```


## Output Structure

```
output/
├── summary_report.md           # AI-generated investment analysis
└── base_report/
    ├── portfolio_analysis_report.csv    # Detailed position data
    ├── portfolio_metrics.csv            # Monte Carlo metrics results 
    └── optimal_portfolio_weights.csv    # Monte Carlo optimization results
```

## Data Sources

### Interactive Brokers Setup

1. **Generate Flex Query**:
   - Log into Interactive Brokers Client Portal
   - Navigate to Reports > Flex Queries
   - Create new query with these sections:
     - Net Asset Value (NAV) in Base
     - Open Positions

2. **Download Data**:
   - Run the query to generate XML report
   - Download and save as `sample.anonymized.xml` manually or run the provided script:
   ```bash
   python download_flex_query_reports.py
   ```

3. **Convert to JSON**:
   - Use provided script to convert XML to JSON format
   ```bash
   python convert_flex_query_reports.py
   ```
   
4. **Place JSON File**:
   - Save the converted JSON file in `data/interactivebrokers/source/portfolio_data.json`


## Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--source` | `-s` | Portfolio data file path | `data/interactivebrokers/source/portfolio_data.json` |
| `--output` | `-o` | Output directory | `output` |
| `--prompt-file` | `-p` | Custom AI prompt file | `default_prompt.txt` |
| `--model` | `-m` | Gemini model to use | `gemini-2.5-flash` |
| `--lang` | `-l` | Language code for Gemini analysis report output | `en-US` |
| `--simulations` | `-n` | Number of Monte Carlo simulations for portfolio optimization | `5000` |
| `--skip-gemini` | | Skip AI analysis | False |
| `--interactive` | `-i` | Enable interactive Q&A mode | False |


## Analysis Components

### 1. Portfolio Composition Analysis
- Total portfolio value breakdown
- Asset category distribution
- Top holdings identification
- Cash position analysis
- Concentration risk assessment

### 2. Monte Carlo Optimization
- Historical return analysis using Yahoo Finance data
- Risk-return optimization using Modern Portfolio Theory
- Sharpe ratio maximization
- Optimal weight recommendations
- Configurable simulation count (default: 5000) for accuracy vs. performance trade-off

### 3. AI-Powered Insights
- Professional investment advisory analysis
- Risk assessment and recommendations
- Market context and strategy suggestions
- Interactive Q&A capability

## Configuration

### Custom Prompts
Create a custom prompt file to tailor AI analysis:

```markdown
# custom_prompt.txt
You are a specialized investment advisor focusing on [your specific area].
Analyze the portfolio with emphasis on [your requirements]...
```

Usage:
```bash
python main.py --prompt-file "custom_prompt.txt"
```

## Sample Output

### Portfolio Analysis Report (CSV)
| Symbol | Description | Asset_Category | Position | Market_Price | Market_Value | Weight_Percent |
|--------|-------------|----------------|----------|--------------|--------------|----------------|
| AAPL | Apple Inc | STK | 100 | 150.00 | 15000.00 | 25.5 |
| GOOGL | Alphabet Inc | STK | 50 | 2500.00 | 125000.00 | 42.8 |

### Portfolio Metrics (CSV)
| Metric | Value | Formatted_Value |
|--------|-------|-----------------|
| Expected Annual Return | 0.15183865429839527 | 15.18% |
| Annual Volatility | 0.28284701150019464 | 28.28% |
| Sharpe Ratio | 0.5368225511489655 | 0.537 |

### AI Analysis Sample

#### Non-interactive Mode
```markdown
# Gemini Portfolio Analysis Report

As a professional investment advisor and portfolio analyst, I have analyzed the provided portfolio data. Below is a comprehensive report with specific recommendations for portfolio optimization and risk management.

## Portfolio Analysis Report

### 1. Portfolio Composition Assessment

The portfolio currently holds a mix of common stocks (STK) and short options (OPT), along with a significant cash position.

**Current Asset Allocation (Approximate based on `portfolio_analysis_report.csv`):**

*   **Stocks:** Approximately 72.73% (sum of `Weight_Percent` for STK assets)
*   **Cash:** Approximately 27.27%
*   **Options:** Approximately 3.15% (sum of absolute `Weight_Percent` for OPT assets) - *Note: Options are typically leveraged instruments, and their "weight" based on market value can be misleading. The negative position value indicates short options.*

**Detailed Stock Holdings:**

| Symbol | Description                  | Market Value (USD) | Weight (%) | Unrealized PnL (USD) |
| :----- | :--------------------------- | :----------------- | :--------- | :------------------- |
| AAP    | ADVANCE AUTO PARTS INC       | 587.00             | 5.87       | -326.52              |
| ALB    | ALBEMARLE CORP               | 572.88             | 5.73       | -641.29              |
| EL     | ESTEE LAUDER COMPANIES-CL A  | 526.80             | 5.27       | -331.36              |
| EPAM   | EPAM SYSTEMS INC             | 624.80             | 6.25       | -369.72              |
| EW     | EDWARDS LIFESCIENCES CORP    | 595.28             | 5.95       | -46.72               |
| GGB    | GERDAU SA -SPON ADR          | 566.02             | 5.66       | 38.21                |
| HAL    | HALLIBURTON CO               | 562.75             | 5.63       | -110.69              |
| NKE    | NIKE INC -CL B               | 567.12             | 5.67       | -22.56               |
| NVO    | NOVO-NORDISK A/S-SPONS ADR   | 552.60             | 5.53       | -117.68              |
| PVH    | PVH CORP                     | 605.71             | 6.06       | -4.15                |
| PYPL   | PAYPAL HOLDINGS INC          | 545.76             | 5.46       | 1.54                 |
| SEE    | SEALED AIR CORP              | 579.70             | 5.80       | -3.78                |
| TGT    | TARGET CORP                  | 528.78             | 5.29       | -115.00              |
| VALE   | VALE SA-SP ADR               | 564.72             | 5.65       | -70.82               |
| VFC    | VF CORP                      | 563.16             | 5.63       | -169.84              |

**Option Holdings:**

| Symbol                      | Description        | Position | Market Value (USD) | Unrealized PnL (USD) | Side  |
| :-------------------------- | :----------------- | :------- | :----------------- | :------------------- | :---- |
| ABNB 250926P00117000        | ABNB 26SEP25 117 P | -7       | -60.62             | -580.70              | Short |
| DEO 251017P00090000         | DEO 17OCT25 90 P   | -1       | -92.50             | -138.80              | Short |
| G 251017P00040000           | G 17OCT25 40 P     | -1       | -65.00             | -89.35               | Short |
| GIS 251121P00045000         | GIS 21NOV25 45 P   | -1       | -40.00             | -75.45               | Short |
| ZIM 251003P00011500         | ZIM 03OCT25 11.5 P | -11      | -57.20             | -217.53              | Short |

**Diversification Level:**
The portfolio holds 15 distinct stock positions, which provides a reasonable level of diversification across individual equities. However, without sector and geographic information, a complete assessment of diversification is challenging. The presence of ADRs (GGB, NVO, VALE) indicates some international exposure.

**Concentration Risks:**
While individual stock positions are relatively balanced in terms of `percentOfNAV` (mostly between 5-6%), the overall portfolio might have concentration risks if these stocks belong to highly correlated sectors or geographies. The significant cash position (27.27%) reduces overall market exposure but also limits potential growth.

### 2. Risk Analysis

**Portfolio Volatility:**
The portfolio includes short put options, which can introduce significant volatility and tail risk, especially if the underlying stocks experience sharp declines. The unrealized PnL for these options is significantly negative, indicating that the market has moved against these short positions.

**Sector Concentration:**
Without explicit sector data, it's difficult to assess sector concentration. However, based on company descriptions:
*   **Consumer Discretionary/Retail:** AAP, EL, NKE, PVH, TGT, VFC
*   **Materials/Chemicals:** ALB, SEE, GGB, VALE
*   **Technology/IT Services:** EPAM, PYPL
*   **Healthcare:** EW, NVO
*   **Energy:** HAL

This suggests a potential concentration in Consumer Discretionary/Retail and Materials sectors.

**Geographic Exposure:**
The majority of stock holdings appear to be US-based companies. However, GGB (Brazil), NVO (Denmark), and VALE (Brazil) are ADRs, providing some international exposure.

**Correlation Risks:**
The performance of stocks within the same sector or geography can be highly correlated. A downturn in a concentrated sector could significantly impact the portfolio. The short put options further amplify this risk, as they are highly sensitive to downward movements in their underlying assets.

### 3. Performance Evaluation

**Historical Performance Metrics:**
The `fifoPnlUnrealized` values indicate that most stock positions are currently at an unrealized loss. Only GGB and PYPL show a positive unrealized PnL. The short option positions are all showing significant unrealized losses. This suggests that the portfolio has experienced a challenging period, or the entry points for many positions were at higher prices.

**Risk-Adjusted Returns and Benchmark Comparisons:**
The provided data does not include historical price series or benchmark data, making it impossible to calculate risk-adjusted returns (e.g., Sharpe Ratio) or perform a quantitative comparison against relevant market benchmarks.

### 4. Optimization Recommendations

**Asset Allocation & Rebalancing Strategies:**

The `optimal_portfolio_weights.csv` provides target weights for various tickers. Comparing these to the current portfolio, there are notable differences that suggest rebalancing opportunities.

**Optimal Weights vs. Current Weights (Selected Examples):**

| Ticker | Optimal Weight (%) | Current Weight (%) | Difference (Optimal - Current) |
| :----- | :----------------- | :----------------- | :----------------------------- |
| AAP    | 14.96              | 5.87               | +9.09                          |
| PVH    | 11.92              | 6.06               | +5.86                          |
| ALB    | 9.67               | 5.73               | +3.94                          |
| VALE   | 9.17               | 5.65               | +3.52                          |
| NVO    | 0.77               | 5.53               | -4.76                          |
| HAL    | 3.09               | 5.63               | -2.54                          |
| GGB    | 2.49               | 5.66               | -3.17                          |

**Recommendations:**

*   **Increase Exposure:** Consider increasing exposure to AAP, PVH, ALB, and VALE to align with optimal weights. This could involve purchasing more shares of these companies.
*   **Decrease Exposure:** Reduce exposure to NVO, HAL, and GGB to move closer to the optimal allocation. This might involve selling a portion of these holdings.
*   **Re-evaluate Cash Position:** The current cash position of 27.27% is substantial. While providing liquidity and risk mitigation, it also represents a drag on potential returns in a rising market. Consider deploying a portion of this cash into underweighted assets, especially those with positive outlooks or strong fundamentals.
*   **Options Strategy Review:** The short put options are currently experiencing significant unrealized losses. A thorough review of the options strategy is critical.
    *   **Risk Management:** Implement stricter risk management protocols for options, including stop-loss orders or defined exit strategies.
    *   **Position Sizing:** Ensure that option positions are appropriately sized relative to the overall portfolio to avoid outsized losses.
    *   **Underlying Analysis:** Re-evaluate the fundamental outlook of the underlying assets for the short put options. If the outlook is deteriorating, consider closing or rolling the positions to manage risk.

**Risk Management:**

*   **Diversification by Sector/Geography:** Conduct a deeper analysis of the sector and geographic breakdown of the stock holdings. If concentrations are identified, consider diversifying into underrepresented sectors or regions.
*   **Stop-Loss Orders:** Implement stop-loss orders for individual stock positions to limit potential downside.
*   **Regular Rebalancing:** Establish a regular rebalancing schedule (e.g., quarterly or semi-annually) to bring the portfolio back in line with target asset allocations and optimal weights.
*   **Scenario Analysis:** Perform scenario analysis to understand how the portfolio would perform under various market conditions (e.g., significant market downturn, interest rate hikes).

### 5. Market Context

The current market conditions and economic environment are crucial for investment decisions. Without specific market data, general considerations include:

*   **Inflation and Interest Rates:** The impact of inflation and central bank interest rate policies on different asset classes.
*   **Economic Growth:** The overall health and growth prospects of the global economy.
*   **Geopolitical Events:** Potential impacts of international events on market stability and specific sectors.

These factors should be continuously monitored and incorporated into investment decisions.

### 6. Investment Strategy

Based on the analysis, the overarching investment strategy should focus on:

*   **Disciplined Rebalancing:** Actively rebalance the portfolio to align with the optimal weights, taking advantage of market fluctuations to buy low and sell high.
*   **Prudent Risk Management:** Prioritize risk management, especially concerning the options strategy. This includes setting clear entry and exit points, using stop-loss orders, and carefully sizing positions.
*   **Fundamental Analysis:** Continue to perform fundamental analysis on individual stock holdings to ensure they meet investment criteria and have strong long-term prospects.
*   **Diversification:** Continuously seek opportunities to enhance diversification across sectors, geographies, and asset classes to mitigate concentration risks.
*   **Cash Deployment:** Strategically deploy the cash position into high-conviction investment opportunities that align with the optimal portfolio structure and current market outlook.

This report provides a framework for optimizing the portfolio. It is recommended to review these recommendations with a financial advisor to tailor them to individual financial goals, risk tolerance, and time horizon.
```

#### Interactive Mode

##### Task1:
```markdown

╭───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│  > Please analyze the portfolio_data.json (produced earlier by portfolio_analysis main.py) together with the base_report data, and generate a detailed asset allocation analysis report.  │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

 ╭────────────────────────────────────────────────────────╮
 │ ✓  ReadFile data\source\portfolio_data.json            │
 │                                                        │
 │ ✓  ReadFile ...output\\optimal_portfolio_weights.csv   │
 │                                                        │
 │ ✓  ReadFile ...output\\portfolio_analysis_report.csv   │
 │                                                        │
 │ ✓  ReadFile ...tput\base_report\portfolio_metrics.csv  │
 ╰────────────────────────────────────────────────────────╯
✦ Asset Allocation Analysis Report

  Date: 2025年9月22日

  ---

  ### 1. Executive Summary


  This report provides a detailed analysis of the current portfolio's asset allocation, comparing it against an optimized allocation strategy. The portfolio currently holds a mix of stocks (STK), Exchange
  Traded Funds (ETF), Options (OPT), and Cash. The analysis highlights current holdings, their market values, and their percentage allocation within the portfolio, alongside key performance indicators.

  ---

  ### 2. Portfolio Overview


  Total Portfolio Value (excluding options):
  Based on portfolio_analysis_report.csv, the total market value of stocks, ETFs, and cash is approximately $9,999.98.

  Overall Portfolio Performance Metrics:


  | Metric                  | Value   |
  | :---------------------- | :------ |
  | Expected Annual Return  | 14.11%  |
  | Annual Volatility       | 27.31%  |
  | Sharpe Ratio            | 0.517   |

  ---

  ### 3. Current Asset Allocation

  The current portfolio is allocated across various assets as follows:

  Holdings by Asset Category:


  | Asset Category | Total Market Value (USD) | Percentage of Portfolio |
  | :------------- | :----------------------- | :---------------------- |
  | STK            | 6,817.62                 | 68.18%                  |
  | ETF            | 2,996.75                 | 29.97%                  |
  | CASH           | 88.54                    | 0.89%                   |
  | OPT            | -315.32                  | -3.15%                  |
  | Total      | 9,587.59             | 95.89%              |


  Note: The total market value includes options, which have a negative value in this report, leading to a total percentage less than 100% if only positive assets are considered. The `percentOfNAV` in 
  `portfolio_data.json` sums to approximately 95.89% for all assets including options.

  Detailed Current Holdings:


  | Symbol | Description                 | Asset Category | Market Value (USD) | Current Weight (%) | Unrealized PnL (USD) | Issuer Country |
  | :----- | :-------------------------- | :------------- | :----------------- | :----------------- | :------------------- | :------------- |
  | QQQ    | Invesco QQQ Trust           | ETF            | 2996.75            | 29.97              | 0.00                 | US             |
  | PVH    | PVH CORP                    | STK            | 605.71             | 6.06               | -4.15                | US             |
  | EW     | EDWARDS LIFESCIENCES CORP   | STK            | 595.28             | 5.95               | -46.72               | US             |
  | AAP    | ADVANCE AUTO PARTS INC      | STK            | 587.00             | 5.87               | -326.52              | US             |
  | SEE    | SEALED AIR CORP             | STK            | 579.70             | 5.80               | -3.78                | US             |
  | ALB    | ALBEMARLE CORP              | STK            | 572.88             | 5.73               | -641.29              | US             |
  | NKE    | NIKE INC -CL B              | STK            | 567.12             | 5.67               | -22.56               | US             |
  | GGB    | GERDAU SA -SPON ADR         | STK            | 566.02             | 5.66               | 38.21                | BR             |
  | VALE   | VALE SA-SP ADR              | STK            | 564.72             | 5.65               | -70.82               | BR             |
  | VFC    | VF CORP                     | STK            | 563.16             | 5.63               | -169.84              | US             |
  | HAL    | HALLIBURTON CO              | STK            | 562.75             | 5.63               | -110.69              | US             |
  | NVO    | NOVO-NORDISK A/S-SPONS ADR  | STK            | 552.60             | 5.53               | -117.68              | DK             |
  | PYPL   | PAYPAL HOLDINGS INC         | STK            | 545.76             | 5.46               | 1.54                 | US             |
  | TGT    | TARGET CORP                 | STK            | 528.78             | 5.29               | -115.00              | US             |
  | EL     | ESTEE LAUDER COMPANIES-CL A | STK            | 526.80             | 5.27               | -331.36              | US             |
  | EPAM   | EPAM SYSTEMS INC            | STK            | 624.80             | 6.25               | -369.72              | US             |
  | CASH   | Cash Position               | CASH           | 88.54              | 0.89               | 0.00                 | N/A            |
  | ABNB   | ABNB 26SEP25 117 P          | OPT            | -60.62             | 0.61               | -580.70              | N/A            |
  | G      | G 17OCT25 40 P              | OPT            | -65.00             | 0.65               | -89.35               | N/A            |
  | DEO    | DEO 17OCT25 90 P            | OPT            | -92.50             | 0.92               | -138.80              | N/A            |
  | ZIM    | ZIM 03OCT25 11.5 P          | OPT            | -57.20             | 0.57               | -217.53              | N/A            |
  | GIS    | GIS 21NOV25 45 P            | OPT            | -40.00             | 0.40               | -75.45               | N/A            |

  Geographical Allocation (based on Issuer Country Code for Stocks/ADRs):


  | Country Code | Number of Holdings |
  | :----------- | :----------------- |
  | US           | 12                 |
  | BR           | 2                  |
  | DK           | 1                  |

  ---

  ### 4. Optimal Portfolio Weights

  The optimal portfolio weights, as determined by the analysis, are as follows:


  | Ticker | Optimal Weight |
  | :----- | :------------- |
  | SEE    | 13.22%         |
  | AAP    | 11.88%         |
  | ALB    | 11.29%         |
  | EW     | 10.85%         |
  | EL     | 9.56%          |
  | VFC    | 8.12%          |
  | PYPL   | 7.74%          |
  | GGB    | 7.54%          |
  | PVH    | 6.60%          |
  | NVO    | 4.36%          |
  | HAL    | 2.44%          |
  | QQQ    | 2.11%          |
  | NKE    | 1.34%          |
  | VALE   | 1.27%          |
  | TGT    | 1.00%          |
  | EPAM   | 0.70%          |

  ---

  ### 5. Comparison and Analysis

  Key Observations:


   * QQQ (ETF): Currently, QQQ represents a significant portion of the portfolio (29.97%), while its optimal weight is considerably lower at 2.11%. This indicates a substantial overweighting in this ETF.
  The current allocation deviates significantly from the optimal weights, particularly with the large allocation to QQQ and the underallocation to several individual stocks. This suggests that the
  portfolio could benefit from rebalancing to align with the optimal strategy, which aims to maximize return for a given level of risk (as implied by the Sharpe Ratio).

  ---

  ### 6. Recommendations


   1. Rebalance towards Optimal Weights: Consider reducing the position in QQQ and increasing allocations to individual stocks such as SEE, AAP, ALB, EW, EL, VFC, PYPL, GGB, and PVH to align with the optimal
      portfolio weights.
  This report provides a high-level overview of the asset allocation. A deeper dive into sector analysis, correlation between assets, and specific risk contributions would provide a more comprehensive
  understanding.
```

##### Task2:
```markdown
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│  > Reallocate all cash holdings into QQQ, update portfolio_data.json accordingly, run portfolio_analysis main.py, and re-evaluate whether the revised portfolio outperforms the previous asset allocation  │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

 ╭──────────────────────────────────────────────╮
 │ ✓  ReadFile data\source\portfolio_data.json  │
 ╰──────────────────────────────────────────────╯
 ╭─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
 │ ✓  WriteFile Writing to data\source\portfolio_data.json         

 ...

 │    ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════  │
 │    1967 +   "cash_value": 0.0                                                                                                                                                                       │
 │    1968   }                                                                                                                                                                                         │
 ╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
 ╭─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
 │ ✓  Shell python main.py (Run the main portfolio analysis script to regenerate reports with the updated portfolio data.)                                                                             │
 │                                                                                                                                                                                                     │
 │    ... first 212 lines hidden ...                                                                                                                                                                   │

...

 │    Summary report generated at: C:\zmcx16\work\investment-think-tank\portfolio_analysis\output\summary_report.md                                                                                    │
 ╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
✦ The portfolio analysis script has been run with the updated portfolio_data.json.

  Here's a comparison of the portfolio metrics before and after reallocating cash to QQQ:


  Previous Portfolio Metrics:
     Expected Annual Return:* 14.83%
     Annual Volatility:* 29.97%
     Sharpe Ratio:* 0.495


  Revised Portfolio Metrics (with cash in QQQ):
     Expected Annual Return:* 17.91%
     Annual Volatility:* 29.52%
     Sharpe Ratio:* 0.607

  Conclusion:

  The revised portfolio, with cash holdings reallocated to QQQ, outperforms the previous asset allocation in terms of both expected return and risk-adjusted return.


   * The Expected Annual Return increased from 14.83% to 17.91%.
  This suggests that investing the cash into QQQ has improved the overall efficiency of the portfolio.
```