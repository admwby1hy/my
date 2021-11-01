import pandas as pd
import math

pd.set_option('display.width', 1000)  # 设置字符显示宽度
pd.set_option('display.max_rows', None)  # 设置显示最大行

stockcode  = input("请输入证券代码:")
if len(stockcode) == 0:
    stockcode = '510300'

startdate = istartdatenput("请输入起始日期:")
if len(startdate) == 0:
    stockcode = '19900101'


basetrade = 20000

stock_df = pd.read_csv(stockcode + '.csv')
#stock_df = stock_df.sort_values(by = 'trade_date',axis = 0,ascending = True).reset_index(drop=True)

stock_df = stock_df[stock_df['trade_date']>=int(startdate)]
stock_df = stock_df.sort_values(by = 'trade_date',axis = 0,ascending = True).reset_index(drop=True)

thismoney = 0.0 
totalbuymoney = 0.0
totalamount = 0.0
totalvolume = 0.0
totalsellmoney = 0.0

result_list = []
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

    if abs(dif_pb)>=0.5:
        thismoney = abs(round(basetrade * dif_pb * 1,2))
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

        if thisamount == 0:
            thismoney = 0.0

        totalbuymoney = totalbuymoney + thismoney
        totalamount = totalamount + thisamount
        totalvolume = round(totalamount * close,2)
         
        #resultcsvtitle = ['操作日期','操作月份','PB-PB*','本次单价','本次金额','累计买入金额','累计卖出金额','股票剩余资产']
        result_list.append([trade_date,round(dif_pb,3),close,-thismoney,totalbuymoney,totalsellmoney,totalvolume])


    #当前pb大于ndays天pb均线，卖    
    else:
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

        if thisamount == 0:
            thismoney = 0.0

        totalamount = totalamount - thisamount
        totalvolume = round(totalamount * close,2)
        totalsellmoney = totalsellmoney + thismoney

        #resultcsvtitle = ['操作日期','操作月份','PB-PB*','本次单价','本次金额','累计买入金额','累计卖出金额','股票剩余资产']
        result_list.append([trade_date,round(dif_pb,3),close,thismoney,totalbuymoney,totalsellmoney,totalvolume])

pd.DataFrame(data=result_list,columns=['trade_date','dif_pb','close','本次金额','累计买入金额','累计卖出金额','股票剩余资产']).to_csv(stockcode+'_result.csv',encoding='utf_8_sig')


    