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

def compute_amount(a):
    b = math.floor((a+0.009) * 100)
    return 100*b

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

"""
#斐波那契数列指的是这样一个数列 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233，377，610，987，1597...
period_list = ['987','610','377','233','144','89','55','','','','','','','']
i = 0
for period in period_list:
    if not period:
        continue
    if i == 0:
        history_pb_dict = get_ndays_average_stock_pb(pbarray,int(period))
        df = pd.DataFrame(list(history_pb_dict.items()), columns=['trade_date', 'pb'+period])
    else:
        history_pb_dict = get_ndays_average_stock_pb(pbarray,int(period))
        tmpdf = pd.DataFrame(list(history_pb_dict.items()), columns=['trade_date', 'pb'+period])
        df = pd.merge(df,tmpdf.loc[:,['trade_date','pb'+period]],how='inner',on = 'trade_date')
    i += 1

tmpdf = df
tmpdf = tmpdf.drop(columns=['trade_date'])
tmparr = tmpdf.values

df['min1']=tmpdf.min(axis=1)

tmparr[tmpdf.index,np.argmin(tmparr,axis=1)]=100000
tmpdf=pd.DataFrame(tmparr)
df['min2']=tmpdf.min(axis=1)

tmparr[tmpdf.index,np.argmin(tmparr,axis=1)]=100000
tmpdf=pd.DataFrame(tmparr)
df['min3']=tmpdf.min(axis=1)

tmpdf = df
tmpdf = tmpdf.drop(columns=['trade_date','min1','min2','min3'])
tmparr = tmpdf.values
df['max1']=tmpdf.max(axis=1)

tmparr[tmpdf.index,np.argmax(tmparr,axis=1)]=-100000
tmpdf=pd.DataFrame(tmparr)
df['max2']=tmpdf.max(axis=1)

tmparr[tmpdf.index,np.argmax(tmparr,axis=1)]=-100000
tmpdf=pd.DataFrame(tmparr)
df['max3']=tmpdf.max(axis=1)

tmpdf = get_stock_close_from_tushare(stockcode)
tmpdf['trade_date'] = tmpdf['trade_date'].astype('int')
df = pd.merge(df,tmpdf.loc[:,['trade_date','close']],how='inner',on = 'trade_date')

tmpdf = pd.DataFrame(stocklist,columns=['trade_date','pb1'])
tmpdf['trade_date'] = tmpdf['trade_date'].astype('int')
df = pd.merge(df,tmpdf.loc[:,['trade_date','pb1']],how='inner',on = 'trade_date')

df.to_csv(stockcode+'_p.csv',index=False,encoding='utf_8_sig')

"""



period_list = ['1220','1098','854','732','610','488','366','244','122','61']
i = 0
for period in period_list:
    if not period:
        continue
    if i == 0:
        history_pb_dict = get_ndays_average_stock_pb(pbarray,int(period))
        df = pd.DataFrame(list(history_pb_dict.items()), columns=['trade_date', 'pb'+period])
    else:
        history_pb_dict = get_ndays_average_stock_pb(pbarray,int(period))
        tmpdf = pd.DataFrame(list(history_pb_dict.items()), columns=['trade_date', 'pb'+period])
        df = pd.merge(df,tmpdf.loc[:,['trade_date','pb'+period]],how='inner',on = 'trade_date')
    i += 1

tmpdf = df
tmpdf = tmpdf.drop(columns=['trade_date'])
tmparr = tmpdf.values
df['min1']=tmpdf.min(axis=1)

tmparr[tmpdf.index,np.argmin(tmparr,axis=1)]=100000
#tmpdf=pd.DataFrame(tmparr,columns=["pb144","pb89","pb55","pb34","pb21","pb13","pb5"])
tmpdf=pd.DataFrame(tmparr)
df['min2']=tmpdf.min(axis=1)

tmparr[tmpdf.index,np.argmin(tmparr,axis=1)]=100000
tmpdf=pd.DataFrame(tmparr)
df['min3']=tmpdf.min(axis=1)

tmpdf = df
tmpdf = tmpdf.drop(columns=['trade_date','min1','min2','min3'])
tmparr = tmpdf.values
df['max1']=tmpdf.max(axis=1)

tmparr[tmpdf.index,np.argmax(tmparr,axis=1)]=-100000
tmpdf=pd.DataFrame(tmparr)
df['max2']=tmpdf.max(axis=1)

tmparr[tmpdf.index,np.argmax(tmparr,axis=1)]=-100000
tmpdf=pd.DataFrame(tmparr)
df['max3']=tmpdf.max(axis=1)


