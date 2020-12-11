from mystock import *
import time

pd.set_option('display.width', 1000)  # 设置字符显示宽度
pd.set_option('display.max_rows', None)  # 设置显示最大行


stockcode  = input("请输入证券代码(601398):")
if len(stockcode) == 0:
    stockcode = '601398'
#stockcode = '510300'

if stockcode[0:1] == '5':
    stocklist = get_shanghai_from_tushare()
else:
    stocklist = get_anystock_from_tushare(stockcode)
    
pbarray = np.array(stocklist,dtype=np.float64)

history_pb_dif_dict = {}
moni_list = []

starttime = time.process_time()

stockdf = get_stock_close_from_tdx(stockcode)

  

ndays  = 244 * 5
while ndays>=200:
    starttime = time.process_time()
    history_pb_dif_dict = get_ndays_average_stock_pb_dif(pbarray,ndays)

    startdate = '20150615'  
    #startdate = history_pb_dif_dict[19000000]                 #从20181028开始买
    while startdate<='20190630':

        tmpstockdf = stockdf[stockdf['trade_date']>=int(startdate)]
        tmpstockdf = tmpstockdf.reset_index(drop=True)

        d = 0.1
        while d>=-0.1:
            tmplist = moni(stockcode,history_pb_dif_dict,tmpstockdf,ndays,round(d,2))

            if not tmplist:
                d -= 0.01
                continue

            d -= 0.01
            moni_list.append(tmplist)

        startdate = strtodate(startdate,30)

    endtime = time.process_time()
    print (endtime - starttime)
    print(ndays)
    ndays -= 10

tmpdf = pd.DataFrame(data=moni_list,columns=['开始日期','结束日期','ndays','justvalue','累计买入金额','累计卖出金额','股票剩余资产','IRR','操作次数'])
tmpdf.to_csv(stockcode+'综合结果'+'.csv',encoding='utf_8_sig')
#endtime = time.process_time()
#print (endtime - starttime)





