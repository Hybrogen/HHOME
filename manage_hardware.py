#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import json
import time

def ttime(gt_mode: str = 'all'):
    if gt_mode == 'all': return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    temp_strs = {
        'all': '%Y-%m-%d %H:%M:%S',
        'year': '%Y',
        'mounth': '%m',
        'day': '%d',
        'hour': '%H',
        'minute': '%M',
        'second': '%S',
    }
    return int(time.strftime(temp_strs[gt_mode], time.localtime(time.time())))

def hlog(msg, msg_type = 'info'):
    if msg_type in ['info']: return
    print(f"{ttime()} - {msg_type}: {msg}")

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

h_config = {
        'temperature': 24,
        'humidity': 50,
        'light': 5,
        'curtain_auto': True,
        'curtain_state': True,
        'water_auto': True,
        'water_state': True,
    }

HCONFIGS = HARDMODULEDIR + "/thresholds"
check_file('file', HCONFIGS, json.dumps(h_config))

RECONFIG = HCONFIGS + '_reset'

PORTID = 1

def reset_threshold(h_config, first_init: bool = False):
    if os.path.isfile(RECONFIG):
        hlog(f"reset_threshold - 有 {RECONFIG} 文件")
        with open(RECONFIG, encoding = 'utf8') as f:
            h_config = json.loads(f.readline())
        os.rename(RECONFIG, HCONFIGS)
        hlog(f"reset_threshold - 新 config = {h_config}")
        return h_config
    if first_init and os.path.isfile(HCONFIGS):
        with open(HCONFIGS, encoding = 'utf8') as f:
            h_config = json.loads(f.readline())
    return h_config

def update_threshold_file(h_config):
    with open(HCONFIGS, 'w', encoding = 'utf8') as f: f.write(json.dumps(h_config))

################################## 初始化各个模块 ##################################
from HModules import HActuator, HMySQL, HSensors

sql = HMySQL.HSQL('HGreenhouse')
s_light = HSensors.IOSENSOR(5)
s_dht = HSensors.DHT(23, 'DHT22')
a_curtain = HActuator.SteeppingMOTOR([6, 13, 19, 26])
a_water = HActuator.HRELAY(24)

################################  定义各个功能模块  ################################

def module_1_autoWater(h_config) -> int:
    start_run_time = time.time()
    # h_config = reset_threshold(h_config)
    data = s_dht.check()
    if data.get('state') == 'error': return
    data['pid'] = PORTID
    sql.dht_save(data)
    humidity, temperature = data['humidity'], data['temperature']

    hlog(f"检测到温湿度数据: data = {data}", 'data')
    waterOn = humidity < h_config['humidity'] or temperature > h_config['temperature']
    a_water.run(waterOn)
    h_config['water_state'] = waterOn
    update_threshold_file(h_config)
    return ((10 if waterOn else 600) - int(time.time() - start_run_time), h_config)

def module_2_autoCurtain(h_config) -> int:
    start_run_time = time.time()
    # h_config = reset_threshold(h_config)
    have_light = s_light.check()
    data = dict()
    data['pid'] = PORTID
    data['light'] = 22.2
    sql.light_save(data)

    # 自动模式 - 
    if h_config['curtain_auto']:
        if have_light == h_config['curtain_state']:
            a_curtain.run(not have_light)
            h_config['curtain_state'] = not have_light
            update_threshold_file()
    # 手动模式 - 如果检测状态与手动设定状态不同，活动窗帘
    # 并将窗帘重置为自动模式
    else:
        h_config['curtain_auto'] = True
        a_curtain.run(h_config['curtain_state'])
        update_threshold_file(h_config)

    hlog(f"检测到光照度数据: have_light = {have_light}", 'data')
    return (600 - int(time.time() - start_run_time), h_config)

def main(h_config):
    h_config = reset_threshold(h_config, True)
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
        # hlog(f"os.path.isfile({RECONFIG}) = {os.path.isfile(RECONFIG)}")
        # hlog(f"h_config = {h_config}\n{'-'*100}")
        # input()
        if os.path.isfile(RECONFIG):
            hlog(f"main 存在文件 {RECONFIG}")
            h_config = reset_threshold(h_config)
            for module in modules_run_info.keys():
                modules_run_info[module]['run_interval'] = 1
        for module in modules_run_info.keys():
            time.sleep(1)
            # if int(time.time() - modules_run_info[module]['last_run_time']) > modules_run_info[module]['run_interval']:
            #     modules_run_info[module]['run_interval'], h_config = eval(f"module_{module}")(h_config)
            #     modules_run_info[module]['last_run_time'] = time.time()
            try:
                if int(time.time() - modules_run_info[module]['last_run_time']) > modules_run_info[module]['run_interval']:
                    modules_run_info[module]['run_interval'], h_config = eval(f"module_{module}")(h_config)
                    modules_run_info[module]['last_run_time'] = time.time()
            except TypeError:
                hlog(f"main module = {module}", 'error')
                modules_run_info[module]['run_interval'] = 1

if __name__ == '__main__':
    try:
        main(h_config)
    except KeyboardInterrupt:
        hlog('智能温室大棚硬件系统停止工作')
