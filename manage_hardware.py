#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import json
import time

def check_file(f_type: str, f_name: str, content: str = "{}"):
    if f_type == 'dir' and not os.path.isdir(f_name):
        if os.path.isfile(f_name): raise Exception(f"已存在同名文件 [{f_name}]，请检查系统所需文件夹路径是否被占用")
        else: os.mkdir(f_name)
    elif f_type == 'file' and not os.path.isfile(f_name):
        if os.path.isdir(f_name): raise Exception(f"已存在同名文件夹 [{f_name}]，请检查系统所需文件路径是否被占用")
        else:
            with open(f_name, 'w', encoding = 'utf8') as f: f.write(content)

HARDMODULEDIR = "HModules"
check_file('dir', HARDMODULEDIR)

LCONFIGS = HARDMODULEDIR + "/light_config"

PORTID = 1

################################## 初始化各个模块 ##################################
from HModules import HActuator, HMySQL, HSensors, HConfig, HLog

# 数据库
sql = HMySQL.HSQL('HHOME')
# 传感器
s_dht = HSensors.DHT(21, 'DHT22')
# Adoor = HActuator.SteeppingMOTOR([6, 13, 19, 26])
Adoor = HActuator.([6, 13, 19, 26])
Aheater = HActuator.HRELAY(16)
Ahumidifier = HActuator.HRELAY(20)
lightPins = [19, 26]
Alight = [HActuator.HRELAY(pin) for pin in lightPins]
# 其他模块
hconf = HConfig.CONFIG(LCONFIGS, LCONFIGS + '_rest')
log = HLog.LOG()

################################  定义各个功能模块  ################################

def module_1_autoWater() -> int:
    start_run_time = time.time()
    data = s_dht.check()
    if data.get('state') == 'error': return
    data['pid'] = PORTID
    sql.dht_save(data)
    humidity, temperature = data['humidity'], data['temperature']

    log.ldata(f"检测到温湿度数据: data = {data}")
    waterOn = humidity < hcond.get_data(['humidity']) or temperature > hcond.get_data(['temperature'])
    a_water.run(waterOn)
    hconf.updata('water_state', waterOn)
    return (10 if waterOn else 600) - int(time.time() - start_run_time)

def module_2_autoCurtain() -> int:
    start_run_time = time.time()
    have_light = s_light.check()
    data = dict()
    data['pid'] = PORTID
    data['light'] = 22.2
    sql.light_save(data)

    # 自动模式 - 
    if hcond.get_data(['curtain_auto']):
        if have_light == hconf.get_data(['curtain_state']):
            a_curtain.run(not have_light)
            hconf.updata('curtain_state', not have_light)
    # 手动模式 - 如果检测状态与手动设定状态不同，活动窗帘
    # 并将窗帘重置为自动模式
    else:
        a_curtain.run(hconf.get_data(['curtain_state']))
        hconf.updata('curtain_auto', True)

    log.ldata(f"检测到光照度数据: have_light = {have_light}")
    return 600 - int(time.time() - start_run_time)

def main():
    modules_run_info = {
        '1_autoWater': {
            'last_run_time': time.time(),
            'run_interval': 6,
        },
        '2_autoCurtain': {
            'last_run_time': time.time(),
            'run_interval': 6,
        },
    }
    while True:
        if hconf.setFile:
            log.linfo(f"main 存在文件 {RECONFIG}")
            for module in modules_run_info.keys():
                modules_run_info[module]['run_interval'] = 1
        for module in modules_run_info.keys():
            time.sleep(1)
            try:
                if int(time.time() - modules_run_info[module]['last_run_time']) > modules_run_info[module]['run_interval']:
                    modules_run_info[module]['run_interval'] = eval(f"module_{module}")()
                    modules_run_info[module]['last_run_time'] = time.time()
            except TypeError:
                log.lerror(f"main module = {module}")
                modules_run_info[module]['run_interval'] = 1

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log.log('个性化智能房屋硬件系统停止工作', 'exit')
