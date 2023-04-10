import glob
import os.path
from typing import List, Dict

import px4tools
# import px4tools.logsysid
import pandas as pd
import numpy as np
import control
import json
from pyulog import ULog
import datetime
import matplotlib.pyplot as plt


def show_topic_list(ulog: ULog) -> None:
    topics = [t.name for t in ulog.data_list]
    print(topics)


def show_filed_list(ulog: ULog, topic_name: str) -> None:
    fields = []
    for t in ulog.data_list:
        if t.name == topic_name:
            fields = [f.field_name for f in t.field_data]
    print(fields)


def log_data(ulog: ULog, topic_name: str, messages: str) -> List:
    if messages:
        msg_filter = [m.strip() for m in messages.split(',')]
    else:
        msg_filter = None
    return [ulog.get_dataset(topic_name).data[m] for m in msg_filter]


def log_dic(ulog: ULog, topic_name: str) -> Dict:
    fields = []
    for t in ulog.data_list:
        if t.name == topic_name:
            fields = [f.field_name for f in t.field_data]

    return {f: ulog.get_dataset(topic_name).data[f] for f in fields}


def check_error(ulog: ULog) -> None:
    stat = log_dic(ulog, "vehicle_status")
    rtk = log_dic(ulog, "piksi_rtk")
    lpos = log_dic(ulog, "vehicle_local_position")

    nav = pd.DataFrame({'stat': stat['nav_state']})
    gt = pd.DataFrame({'rtk': rtk['nsats']})
    et = pd.DataFrame({'lpos': lpos['x']})
    df = pd.concat([gt, et], axis=1)
    df = df.interpolate()

    df = (df['rtk'] - df['lpos']).abs()
    df = [d for d in df[100:] if d > 0.]

    print('mean: ', np.mean(df))
    print('max : ', np.max(df))


def search_latest_ulog(path):
    list_of_files = glob.glob(path + '*.ulg')
    return max(list_of_files, key=os.path.getctime)

def main():
    ulog_path = ''
    ulog_file = 'logfile/07_59_42.ulg'
    offset = 0.051 * 1e8

    # ulog_file = /home/stmoon/Project/PX4/Firmware.px4/build/posix_sitl_lpe_replay/logs/2018-05-03/08_34_01_replayed.ulg
    # offset = 0.0

    data_len = 500

    # replay_path = ''
    # replay_file = search_latest_ulog(replay_path + '2018-05-04/')
    replay_file = 'logfile/08_00_54.ulg'

    print(ulog_file)
    print(replay_file)

    try:
        ulog = ULog(ulog_file, None)
    except:
        print("ERROR: cannot open file ", ulog_file)

    try:
        replay = ULog(replay_file, None)
    except:
        print("ERROR: cannot open file ", replay_file)
    # show_topic_list(ulog)
    # show_field_list(ulog, vehicle_status)
    check_error(ulog)
    print(type(ulog))
    status = log_dic(ulog, "vehicle_status")
    gps = log_dic(ulog, "vehicle_gps_position")
    rtk = log_dic(ulog, "piksi_rtk")
    lpos = log_dic(ulog, "vehicle_local_position")
    lpsp = log_dic(ulog, "vehicle_local_position_setpoint")
    sensor = log_dic(ulog, "sensor_combined")
    att = log_dic(ulog, "vehicle_attitude")
    rate = log_dic(ulog, "vehicle_rates_setpoint")

    gps_rp = log_dic(replay, "vehicle_gps_position")
    status_rp = log_dic(replay, "vehicle_status")
    rtk_rp = log_dic(replay, "piksi_rtk")
    lpos_rp = log_dic(replay, "vehicle_local_position")
    lpsp_rp = log_dic(replay, "vehicle_local_position_setpoint")
    sensor_rp = log_dic(replay, "sensor_combined")

    plt.figure(figsize=(20, 8), dpi=200, facecolor='w', edgecolor='k')

    # plt.ylim(2,5)
    # Plot the data

    # plt.plot(att['timestamp'], att['yawspeed'], label='att_yawspeed')

    # plt.plot(rtk['timestamp'], rtk['vd'], label='rtk_vd')
    plt.plot(lpos['timestamp'][:data_len], lpos['z'][:data_len], label='lpos_z')
    # plt.plot(lpsp['timestamp'][:data_len], lpsp['z'][:data_len], label='lpsp_vx')
    # plt.plot(status['timestamp'][:30], status['nav_state'][:30]*0.1, label='status_rp')

    plt.plot(lpos_rp['timestamp'][:data_len] + offset, lpos_rp['z'][:data_len], label='lpos_rp_z')
    # plt.plot(lpsp_rp['timestamp'][:data_len]+offset, lpsp_rp['z'][:data_len], label='lpsp_rp_vx')
    plt.plot(rtk_rp['timestamp'][:data_len] + offset, rtk_rp['d'][:data_len] - 1.45, label='rtk_rp_vx')

    # Title
    plt.title("Position Error")

    #Add a legend
    plt.legend(loc='upper right')

    #Show the plot
    plt.show()


if __name__ == '__main__':
    main()
