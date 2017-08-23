import pandas as pd
from marketdata import *
from analytics import *
import math

def tsmom_daily(data,signal_lookback,vol_lookback=20):
	mul=get_contract_multipliers()[data.columns]
	vol=pd.ewmstd(data,vol_lookback,min_periods=vol_lookback)*math.sqrt(256)
	signal=pd.rolling_mean(data,signal_lookback)
	signal = signal /abs(signal)
	position=(signal / (vol *mul))
	return position.shift(1)

# Calculate in position space 
def tsmom_daily_signal(data,signal_lookback,vol_lookback=20):
    vol=pd.ewmstd(data,vol_lookback,min_periods=vol_lookback)*math.sqrt(256)
    signal=pd.rolling_mean(data,signal_lookback)
    signal = signal /abs(signal)
    return (signal / (vol)).shift(1)

# TODO: Further test this out to ensure the vol targeting hits the appropriate
#  level and to ensure the lookback for z-scoring is correct as well
def ewma_mom_daily(data,short_lookback,long_lookback,vol_lookback=20):
	mkts=data.columns
	mul=get_contract_multipliers()[mkts]
	vol=pd.ewmstd(data,vol_lookback,min_periods=vol_lookback)*math.sqrt(256)
	signal=signal=pd.ewma(data,short_lookback)-pd.ewma(data,long_lookback)
	# Rolling z secore using longer lookback
	zscore= calc_zscore(signal,long_lookback)
	position=(zscore / (vol*mul))
	return position.shift(1)

# TODO: Further test this out to ensure the vol targeting hits the appropriate
#  level and to ensure the lookback for z-scoring is correct as well
def ewma_mom_daily_signal(data,short_lookback,long_lookback,vol_lookback=20):
	vol=pd.ewmstd(data,vol_lookback,min_periods=vol_lookback)*math.sqrt(256)
	signal=signal=pd.ewma(data,short_lookback)-pd.ewma(data,long_lookback)
	# Rolling z secore using longer lookback
	zscore= calc_zscore(signal,long_lookback)
	position=(zscore / (vol))
	return position.shift(1)

# TODO: Think about winsorising the tails
def calc_zscore(signal,lookback):
    return (signal/pd.ewmstd(signal,lookback,min_periods=lookback*2))

# Equal weight of two lookbacks. Internal method for faster execution
# since get current prices take a while to run
def _get_positions_two_lookbacks(sh,lg,mkts,df,FundAUM,curr_px):
    pos=tsmom_daily(df[mkts],sh)
    pnl_short=calc_pnl_wc(pos,df[mkts])
    pos=tsmom_daily(df[mkts],lg)
    pnl_long=calc_pnl_wc(pos,df[mkts])
    combined_pnl=(pnl_short*.5+pnl_long*.5)
    scaling_factor=calc_scaling_factor(combined_pnl)
    s_short=tsmom_daily_signal(df,sh)
    s_long=tsmom_daily_signal(df,lg)
    s_combined = (s_short*.5+s_long*.5)
    return calc_position(s_combined,FundAUM,scaling_factor,curr_px)
    
def calc_positions_two_lookbacks(sh,lg,mkts,df,FundAUM):
    curr_px=get_most_liquid_price(mkts)
    return _get_positions_two_lookbacks(sh,lg,mkts,df,FundAUM,curr_px)
