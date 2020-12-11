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

from numba import njit

tushare_token = '1e405fa29516d0c96f66ee71f4f2833b31b566cd6ad4f0faa895c671'

basetrade = 20000

def strtodate(strbegindate,adddays=0):
    tmpdate = datetime.datetime.strptime(strbegindate,'%Y%m%d')
    tmpdate = tmpdate + datetime.timedelta(days = adddays)
    return datetime.datetime.strftime(tmpdate,'%Y%m%d')

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
    #return np.array(df).tolist()
    

#获取深证成指历史数据
def get_shenzhen_from_tushare():
    if datetime.datetime.now().hour > 17:
        strenddate = datetime.datetime.strftime(datetime.date.today(),'%Y%m%d')
    else:
        strenddate = datetime.datetime.strftime((datetime.date.today()  + datetime.timedelta(days = -1)),'%Y%m%d')
    ts.set_token(tushare_token)
    pro = ts.pro_api()

    #['ts_code','total_mv', 'float_mv', 'total_share', 'float_share', 'free_share', 'turnover_rate', 'turnover_rate_f', 'pe', 'pe_ttm']
    df1 = pro.index_dailybasic(ts_code = "399001.SH",start_date = '20001219',end_date = '20160731',fields='trade_date,pb')
    df2 = pro.index_dailybasic(ts_code = "399001.SH",start_date = '20160801',end_date = strenddate,fields='trade_date,pb')
    df = df2.append(df1)

    df = df.sort_values(by = 'trade_date',axis = 0,ascending = True).reset_index(drop=True)

    return np.array(df).tolist()


#获取任意A股市盈率
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
    df1 = pro.daily_basic(ts_code = stockcode,start_date = '19900101',end_date = '20031230',fields='trade_date,pb')
    df2 = pro.daily_basic(ts_code = stockcode,start_date = '20040101',end_date = '20181230',fields='trade_date,pb')
    df2 = df2.append(df1)
    df3 = pro.daily_basic(ts_code = stockcode,start_date = '20190101',end_date = strenddate,fields='trade_date,pb')
    df3 = df3.append(df2)

    return np.array(df3.sort_values(by = 'trade_date',axis = 0,ascending = True).reset_index(drop=True)).tolist()


def get_stock_close_from_tdx(stockcode):
    tmplist = []

    #深沪市场股票历史数据存在不同的目录
    if stockcode[0:1] == '6' or stockcode[0:1] == '5':
        file = 'C:/new_tdx/vipdoc/sh/lday/sh' + stockcode + '.day'
        if not os.path.exists(file):
            file = 'D:/new_tdx/vipdoc/sh/lday/sh' + stockcode + '.day'
    else:
        file = 'C:/new_tdx/vipdoc/sz/lday/sz' + stockcode + '.day'
        if not os.path.exists(file):
            file = 'D:/new_tdx/vipdoc/sz/lday/sz' + stockcode + '.day'

    dividend = 0
    if stockcode[0:1] == '5':
        dividend = 1000
    else:
        dividend = 100

    with open(file, 'rb') as f:
        buffer=f.read()                         #读取数据到缓存
        size=len(buffer) 
        rowSize=32                              #通信达day数据，每32个字节一组数据
        for i in range(0,size,rowSize):         #步长为32遍历buffer
            row = list( struct.unpack('IIIIIfII',buffer[i:i+rowSize]) )
            row[0]=row[0]
            row[4]=row[4]/dividend
            
            tmplist.append([row[0],row[4]])

    #['stockcode','trade_date','open','high','low','close','amount','vol']
    df = pd.DataFrame(data=tmplist,columns=['trade_date','close'])
    return df
    #return tmplist

@jit(nopython=True)  
def get_ndays_average_stock_pb_dif(pbarray,ndays):
    history_pb_dif_dict = dict()
    for i in range( pbarray.shape[0] - ndays ):
        total_pb = 0.0
         
        j = i

        while j<ndays+i:
            total_pb = total_pb + pbarray[j,1]               #11列pb
            j += 1
  
        trade_date = pbarray[j,0]
        if i == 0:
            history_pb_dif_dict[int(19000000.0)] = trade_date

        pb = pbarray[j,1]
        history_pb_dif_dict[int(trade_date)] = round(pb - total_pb / ndays,4)
    return history_pb_dif_dict   
 
