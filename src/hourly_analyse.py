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


def fetch_nasdaq_list():
    url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"
    df = pd.read_csv(url, sep="|")
    return list(df['Symbol'])


df = pd.read_csv('./nasdaq/2022-08-11.csv', header=[0, 1])
tickers = fetch_nasdaq_list()
new_list = [lis for lis in tickers if type(lis) == str]
tickers = new_list[0:2000]
dic = []
for ticker in tickers:
    a = [100*(df.iloc[7]["Open"][ticker] - df.iloc[0]["Open"]
              [ticker])/df.iloc[0]["Open"][ticker], ticker, 100*(df.iloc[25]["Open"][ticker] - df.iloc[7]["Open"]
                                                                 [ticker])/df.iloc[7]["Open"][ticker]]
    dic.append(a)

e = sorted(dic, key=lambda x: x[0])
print(e)
