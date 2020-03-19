# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime
from urllib import parse
import jsonpath
import re
import time
import requests
import math
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
import csv
import random
import sys
import pandas as pd
import pymongo
from pymongo import MongoClient

db = MongoClient('127.0.0.1', 28017).judge
nlist = db.court
nlist2 = db.judge
nlist3 = db.judge_nodata


class Judges():
    def __init__(self):
        self.url1 = "https://splcgk.court.gov.cn/gzfwww//getFyLbBySf"
        self.url2 = 'https://splcgk.court.gov.cn/gzfwww//getFyLbByXq'
        self.url3 = 'https://splcgk.court.gov.cn/gzfwww///fgmlList'
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': '', # add cookie here
            'Host': 'splcgk.court.gov.cn',
            'Origin': 'https://splcgk.court.gov.cn',
            'Referer': 'https://splcgk.court.gov.cn/gzfwww//fgml',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        self.province = ['北京', '天津', '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江', '上海', '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖南', '湖北', '广东',
                         '广西', '海南', '重庆', '四川', '云南', '贵州', '陕西', '宁夏', '甘肃',  '西藏', '青海', '新疆']
        self.session = requests.Session()

    def courtlist1(self):
        for p in self.province:
            data1 = {
                'sf': p,
            }
            response = self.session.post(
                self.url1, headers=self.headers, data=data1)
            r = response.json()
            # cname, cid, cgbm | courtname, courtid, courtcode
            for court in r:
                court_dict = {key: court[key]
                              for key in ['cname', 'cid', 'cgbm']}
                court_dict['province'] = p
                nlist.insert_one(court_dict)

    def courtlist2(self):
        court = list(nlist.find(
            {}, {'_id': 0, 'cgbm': 1, 'province': 1, 'cname': 1}))
        for c in court:
            if '00' in c['cgbm']:
                court.remove(c)
        for c in court[1:]:
            i = c['cgbm']
            data2 = {
                'sf': i,  # cgbm
            }
            response = self.session.post(
                self.url2, headers=self.headers, data=data2)
            try:
                r = response.json()
                for court in r:
                    court_dict = {key: court[key]
                                  for key in ['cname', 'cid', 'cgbm']}
                    court_dict['province'] = c['province']
                    nlist.insert_one(court_dict)
            except Exception as e:
                print(c['cname'], ' 没有下一级法院')
                continue

    def judgelist(self):
        court = list(nlist.find(
            {}, {'_id': 0, 'cid': 1, 'cname': 1}))
        for c in court[1:]:
            data3 = {
                'fyid': c['cid'],  # cid
                'fymc': c['cname'],  # cname
            }
            response = self.session.post(
                self.url3, headers=self.headers, data=data3)
            soup = BeautifulSoup(response.content, 'lxml')
            t = soup.find('div', {'id': 'divList'}).text
            if len(t) <= 2:
                # print('This court has no data on the website.')
                nlist3.insert_one(c)
            else:
                table = soup.find('table')
                df = pd.read_html(str(table), header=0)
                df = df[0]
                df['courtname'] = c['cname']
                df['courtid'] = c['cid']
                judgelist = df.to_dict('records')
                nlist2.insert_many(judgelist)


if __name__ == '__main__':
    j = Judges()
    j.courtlist1()  # 431 courts
    j.courtlist2()  # 3487 courts
    j.judgelist()
