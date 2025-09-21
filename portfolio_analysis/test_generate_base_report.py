import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil
import os
import sys

# Add the current directory to Python path to import main module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from main import generate_base_report


class TestGenerateBaseReport(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create temporary directory for test outputs
        self.test_dir = tempfile.mkdtemp()

        # Create sample portfolio data
        self.sample_df = pd.DataFrame({
            'symbol': ['AAPL', 'GOOGL', 'MSFT', 'CASH'],
            'description': ['Apple Inc', 'Alphabet Inc', 'Microsoft Corp', 'Cash'],
            'assetCategory': ['STK', 'STK', 'STK', 'CASH'],
            'position': [100, 50, 75, 1],
            'markPrice': [150.0, 2500.0, 300.0, 10000.0],
            'costBasisPrice': [120.0, 2000.0, 250.0, 10000.0],
            'positionValue': [15000.0, 125000.0, 22500.0, 10000.0],
            'marketValue': [15000.0, 125000.0, 22500.0, 10000.0],
            'percentOfNAV': [8.7, 72.5, 13.0, 5.8],
            'costBasisMoney': [12000.0, 100000.0, 18750.0, 10000.0],
            'fifoPnlUnrealized': [3000.0, 25000.0, 3750.0, 0.0]
        })

        # Create equity subset (excluding cash)
        self.sample_equity_df = self.sample_df[self.sample_df['assetCategory'] != 'CASH'].copy()

        # Sample cash value
        self.sample_cash_value = 10000.0

        # Sample optimal weights
        self.sample_optimal_weights = pd.DataFrame({
            'Ticker': ['AAPL', 'GOOGL', 'MSFT'],
            'Weight': [0.3, 0.4, 0.3]
        })

    def tearDown(self):
        """Clean up after each test method."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_generate_base_report_with_output_dir(self):
        """Test generate_base_report with specified output directory."""
        # Call the function
        generate_base_report(
            df=self.sample_df,
            equity_df=self.sample_equity_df,
            cash_value=self.sample_cash_value,
            optimal_weights=self.sample_optimal_weights,
            output_dir=self.test_dir
        )

        # Check if output files are created
        portfolio_report_file = Path(self.test_dir) / "portfolio_analysis_report.csv"
        optimal_weights_file = Path(self.test_dir) / "optimal_portfolio_weights.csv"

        self.assertTrue(portfolio_report_file.exists(), "Portfolio analysis report should be created")
        self.assertTrue(optimal_weights_file.exists(), "Optimal weights report should be created")

        # Verify portfolio report content
        report_df = pd.read_csv(portfolio_report_file)
        expected_columns = [
            'Symbol', 'Description', 'Asset_Category', 'Position',
            'Market_Price', 'Market_Value', 'Cost_Basis',
            'Unrealized_PnL', 'Weight_Percent'
        ]

        for col in expected_columns:
            self.assertIn(col, report_df.columns, f"Column {col} should be in the report")

        # Check if all symbols are included (including cash)
        expected_symbols = ['AAPL', 'GOOGL', 'MSFT', 'CASH']
        actual_symbols = report_df['Symbol'].tolist()
        for symbol in expected_symbols:
            self.assertIn(symbol, actual_symbols, f"Symbol {symbol} should be in the report")

        # Verify optimal weights content
        weights_df = pd.read_csv(optimal_weights_file)
        self.assertIn('Ticker', weights_df.columns)
        self.assertIn('Weight', weights_df.columns)
        self.assertEqual(len(weights_df), 3, "Should have 3 tickers in optimal weights")

    def test_generate_base_report_without_output_dir(self):
        """Test generate_base_report without specified output directory (current directory)."""
        # Change to test directory to avoid cluttering actual directory
        original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        try:
            # Call the function without output_dir
            generate_base_report(
                df=self.sample_df,
                equity_df=self.sample_equity_df,
                cash_value=self.sample_cash_value,
                optimal_weights=self.sample_optimal_weights,
                output_dir=None
            )

            # Check if output files are created in current directory
            portfolio_report_file = Path("portfolio_analysis_report.csv")
            optimal_weights_file = Path("optimal_portfolio_weights.csv")

            self.assertTrue(portfolio_report_file.exists(), "Portfolio analysis report should be created in current directory")
            self.assertTrue(optimal_weights_file.exists(), "Optimal weights report should be created in current directory")

        finally:
            # Always change back to original directory
            os.chdir(original_cwd)

    def test_generate_base_report_without_optimal_weights(self):
        """Test generate_base_report without optimal weights."""
        # Call the function without optimal_weights
        generate_base_report(
            df=self.sample_df,
            equity_df=self.sample_equity_df,
            cash_value=self.sample_cash_value,
            optimal_weights=None,
            output_dir=self.test_dir
        )

        # Check if portfolio report is created but optimal weights is not
        portfolio_report_file = Path(self.test_dir) / "portfolio_analysis_report.csv"
        optimal_weights_file = Path(self.test_dir) / "optimal_portfolio_weights.csv"

        self.assertTrue(portfolio_report_file.exists(), "Portfolio analysis report should be created")
        self.assertFalse(optimal_weights_file.exists(), "Optimal weights report should not be created when optimal_weights is None")

    def test_portfolio_report_data_accuracy(self):
        """Test the accuracy of data in the generated portfolio report."""
        generate_base_report(
            df=self.sample_df,
            equity_df=self.sample_equity_df,
            cash_value=self.sample_cash_value,
            optimal_weights=self.sample_optimal_weights,
            output_dir=self.test_dir
        )

        # Read the generated report
        portfolio_report_file = Path(self.test_dir) / "portfolio_analysis_report.csv"
        report_df = pd.read_csv(portfolio_report_file)

        # Test AAPL data
        aapl_row = report_df[report_df['Symbol'] == 'AAPL'].iloc[0]
        self.assertEqual(aapl_row['Position'], 100)
        self.assertEqual(aapl_row['Market_Price'], 150.0)
        self.assertEqual(aapl_row['Market_Value'], 15000.0)
        self.assertEqual(aapl_row['Asset_Category'], 'STK')

        # Test CASH data
        cash_row = report_df[report_df['Symbol'] == 'CASH'].iloc[0]
        self.assertEqual(cash_row['Position'], 1)
        self.assertEqual(cash_row['Market_Price'], 10000.0)
        self.assertEqual(cash_row['Market_Value'], 10000.0)
        self.assertEqual(cash_row['Asset_Category'], 'CASH')
        self.assertEqual(cash_row['Unrealized_PnL'], 0)

        # Test total number of rows (3 stocks + 1 cash = 4)
        self.assertEqual(len(report_df), 4, "Should have 4 positions in total")

    def test_weight_calculations(self):
        """Test that weight percentages are calculated correctly."""
        generate_base_report(
            df=self.sample_df,
            equity_df=self.sample_equity_df,
            cash_value=self.sample_cash_value,
            optimal_weights=self.sample_optimal_weights,
            output_dir=self.test_dir
        )

        # Read the generated report
        portfolio_report_file = Path(self.test_dir) / "portfolio_analysis_report.csv"
        report_df = pd.read_csv(portfolio_report_file)

        # Calculate expected total value
        total_market_value = self.sample_df["marketValue"].sum() + self.sample_cash_value
        expected_total = 15000 + 125000 + 22500 + 10000 + 10000  # Note: cash appears twice

        # Check cash weight calculation
        cash_row = report_df[report_df['Symbol'] == 'CASH'].iloc[0]
        expected_cash_weight = (self.sample_cash_value / (self.sample_df["marketValue"].sum() + self.sample_cash_value)) * 100
        self.assertAlmostEqual(cash_row['Weight_Percent'], expected_cash_weight, places=2)

    def test_missing_optional_columns(self):
        """Test generate_base_report with missing optional columns in input data."""
        # Create sample data without some optional columns
        minimal_df = pd.DataFrame({
            'symbol': ['AAPL', 'GOOGL'],
            'description': ['Apple Inc', 'Alphabet Inc'],
            'assetCategory': ['STK', 'STK'],
            'position': [100, 50],
            'markPrice': [150.0, 2500.0],
            'marketValue': [15000.0, 125000.0],
            'percentOfNAV': [10.7, 89.3]
            # Missing costBasisMoney and fifoPnlUnrealized
        })

        minimal_equity_df = minimal_df.copy()

        # Should not raise an exception
        try:
            generate_base_report(
                df=minimal_df,
                equity_df=minimal_equity_df,
                cash_value=0,
                optimal_weights=None,
                output_dir=self.test_dir
            )

            # Check if file was created
            portfolio_report_file = Path(self.test_dir) / "portfolio_analysis_report.csv"
            self.assertTrue(portfolio_report_file.exists())

            # Check that missing columns are handled with default values
            report_df = pd.read_csv(portfolio_report_file)
            aapl_row = report_df[report_df['Symbol'] == 'AAPL'].iloc[0]
            self.assertEqual(aapl_row['Cost_Basis'], 0.0)  # Should default to 0
            self.assertEqual(aapl_row['Unrealized_PnL'], 0.0)  # Should default to 0

        except Exception as e:
            self.fail(f"generate_base_report should handle missing optional columns gracefully, but raised: {e}")

    def test_utf8_encoding(self):
        """Test that the CSV files are saved with UTF-8 encoding."""
        # Create sample data with special characters
        unicode_df = pd.DataFrame({
            'symbol': ['AAPL', '測試'],
            'description': ['Apple Inc', 'Test 測試 Company'],
            'assetCategory': ['STK', 'STK'],
            'position': [100, 50],
            'markPrice': [150.0, 100.0],
            'marketValue': [15000.0, 5000.0],
            'percentOfNAV': [75.0, 25.0]
        })

        unicode_equity_df = unicode_df.copy()

        generate_base_report(
            df=unicode_df,
            equity_df=unicode_equity_df,
            cash_value=0,
            optimal_weights=None,
            output_dir=self.test_dir
        )

        # Read the file and check if special characters are preserved
        portfolio_report_file = Path(self.test_dir) / "portfolio_analysis_report.csv"

        # Try reading with different encodings to verify UTF-8
        try:
            report_df = pd.read_csv(portfolio_report_file, encoding='utf-8-sig')
            test_row = report_df[report_df['Symbol'] == '測試'].iloc[0]
            self.assertEqual(test_row['Description'], 'Test 測試 Company')
        except UnicodeDecodeError:
            self.fail("CSV should be readable with UTF-8 encoding")


def run_tests():
    """Run all tests and return results."""
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestGenerateBaseReport)

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    return result


if __name__ == "__main__":
    print("Running generate_base_report test cases...")
    print("=" * 60)

    # Run the tests
    test_result = run_tests()

    print("\n" + "=" * 60)
    print(f"Tests run: {test_result.testsRun}")
    print(f"Failures: {len(test_result.failures)}")
    print(f"Errors: {len(test_result.errors)}")

    if test_result.failures:
        print("\nFailures:")
        for test, traceback in test_result.failures:
            print(f"- {test}: {traceback}")

    if test_result.errors:
        print("\nErrors:")
        for test, traceback in test_result.errors:
            print(f"- {test}: {traceback}")

    if test_result.wasSuccessful():
        print("\nAll tests passed! ✓")
    else:
        print(f"\nSome tests failed. ✗")

    sys.exit(0 if test_result.wasSuccessful() else 1)
