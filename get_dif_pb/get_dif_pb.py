import tushare as ts
import datetime
import pandas as pd
import numpy as np
import struct
import os
import math
from statistics import mean
from numba import jit
from numba.typed import List

tushare_token = '1e405fa29516d0c96f66ee71f4f2833b31b566cd6ad4f0faa895c671'

#获取上证综指历史数据，含市净率，市盈率
def get_shanghai_from_tushare():
    if datetime.datetime.now().hour > 17:
        strenddate = datetime.datetime.strftime(datetime.date.today(),'%Y%m%d')
    else:
        strenddate = datetime.datetime.strftime((datetime.date.today()  + datetime.timedelta(days = -1)),'%Y%m%d')

    ts.set_token(tushare_token)
    pro = ts.pro_api()

    #['ts_code', 'trade_date', 'total_mv', 'float_mv', 'total_share', 'float_share', 'free_share', 'turnover_rate', 'turnover_rate_f', 'pe', 'pe_ttm', 'pb']
    df1 = pro.index_dailybasic(ts_code = "000001.SH",start_date = '20001219',end_date = '20160731',fields='trade_date,pb')
    df2 = pro.index_dailybasic(ts_code = "000001.SH",start_date = '20160801',end_date = strenddate,fields='trade_date,pb')
    df = df2.append(df1)

    df = df.sort_values(by = 'trade_date',axis = 0,ascending = True).reset_index(drop=True)

    return df.values.tolist()

def get_anystock_from_tushare(stockcode):
    if datetime.datetime.now().hour > 17:
        strenddate = datetime.datetime.strftime(datetime.date.today(),'%Y%m%d')
    else:
        strenddate = datetime.datetime.strftime((datetime.date.today()  + datetime.timedelta(days = -1)),'%Y%m%d')

    if stockcode[0:1] == '6':
        stockcode = stockcode + '.SH'
    else:
        stockcode = stockcode + '.SZ'

    ts.set_token(tushare_token)
    pro = ts.pro_api()

    #['ts_code', 'trade_date', 'close', 'turnover_rate', 'turnover_rate_f', 'volume_ratio', 'pe', 'pe_ttm', 'pb', 'ps', 'ps_ttm', 'total_share', 'float_share', 'free_share', 'total_mv', 'circ_mv']
    df1 = pro.daily_basic(ts_code = stockcode,start_date = '19900101',end_date = '20031231',fields='trade_date,pb')
    df2 = pro.daily_basic(ts_code = stockcode,start_date = '20040101',end_date = '20181231',fields='trade_date,pb')
    df2 = df2.append(df1)
    df3 = pro.daily_basic(ts_code = stockcode,start_date = '20190101',end_date = strenddate,fields='trade_date,pb')
    df3 = df3.append(df2)

    return np.array(df3.sort_values(by = 'trade_date',axis = 0,ascending = True).reset_index(drop=True)).tolist()

@jit(nopython=True)  
def get_ndays_average_stock_pb(pbarray,ndays):
    history_pb_dict = dict()
    for i in range( pbarray.shape[0] - ndays ):
        total_pb = 0.0
         
        j = i

        while j<ndays+i:
            total_pb = total_pb + pbarray[j,1]               #11列pb
            j += 1
  
        trade_date = pbarray[j,0]
        
        pb = pbarray[j,1]
        history_pb_dict[int(trade_date)] = round(total_pb / ndays,4)
    return history_pb_dict

def get_stock_close_from_tushare(stockcode):
    if datetime.datetime.now().hour > 17:
        strenddate = datetime.datetime.strftime(datetime.date.today(),'%Y%m%d')
    else:
        strenddate = datetime.datetime.strftime((datetime.date.today()  + datetime.timedelta(days = -1)),'%Y%m%d')

    if stockcode[0:1] == '6' or stockcode[0:1] == '5':
        stockcode = stockcode + '.SH'
    else:
        stockcode = stockcode + '.SZ'

    ts.set_token(tushare_token)
    pro = ts.pro_api()

    #['ts_code', 'trade_date', 'close', 'turnover_rate', 'turnover_rate_f', 'volume_ratio', 'pe', 'pe_ttm', 'pb', 'ps', 'ps_ttm', 'total_share', 'float_share', 'free_share', 'total_mv', 'circ_mv']
    if stockcode[0:1] == '5':
        df1 = pro.fund_daily(ts_code = stockcode,start_date = '19900101',end_date = '20031231',fields='trade_date,close')
        df2 = pro.fund_daily(ts_code = stockcode,start_date = '20040101',end_date = '20181231',fields='trade_date,close')
        df2 = df2.append(df1)
        df3 = pro.fund_daily(ts_code = stockcode,start_date = '20190101',end_date = strenddate,fields='trade_date,close')
        df3 = df3.append(df2)
    else:
        df1 = pro.daily_basic(ts_code = stockcode,start_date = '19900101',end_date = '20031231',fields='trade_date,close')
        df2 = pro.daily_basic(ts_code = stockcode,start_date = '20040101',end_date = '20181231',fields='trade_date,close')
        df2 = df2.append(df1)
        df3 = pro.daily_basic(ts_code = stockcode,start_date = '20190101',end_date = strenddate,fields='trade_date,close')
        df3 = df3.append(df2)

    return df3

