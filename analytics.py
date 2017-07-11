import pandas as pd
import numpy as np
from marketdata import *


def calc_pnl(position,data):
	mul=get_contract_multipliers()[data.columns]
	return position*data*mul

def calc_pnl_wc(position,data,fee=0.0005):
	mul=get_contract_multipliers()[data.columns]
	return position*data*mul-cost_model(position,fee)

def calc_pnl_position_wc(position,data,curr_px,fee=0.0005):
    mul=get_contract_multipliers()[data.columns]
    return (position*data*mul*curr_px)-cost_model_position(position,curr_px,mul,fee)

def cost_model(pos,fee=0.0005):
	return (pos.diff().abs()*fee)

def cost_model_position(position,curr_px,mul,fee):
    return position.diff().abs()*(curr_px*mul*fee)

def calc_Sharpe(pnl,N=260):
    return np.sqrt(N) * pnl.mean() / pnl.std()

def ew_portfolio_pnl(pnl):
	x=pnl.dropna(how='all')
	return x.divide(x.count(axis=1),axis=0).sum(axis=1)

# Has a bit of hindsight bias involved since it uses entire time for Covariance matrix
def calc_scaling_factor(pnl,vol_target=0.2):
    Sigma_all=pnl.cov().dropna(how='all',axis=1).dropna(how='all')
    ind=pnl.dropna(how='all').index
    SF=[]
    for row in pnl.dropna(how='all').iterrows():
        no_mkts=row[1].dropna().count()
        w=np.array([1/float(no_mkts)]*no_mkts)
        mkt_list=row[1].dropna().index
        Sig = Sigma_all[mkt_list].T[mkt_list]
        vol_ach=np.sqrt(np.dot(np.dot(w.T,Sig.as_matrix()),w))*16
        SF.append(vol_target/vol_ach)
    return pd.Series(SF,index=ind)

def calc_position(signal,FundAUM,scaling_factor,curr_px):
    mul=get_contract_multipliers()[signal.columns]
    w=(1/signal.dropna(how='all').count(axis=1))
    dict={}
    for m in signal.columns:
        dict[m]=(signal[m]*FundAUM*w*scaling_factor)/(curr_px[m]*mul[m]).dropna()
    return pd.DataFrame().from_dict(dict).round()

def calc_net_performance(gross_pnl,management_fee,performance_fee):
    track=gross_pnl-management_fee/12.
    s = pd.Series()
    hwm=1
    curr=1
    for t,perf in track.iteritems():
        perf=perf+1
        if hwm<curr*perf:
            perf = ((perf-1)*(1-performance_fee))+1
            hwm=curr*perf
        curr=curr*perf
        s[t] =curr
    return s



