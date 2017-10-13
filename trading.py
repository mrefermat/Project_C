from marketdata import *
import datetime as dt

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
	trades=_calculated_new_trades(lots.ix[-1])
	for mkt in trades.index:
		contract = get_traded_contract(mkt)
		td =int(trades[mkt]) 
		if  td >0:
			msg=msg+ 'BUY: ' + str(int(trades[mkt])) + ' of ' + mkt + ' '+ contract +' at '+ str(curr_px.ix[-1][mkt]) +'\n'
		elif td==0:
			continue
		else:
			msg=msg+ 'SELL: ' + str(int(trades[mkt])) + ' of ' + mkt + ' '+ contract +' at '+ str(curr_px.ix[-1][mkt])+'\n'
	return msg

def set_FUM(fum):
    FUM_table=store['FUM']
    f=pd.Series(fum,index=['FUM'])
    FUM_table.write('FUM',f)

def get_FUM():
    FUM=store['FUM']
    return FUM.read('FUM').data.FUM

def get_current_position(new_position):
    position=store['POSITION']
    try:
        return position.read('Current').data
    except:
        position_history=pd.DataFrame(index=new_position.index)
        position_history[dt.date(2000,1,1)]=0
        return position_history
    
def set_position(data):
    position=store['POSITION']
    position.delete('Current')
    position.write('Current',data)

def _calculated_new_trades(new_position):
    new_position=new_position.replace(np.nan,0)
    position_history=get_current_position(new_position)
    position_history[dt.date.today()]=new_position
    trades=position_history.T.ix[-1]-position_history.T.ix[-2]
    set_position(position_history)
    return trades
    
    