stockcode  = input("请输入证券代码(510300):")
if len(stockcode) == 0:
    stockcode = '510300'

if stockcode[0:1] == '5':
    stocklist = get_shanghai_from_tushare()
else:
    stocklist = get_anystock_from_tushare(stockcode)
pbarray = np.array(stocklist,dtype=np.float64)

history_pb_dict = get_ndays_average_stock_pb(pbarray,1220)
df = pd.DataFrame(list(history_pb_dict.items()), columns=['trade_date', 'pb1220'])

ndays  = int(244 * 4.5)
while ndays>=122:

    history_pb_dict = get_ndays_average_stock_pb(pbarray,ndays)
    tmpdf = pd.DataFrame(list(history_pb_dict.items()), columns=['trade_date', 'pb'+str(ndays)])

    df = pd.merge(df,tmpdf.loc[:,['trade_date','pb'+str(ndays)]],how='inner',on = 'trade_date')
    #df.to_csv(stockcode+'_pb_'+str(ndays)+'.csv',encoding='utf_8_sig')
    ndays -= 122


ndays = 1
history_pb_dict = get_ndays_average_stock_pb(pbarray,ndays)
tmpdf = pd.DataFrame(list(history_pb_dict.items()), columns=['trade_date', 'pb'+str(ndays)])
df = pd.merge(df,tmpdf.loc[:,['trade_date','pb'+str(ndays)]],how='inner',on = 'trade_date')

#for i in range(len(df)):
#    tmpdf = df[i:i+1]

tmpdf = df
tmpdf = tmpdf.drop(columns=['trade_date','pb1'])
tmparr = tmpdf.values

df['min1']=tmpdf.min(axis=1)

tmparr[tmpdf.index,np.argmin(tmparr,axis=1)]=100
tmpdf=pd.DataFrame(tmparr,columns=["pb1220","pb1098","pb976","pb854","pb732","pb610","pb488","pb366","pb244","pb122"])
df['min2']=tmpdf.min(axis=1)

tmparr[tmpdf.index,np.argmin(tmparr,axis=1)]=100
tmpdf=pd.DataFrame(tmparr,columns=["pb1220","pb1098","pb976","pb854","pb732","pb610","pb488","pb366","pb244","pb122"])
df['min3']=tmpdf.min(axis=1)

tmpdf = df
tmpdf = tmpdf.drop(columns=['trade_date','pb1','min1','min2','min3'])
tmparr = tmpdf.values

df['max1']=tmpdf.max(axis=1)

tmparr[tmpdf.index,np.argmax(tmparr,axis=1)]=-100
tmpdf=pd.DataFrame(tmparr,columns=["pb1220","pb1098","pb976","pb854","pb732","pb610","pb488","pb366","pb244","pb122"])
df['max2']=tmpdf.max(axis=1)

tmparr[tmpdf.index,np.argmax(tmparr,axis=1)]=-100
tmpdf=pd.DataFrame(tmparr,columns=["pb1220","pb1098","pb976","pb854","pb732","pb610","pb488","pb366","pb244","pb122"])
df['max3']=tmpdf.max(axis=1)

#df.to_csv(stockcode+'_pb_'+str(ndays)+'.csv',encoding='utf_8_sig')
#df['trade_date'] = df['trade_date'].astype('object')
#df = df.sort_values(by = 'trade_date',axis = 0,ascending = True).reset_index(drop=True)
tmpdf = get_stock_close_from_tushare(stockcode)
tmpdf['trade_date'] = tmpdf['trade_date'].astype('int')
df = pd.merge(df,tmpdf.loc[:,['trade_date','close']],how='inner',on = 'trade_date')
#df.to_csv(stockcode+'_close'+'.csv',encoding='utf_8_sig')
df.to_csv(stockcode+'.csv',index=False,encoding='utf_8_sig')