def moni(stockcode,dif_pb_dict,stockdf,ndays,justvalue=0,buycycle=5):
    tmplist = []
    thismoney = 0.0
    thisamount = 0

    
    totalamount = 0
    totalvolume = 0.0
    totalbuymoney = 0.0
    totalsellmoney = 0.0

    begindate = 0.0
    enddate = 0.0

    count = 0

    for i in range(len(stockdf)):
            
        if i%buycycle == 0:
            trade_date = stockdf.at[i,'trade_date']
            if i==0:
                begindate = trade_date

            dif_pb = round(dif_pb_dict[int(trade_date)] + justvalue,2)
            close = stockdf.at[i,'close']

            if abs(dif_pb)>=1:
                thismoney = abs(round(basetrade * dif_pb ** 1,2))
            else:               
                thismoney = abs(round(basetrade * dif_pb,2))

            thisamount = math.floor(thismoney/close/100) * 100

            #当前pb小于ndays天pb均线，买
            if dif_pb < 0:  
                if thisamount == 0:
                    thismoney = 0.00
                else:
                    count += 1
                    if stockcode[0:1] !=  '5':
                        if thismoney >= 20000:
                            thismoney = round(thisamount * close * (1 + 0.00025) + thisamount/10000,2)
                        else:
                            thismoney = round(thisamount * close + 5 + thisamount/10000,2)
                    else:
                        thismoney = thisamount * close * (1 + 0.00025)

                totalamount = totalamount + thisamount
                totalvolume = totalamount * close
                totalbuymoney += thismoney

                tmplist.append([str(trade_date)[0:4],str(trade_date)[0:6],-thismoney])
                
            #当前pb大于ndays天pb均线，卖    
            else:
                if not tmplist:
                    continue
               
                if totalamount<thisamount:
                    thisamount = totalamount
                
                if thisamount == 0:
                    thismoney = 0.00
                else:
                    count += 1
                    if stockcode[0:1] !=  '5':
                        if thismoney >= 20000:
                            thismoney = round(thisamount * close * (1 - 0.00025 - 0.001) - thisamount/10000,2)
                        else:
                            thismoney = round(thisamount * close * (1 - 0.001) - 5 - thisamount/10000,2)
                    else:
                        thismoney = thisamount * close * (1 - 0.00025)

                totalamount = totalamount - thisamount
                totalvolume = totalamount * close
                totalsellmoney += thismoney

                tmplist.append([str(trade_date)[0:4],str(trade_date)[0:6],thismoney])
               
        else:
            continue

    if totalbuymoney == 0:
        return []

    totalvolume = round(totalvolume,2)
    tmplist.append([None,None,totalvolume])

    tmpdf = pd.DataFrame(data=tmplist, columns=['操作年份','操作月份','发生金额'])

    irr_rate =np.irr(tmpdf['发生金额'])*100

    enddate = trade_date
    return [begindate,enddate,ndays,justvalue,round(totalbuymoney,2),round(totalsellmoney,2),round(totalvolume,2),irr_rate,count]



def moni1(stockcode,dif_pb_dict,stock_df,ndays,justvalue=0,buycycle=5):
    result_list = []
    rate_list = []
    basetrade = 10000

    thismoney = 0.0 

    totalbuymoney = 0.0
    totalamount = 0.0
    totalvolume = 0.0

    totalsellmoney = 0.0

    begindate = ''
    enddate = ''

    for i in range(len(stock_df)):
            
        if i%buycycle == 0:
            trade_date = stock_df.at[i,'trade_date']
            if i==0:
                begindate = trade_date

            dif_pb = round(dif_pb_dict[int(trade_date)] + justvalue,2)
            close = stock_df.at[i,'close']

            if abs(dif_pb)>=1:
                thismoney = abs(round(basetrade * dif_pb ** 1,2))
            else:               
                thismoney = abs(round(basetrade * dif_pb,2))
            #当前pb小于ndays天pb均线，买
            if dif_pb < 0:  
                thisamount = math.floor(thismoney/close/100) * 100
                if stockcode[0:1] !=  '5':
                    if thismoney >= 20000:
                        thismoney = round(thisamount * close * (1 + 0.00025) + thisamount/10000,2)
                    else:
                        thismoney = round(thisamount * close + 5 + thisamount/10000,2)
                else:
                    thismoney = thisamount * close * (1 + 0.00025)

                totalbuymoney = totalbuymoney + thismoney
                totalamount = totalamount + thisamount
                totalvolume = totalamount * close
                rate_list.append([trade_date,round(-thismoney,2)])

                #resultcsvtitle = ['操作日期','PB-PB*','本次单价','本次投入本金','累计投入本金','总资产','回收资金','绝对收益率','月化收益率']
                #resultlist.append([trade_date,dif_pb,close,thismoney,totalbuymoney,totalvolume + totalsellmoney,totalsellmoney,0,0])

            #当前pb大于ndays天pb均线，卖    
            else:
                if not rate_list:
                    continue
                thisamount = math.floor(thismoney/close/100) * 100
                if totalamount<thisamount:
                    thisamount = totalamount

                if stockcode[0:1] !=  '5':
                    if thismoney >= 20000:
                        thismoney = round(thisamount * close * (1 - 0.00025 - 0.001) - thisamount/10000,2)
                    else:
                        thismoney = round(thisamount * close * (1 - 0.001) - 5 - thisamount/10000,2)
                else:
                    thismoney = thisamount * close * (1 - 0.00025)

                totalbuymoney = totalbuymoney - thismoney
                totalamount = totalamount - thisamount
                totalvolume = totalamount * close
                totalsellmoney = totalsellmoney + thismoney

                
                rate_list.append([trade_date,round(thismoney,2)])

                #resultcsvtitle = ['操作日期','PB-PB*','本次单价','本次投入本金','累计投入本金','总资产','回收资金','绝对收益率','月化收益率']
                #resultlist.append([trade_date,dif_pb,close,0,totalbuymoney,totalvolume + totalsellmoney,totalsellmoney,0,0])

        else:
            continue

    if totalbuymoney == 0:
        return []

    totalvolume = round(totalvolume,2)
    rate_list.append([trade_date,totalvolume])

    rate_df = pd.DataFrame(data=rate_list, columns=['操作日期','发生金额'])

    irr_rate =np.irr(rate_df['发生金额'])*100

    enddate = trade_date
    return [ndays,justvalue,round(totalbuymoney,2),round(totalsellmoney,2),round(totalvolume,2),begindate,enddate,irr_rate]


