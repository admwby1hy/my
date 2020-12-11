
import os
import sys
import time

import win32.lib.win32serviceutil as win32serviceutil
import win32.win32service as win32service
import win32.win32event as win32event


project_name = os.path.basename(__file__).split(".")[0]
#print(project_name)
project_dir = os.path.abspath(os.path.dirname(__file__))
#print(project_dir)

root_path = os.path.dirname(project_dir)
sys.path.append(root_path)
#print(sys.path)

import myfunc as my

class PythonService(win32serviceutil.ServiceFramework):
    _svc_name_ = "PythonService"                        #服务名
    _svc_display_name_ = "PythonService"                #job在windows services上显示的名字
    _svc_description_ = "计算两市股票上涨的个数"        #job的描述

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.logger = my.getLogger(project_dir)
        self.T = time.time()
        self.run = True
        self.ini_file = '%s\\%s.ini'%(project_dir,project_name)
    
    def SvcDoRun(self):
        count_list = ['','','']
        count_list = my.read_ini(self.ini_file)

        self.logger.info("冰点服务开始运行....")
        my.send_notice('冰点服务开始运行....')

        while self.run:
            try:
                now_localtime = time.strftime("%H:%M:%S", time.localtime())
                
                while my.istodayopen() == 0:
                    self.logger.info('今日休市')
                    my.send_notice('今日休市')
                    time.sleep(my.cal_difftime(now_localtime,'23:59:59'))

                if "00:00:00" <= now_localtime < "09:29:00":
                    time.sleep(my.cal_difftime(now_localtime,'09:29:00'))

                if "09:29:00" <= now_localtime < "09:30:30":
                    this_count = my.get_up_count()
                    self.logger.info('开盘竞价阶段：%s'%this_count)
                    my.send_notice('开盘竞价阶段：%s'%this_count)
                    time.sleep(my.cal_difftime(now_localtime,'09:30:30'))

                if "11:30:00" < now_localtime < "13:00:00":
                    self.logger.info('午间休息')
                    my.send_notice('午间休息')
                    time.sleep(my.cal_difftime(now_localtime,'13:00:00'))

                if "09:30:30" <= now_localtime <= "11:30:00" or "13:00:00" <= now_localtime <= "15:00:00":
                    this_count = my.get_up_count()
                    
                    self.logger.info('当前两市上涨个数:'+str(this_count))

                    if 600 >= this_count > 500:
                        self.logger.info('冰点来了，次日好转概率80%')
                        my.send_notice('冰点来了，次日好转概率80%') 
                        time.sleep(60)
                    
                    if 500 >= this_count > 400:
                        self.logger.info('冰点来了，次日好转概率90%')
                        my.send_notice('冰点来了，次日好转概率90%')
                        time.sleep(60)

                    if this_count <= 400:
                        self.logger.info('深冰冰点来了，次日好转概率100%')
                        my.send_notice('深冰冰点来了，次日好转概率100%)')
                        time.sleep(60)
                        
                    if 650 < int(count_list[0]) < 750 and this_count <= 400:
                        self.logger.info('日内情绪冰点,请立即补票')
                        my.send_notice('日内情绪冰点,请立即补票)')
                        time.sleep(60)

                    if 600 < this_count < 800:
                        self.logger.info('上涨个数小于800，共'+str(this_count))
                        my.send_notice('上涨个数小于800，共'+str(this_count))
                        time.sleep(120)

                    time.sleep(60)

                if "15:00:00" < now_localtime <= "15:01:00":
                    this_count = my.get_up_count()

                    self.logger.info('收盘竞价阶段：%s'%this_count)
                    my.send_notice('收盘竞价阶段：%s'%this_count)
                    time.sleep(my.cal_difftime(now_localtime,'15:01:00'))
                
                if "15:01:00" < now_localtime <= "16:05:00":
                    this_count = my.get_up_count()
                    
                    self.logger.info('最近三天收盘前：%s'%count_list)
                    count_list[2] = count_list[1]
                    count_list[1] = count_list[0]
                    count_list[0] = str(this_count)
                    my.write_ini(self.ini_file,count_list)
                    self.logger.info('最近三天收盘后：%s'%count_list)

                    if int(count_list[2]) <= 1300 and int(count_list[1]) <= 1300 and int(count_list[0]) <= 1300:
                        self.logger.info('连续3天跌破1300，明天好转概率接近100%')
                        my.send_notice('连续3天跌破1300，明天好转概率接近100%')
                        
                    if int(count_list[2]) > 1300 and int(count_list[1]) <= 1300 and int(count_list[0]) <= 1300:
                        self.logger.info('连续2天跌破1300，明天有概率好转')
                        my.send_notice('连续2天跌破1300，明天有概率好转')
                           
                    self.logger.info('冰点服务今日已完成,最终上涨个数：%s'%this_count)
                    my.send_notice('冰点服务今日已完成,最终上涨个数：%s'%this_count)
                    time.sleep(my.cal_difftime(now_localtime,'16:05:00'))

                if "16:05:00" < now_localtime <= "23:59:59":
                    self.logger.info('收盘了，我要休息了')
                    my.send_notice('收盘了，我要休息了')
                    time.sleep(my.cal_difftime(now_localtime,'23:59:59'))

            except Exception as e:
                self.logger.info('冰点服务异常!!!')
                self.logger.info(e)
                my.send_notice('冰点服务异常!!!')
                time.sleep(60)

    def SvcStop(self):
        self.logger.info("冰点服务停止运行....")
        my.send_notice('冰点服务停止运行....')
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.run = False


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(PythonService)

"""
备注
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