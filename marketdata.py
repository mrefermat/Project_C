import pandas as pd
import quandl
from arctic import Arctic
store = Arctic('localhost')
price_table = store['CHINA_PX']
OI_table = store['CHINA_OI']
static_table = store['CHINA_STATIC']
import math
from datetime import datetime
token="Us3wFmXGgAj_1cUtHAAR"

# Currently returns a Series with just the adjusted price.
# We could think about adding the 'adjusted' or total volume
def get_timeseries(market):
	price=load_market_price(market)
	volume=load_market_open_interest(market)
	return adjusted_returns(price,volume).dropna().astype(dtype='float')

def compare(last,this):
    if this[1:]>last[1:] or this[0] > last[0]:
        return this
    else:
        return last

def intital_load(mkt,ticker,exchange,price,OI):
	price_table.write(mkt, price, metadata={'ticker': ticker,'exchange':exchange})
	OI_table.write(mkt, OI, metadata={'ticker': ticker,'exchange':exchange})

def get_market_static_data():
    return static_table.read('Markets').data

def get_market_list(how='live'):
    mkts=static_table.read('Markets').data
    if how=='all':
    	return mkts.index
    else:
    	return ['A', 'AG', 'AL', 'AU', 'B', 'BU', 'C', 'CF', 'CS', 'CU', 'ER', 'FB',
      'FG', 'GN', 'HC', 'I', 'J', 'JD', 'JM', 'L', 'M', 'MA', 'ME', 'NI', 'P',
      'PB', 'PP', 'RB', 'RM', 'RO', 'SN', 'SR', 'TA', 'V', 'WH', 'WS', 'WT',
      'Y','ZN']

def load_market_price(market):
	return price_table.read(market).data

def load_market_open_interest(market):
	return OI_table.read(market).data

def get_contract_multipliers():
	mkts=get_market_static_data()
	return mkts.contract_multiplier

def adjusted_returns(price,volume):
    rtn=price.pct_change()
    ww=volume.apply(lambda s: s.nlargest(2).index.tolist(), axis=1)
    s=ww.copy()
    mon='A00'
    spread=0
    for ind, val in ww.iteritems():
        mon=compare(mon,val[0])
        s.ix[ind]=rtn[val[0]].ix[ind]
    return s

# To impliment 
def update_data():
	mkts=get_market_static_data()
	for exchange in mkts.exchange.unique():
		list_of_markets=mkts[mkts.exchange==exchange].index
		for mkt in list_of_markets:
			price, OI = quandl_load_data(mkt,exchange)
	    	intital_load(mkt,ticker,exchange,price,OI)

def get_quandl_fields(exchange):
    field ={'DCE':['Close','Volume','Turnover','Open Interest'],
            'SHFE':['Close','Volume','O.I.'],
            'CZCE':['Close','Volume','Turnover','Open Interest'],
           'CFFEX':['Close','Volume','Turnover','Open Interest']}
    return field[exchange]

def _most_liquid_price(mkt):
    OI = load_market_open_interest(mkt).dropna(how='all')
    px= load_market_price(mkt).dropna(how='all')
    s=pd.Series()
    if px.size != 0:
        maxContract=OI.idxmax(axis=1)
        for row in maxContract.iteritems():
            s[row[0]]=px.ix[row[0]][row[1]]
    return s

def get_most_liquid_price(mkt):
    if type(mkt)==str:
        return _most_liquid_price(mkt)
    else:
        dic={}
        for m in mkt:
            dic[m]=get_most_liquid_price(m)
        return pd.DataFrame().from_dict(dic)

def quandl_load_data(market,exchange):
    list_of_months = ['F','G','H','J','K','M','N',
                        'Q','U','V','X','Z']
    fields=get_quandl_fields(exchange)
    if exchange=='CZCE':
        exchange='ZCE'
    ticker = exchange + '/' + market
    ddf={}
    mini_list = list(list_of_months)
    for y in range(2018,2000,-1):
        for m in mini_list:
            try:
                ddf[m + str(y)[2:]]=quandl.get(ticker + m + str(y),authtoken=token)[fields]
            except:
                mini_list.remove(m)
                print 'Missing '+m + ' '+ str(y)
    ix = pd.DatetimeIndex(start=datetime(2000, 1, 1), end=datetime(2018, 12, 31), freq='D')
    price=pd.DataFrame(index=ix)
    for k in ddf.keys():
        price[k]=ddf[k].Close
    price=price.dropna(how='all')
    OI=pd.DataFrame(index=ix)
    for k in ddf.keys():
        try:
            OI[k]=ddf[k]['Open Interest']
        except:
            OI[k]=ddf[k]['O.I.']
    OI=OI.dropna(how='all')
    return price,OI