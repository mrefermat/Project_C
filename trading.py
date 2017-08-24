from marketdata import *


def switch_contracts(lots):
    msg =""    
    for mkt in lots.columns:
        OI=load_market_open_interest(mkt).dropna(how='all')
        if OI.size==0:
            continue
        prev_contract = OI.idxmax(axis=1).tail(2).ix[0] 
        today_contract = OI.idxmax(axis=1).tail(2).ix[1]
        if prev_contract != today_contract:
            prev = lots[mkt].tail(2).ix[0]
            today = lots[mkt].tail(2).ix[1]
            msg=msg+ 'SWITCH: ' +str(prev) + ' lots of '  + mkt + ' from: ' + prev_contract + ' to: ' + today_contract +'\n'
    return msg

def generate_trades(lots,curr_px):
	msg=''
	trades=lots.diff().ix[lots.index[-1]].dropna()
	for mkt in trades.index:
		contract = get_traded_contract(mkt)
		td =int(trades[mkt]) 
		if  td >0:
			msg=msg+ 'BUY: ' + str(trades[mkt]) + ' of ' + mkt + ' '+ contract +' at '+ str(curr_px.ix[-1][mkt]) +'\n'
		elif td==0:
			continue
		else:
			msg=msg+ 'SELL: ' + str(trades[mkt]) + ' of ' + mkt + ' '+ contract +' at '+ str(curr_px.ix[-1][mkt])+'\n'
	return msg
