import pandas as pd
import yfinance as yf
url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"
df = pd.read_csv(url, sep="|")
print(df.head())
print(df['Symbol'].head())
print(len(df['Symbol']))
print(df['Symbol'][0])
print(len(df))


def lookup_fn(df, key_row, key_col):
    try:
        return df.iloc[key_row][key_col]
    except IndexError:
        return 0


movementlist = []
for stock in df['Symbol']:
    # get history
    thestock = yf.Ticker(stock)
    hist = thestock.history(period="5d")
    # print(stock)
    low = float(10000)
    high = float(0)
    # print(thestock.info)
    for day in hist.itertuples(index=True, name='Pandas'):
        if day.Low < low:
            low = day.Low
        if high < day.High:
            high = day.High

    deltapercent = 100 * (high - low)/low
    Open = lookup_fn(hist, 0, "Open")
    # some error handling:
    if len(hist >= 5):
        Close = lookup_fn(hist, 4, "Close")
    else:
        Close = Open
    if (Open == 0):
        deltaprice = 0
    else:
        deltaprice = 100 * (Close - Open) / Open
    print(stock+" "+str(deltapercent) + " " + str(deltaprice))
    pair = [stock, deltapercent, deltaprice]
    movementlist.append(pair)

for entry in movementlist:
    if entry[1] > float(100):
        print(entry)
