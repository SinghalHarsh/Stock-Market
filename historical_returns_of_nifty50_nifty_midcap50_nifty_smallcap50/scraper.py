import pandas as pd
import numpy as np

import math

import time
from datetime import datetime, timedelta, date

import urllib
import requests

import io

# to ignore SSL certificate errors
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ---- REQUEST WRAPPER ---- #

## wrapper around request package to make it resilient
def request_wrapper(url):
    response = requests.get(url,
                            verify=False,
                            headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko)'}
                           )
    return response

# ---- NSE INDEX COMPANIES DETAILS ---- #

## https://www.nseindia.com/market-data/live-market-indices (index name)
def nse_index_stocks_list(index_name):
    
    ## processing index name
    index_processed_name = urllib.parse.quote_plus(index_name)
    
    ##
    path = "https://www.nseindia.com/api/equity-stockIndices?csv=true&index={}"
    
    ## scraper
    response = request_wrapper(path.format(index_processed_name)).content

    ## converting into df
    data = pd.read_csv(io.StringIO(response.decode('utf-8')))
    
    ## processing column names
    data.columns = [col_.replace("\n", '').strip() for col_ in data.columns]
    
    ##
    data = data[data['SYMBOL'] != index_name]
    
    return data

# ---- YAHOO FINANCE ---- #

def yahoo_finance_scraper(symbol, start_date=datetime(2000, 1, 1).date(), end_date=datetime.today().date()):
    """
    Parameters:
    a. symbol
    b. start_date
    c. end_date
    """
    data = None
    
    ## processing symbol name
    processsed_symbol = urllib.parse.quote_plus(symbol)
    
    ## scraper
    path = "https://query1.finance.yahoo.com/v7/finance/download/{}?period1={}&period2={}&interval=1d&events=history"
    period1, period2 = int(time.mktime(start_date.timetuple())), int(time.mktime((end_date+timedelta(1)).timetuple()))
    path = path.format(processsed_symbol, period1, period2)
    
    response = request_wrapper(path).content
    
    ## converting into df
    data = pd.read_csv(io.StringIO(response.decode('utf-8')))
        
    ## preprocessing column names
    data.columns = [col.lower().replace(' ', '_') for col in data.columns]

    ## date
    data['date'] = data['date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d').date())
    
    ## creating symbol column
    data['symbol'] = symbol.split('.')[0]

    return data

