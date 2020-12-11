from mystock import *
import time

pd.set_option('display.width', 1000)        # 设置字符显示宽度
pd.set_option('display.max_rows', None)     # 设置显示最大行

if istodayopen() == 1:

    stockcode = '510300'

    if stockcode[0:1] == '5':
        stocklist = get_shanghai_from_tushare()
    else:
        stocklist = get_anystock_from_tushare(stockcode)

    pbarray = np.array(stocklist,dtype=np.float64)

    ndays  = 480
    justvalue = 0.0
    history_pb_dif_dict = {}
    history_pb_dif_dict = get_ndays_average_stock_pb_dif(pbarray,ndays)

    trade_date = stocklist[len(stocklist)-1][0]
    pb = stocklist[len(stocklist)-1][1]

    if trade_date != datetime.datetime.strftime(datetime.date.today(),'%Y%m%d'):
        dif_pb = history_pb_dif_dict[int(trade_date)] 
    
        if abs(dif_pb)>=1:
            thismoney = abs(round(basetrade * dif_pb ** 1,2))
        else:               
            thismoney = abs(round(basetrade * dif_pb,2))
    
        #数量
        stockdf = get_stock_close_from_tushare(stockcode)
        stockdf = stockdf[stockdf['trade_date']==trade_date]
        close = stockdf.at[0,'close']
        thisamount = math.floor(thismoney/close/100) * 100

    
        if thisamount != 0:
            if dif_pb < 0:                  #买入
                #单价
                if stockcode[0:1] !=  '5':
                    if thismoney >= 20000:
                        thismoney = round(thisamount * close * (1 + 0.00025) + thisamount/10000,2)
                    else:
                        thismoney = round(thisamount * close + 5 + thisamount/10000,2)
                else:
                    thismoney = thisamount * close * (1 + 0.00025)
            
                i = send_email('提示日期：%s'%trade_date,'下个交易日买入数量：%d\n下个交易日买入单价：%.3f\n下个交易日买入花费金额（约等于）：%.2f'%(thisamount,close,thismoney))
                if i == 0:
                    print('邮件发送成功')
                else:
                    print('邮件发送失败')
            
            else:                           #卖出
                #单价
                if stockcode[0:1] !=  '5':
                    if thismoney >= 20000:
                        thismoney = round(thisamount * close * (1 + 0.00025) + thisamount/10000,2)
                    else:
                        thismoney = round(thisamount * close + 5 + thisamount/10000,2)
                else:
                    thismoney = thisamount * close * (1 + 0.00025)
            
                i = send_email('提示日期：%s'%trade_date,'下个交易日卖出数量：%d\n下个交易日卖出单价：%.3f\n下个交易日卖出收到金额（约等于）：%.2f'%(thisamount,close,thismoney))
                if i == 0:
                    print('邮件发送成功')
                else:
                    print('邮件发送失败')
        else:
            i = send_email('提示日期：%s'%trade_date,'下个交易日不用操作')
            if i == 0:
                print('邮件发送成功')
            else:
                print('邮件发送失败')

else:
    i = send_email('今天不开盘','出去玩啦')