tmpdf = get_stock_close_from_tushare(stockcode)
tmpdf['trade_date'] = tmpdf['trade_date'].astype('int')
df = pd.merge(df,tmpdf.loc[:,['trade_date','close']],how='inner',on = 'trade_date')

tmpdf = pd.DataFrame(stocklist,columns=['trade_date','pb1'])
tmpdf['trade_date'] = tmpdf['trade_date'].astype('int')
df = pd.merge(df,tmpdf.loc[:,['trade_date','pb1']],how='inner',on = 'trade_date')


df.to_csv(stockcode+'.csv',index=False,encoding='utf_8_sig')



df = pd.read_csv(stockcode+'.csv')

begindate = ''
enddate = ''
tmplist = []
for index, row in df.iterrows():
    if row['pb1'] < row['min1']:
        if len(begindate) == 0:
            begindate = str(int(row['trade_date']))
        else:
            continue
    else:
        if len(begindate) != 0:
            enddate = str(int(row['trade_date']))
            tmplist.append([begindate,enddate])
            begindate = ''
        else:
            continue
#print(tmplist)

basetrade = 200000
#stock_df = pd.read_csv(stockcode + '.csv')
for period in tmplist:
    begindate = period[0]
    enddate = period[1]

    stock_df = df

    stock_df = stock_df[stock_df['trade_date']>=int(begindate)]
    stock_df = stock_df[stock_df['trade_date']<=int(enddate)]
    stock_df = stock_df.sort_values(by = 'trade_date',axis = 0,ascending = True).reset_index(drop=True)

    thismoney = 0.0 
    totalbuymoney = 0.0
    totalamount = 0.0
    totalvolume = 0.0
    totalsellmoney = 0.0

    result_list = []
    irrdf = pd.DataFrame()

    for i in range(len(stock_df)):
        trade_date = stock_df.at[i,'trade_date']
  
        dif_pb = round(stock_df.at[i,'pb1'] - stock_df.at[i,'min1'],3)
        if dif_pb >= 0.0:
            dif_pb = round(stock_df.at[i,'pb1'] - stock_df.at[i,'min2'],3)
            if dif_pb >= 0.0:
                dif_pb = round(stock_df.at[i,'pb1'] - stock_df.at[i,'min3'],3)
                if dif_pb >= 0.0:
                    dif_pb = round(stock_df.at[i,'pb1'] - stock_df.at[i,'min1'],3)


        close = float(stock_df.at[i,'close'])

        thisamount = compute_amount(abs(dif_pb))

        #if abs(dif_pb)>=0.5:
        #    thismoney = abs(round(basetrade * dif_pb * 1,2))
        #else:               
        #    thismoney = abs(round(basetrade * dif_pb,2))
        #当前pb小于ndays天pb均线，买
        if dif_pb < 0:  
            #thisamount = math.floor(thismoney/close/100) * 100
            if stockcode[0:1] !=  '5':
                if thismoney >= 20000:
                    thismoney = round(thisamount * close * (1 + 0.00025) + thisamount/10000,2)
                else:
                    thismoney = round(thisamount * close + 5 + thisamount/10000,2)
            else:
                thismoney = round(thisamount * close * (1 + 0.00025),2)

            if thisamount == 0:
                thismoney = 0.0

            totalbuymoney = totalbuymoney + thismoney
            totalamount = totalamount + thisamount
            totalvolume = round(totalamount * close,2)
            if totalvolume != 0:
                if stockcode[0:1] !=  '5':
                    if totalvolume >= 20000:
                        totalvolume = round(totalamount * close * (1 - 0.00025 - 0.001) - totalamount/10000,2)
                    else:
                        totalvolume = round(totalamount * close * (1 - 0.001) - 5 - totalamount/10000,2)
                else:
                    totalvolume = round(totalamount * close * (1 - 0.00025),2)
            
            if stockcode[0:1] !=  '5':
                if (totalamount-thisamount)*close >= 20000:
                    irrvalue = round((totalamount-thisamount)*close * (1 - 0.00025 - 0.001) - (totalamount-thisamount)/10000,2)
                else:
                    irrvalue = round((totalamount-thisamount) * close * (1 - 0.001) - 5 - (totalamount-thisamount)/10000,2)
            else:
                irrvalue = round((totalamount-thisamount) * close * (1 - 0.00025),2)

            irrdf = irrdf.append([[irrvalue]])
            irr=np.irr(irrdf[0])*100

            #if irr < 0.1 or math.isnan(irr):
            irrdf = irrdf[:-1]
            
            irrdf = irrdf.append([[-thismoney]])
            #resultcsvtitle = ['操作日期','操作月份','PB-PB*','本次单价','本次数量','本次金额','累计买入金额','累计卖出金额','股票剩余股数','股票剩余资产','IRR']
            result_list.append([trade_date,round(dif_pb,3),close,thisamount,-thismoney,totalbuymoney,totalsellmoney,totalamount,totalvolume,irr])
            #else:
                #result_list.append([trade_date,round(dif_pb,3),close,(totalamount-thisamount),irrvalue,totalbuymoney-thismoney,irrvalue,0,0,irr])
                #pd.DataFrame(data=result_list,columns=['trade_date','dif_pb','close','本次数量','本次金额','累计买入金额','累计卖出金额','股票剩余股数','股票剩余资产','IRR']).to_csv(stockcode+'_'+begindate+'_result.csv',encoding='utf_8_sig')
                #break
        #if irr > 0.1:
        #当前pb大于ndays天pb均线，卖    
        else:
            if not result_list:
                continue

            #thisamount = math.floor(thismoney/close/100) * 100
            if totalamount<thisamount:
                thisamount = totalamount

            if stockcode[0:1] !=  '5':
                if thismoney >= 20000:
                    thismoney = round(thisamount * close * (1 - 0.00025 - 0.001) - thisamount/10000,2)
                else:
                    thismoney = round(thisamount * close * (1 - 0.001) - 5 - thisamount/10000,2)
            else:
                thismoney = round(thisamount * close * (1 - 0.00025),2)

            if thisamount == 0:
                thismoney = 0.0

            totalamount = totalamount - thisamount
            totalvolume = round(totalamount * close ,2)

            if totalvolume != 0:
                if stockcode[0:1] !=  '5':
                    if totalvolume >= 20000:
                        totalvolume = round(totalamount * close * (1 - 0.00025 - 0.001) - totalamount/10000,2)
                    else:
                        totalvolume = round(totalamount * close * (1 - 0.001) - 5 - totalamount/10000,2)
                else:
                    totalvolume = round(totalamount * close * (1 - 0.00025),2)
            
            totalsellmoney = totalsellmoney + thismoney

            if stockcode[0:1] !=  '5':
                if (totalamount+thisamount)*close >= 20000:
                    irrvalue = round((totalamount+thisamount)*close * (1 - 0.00025 - 0.001) - (totalamount+thisamount)/10000,2)
                else:
                    irrvalue = round((totalamount+thisamount) * close * (1 - 0.001) - 5 - (totalamount+thisamount)/10000,2)
            else:
                irrvalue = round((totalamount+thisamount) * close * (1 - 0.00025),2)

            irrdf = irrdf.append([[irrvalue]])
            irr=np.irr(irrdf[0])*100

            #if irr < 0.1:
            irrdf = irrdf[:-1]
            
            irrdf = irrdf.append([[thismoney]])
            #resultcsvtitle = ['操作日期','操作月份','PB-PB*','本次单价','本次数量','本次金额','累计买入金额','累计卖出金额','股票剩余股数','股票剩余资产','IRR']
            result_list.append([trade_date,round(dif_pb,3),close,thisamount,thismoney,totalbuymoney,totalsellmoney,totalamount,totalvolume,irr])
            #else:
                #result_list.append([trade_date,round(dif_pb,3),close,(totalamount+thisamount),irrvalue,totalbuymoney,irrvalue,0,0,irr])
                #pd.DataFrame(data=result_list,columns=['trade_date','dif_pb','close','本次数量','本次金额','累计买入金额','累计卖出金额','股票剩余股数','股票剩余资产','IRR']).to_csv(stockcode+'_'+begindate+'_result.csv',encoding='utf_8_sig')
                #break
        #if irr > 0.1:
            #pd.DataFrame(data=result_list,columns=['trade_date','dif_pb','close','本次数量','本次金额','累计买入金额','累计卖出金额','股票剩余股数','股票剩余资产','IRR']).to_csv(stockcode+'_'+begindate+'_result.csv',encoding='utf_8_sig')
            #print(irrdf)
            #break

    pd.DataFrame(data=result_list,columns=['trade_date','dif_pb','close','本次数量','本次金额','累计买入金额','累计卖出金额','股票剩余股数','股票剩余资产','IRR']).to_csv(stockcode+'_'+begindate+'_result.csv',encoding='utf_8_sig')
    
    #print(pd.DataFrame(tmplist,columns=["begindate","enddate"]))
       


