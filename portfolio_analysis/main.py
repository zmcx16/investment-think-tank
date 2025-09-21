import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import yfinance as yf
from pathlib import Path
import warnings
import argparse
import sys
import subprocess
import shutil
import os
import logging

warnings.filterwarnings('ignore')

# Setup logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('portfolio_analysis.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

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
    logger.info("=== Portfolio Composition Analysis ===")
    logger.info(f"Total Market Value: ${total_value:,.2f}")
    logger.info(f"Cash: ${cash_value:,.2f} ({cash_value/total_value*100:.2f}%)")
    logger.info(f"Stock Investment: ${equity_df['marketValue'].sum():,.2f} ({equity_df['marketValue'].sum()/total_value*100:.2f}%)")

    # Top holdings
    top_holdings = equity_df.nlargest(5, "marketValue")[["symbol", "description", "marketValue", "percentOfNAV"]]
    logger.info("\nTop 5 Holdings:")
    for _, row in top_holdings.iterrows():
        logger.info(f"{row['symbol']}: ${row['marketValue']:,.2f} ({row['percentOfNAV']:.2f}%)")

    # Risk metrics
    top3_weight = equity_df.nlargest(3, "marketValue")["percentOfNAV"].sum()
    logger.info(f"\nTop 3 Holdings Weight: {top3_weight:.2f}%")

    # Asset category distribution
    category_dist = df.groupby("assetCategory")["marketValue"].sum()
    logger.info("\nAsset Category Distribution:")
    for cat, value in category_dist.items():
        logger.info(f"{cat}: ${value:,.2f} ({value/total_value*100:.2f}%)")

    return total_value

def monte_carlo_optimization(equity_df, n_simulations=1000):
    """Perform Monte Carlo portfolio optimization"""
    # Get unique stock symbols
    tickers = equity_df["symbol"].unique().tolist()

    if len(tickers) < 2:
        logger.warning("At least 2 stocks are required for portfolio optimization")
        return None

    logger.info(f"\n=== Starting Monte Carlo Portfolio Optimization (Analyzing {len(tickers)} stocks) ===")

    try:
        # Download historical data
        logger.info(f"Downloading historical data for {len(tickers)} stocks...")
        hist_data = yf.download(tickers, period="1y", progress=False)

        if hist_data.empty:
            logger.warning("Unable to download historical data")
            return None

        logger.info(f"Download successful, data shape: {hist_data.shape}")
        logger.info(f"Data columns: {hist_data.columns.tolist()}")

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
            logger.warning("Unable to obtain sufficient historical data")
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

        # find the best portfolio (max Sharpe ratio)
        best_portfolio = max(results, key=lambda x: x['sharpe'])

        logger.info("\n=== Optimal Portfolio Allocation (Maximum Sharpe Ratio) ===")
        logger.info(f"Expected Annual Return: {best_portfolio['return']:.2%}")
        logger.info(f"Annual Volatility: {best_portfolio['volatility']:.2%}")
        logger.info(f"Sharpe Ratio: {best_portfolio['sharpe']:.3f}")

        logger.info("\nRecommended Allocation:")
        optimal_weights = pd.DataFrame({
            'Ticker': tickers,
            'Weight': best_portfolio['weights']
        }).sort_values('Weight', ascending=False)

        for _, row in optimal_weights.iterrows():
            logger.info(f"{row['Ticker']}: {row['Weight']*100:.2f}%")

        return optimal_weights

    except Exception as e:
        logger.error(f"Monte Carlo optimization failed: {str(e)}")
        return None

