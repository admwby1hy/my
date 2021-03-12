import os
import sys
import time

project_name = os.path.basename(__file__).split(".")[0]
#print(project_name)
project_dir = os.path.abspath(os.path.dirname(__file__))
#print(project_dir)

root_path = os.path.dirname(project_dir)
sys.path.append(root_path)
#print(sys.path)

import myfunc as my

def main():
    ini_file = '%s\\%s.ini'%(project_dir,project_name)
    count_list = [0,0,0]
    count_list = my.read_ini(ini_file)

    logger = my.getLogger(project_dir)

    logger.info("开始啦")
    print('开始啦')
    #my.send_toaster('开始啦')
    
    while 1 == 1:
        try:
            now_localtime = time.strftime("%H:%M:%S", time.localtime())

            while my.istodayopen() == 0:
                print('今日休市')
                logger.info('今日休市')
                my.send_toaster('今日休市')
                time.sleep(my.cal_difftime(now_localtime,'23:59:59')+3600)

            if "00:00:00" <= now_localtime < "09:25:00":
                time.sleep(my.cal_difftime(now_localtime,'09:25:00'))

            if "09:25:00" <= now_localtime < "09:30:00":
                this_count = my.get_up_count()
                print('开盘竞价阶段：%s'%this_count)
                logger.info('开盘竞价阶段：%s'%this_count)
                my.send_toaster('开盘竞价阶段：%s'%this_count)
                time.sleep(60)

            if "11:30:00" < now_localtime < "13:00:00":
                print('午间休息')
                logger.info('午间休息')
                my.send_toaster('午间休息')
                time.sleep(my.cal_difftime(now_localtime,'13:00:00'))

            if "09:30:00" <= now_localtime <= "11:30:00" or "13:00:00" <= now_localtime <= "14:57:00":
                this_count = my.get_up_count()
                print('当前两市上涨个数:%s'%str(this_count))
                    
                logger.info('当前两市上涨个数:%s'%str(this_count))

                if 600 >= this_count > 500:
                    print('冰点来了，次日好转概率80%')
                    logger.info('冰点来了，次日好转概率80%')
                    my.send_toaster('冰点来了，次日好转概率80%')

                if 500 >= this_count > 400:
                    print('冰点来了，次日好转概率90%')
                    logger.info('冰点来了，次日好转概率90%')
                    my.send_toaster('冰点来了，次日好转概率90%')

                if this_count <= 400:
                    print('深冰冰点来了，次日好转概率100%')
                    logger.info('深冰冰点来了，次日好转概率100%')
                    my.send_toaster('深冰冰点来了，次日好转概率100%')
                        
                if 650 < int(count_list[0]) < 750 and this_count <= 400:
                    print('日内情绪冰点,请立即补票')
                    logger.info('日内情绪冰点,请立即补票')
                    my.send_toaster('日内情绪冰点,请立即补票')

                if 600 < this_count < 1000:
                    print('上涨个数小于1000，共'+str(this_count))
                    logger.info('上涨个数小于1000，共'+str(this_count))
                    my.send_toaster('上涨个数小于1000，共'+str(this_count))

                time.sleep(10)

            if "14:57:00" < now_localtime <= "15:01:00":
                this_count = my.get_up_count()
                print('收盘竞价阶段：%s'%this_count)
                logger.info('收盘竞价阶段：%s'%this_count)
                time.sleep(60)
                
            if "15:01:00" < now_localtime <= "15:05:00":
                this_count = my.get_up_count()

                print('最近三天收盘前：%s'%count_list)
                logger.info('最近三天收盘前：%s'%count_list)
                count_list[2] = count_list[1]
                count_list[1] = count_list[0]
                count_list[0] = str(this_count)
                my.write_ini(ini_file,count_list)
                print('最近三天收盘后：%s'%count_list)
                logger.info('最近三天收盘后：%s'%count_list)

                if int(count_list[2]) <= 1300 and int(count_list[1]) <= 1300 and int(count_list[0]) <= 1300:
                    print('连续3天跌破1300，明天好转概率接近100%')
                    logger.info('连续3天跌破1300，明天好转概率接近100%')
                    my.send_toaster('连续3天跌破1300，明天好转概率接近100%')
                        
                if int(count_list[2]) > 1300 and int(count_list[1]) <= 1300 and int(count_list[0]) <= 1300:
                    print('连续2天跌破1300，明天有概率好转')
                    logger.info('连续2天跌破1300，明天有概率好转')
                    my.send_toaster('连续2天跌破1300，明天有概率好转')
                
                print('冰点服务今日已完成!!!')
                logger.info('冰点服务今日已完成!!!')
                my.send_toaster('冰点服务今日已完成!!!')
                time.sleep(my.cal_difftime(now_localtime,'15:05:00'))

            if "15:05:00" < now_localtime <= "23:59:59":
                time.sleep(10)
                print('收盘了，我要休息了')
                logger.info('收盘了，我要休息了')
                my.send_toaster('收盘了，我要休息了')
                time.sleep(my.cal_difftime(now_localtime,'23:59:59'))

        except Exception as e:
            my.send_toaster('冰点服务异常!!!')
            logger.info(e)
            print(e)
            time.sleep(60)


if (__name__ == '__main__'):
    main()


"""
copied pywintypes37.dll and pythoncom37.dll to ..\Lib\site-packages\win32

https://maker.ifttt.com/trigger/{event}/with/key/w994LSAKNylJfUWT9cxwp

#安装服务
python PythonService.py install

#开启服务
python PythonService.py start

#停止服务
python PythonService.py stop

#移除服务
python PythonService.py remove



"""