from copyreg import constructor
from operator import le
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


def fetch_nasdaq_list():
    url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"
    df = pd.read_csv(url, sep="|")
    return list(df['Symbol'])


def download_one_day_data(tickers, start_date, end_date, interval='15m'):
    data = yf.download(tickers=tickers, start=start_date,
                       end=end_date, interval=interval)
    df = pd.DataFrame(data)
    if (len(df) > 0):
        df.to_csv("./pacb/"+start_date+'.csv')


def download_last_n_days_data(tickers, n: int, interval='15m', ):
    today = datetime.date.today()
    for i in range(len(tickers)):
        if (type(tickers[i]) != str):
            del (tickers[i])
    print(len(tickers))
    for i in range(1, n):
        download_one_day_data(tickers[0:1], (today - datetime.timedelta(days=i)).strftime('%Y-%m-%d'),
                              (today - datetime.timedelta(days=i-1)).strftime('%Y-%m-%d'), interval)


#tickers = fetch_nasdaq_list()
# print(len(tickers))
#new_list = [lis for lis in tickers if type(lis) == str]
#tickers = new_list
# print(len(tickers))

def stop_limit_by_sell_at_determined_price_or_end_of_day(data, stop_by_percentage, limit_sell_percentage):
    result = 0
    count = 0
    for i in range(len(data)):

        sell_price = 0
        max_gain = ((data.iloc[i]["High"]-data.iloc[i]["Open"])
                    / data.iloc[i]["Open"])*100
        if (max_gain > stop_by_percentage):
            count += 1

            buy_price = data.iloc[i]["Open"]*(1+stop_by_percentage/100)
            target_sell_price = data.iloc[i]["Open"] * \
                (1+limit_sell_percentage/100)
            if (data.iloc[i]["High"] > target_sell_price):
                sell_price = target_sell_price
            else:
                sell_price = data.iloc[i]["Close"]
            gain = ((sell_price-buy_price)/buy_price)*100
            result = result + gain

            print(i, sell_price, buy_price, data.iloc[i]["Date"], gain, result)
         #   sell_price = data.iloc[i]["Close"]
          #  result += (sell_price-buy_price)/buy_price*100
          #  print(result)

      #      print(max_gain-stop_by_percentage)
      #      result += (max_gain-stop_by_percentage)
    print(result, count)
    return result


# tickers = ["PACB"]
# download_last_n_days_data(tickers, 60, '5m')
data = pd.read_csv('./PACB.csv')

a = stop_limit_by_sell_at_determined_price_or_end_of_day(data, 3, 40)

print(a)
