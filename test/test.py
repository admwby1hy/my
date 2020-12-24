
#from mystock import *
#import requests

#import time
#import math
#import numpy as np

#import configparser
import os
import sys
import time
from pytdx.hq import TdxHq_API
#import json


project_name = os.path.basename(__file__).split(".")[0]
print(project_name)
project_dir = os.path.abspath(os.path.dirname(__file__))
print(project_dir)

root_path = os.path.dirname(project_dir)
sys.path.append(root_path)
print(sys.path)

import myfunc as my
now_localtime = time.strftime("%H:%M:%S", time.localtime())
print(now_localtime)

print(my.cal_difftime('00:00:03','23:59:59'))
print(my.cal_difftime('00:00:03','15:30:01'))

import re,urllib2,urllib
 
user = {'session[username_or_email]':'hejiang72@gmail.com','session[password]':'hjhmhbwwfx'}
data = {
    'status':"""
Send by Python!
""",
    'tab':'home',
    'source':'web',
    }
 
def u(s, encoding):
    if isinstance(s, unicode):
        return s
    else:
        try:
            return unicode(s, encoding)
        except:
            return s
 
def send(user=user,data=data):
    c = urllib2.HTTPCookieProcessor()
    builder = urllib2.build_opener(c)
    url = 'https://twitter.com/sessions'
    request = urllib2.Request(
        url=url,
        data = urllib.urlencode(user)
        )
    d = builder.open(request)
    r = re.compile('<input name="authenticity_token" type="hidden" value="(.*?)" />')
    x = d.read()
    if len(re.compile(r"name=\"session\[username_or_email\]\"").findall(x))>0:
        print( "Login Error!" )
        return False
    auth = {'authenticity_token':r.findall(x)[0]}
    send = '%s&%s'%(
        urllib.urlencode(auth),
        urllib.urlencode(data)
        )
    request = urllib2.Request(
        url='http://twitter.com/status/update',
        data = send ,
        )
    builder.open(request)
    return True
 
if __name__=="__main__":
    import sys
    if len(sys.argv)>1 and sys.argv[1]!="":
        data["status"] = u(" ".join(sys.argv[1:]),"gb2312").encode("utf-8")
    if send():
        print ('ok')




