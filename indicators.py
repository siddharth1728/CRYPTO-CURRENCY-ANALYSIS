import pandas as pd

def add_moving_average(df, window=7):

    df["MA_7"] = (
        df["price"]
        .rolling(window=window)
        .mean()
    )

    return df


def add_rsi(df, period=14):

    delta = df["price"].diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss

    df["RSI"] = 100 - (100 / (1 + rs))

    return df