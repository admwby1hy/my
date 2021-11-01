import os
import sys
import time
import pandas as pd
import struct
import datetime
import math

project_name = os.path.basename(__file__).split(".")[0]
#print(project_name)
project_dir = os.path.abspath(os.path.dirname(__file__))
#print(project_dir)

root_path = os.path.dirname(project_dir)
sys.path.append(root_path)
#print(sys.path)

import myfunc as my

import tushare as ts

ts.set_token(my.tushare_token)
pro = ts.pro_api()


def strtodate(strbegindate,adddays=0):
    tmpdate = datetime.datetime.strptime(strbegindate,'%Y%m%d')
    tmpdate = tmpdate + datetime.timedelta(days = adddays)
    return datetime.datetime.strftime(tmpdate,'%Y%m%d')

def is_open(df_open_date,str_date):    

    if df_open_date[df_open_date['cal_date'] == str_date].iat[0,2] == 1:
        return 1
    else:
        return 0

def get_next_trade_day(str_current_date):
    str_next_date = strtodate(str_current_date,1)
    while not is_open(df_open_date,str_next_date):
        str_next_date = strtodate(str_next_date,1)

    return str_next_date

    
def get_stock_close_from_tdx(stockcode):
    try:

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
    except Exception as e:
        return pd.DataFrame(columns=['trade_date','close']) 
    #return df.set_index('trade_date')
    #return tmplist

df_stock_list_H = pro.stock_basic(is_hs = 'H',exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
df_stock_list_S = pro.stock_basic(is_hs = 'S',exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')

df_open_date = pro.trade_cal(exchange='', start_date='20210101')

df_a = df_open_date[df_open_date['cal_date'] == '20211012']

#df_stock_list = df_stock_list_H.append(df_stock_list_S)
df_stock_list = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
df_stock_list = df_stock_list.drop_duplicates()

#list_ice_point_date = ['20210929','20211012','20211028']
list_ice_point_date = ['20211012','20211028']

leftmoney = 0.0 
totalbuymoney = 0.0
totalamount = 0.0
totalvolume = 0.0
totalsellmoney = 0.0
result_list = []

all_result_list = []
for i in range(len(df_stock_list)):
    every_result_list = []
    
    totalmoney = 200000.00

    stock_code = df_stock_list.iat[i,1]
    stock_name = df_stock_list.iat[i,2]
    df = get_stock_close_from_tdx(stock_code)

    if df.empty:
        continue

    #print(stock_name)

    for ice_point_date in list_ice_point_date:

        if  df[df['trade_date'] == int(ice_point_date)].empty:
            continue

        buy_close = df[df['trade_date'] == int(ice_point_date)].iat[0,1]

        thisamount = math.floor(totalmoney/buy_close/100) * 100

        thismoney = thisamount * buy_close

        leftmoney = totalmoney - thismoney

        str_next_trade_day  = get_next_trade_day(ice_point_date)

        if df[df['trade_date'] == int(str_next_trade_day)].empty:
            continue

        sell_close = df[df['trade_date'] == int(str_next_trade_day)].iat[0,1]

        totalmoney =  sell_close * thisamount + leftmoney

        #resultcsvtitle = ['操作日期','本次买入单价','本次卖出单价','本次股数','总资产']
        every_result_list.append([ice_point_date,buy_close,sell_close,thisamount,totalmoney])

    tmpdf = pd.DataFrame(data=every_result_list,columns=['操作日期','本次买入单价','本次卖出单价','本次股数','总资产'])
    tmpdf.to_csv('D:\\python_xls\\'+stock_code+'综合结果'+'.csv',encoding='utf_8_sig')



    all_result_list.append([stock_code,stock_name,round(totalmoney - 200000,0)])

tmpdf = pd.DataFrame(data=all_result_list,columns=['代码','名称','盈利额'])
tmpdf = tmpdf.sort_values(by = '盈利额',axis = 0,ascending = False).reset_index(drop=True)
tmpdf.to_csv('0综合结果'+'.csv',encoding='utf_8_sig')

