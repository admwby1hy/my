from mystock import *
import time

starttime = time.process_time()

pd.set_option('display.width', 1000)  # 设置字符显示宽度
pd.set_option('display.max_rows', None)  # 设置显示最大行

stockcode  = input("请输入证券代码(510300):")
if len(stockcode) == 0:
    stockcode = '510300'

strndays = input("请输入ndays(480):")
if len(strndays) == 0:
    ndays = 480 #244 * 5
else:
    ndays = int(strndays)

strjustvalue = input("请输入justvalue(0):")
if len(strjustvalue) == 0:
    justvalue = 0.0
else:
    justvalue = round(float(strjustvalue),2)


startdate = '20190828'

df = monimingxi1(stockcode,startdate,ndays,justvalue)
df.to_csv(stockcode+'_'+str(ndays)+'_'+str(justvalue)+'_result.csv',encoding='utf_8_sig')

endtime = time.process_time()
print (endtime - starttime)

