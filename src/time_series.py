from copyreg import constructor
import bs4 as bs
import yfinance as yf
import datetime
import requests
import pandas as pd


def buy_after_n_down_days(df, n):
    result = []
    count = 0
    for i in range(0, len(df)):
        if (count >= n):
            result.append(df.iloc[i]['Possible Gain'])
        if (df.iloc[i]['Percent Change'] < 0):
            count += 1
        else:
            count = 0
    return result, sum(result), len(result)


def stocks_are_down_for_n_days(df, n, date):
    down_stocks = []
    symbols = df.Symbol.unique().tolist()
    for symbol in symbols:
        df_symbol = df[df['Symbol'] == symbol]
        df_symbol = df_symbol[df_symbol["Date"] <= date]
        df_symbol = df_symbol.tail(n)
        is_down = True
        for i in range(0, len(df_symbol)):
            if (df_symbol.iloc[i]['Percent Change'] > 0):
                is_down = False

        if (is_down):
            down_stocks.append(symbol)
    return down_stocks


df = pd.read_csv('coinbase_with_additional_rows.csv')
# df = df[df["Symbol"] == "GOOGL"]
# df = df[df["Date"] <= "2018-01-01"]
# df = df[df["Date"] >= "2017-01-01"]
# print(df["Possible Gain"].sum())
# print(buy_after_n_down_days(df, 3))

date = "2022-08-23"
a = (stocks_are_down_for_n_days(df, 8, date))
print(a)
b = df[df["Date"] == date]
c = b[b["Symbol"].isin(a)]
print(c)
# print(df[df["Date"] == "2022-08-15"]["Percent Change"].mean())
# c.to_csv('two_fails.csv')

# df = df[df["Symbol"].isin(a)]
# print(df[df["Date"] == "2022-07-27"]["Possible Gain"].mean())
# print(df[df["Date"] == "2022-07-27"]["Percent Change"].mean())
