import pandas as pd
import xml.etree.ElementTree as ET
import json
import os


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


def save_portfolio_data_to_json(df, equity_df, cash_value, output_file="portfolio_data.json"):
    """Save portfolio data (df, equity_df, cash_value) to JSON file"""
    data = {
        "df": df.to_dict(orient='records'),
        "equity_df": equity_df.to_dict(orient='records'),
        "cash_value": cash_value
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Portfolio data saved to {output_file}")


def load_portfolio_data_from_json(input_file="portfolio_data.json"):
    """Load portfolio data from JSON file and return df, equity_df, cash_value"""
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"JSON file {input_file} not found")

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    df = pd.DataFrame(data["df"])
    equity_df = pd.DataFrame(data["equity_df"])
    cash_value = data["cash_value"]

    # Convert numeric columns back to proper types
    numeric_cols = ["position", "markPrice", "costBasisPrice", "positionValue", "percentOfNAV", "marketValue"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        if col in equity_df.columns:
            equity_df[col] = pd.to_numeric(equity_df[col], errors="coerce")

    print(f"Portfolio data loaded from {input_file}")
    return df, equity_df, cash_value


# Example usage:
if __name__ == "__main__":
    with open("sample.anonymized.xml", "r") as f:
        xml_file = "sample.anonymized.xml"

    if os.path.exists(xml_file):
        df, equity_df, cash_value = parse_ib_xml(xml_file)
        save_portfolio_data_to_json(df, equity_df, cash_value)
