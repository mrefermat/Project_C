import quandl
import pandas as pd
import numpy as np
from marketdata import *
from model import *
from trading import *
from utils import *
from datetime import datetime
from arctic import Arctic

store = Arctic('localhost')
static_table = store['CHINA_STATIC']
token="Us3wFmXGgAj_1cUtHAAR"

# Load data from quandl
update_data()

# Load data
FundAUM=get_FUM()
mkts=get_market_list()
curr_px=get_most_liquid_price(mkts)
df=pd.DataFrame()
for m in mkts:
    try:
        df[m]=get_timeseries(m)
    except:
        print m
df=df.fillna(0)

# Run signals
pos=tsmom_daily(df[mkts],10)
pnl_short=calc_pnl_wc(pos,df[mkts])
pos=tsmom_daily(df[mkts],80)
pnl_long=calc_pnl_wc(pos,df[mkts])
combined_pnl=(pnl_short*.5+pnl_long*.5)
scaling_factor=calc_scaling_factor(combined_pnl)
s_short=tsmom_daily_signal(df,10)
s_long=tsmom_daily_signal(df,80)
s_combined = (s_short*.5+s_long*.5)
lots=calc_position(s_combined,FundAUM,scaling_factor,curr_px)

msg=generate_trades(lots,curr_px)
msg=msg+'\n============SWITCH=================='
msg=msg+switch_contracts(lots)

send_email('mark.refermat@gmail.com,chen.wen@outlook.com','Trades for today',msg)