from copyreg import constructor
import bs4 as bs
import yfinance as yf
import datetime
import requests
import pandas as pd


def fetch_s_and_p_500_list():
    resp = requests.get(
        'http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        tickers.append(ticker)
    tickers = [s.replace('\n', '') for s in tickers]
    return tickers


def fetch_s_and_p_500_information(start_date, end_date):
    tickers = fetch_s_and_p_500_list()
    data = yf.download(tickers, start=start_date, end=end_date)
    df = data.stack().reset_index().rename(index=str, columns={
        "level_1": "Symbol"}).sort_values(['Symbol', 'Date'])
    df.set_index('Date', inplace=True)
    df.to_csv('sp500.csv')


def fetch_one_symbol_information(symbol, start_date, end_date):
    tickers = [symbol]
    data = yf.download(tickers, start=start_date, end=end_date)
    df = pd.DataFrame(data)
    return df


def fetch_multiple_symbols_information(symbols, start_date, end_date):
    tickers = symbols
    data = yf.download(tickers, start=start_date, end=end_date)
    df = data.stack().reset_index().rename(index=str, columns={
        "level_1": "Symbol"}).sort_values(['Symbol', 'Date'])
    df.set_index('Date', inplace=True)
    return df


def calculate_additional_rows(df):
    for i in range(1, len(df)):
        #    print(i)

        if (df.iloc[i]['Symbol'] != df.iloc[i-1]['Symbol']):
            df.loc[i, 'Percent Change'] = 0
            df.loc[i, 'Possible Gain'] = 0
        else:
            #    print(df.iloc[i]['Close'], df.iloc[i-1]['Close'], "this is close")
            df.loc[i, 'Percent Change'] = (
                (df.loc[i, 'Close'] / df.loc[i-1, 'Close'])-1)*100
         #   print(df.iloc[i]['Close'], df.iloc[i-1]['Close'], "this is close")

            df.loc[i, 'Possible Gain'] = (
                (df.loc[i, 'Close'] / df.loc[i, 'Open'])-1)*100

            df.loc[i, 'Magic Gain'] = (
                (df.loc[i, 'High'] / df.loc[i, 'Open'])-1)*100
    return df


# def main():
#     fetch_s_and_p_500_information('2022-03-01', '2022-8-23')
#     df = pd.read_csv('sp500.csv')
#   #  df = fetch_multiple_symbols_information(
#   #      ['GOOGL', "COIN", "MSFT", "AAPL", "META", "NVDA", "SNAP", "WMT", "T", "MCD"], '2011-01-01', '2022-8-13')
#     df.to_csv('coinbase.csv')
#     df = pd.read_csv('coinbase.csv')
#     a = calculate_additional_rows(df)
#     a.to_csv('coinbase_with_additional_rows.csv')
#     print(calculate_mean_magic_gain(
#         df, 'GOOGL'))


# main()


def get_top_gainers(df, n: int):
  #  df = df.sort_values(by=['Percent Change'], ascending=False)
    df = df.sort_values(by=['Possible Gain'], ascending=False)
    print(df.head(n))
    return df.head(n)


def get_top_losers(df, n: int):
    df = df.sort_values(by=['Percent Change'], ascending=True)
  #  df = df.sort_values(by=['Possible Gain'], ascending=True)
    return df.head(n)


def filter_by_date(df, date):
    return df[(df['Date'] == date)]


def filter_by_date_and_symbol(df, date, symbols):
    a = df[(df['Date'] == date)]
    b = a[a['Symbol'].isin(symbols)]
    return b


# In this strategy, we will buy the stocks that are the top gainers in the past day.
# We imaagine that we are magician and we can predict the future. We sell the stock at the daily high price.
def buy_at_open_sell_at_high_yesterday_top_gainers(df):
    result = []
    date = datetime.datetime(2007, 6, 15)
    while (date < datetime.datetime(2008, 6, 15)):
        yesterday = date-datetime.timedelta(days=1)
        yesterday_daily_data = (filter_by_date(
            df, yesterday.strftime('%Y-%m-%d')))
        today_daily_data = (filter_by_date(df, date.strftime('%Y-%m-%d')))
        if (len(yesterday_daily_data) == 0 or len(today_daily_data) == 0):
            date = date+datetime.timedelta(days=1)
            continue
        top_gainers = list(
            (get_top_gainers(yesterday_daily_data, 5))["Symbol"])
        today_result_of_yesterday_top_gainers = filter_by_date_and_symbol(
            df, date.strftime('%Y-%m-%d'), top_gainers)
        print((today_result_of_yesterday_top_gainers))
        print(date)
        date = date+datetime.timedelta(days=1)


# this one is the real strategy. It buys the stocks that are the top gainers in the past day.
# It sells the same day at target price or at daily close price.
def buy_at_open_sell_after_determined_gain_or_at_close(df, target_gain, n):
    result = []
    date = datetime.datetime(2022, 1, 1)
    while (date < datetime.datetime(2023, 1, 1)):
        yesterday = date-datetime.timedelta(days=1)
        yesterday_daily_data = (filter_by_date(
            df, yesterday.strftime('%Y-%m-%d')))
        today_daily_data = (filter_by_date(df, date.strftime('%Y-%m-%d')))
        if (len(yesterday_daily_data) == 0 or len(today_daily_data) == 0):
            date = date+datetime.timedelta(days=1)
            continue
        top_gainers = list(
            (get_top_losers(yesterday_daily_data, n))["Symbol"])
        today_result_of_yesterday_top_gainers = filter_by_date_and_symbol(
            df, date.strftime('%Y-%m-%d'), top_gainers)
        print((today_result_of_yesterday_top_gainers))
        gain = 0
        for i in range(0, len(today_result_of_yesterday_top_gainers)):
            if (today_result_of_yesterday_top_gainers.iloc[i]['Magic Gain'] > target_gain):
                gain = gain+target_gain
            else:
                gain = gain + \
                    today_result_of_yesterday_top_gainers.iloc[i]['Possible Gain']
        result.append(gain/len(today_result_of_yesterday_top_gainers))
        print(result[-1])
        date = date+datetime.timedelta(days=1)

    return result


def calculate_mean_magic_gain(df, symbol):
    return df[df['Symbol'] == symbol]['Magic Gain'].mean()


def calculate_mean_possible_gain(df, symbol):
    return df[df['Symbol'] == symbol]['Possible Gain'].mean()


#df = pd.read_csv('sp500.csv')
#df = df[df["Date"] == "2022-08-17"]
#print(get_top_losers(df, 5))

# df = df[df['Date'] > '2022-06-14']
# df = df[df['Date'] > '2019-01-01']
# result = (buy_at_open_sell_after_determined_gain_or_at_close(df, 1000, 3))
# print(len(result), sum(result), sum(result)/len(result))


# print(get_top_gainers(df, 100))

# a = calculate_mean_possible_gain(df, 'AAPL')
# print(a)


# date = ((datetime.datetime(2022, 8, 12)))
# print(date.strftime('%Y-%m-%d'))
# daily_data = (filter_by_date(df, date.strftime('%Y-%m-%d')))
# top_gainers = ((get_top_gainers(daily_data, 5)))
# print(top_gainers)
# top_gainers = list(top_gainers["Symbol"])

# tommorow = date+datetime.timedelta(days=1)
# print(filter_by_date(df, tommorow.strftime(
#     '%Y-%m-%d'))["Possible Gain"].mean())
# print(filter_by_date(df, tommorow.strftime(
#     '%Y-%m-%d'))["Percent Change"].mean())

# print(filter_by_date_and_symbol(
#     df, tommorow.strftime(
#         '%Y-%m-%d'), top_gainers)["Possible Gain"].mean())


# buy_at_open_sell_at_high_yesterday_top_gainers(df)
# print(df["Magic Gain"].mean())
# print(calculate_mean_magic_gain(df, 'AAPL'))

ticker = "LABU"
data = fetch_one_symbol_information(ticker, "2021-01-01", "2022-09-18")
df = pd.DataFrame(data)
print(df)
df.to_csv(ticker+".csv")

