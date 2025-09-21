import xml.etree.ElementTree as ET
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


def quant(x, places=2):
    return str(Decimal(x).quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP))


def main():
    # Use a path relative to this script's location so the script is portable across machines
    base = (Path(__file__).resolve().parent.parent / "portfolio" / "data" / "interactivebrokers" / "sample.anonymized.xml").resolve()
    tree = ET.parse(base)
    root = tree.getroot()

    NAV = Decimal('10000')

    # Collect open positions
    positions = root.findall('.//OpenPosition')

    # Strategy: assign ~85% of NAV to equities/funds (STK/ADR/REIT), spread equally across them.
    # Assign ~15% of NAV to options (positionValue small, keep side Short -> negative values)
    equity_positions = [p for p in positions if p.get('assetCategory') in ('STK','ADR','REIT')]
    option_positions = [p for p in positions if p.get('assetCategory') == 'OPT']

    equity_nav = NAV * Decimal('0.85')
    option_nav = NAV - equity_nav

    # Equal-dollar equities
    if equity_positions:
        per_eq = (equity_nav / Decimal(len(equity_positions))).quantize(Decimal('0.01'))
    else:
        per_eq = Decimal('0')

    # For options, give each a small notional (absolute) so they total option_nav
    if option_positions:
        per_opt = (option_nav / Decimal(len(option_positions))).quantize(Decimal('0.01'))
    else:
        per_opt = Decimal('0')

    # Update equities
    for p in equity_positions:
        mark = Decimal(p.get('markPrice') or '0')
        # compute synthetic position size: round to whole shares
        if mark > 0:
            qty = (per_eq / mark).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
            if qty == 0:
                qty = Decimal('1')
        else:
            qty = Decimal('1')

        positionValue = (qty * mark).quantize(Decimal('0.01'))
        costBasisPrice = Decimal(p.get('costBasisPrice') or '0')
        if costBasisPrice == 0:
            costBasisPrice = mark
        costBasisMoney = (qty * costBasisPrice).quantize(Decimal('0.01'))

        p.set('position', str(int(qty)))
        p.set('positionValue', quant(positionValue))
        p.set('costBasisMoney', quant(costBasisMoney))
        # percentOfNAV = positionValue / NAV
        pct = (positionValue / NAV * 100).quantize(Decimal('0.01'))
        p.set('percentOfNAV', str(pct))
        # unrealized pnl: positionValue - costBasisMoney
        fifo = (positionValue - costBasisMoney).quantize(Decimal('0.01'))
        p.set('fifoPnlUnrealized', quant(fifo))

    # Update options: keep side and small notionals; for Shorts, position is negative
    for p in option_positions:
        mark = Decimal(p.get('markPrice') or '0')
        multiplier = Decimal(p.get('multiplier') or '100')
        # per option notional is per_opt; compute contracts (can be fractional -> round to 1)
        if mark > 0:
            contracts = (per_opt / (mark * multiplier)).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
            if contracts == 0:
                contracts = Decimal('1')
        else:
            contracts = Decimal('1')

        positionValue = (contracts * mark * multiplier).quantize(Decimal('0.01'))
        # For short options, represent position as negative contracts
        side = p.get('side') or 'Long'
        if side.lower() == 'short':
            p.set('position', str(-int(contracts)))
            positionValue = -positionValue
        else:
            p.set('position', str(int(contracts)))

        # set fields
        p.set('positionValue', quant(positionValue, 2))
        costBasisPrice = Decimal(p.get('costBasisPrice') or '0')
        if costBasisPrice == 0:
            costBasisPrice = Decimal(p.get('openPrice') or '0')
            if costBasisPrice == 0 and mark != 0:
                costBasisPrice = mark

        costBasisMoney = (abs(contracts) * costBasisPrice * multiplier).quantize(Decimal('0.01'))
        # If positionValue negative (short), keep costBasisMoney positive
        p.set('costBasisMoney', quant(costBasisMoney))
        pct = (Decimal(abs(positionValue)) / NAV * 100).quantize(Decimal('0.01'))
        p.set('percentOfNAV', str(pct))
        fifo = (Decimal(positionValue) - Decimal(costBasisMoney)).quantize(Decimal('0.01'))
        p.set('fifoPnlUnrealized', quant(fifo))

    # Update EquitySummary totals: compute totals from positions
    total_pos_value = Decimal('0')
    for p in positions:
        pv = Decimal(p.get('positionValue') or '0')
        total_pos_value += pv

    # Find EquitySummaryByReportDateInBase nodes and set summary fields
    summaries = root.findall('.//EquitySummaryByReportDateInBase')
    # We'll set 'total' and 'stock' to match computed totals; set cash small positive
    cash_val = (NAV - total_pos_value).quantize(Decimal('0.01'))
    for s in summaries:
        s.set('cash', quant(cash_val))
        s.set('stock', quant(total_pos_value))
        s.set('total', quant(total_pos_value + cash_val))
        # other long/short breakdowns set to 0 or same as stock
        s.set('totalLong', quant(total_pos_value))
        s.set('totalShort', '0')

    # write back
    tree.write(base, encoding='utf-8', xml_declaration=False)
    print(f"Wrote anonymized sample with NAV={NAV} and total positions={total_pos_value}")


if __name__ == '__main__':
    main()
