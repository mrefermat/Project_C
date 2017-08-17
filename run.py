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
mkts=static_table.read('Markets').data
list_of_months = ['F','G','H','J','K','M','N','Q','U','V','X','Z']

for exchange in mkts.exchange.unique():
    list_of_markets=mkts[mkts.exchange==exchange].index
    for mkt in list_of_markets:
        price, OI = quandl_load_data(mkt,exchange)
        intital_load(mkt,price,OI)