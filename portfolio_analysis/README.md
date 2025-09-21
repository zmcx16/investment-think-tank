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

2. **Gemini CLI**: Install Google's Gemini CLI tool
   ```bash
   npm install -g @google-cloud/gemini-cli
   ```

3. **Portfolio Data**: Interactive Brokers Flex Query XML file (see [Data Sources](#data-sources))

### Basic Usage

#### Option 1: Interactive Mode (Recommended)
```bash
# Run with defaults
interactive.bat

# Custom parameters: source_file output_dir model
interactive.bat "my_portfolio.xml" "my_results" "gemini-1.5-pro"
```

#### Option 2: Direct Execution
```bash
# Basic analysis with AI insights
python main.py

# Custom source and output
python main.py --source "path/to/portfolio.xml" --output "path/to/results"

# Skip AI analysis (faster)
python main.py --skip-gemini

# Use different AI model
python main.py --model "gemini-1.5-pro"
```

## Output Structure

```
output/
├── summary_report.md           # AI-generated investment analysis
└── base_report/
    ├── portfolio_analysis_report.csv    # Detailed position data
    └── optimal_portfolio_weights.csv    # Monte Carlo optimization results
```

## Data Sources

### Interactive Brokers Setup

1. **Generate Flex Query**:
   - Log into Interactive Brokers Client Portal
   - Navigate to Reports > Flex Queries
   - Create new query with these sections:
     - Open Positions
     - Equity Summary

2. **Download Data**:
   - Run the query to generate XML report
   - Download and save as `.xml` file

3. **Sample Data**:
   - Use `data/interactivebrokers/source/sample.anonymized.xml` for testing

## Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--source` | `-s` | Portfolio data file path | `data/interactivebrokers/source/sample.anonymized.xml` |
| `--output` | `-o` | Output directory | `output` |
| `--prompt-file` | `-p` | Custom AI prompt file | `default_prompt.txt` |
| `--model` | `-m` | Gemini model to use | `gemini-2.5-flash` |
| `--skip-gemini` | | Skip AI analysis | False |

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

### Supported Models
- `gemini-2.5-flash` (default, fastest)
- `gemini-1.5-pro` (more detailed analysis)
- `gemini-1.5-pro-latest` (latest version)

## Examples

### Example 1: Quick Analysis
```bash
# Analyze default sample data
python main.py
```

### Example 2: Custom Portfolio
```bash
# Analyze your IB export
python main.py --source "my_ib_export.xml" --output "my_analysis"
```

### Example 3: Advanced Configuration
```bash
# Custom analysis with specific model
python main.py \
  --source "portfolio.xml" \
  --output "results" \
  --model "gemini-1.5-pro" \
  --prompt-file "custom_prompt.txt"
```

### Example 4: Interactive Mode
```bash
# Two-step interactive analysis
interactive.bat "portfolio.xml" "results" "gemini-1.5-pro"
```

## Sample Output

### Portfolio Analysis Report (CSV)
| Symbol | Description | Asset_Category | Position | Market_Price | Market_Value | Weight_Percent |
|--------|-------------|----------------|----------|--------------|--------------|----------------|
| AAPL | Apple Inc | STK | 100 | 150.00 | 15000.00 | 25.5 |
| GOOGL | Alphabet Inc | STK | 50 | 2500.00 | 125000.00 | 42.8 |

### AI Analysis Sample
```markdown
# Portfolio Analysis Report

## Executive Summary
Your portfolio shows strong concentration in technology stocks with 68.3% allocation...

## Risk Assessment
- **Concentration Risk**: High - Top 3 holdings represent 75% of portfolio
- **Sector Risk**: Technology overweight at 68%
- **Recommendations**: Consider diversification into other sectors

## Optimization Suggestions
Based on Monte Carlo analysis, optimal allocation would be:
- AAPL: 30% (current: 25.5%)
- GOOGL: 40% (current: 42.8%)
- Add emerging markets exposure: 15%
```

## Troubleshooting

### Common Issues

1. **NumPy Version Conflicts**
   ```bash
   pip install "numpy<2"
   ```

2. **Gemini CLI Not Found**
   ```bash
   npm install -g @google-cloud/gemini-cli
   # Ensure PATH includes npm global bin directory
   ```

3. **XML Parsing Errors**
   - Verify XML file is valid IB Flex Query export
   - Check file encoding (should be UTF-8)

4. **Yahoo Finance Data Issues**
   - Check internet connection
   - Verify ticker symbols are valid
   - Some international symbols may not be available

### Debug Mode
Enable detailed logging:
```bash
python main.py --debug
# Check portfolio_analysis.log for detailed information
```

## Development

### Project Structure
```
portfolio_analysis/
├── main.py                    # Main application
├── interactive.bat           # Interactive batch script
├── default_prompt.txt        # Default AI prompt
├── test_generate_base_report.py  # Unit tests
├── data/
│   └── interactivebrokers/
│       └── source/
│           └── sample.anonymized.xml
└── output/                   # Generated reports
```

### Running Tests
```bash
python test_generate_base_report.py
```

### Contributing
1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## License

See LICENSE file in the root directory.

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review log files in `portfolio_analysis.log`
3. Create issue in GitHub repository

---

*Last updated: September 2025*
