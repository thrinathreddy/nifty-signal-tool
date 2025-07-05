from strategies import (
    rsi_macd_basic,
    ema_crossover,
    bollinger_band_breakout,
    stochastic_rsi,
    supertrend,
    adx_rsi,
    sma_ema_cross,
    rsi_ema_confluence,
    macd_histogram,
    atr_breakout,
)

STRATEGY_MAP = {
    "RSI + MACD": rsi_macd_basic,
    "EMA Crossover": ema_crossover,
    "Bollinger Band Breakout": bollinger_band_breakout,
    "Stochastic RSI": stochastic_rsi,
    "Supertrend": supertrend,
    "ADX + RSI": adx_rsi,
    "SMA + EMA Cross": sma_ema_cross,
    "RSI + EMA Confluence": rsi_ema_confluence,
    "MACD Histogram Surge": macd_histogram,
    "ATR Breakout": atr_breakout,
}