def generate_base_report(df, equity_df, cash_value, optimal_weights=None, output_dir=None):
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

    logger.info(f"\n=== Reports Generated ===")
    logger.info(f"1. {portfolio_report_file} - Complete portfolio analysis")
    if optimal_weights is not None:
        logger.info(f"2. {optimal_weights_file} - Optimal portfolio allocation")

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
  python main.py --source /path/to/portfolio.xml --output /path/to/output --prompt-file /path/to/custom_prompt.txt --model gemini-2.5-flash
        """
    )

    # Default source path (same as current)
    default_source = Path(__file__).parent / "data" / "interactivebrokers" / "source" / "sample.anonymized.xml"

    # Default output path (output folder relative to main.py)
    default_output = Path(__file__).parent / "output"

    # Default prompt file path
    default_prompt_file = Path(__file__).parent / "default_prompt.txt"

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

    parser.add_argument(
        '--interactive', action='store_true',
        help='Run in interactive mode'
    )

    parser.add_argument(
        '--skip-gemini', action='store_true',
        help='Skip Gemini analysis even if Gemini CLI is available'
    )

    parser.add_argument(
        '--prompt-file', '-p',
        type=str,
        default=str(default_prompt_file),
        help=f'Path to the prompt file for Gemini analysis (default: {default_prompt_file})'
    )

    parser.add_argument(
        '--model', '-m',
        type=str,
        default='gemini-2.5-flash',
        help='Gemini model to use for analysis (default: gemini-2.5-flash)'
    )

    return parser.parse_args()

def check_gemini_cli():
    try:
        gemini_path = shutil.which("gemini")
        if gemini_path:
            logger.info(f"Found Gemini CLI at: {gemini_path}")
            return gemini_path

        result = subprocess.run(["gemini", "--version"],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info("Gemini CLI is available")
            return "gemini"
    except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.CalledProcessError):
        pass
    return None

def run_gemini_analysis(input_directories, output_path, prompt_file=None, model='gemini-2.5-flash', interactive=False):
    """Run Gemini CLI analysis with portfolio data"""
    gemini_cmd = check_gemini_cli()

    if not gemini_cmd:
        logger.error("Gemini CLI not found in system PATH or common locations.")
        logger.error("Please ensure Gemini CLI is properly installed and accessible.")
        return False

    # fix cp950 error
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['LC_ALL'] = 'en_US.UTF-8'

    # Implement Gemini CLI execution
    try:
        if interactive:
            gemini_args = [
                gemini_cmd,
                "--include-directories", input_directories,
                "--model", model,
            ]
            logger.info(f"Running Gemini CLI with command: {' '.join(gemini_args)}")
            subprocess.run(
                gemini_args,
                env=env,
                stdin=None,
                stdout=None,
                stderr=None
            )
            return True

        # Non-interactive mode
        # Load prompt from file if specified
        if prompt_file and Path(prompt_file).exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt = f.read()
        else:
            prompt = """You are a professional investment advisor and portfolio analyst. Please analyze the provided portfolio data and reports comprehensively from {input_directories}. Please provide a detailed, professional report with specific recommendations for portfolio optimization and risk management. Format your response in markdown with clear sections and bullet points for easy readability."""

        prompt = prompt.replace("{input_directories}", input_directories)
        # save prompt to temp file
        temp_prompt_file_path = Path("temp_prompt.txt")
        temp_prompt_file = str(temp_prompt_file_path.resolve())
        with open(temp_prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)

        gemini_args = [
            gemini_cmd,
            temp_prompt_file,
            "--include-directories", input_directories,
            "--model", model
        ]
        logger.info(f"Running Gemini CLI with command: {' '.join(gemini_args)}")
        logger.info(f"Using model: {model}")

        result = subprocess.run(
            gemini_args,
            capture_output=True,
            text=True,
            timeout=300,
            encoding='utf-8',
            errors='ignore',
            env=env
        )

        # Clean up temp prompt file
        if temp_prompt_file_path.exists():
            temp_prompt_file_path.unlink()

        if result.returncode == 0:
            logger.info("Gemini analysis completed successfully.")
            if result.stdout:
                logger.info("Gemini Output:")
                logger.info(result.stdout)

            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write("# Gemini Portfolio Analysis Report\n\n")
                    f.write(result.stdout)
                logger.info(f"Analysis saved to: {output_path}")
            except Exception as write_error:
                logger.warning(f"Could not save to file: {write_error}")

            return True
        else:
            logger.error("Gemini analysis failed.")
            if result.stderr:
                logger.error("Error Output:")
                logger.error(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        logger.error("Gemini CLI analysis timed out (5 minutes)")
        return False
    except Exception as e:
        logger.error(f"Error running Gemini CLI: {str(e)}")
        return False

def main():
    """Main function to run portfolio analysis"""
    # Parse command line arguments
    args = parse_arguments()

    source_file = Path(args.source)
    output_dir = Path(args.output)
    base_report_dir = output_dir / "base_report"
    summary_report_path = output_dir / "summary_report.md"

    logger.info(f"Source file: {source_file}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Model: {args.model}")

    if not source_file.exists():
        logger.error(f"Source file not found: {source_file}")
        logger.error("Please ensure the file exists or specify a valid path using --source")
        sys.exit(1)

    try:
        # Parse XML
        logger.info("Parsing portfolio data...")
        df, equity_df, cash_value = parse_ib_xml(str(source_file))

        # Analyze current portfolio
        total_value = analyze_portfolio(df, equity_df, cash_value)

        # Perform Monte Carlo optimization
        optimal_weights = monte_carlo_optimization(equity_df)

        # Generate reports
        generate_base_report(df, equity_df, cash_value, optimal_weights, str(base_report_dir))

    except Exception as e:
        logger.error(f"Error occurred during analysis: {str(e)}")
        sys.exit(1)

    # Run Gemini CLI if available
    if args.skip_gemini:
        logger.info("Skipping Gemini analysis as per user request.")
        sys.exit(0)
    gemini_success = run_gemini_analysis(str(source_file.parent)+","+str(base_report_dir), str(summary_report_path), args.prompt_file, args.model, args.interactive)
    if gemini_success:
        logger.info(f"Summary report generated at: {summary_report_path}")
    else:
        logger.warning("Gemini analysis was not completed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