def monimingxi(stockcode,dif_pb_dict,stock_df,justvalue=0,buycycle=5):
    result_list = []

    totalbuymoney = 0.0
    totalamount = 0.0
    totalvolume = 0.0

    totalsellmoney = 0.0

    for i in range(len(stock_df)):
            
        if i%buycycle == 0:
            trade_date = stock_df.at[i,'trade_date']
            dif_pb = round((float(dif_pb_dict[trade_date]) + justvalue),3)
            close = float(stock_df.at[i,'close'])

            if abs(dif_pb)>=1:
                thismoney = abs(round(basetrade * dif_pb ** 1,2))
            else:               
                thismoney = abs(round(basetrade * dif_pb,2))
            #当前pb小于ndays天pb均线，买
            if dif_pb < 0:  
                thisamount = math.floor(thismoney/close/100) * 100
                if stockcode[0:1] !=  '5':
                    if thismoney >= 20000:
                        thismoney = round(thisamount * close * (1 + 0.00025) + thisamount/10000,2)
                    else:
                        thismoney = round(thisamount * close + 5 + thisamount/10000,2)
                else:
                    thismoney = round(thisamount * close * (1 + 0.00025),2)

                totalbuymoney = totalbuymoney + thismoney
                totalamount = totalamount + thisamount
                totalvolume = round(totalamount * close,2)

                #resultcsvtitle = ['操作日期','操作月份','PB-PB*','本次单价','本次金额','累计买入金额','累计卖出金额','股票剩余资产']
                result_list.append([trade_date,trade_date[0:6],round(dif_pb,2),close,-thismoney,totalbuymoney,totalsellmoney,totalvolume])

            #当前pb大于ndays天pb均线，卖    
            elif dif_pb > 0:
                if not result_list:
                    continue

                thisamount = math.floor(thismoney/close/100) * 100
                if totalamount<thisamount:
                    thisamount = totalamount

                if stockcode[0:1] !=  '5':
                    if thismoney >= 20000:
                        thismoney = round(thisamount * close * (1 - 0.00025 - 0.001) - thisamount/10000,2)
                    else:
                        thismoney = round(thisamount * close * (1 - 0.001) - 5 - thisamount/10000,2)
                else:
                    thismoney = round(thisamount * close * (1 - 0.00025),2)

                #totalbuymoney = totalbuymoney - thismoney
                totalamount = totalamount - thisamount
                totalvolume = round(totalamount * close,2)
                totalsellmoney = totalsellmoney + thismoney

                #resultcsvtitle = ['操作日期','操作月份','PB-PB*','本次单价','本次金额','累计买入金额','累计卖出金额','股票剩余资产']
                result_list.append([trade_date,trade_date[0:6],round(dif_pb,3),close,thismoney,totalbuymoney,totalsellmoney,totalvolume])
        
            #当前pb等于ndays天pb均线，什么也不做
            else:               
                continue
        else:
            continue
    #result_list.append([trade_date,trade_date[0:6],round(dif_pb,3),close,totalvolume,totalbuymoney,totalsellmoney,totalvolume])
    return pd.DataFrame(data=result_list,columns=['操作日期','操作月份','PB-PB*','本次单价','本次金额','累计买入金额','累计卖出金额','股票剩余资产'])

   
def monimingxi1(stockcode,startdate,ndays,justvalue=0,buycycle=5):
    history_pb_dif_dict = {}

    if stockcode[0:1] == '5':
        stockdf = get_shanghai_from_tushare()
        history_pb_dif_dict = get_ndays_average_shanghai_pb_dif(stockdf,ndays)
    else:
        stockdf = get_anystock_from_tushare(stockcode)
        history_pb_dif_dict = get_ndays_average_stock_pb_dif(stockdf,ndays)

    stock_df = get_stock_df_from_tdx(stockcode)
    stock_df = stock_df[stock_df['trade_date']>=startdate]
    stock_df = stock_df.reset_index(drop=True)

    df = monimingxi(stockcode,history_pb_dif_dict,stock_df,justvalue,buycycle)
    return df
