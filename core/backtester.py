def backtest(df, strategy_func, window=5):
    signals = []
    for i in range(50, len(df) - window):
        subset = df.iloc[:i+1]
        signal = strategy_func(subset)
        if signal == "BUY":
            entry = df.iloc[i].Close
            exit_ = df.iloc[i+window].Close
            profit = (exit_ - entry) / entry * 100
            signals.append(profit)
    win_rate = sum(1 for p in signals if p > 0) / len(signals) * 100 if signals else 0
    return win_rate, signals
