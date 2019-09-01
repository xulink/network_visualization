#!/usr/bin/python
# coding=utf-8
import sys
sys.path.append('../')

import csv
import json
from data_analyze.analysis import Analyzer


# TODO 获取位置
def getLocation():
    return 1, 1, 1

# TODO 获取设备
def getDevice():
    return 'computer'

def _save_res(res):
    json_str = json.dumps({'point_data': res})
    with open('../data/res.json', 'w') as wf:
        wf.write(json_str)
    wf.close()

def _save_send(send):
    json_str = json.dumps({'send_data': send})
    with open('../data/send.json', 'w') as wf:
        wf.write(json_str)
    wf.close()

def process(input_file='../data/20180630_anomalous_suspicious.csv', file_type='csv'):

    reader = csv.reader(open(input_file))
    ipIdDict = dict()

    res = []
    st = ''
    des = ''
    send = []
    message = []
    for list in reader:
        if list[1] == '' or list[3] == '':
            continue
        # 很trick，不要第一行
        if list[0] == 'anomalyID':
            continue
        if not ipIdDict.__contains__(list[1]) and list[1] != '':
            ipIdDict[list[1]] = len(ipIdDict)
        if not ipIdDict.__contains__(list[3]) and list[3] != '':
            ipIdDict[list[3]] = len(ipIdDict)
        id1 = ipIdDict[list[1]]
        id2 = ipIdDict[list[3]]
        if len(res) >= id1:
            pointDict = dict()
            pointDict["id"] = id1
            pointDict["ip"] = list[1]
            x,y,z = getLocation()
            loc = dict()
            loc["x"] = x
            loc["y"] = y
            loc["z"] = z
            pointDict["location"] = loc
            pointDict["device"] = getDevice()
            pointDict["link"] = [id2]
            res.append(pointDict)
        if len(res) >= id2:
            pointDict = dict()
            pointDict["id"] = id2
            pointDict["ip"] = list[3]
            x,y,z = getLocation()
            loc = dict()
            loc["x"] = x
            loc["y"] = y
            loc["z"] = z
            pointDict["location"] = loc
            pointDict["device"] = getDevice()
            pointDict["link"] = [id2]
            pointDict["link"] = [id1]
            pointDict["device"] = getDevice()
            res.append(pointDict)

        if len(res[id1]["link"]) == 0 or res[id1]["link"].count(id2) == 0:
            res[id1]["link"].append(id2)
        if len(res[id2]["link"]) == 0 or res[id2]["link"].count(id1) == 0:
            res[id2]["link"].append(id1)

        if st == '' or des == '':
            st = list[1]
            des = list[3]
            messDict = dict()
            messDict["taxonomy"] = list[5]
            messDict["srPort"] = list[2]
            messDict["dstPort"] = list[4]
            messDict["length"] = 1
            message.append(messDict)
        elif st == list[1] and des == list[3]:
            messDict = dict()
            messDict["taxonomy"] = list[5]
            messDict["srPort"] = list[2]
            messDict["dstPort"] = list[4]
            messDict["length"] = 1
            message.append(messDict)
        else:
            sendDict = dict()
            sendDict["srcID"] = ipIdDict[st]
            sendDict["desID"] = ipIdDict[des]
            messDict = dict()
            messDict["taxonomy"] = list[5]
            messDict["srPort"] = list[2]
            messDict["dstPort"] = list[4]
            messDict["length"] = 1
            message.append(messDict)
            sendDict["message"] = message
            send.append(sendDict)
            message = []
            st = list[1]
            des = list[3]

    analyzer = Analyzer(res)
    res = analyzer.process()
    _save_res(res)
    _save_send(send)


if __name__ == '__main__':
    process()

