import pandas as pd
import numpy as np

import math
from datetime import date

from datetime import datetime

import requests

# to ignore SSL certificate errors
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# wrapper around request package to make it resilient
def request_wrapper(url):
    response = requests.get(url,
                            verify=False,
                            headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko)'}
                           )
    return response

    
# RETURN
def absolute_return(start, end):
    return round(100*(end-start)/start, 1)

def annualized_return(opening_value, closing_value, year):
    return round(100*(math.pow(closing_value/opening_value, 1/year) - 1), 1)
    

# READING
sites = ["yahoo", "investing", "niftyindices"]
## date column, close price column, date format
site_parameters = {"yahoo":["Date", "Adj Close", "%Y-%m-%d"],
                   "investing":["Date", "Price", "%b %d, %Y"],
                   "niftyindices":["Date", "Close", "%d %b %Y"]}
def reading_data(name):
    for site in sites:
        try:
            index_df = pd.read_csv('../data/{}/{}.csv'.format(site, name), thousands=',')
            date_col, close_col, date_format = site_parameters[site]
            break
        except:
            pass
    
    ## selecting main columns
    index_df = index_df[[date_col, close_col]]
    
    ## renaming
    index_df.rename(columns={close_col:name+"_close", date_col:"date"}, inplace=True)
    
    ## date -> str to date
    index_df["date"] = index_df["date"].apply(lambda x: datetime.strptime(x, date_format).date())
    
    ## sorting data
    index_df = index_df.sort_values('date', ascending=True, ignore_index=True)
    
    ## dropping null values
    index_df = index_df[~index_df[name+"_close"].isnull()]
    
    ## previous close
    index_df[name+"_prev_close"] = index_df[name+"_close"].shift(1)
    
    ## daily return
    index_df[name+"_daily_return"] = index_df.apply(lambda x: return_(x[name+'_prev_close'], x[name+"_close"]), axis=1)
    
    ## date filter -> last decade
    index_df = index_df[(index_df["date"] >= datetime(2010, 1, 1).date()) & (index_df["date"] <= datetime(2019, 12, 31).date())]
    
    ## returns since 1st January, 2010
    index_df[name+"_returns"] = index_df[name+"_close"].apply(lambda x: return_(index_df.iloc[0][name+"_close"], x))
    return index_df[["date", name+"_close", name+"_daily_return", name+"_returns"]]

## PLOTTING
def plot_chart(title='', title_size=40,
               ylabel='', ylabel_size=10, yticks_size=10, yticks_rotation=0,
               xlabel='', xlabel_size=10, xticks_size=10, xticks_rotation=0, xticks_labels=None,
               legend=False, legend_size=15, legend_loc='best', legend_ncol=1):
    
    plt.title(title, fontsize=title_size, weight='bold')
    
    plt.xlabel(xlabel, fontsize=xlabel_size, weight='bold')
    if (xticks_labels):
        plt.xticks(xticks_labels, fontsize=xticks_size, rotation=xticks_rotation)   
    else:
        plt.xticks(fontsize=xticks_size, rotation=xticks_rotation)
    
    plt.ylabel(ylabel, fontsize=ylabel_size, weight='bold')
    plt.yticks(fontsize=yticks_size, rotation=yticks_rotation)
    
    if (legend):
        plt.legend(prop={'size': legend_size}, loc=legend_loc, ncol=legend_ncol)
    plt.show()
    
def nifty_color(row):
    if row.Index =="Nifty50":
        return ['background-color: yellow'] * len(row)
    return ['color: black'] * len(row)

#
def addYears(d, years):
    try:
        return d.replace(year = d.year + years)
    except ValueError:
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))