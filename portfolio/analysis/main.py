import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import yfinance as yf
from pathlib import Path
import warnings
import argparse
import sys
warnings.filterwarnings('ignore')

def parse_ib_xml(xml_file: str):
    """Parse Interactive Brokers Flex XML file and extract portfolio positions"""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Extract positions from OpenPosition elements
    positions = []
    for pos in root.findall(".//OpenPosition"):
        positions.append(pos.attrib)

    if not positions:
        raise ValueError("No positions found in XML file")

    df = pd.DataFrame(positions)

    # Convert numeric columns
    numeric_cols = ["position", "markPrice", "costBasisPrice", "positionValue", "percentOfNAV"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Calculate market value from positionValue (already calculated in IB XML)
    df["marketValue"] = df["positionValue"]

    # Filter out options and focus on stocks/ETFs for portfolio optimization
    equity_df = df[df["assetCategory"].isin(["STK", "ADR", "REIT"])].copy()

    # Get cash from EquitySummary
    cash_value = 0
    for summary in root.findall(".//EquitySummaryByReportDateInBase"):
        cash_value = float(summary.get("cash", 0))
        break

    return df, equity_df, cash_value

def analyze_portfolio(df, equity_df, cash_value):
    """Analyze portfolio composition and risk metrics"""
    total_value = df["marketValue"].sum() + cash_value

    # Portfolio composition
    print("=== Portfolio Composition Analysis ===")
    print(f"Total Market Value: ${total_value:,.2f}")
    print(f"Cash: ${cash_value:,.2f} ({cash_value/total_value*100:.2f}%)")
    print(f"Stock Investment: ${equity_df['marketValue'].sum():,.2f} ({equity_df['marketValue'].sum()/total_value*100:.2f}%)")

    # Top holdings
    top_holdings = equity_df.nlargest(5, "marketValue")[["symbol", "description", "marketValue", "percentOfNAV"]]
    print("\nTop 5 Holdings:")
    for _, row in top_holdings.iterrows():
        print(f"{row['symbol']}: ${row['marketValue']:,.2f} ({row['percentOfNAV']:.2f}%)")

    # Risk metrics
    top3_weight = equity_df.nlargest(3, "marketValue")["percentOfNAV"].sum()
    print(f"\nTop 3 Holdings Weight: {top3_weight:.2f}%")

    # Asset category distribution
    category_dist = df.groupby("assetCategory")["marketValue"].sum()
    print("\nAsset Category Distribution:")
    for cat, value in category_dist.items():
        print(f"{cat}: ${value:,.2f} ({value/total_value*100:.2f}%)")
    
    return total_value

def monte_carlo_optimization(equity_df, n_simulations=1000):
    """Perform Monte Carlo portfolio optimization"""
    # Get unique stock symbols
    tickers = equity_df["symbol"].unique().tolist()

    if len(tickers) < 2:
        print("At least 2 stocks are required for portfolio optimization")
        return None
    
    print(f"\n=== Starting Monte Carlo Portfolio Optimization (Analyzing {len(tickers)} stocks) ===")

    try:
        # Download historical data
        print(f"Downloading historical data for {len(tickers)} stocks...")
        hist_data = yf.download(tickers, period="1y", progress=False)
        
        if hist_data.empty:
            print("Unable to download historical data")
            return None
        
        print(f"Download successful, data shape: {hist_data.shape}")
        print(f"Data columns: {hist_data.columns.tolist()}")

        # Handle single vs multiple tickers
        if len(tickers) == 1:
            if "Adj Close" in hist_data.columns:
                prices = hist_data["Adj Close"]
            else:
                prices = hist_data["Close"]
            returns = prices.pct_change().dropna()
            # Convert to DataFrame for consistency
            returns = pd.DataFrame({tickers[0]: returns})
        else:
            if isinstance(hist_data.columns, pd.MultiIndex):
                if "Adj Close" in [col[0] for col in hist_data.columns]:
                    prices = hist_data["Adj Close"]
                else:
                    prices = hist_data["Close"]
            else:
                prices = hist_data
            # Calculate returns
            returns = prices.pct_change().dropna()
        
        if returns.empty:
            print("Unable to obtain sufficient historical data")
            return None
        
        # Monte Carlo simulation
        n_assets = len(tickers)
        results = []

        # Ensure we have a DataFrame for mean and cov calculations
        if isinstance(returns, pd.Series):
            returns = pd.DataFrame({tickers[0]: returns})
        
        for _ in range(n_simulations):
            # Random weights
            weights = np.random.random(n_assets)
            weights /= np.sum(weights)
            
            # Portfolio metrics
            if n_assets == 1:
                portfolio_return = returns.mean().iloc[0] * 252
                portfolio_std = returns.std().iloc[0] * np.sqrt(252)
            else:
                portfolio_return = np.sum(weights * returns.mean()) * 252
                portfolio_std = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
            
            sharpe_ratio = portfolio_return / portfolio_std if portfolio_std > 0 else 0
            
            results.append({
                'weights': weights,
                'return': portfolio_return,
                'volatility': portfolio_std,
                'sharpe': sharpe_ratio
            })
        
        # Find best portfolio (max Sharpe ratio)
        best_portfolio = max(results, key=lambda x: x['sharpe'])
        
        print("\n=== Optimal Portfolio Allocation (Maximum Sharpe Ratio) ===")
        print(f"Expected Annual Return: {best_portfolio['return']:.2%}")
        print(f"Annual Volatility: {best_portfolio['volatility']:.2%}")
        print(f"Sharpe Ratio: {best_portfolio['sharpe']:.3f}")

        print("\nRecommended Allocation:")
        optimal_weights = pd.DataFrame({
            'Ticker': tickers,
            'Weight': best_portfolio['weights']
        }).sort_values('Weight', ascending=False)
        
        for _, row in optimal_weights.iterrows():
            print(f"{row['Ticker']}: {row['Weight']*100:.2f}%")
        
        return optimal_weights
        
    except Exception as e:
        print(f"Monte Carlo optimization failed: {str(e)}")
        return None

def generate_report(df, equity_df, cash_value, optimal_weights=None, output_dir=None):
    """Generate comprehensive portfolio report"""
    total_value = df["marketValue"].sum() + cash_value

    # Create detailed portfolio report
    report_data = []

    # Add equity positions
    for _, row in equity_df.iterrows():
        report_data.append({
            'Symbol': row['symbol'],
            'Description': row['description'],
            'Asset_Category': row['assetCategory'],
            'Position': int(float(row['position'])),
            'Market_Price': float(row['markPrice']),
            'Market_Value': float(row['marketValue']),
            'Cost_Basis': float(row.get('costBasisMoney', 0)),
            'Unrealized_PnL': float(row.get('fifoPnlUnrealized', 0)),
            'Weight_Percent': float(row['percentOfNAV'])
        })

    # Add cash position
    report_data.append({
        'Symbol': 'CASH',
        'Description': 'Cash Position',
        'Asset_Category': 'CASH',
        'Position': 1,
        'Market_Price': cash_value,
        'Market_Value': cash_value,
        'Cost_Basis': cash_value,
        'Unrealized_PnL': 0,
        'Weight_Percent': cash_value/total_value*100
    })

    # Create DataFrame and save to CSV
    report_df = pd.DataFrame(report_data)

    # Ensure output directory exists
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        portfolio_report_file = output_path / "portfolio_analysis_report.csv"
        optimal_weights_file = output_path / "optimal_portfolio_weights.csv"
    else:
        portfolio_report_file = "portfolio_analysis_report.csv"
        optimal_weights_file = "optimal_portfolio_weights.csv"

    report_df.to_csv(portfolio_report_file, index=False, encoding='utf-8-sig')

    if optimal_weights is not None:
        optimal_weights.to_csv(optimal_weights_file, index=False)

    print(f"\n=== Reports Generated ===")
    print(f"1. {portfolio_report_file} - Complete portfolio analysis")
    if optimal_weights is not None:
        print(f"2. {optimal_weights_file} - Optimal portfolio allocation")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Portfolio Analysis Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py
  python main.py --source /path/to/portfolio.xml
  python main.py --output /path/to/output
  python main.py --source /path/to/portfolio.xml --output /path/to/output
        """
    )

    # Default source path (same as current)
    default_source = Path(__file__).parent.parent / "data" / "interactivebrokers" / "sample.anonymized.xml"

    # Default output path (output folder relative to main.py)
    default_output = Path(__file__).parent / "output"

    parser.add_argument(
        '--source', '-s',
        type=str,
        default=str(default_source),
        help=f'Path to the portfolio data file (default: {default_source})'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        default=str(default_output),
        help=f'Output directory for generated reports (default: {default_output})'
    )

    return parser.parse_args()

def main():
    """Main function to run portfolio analysis"""
    # Parse command line arguments
    args = parse_arguments()

    source_file = Path(args.source)
    output_dir = Path(args.output)

    print(f"Source file: {source_file}")
    print(f"Output directory: {output_dir}")

    if not source_file.exists():
        print(f"Error: Source file not found: {source_file}")
        print("Please ensure the file exists or specify a valid path using --source")
        sys.exit(1)

    try:
        # Parse XML
        print("Parsing portfolio data...")
        df, equity_df, cash_value = parse_ib_xml(str(source_file))

        # Analyze current portfolio
        total_value = analyze_portfolio(df, equity_df, cash_value)

        # Perform Monte Carlo optimization
        optimal_weights = monte_carlo_optimization(equity_df)

        # Generate reports
        generate_report(df, equity_df, cash_value, optimal_weights, str(output_dir))

    except Exception as e:
        print(f"Error occurred during analysis: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
