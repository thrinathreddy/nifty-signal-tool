import yfinance as yf
import time

def get_fundamentals(symbol):
    try:
        stock = yf.Ticker(symbol+".NS")
        fin = stock.info

        # Print keys only once to explore available fields
        # print(f"\n{symbol} info keys:\n", fin.keys())

        roe = fin.get('returnOnEquity') or 0
        de = fin.get('debtToEquity') or 0
        eps = fin.get('trailingEps') or 0
        pe = fin.get('trailingPE') or 0
        profit_margin = fin.get('profitMargins') or 0
        current_ratio = fin.get('currentRatio') or 0
        peg = fin.get('pegRatio') or 0

        return {
            'symbol': symbol,
            'roe': roe,
            'de': de,
            'eps': eps,
            'pe': pe,
            'profit_margin': profit_margin,
            'current_ratio': current_ratio,
            'peg': peg
        }

    except Exception as e:
        print(f"[❌] fundamental error for {symbol}: {e}")
        return {
            'symbol': symbol,
            'roe': 0,
            'de': 0,
            'eps': 0,
            'pe': 0,
            'profit_margin': 0,
            'current_ratio': 0,
            'peg': 0
        }


def evaluate_fundamentals(data):
    roe = data['roe']
    de = data['de']
    eps = data['eps']
    pe = data['pe']
    profit_margin = data['profit_margin']
    current_ratio = data['current_ratio']
    peg = data['peg']

    # Defensive check: missing data
    if any(v == 0 for v in [roe, de, eps, pe, profit_margin, current_ratio]):
        return "HOLD"

    # 🔥 Strong fundamentals
    if (
            roe > 0.18 and
            de < 1.5 and
            eps > 1 and
            5 < pe < 25 and
            profit_margin > 0.1 and
            current_ratio > 1.5 > peg
    ):
        return "LONG_TERM_BUY"

    # ⚖️ Decent fundamentals
    if (
        0.12 < roe <= 0.18 and
        1.5 <= de <= 2.5 and
        0.5 < eps <= 1 and
        10 < pe <= 30 and
        profit_margin > 0.05 and
        current_ratio > 1.2
    ):
        return "HOLD"

    return "HOLD"
