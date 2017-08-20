import quandl
import pandas as pd
import numpy as np
from marketdata import *
from datetime import datetime
from arctic import Arctic

store = Arctic('localhost')
static_table = store['CHINA_STATIC']
token="Us3wFmXGgAj_1cUtHAAR"

# Load data from quandl
update_data()

# Run signals
FundAUM=1e9
mkts=get_market_list()
df=pd.DataFrame()
for m in mkts:
    try:
        df[m]=get_timeseries(m)
    except:
        print m

lots=calc_positions_two_lookbacks(10,80,mkts,df,FundAUM).dropna(how='all')
lots.ix[lots.index[-1]].plot(kind='bar',title='Current Positions')