"""

api = TdxHq_API()

while 0==0:
    try:
        with api.connect('119.147.212.81', 7709):
            data = api.get_security_quotes([(1, '880005')])
        print(time.strftime("%H:%M:%S", time.localtime()),data[0]['price'])
    except Exception as e:
        print(e)

    time.sleep(60)
this_file = inspect.getfile(inspect.currentframe())
dirpath = os.path.abspath(os.path.dirname(this_file))

logger = myfunc.getLogger(dirpath)

logger.info("开始啦")

#print(__name__)

os.path.abspath(os.path.dirname(__file__)).join()
abc = os.path.abspath(os.path.dirname(__file__)).split('\\')

print(os.path.abspath(os.path.dirname(__file__)).split('//')[1])
    
    

pd.set_option('display.width', 1000)        # 设置字符显示宽度
pd.set_option('display.max_rows', None)     # 设置显示最大行

irrdf = pd.DataFrame()
irrdf = irrdf.append([[-110]])
print(irrdf)

print(np.irr(irrdf[0])*100)

irrdf = irrdf.append([[100+10]])
print(np.irr(irrdf[0])*100)


def read_ini(ini_file):
    count = [0,0,0]
    cf = configparser.ConfigParser()
    cf.read(ini_file)

    secs = cf.sections() 

    for i,sec in enumerate(secs):
        count[i] = cf.get(sec, "value")

    return count

def write_ini(ini_file,count):
    cf = configparser.ConfigParser()
    cf.read(ini_file)

    secs = cf.sections() 
    for i,item in enumerate(secs):
        cf.set(item,'value',str(count[i]))

    o = open(ini_file, 'w')
    cf.write(o)
    o.close()       #不要忘记关闭


#"Content-Type: application/json" -d '{"value1":"hello world"}' https://maker.ifttt.com/trigger/notice_phone/with/key/w994LSAKNylJfUWT9cxwp
def send_notice(event_name, key, text):
    url = "https://maker.ifttt.com/trigger/"+event_name+"/with/key/"+key+""

    msg = {'value1':''}
    msg['value1'] = text 
    headers = {
    'Content-Type': "application/json"
    }
    reutnrcode = requests.request("POST", url, data=json.dumps(msg), headers=headers)
    data=json.dumps(msg,ensure_ascii=False)
    print(data)

def get_up_count(webname='ths'):
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        '(KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        }

    if webname == 'ths':
        try:
            #从同花顺取值
            url = 'http://q.10jqka.com.cn/api.php?t=indexflash&'
            html=requests.get(url,headers=headers)
            jsoninfo = json.loads(html.text)
            this_count = jsoninfo['zdfb_data']['znum'] 
            return this_count

        except Exception as e:
            #从东方财富取值
            url = 'http://push2.eastmoney.com/api/qt/ulist.np/get?fid=f3&pi=0&pz=20&po=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&fields=f104&np=1&secids=1.000001,0.399001'
            html=requests.get(url,headers=headers)
            jsoninfo = json.loads(html.text)
            this_count = jsoninfo['data']['diff'][0]['f104'] + jsoninfo['data']['diff'][1]['f104'] - 30
            return this_count

    if webname == 'dfcf':
        try:
            #从东方财富取值
            url = 'http://push2.eastmoney.com/api/qt/ulist.np/get?fid=f3&pi=0&pz=20&po=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&fields=f104&np=1&secids=1.000001,0.399001'
            html=requests.get(url,headers=headers)
            jsoninfo = json.loads(html.text)
            this_count = jsoninfo['data']['diff'][0]['f104'] + jsoninfo['data']['diff'][1]['f104'] - 30
            return this_count
            
        except Exception as e:
            #从同花顺取值
            url = 'http://q.10jqka.com.cn/api.php?t=indexflash&'
            html=requests.get(url,headers=headers)
            jsoninfo = json.loads(html.text)
            this_count = jsoninfo['zdfb_data']['znum'] 
            return this_count

a = get_up_count()
b = get_up_count('dfcf')
c = get_up_count('ths')

print(get_up_count())
print(get_up_count('ths')) 
print(get_up_count('dfcf'))


    



#send_notice('notice_phone', 'w994LSAKNylJfUWT9cxwp', '今日休市1')

#r = requests.get('http://q.10jqka.com.cn')
#headers = 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'
headers = {
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                '(KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
           }
#r1 = requests.request("POST", 'http://q.10jqka.com.cn', data='', headers=headers)
#r2 = r1.content.decode("gbk")

url = "http://q.10jqka.com.cn/api.php?t=indexflash&"
html=requests.get(url,headers=headers)
jsoninfo = json.loads(html.text)
this_count = jsoninfo['zdfb_data']['znum']

dict = {'value1':'今日休市1'}
print(dict)

this_file = inspect.getfile(inspect.currentframe())
dirpath = os.path.abspath(os.path.dirname(this_file))
print(this_file)
print(dirpath)

if os.path.isdir('%s\\ini'%dirpath):  #创建log文件夹
    pass
else:
    os.mkdir('%s\\ini'%dirpath)

dir = '%s\\ini' % dirpath

print(dir)

ini_file = '%s.ini'%(this_file)
if os.path.isfile('%s.ini'%(this_file)):
    print('yes')
else:
    print('no')

print('%s.ini'%(this_file))


cf = configparser.ConfigParser()
cf.read(ini_file)  # 读取配置文件，如果写文件的绝对路径，就可以不用os模块

secs = cf.sections()  # 获取文件中所有的section(一个配置文件中可以有多个配置，如数据库相关的配置，邮箱相关的配置，
                      # 每个section由[]包裹，即[section])，并以列表的形式返回
print(secs)

options = cf.options("count_3")  # 获取某个section名为Mysql-Database所对应的键
print(options)

items = cf.items("count_3")  # 获取section名为Mysql-Database所对应的全部键值对
print(items)

value1 = cf.get("count_1", "value")  # 获取[Mysql-Database]中host对应的值
print(value1)


count = [2176,2087,2343]
print('最近三天：%s'%count)

count1 = read_ini(ini_file)
print('最近三天：%s'%count1)

write_ini(ini_file,count)

i = 1
#for item in secs:
for i,item in enumerate(secs):
    cf.set(item,'value',str(i+1))
    print(i,item)

o = open(ini_file, 'w')
cf.write(o)
o.close()#不要忘记关闭



[count_1]
value = 2176

[count_2]
value = 2087

[count_3]
value = 2343


def compute_amount(a):
    b = math.floor((a+0.005) * 100)
    return 100*b

print(compute_amount(0.001))
print(compute_amount(0.006))
print(compute_amount(0.011))
print(compute_amount(0.016))
print(compute_amount(0.171))





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
while ndays>=1200:
    starttime = time.process_time()
    history_pb_dif_dict = get_ndays_average_stock_pb_dif(pbarray,ndays)

    startdate = '20150615'  
    #startdate = str(int(history_pb_dif_dict[19000000]))
    while startdate<='20191030':

        tmpstockdf = stockdf[stockdf['trade_date']>=int(startdate)]
        tmpstockdf = tmpstockdf.reset_index(drop=True)

        d = 0.2
        while d>=-0.2:
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
"""