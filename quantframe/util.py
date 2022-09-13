#coding:utf-8
import sys

import datetime 

import math
'''
所有通用函数

方向计算

'''


def genMaxDrawBack(NetList):
	max_now = 0
	drawback = 0
	max_drawback = 0
	for n in NetList:
		max_now = max(max_now,n)
		drawback = max(max_now-n,drawback)
		max_drawback = drawback/max_now
	return max_drawback


def gen_std(u_list):
	u_ave = sum(u_list)/len(u_list)
	u_std = math.sqrt(sum(map(lambda x:(x-u_ave)*(x-u_ave),u_list))/(len(u_list)-1))
	return u_std



def getDateList(startDate,endDate):
	'''
	function：
	  获取从开始时间到结束时间的列表
	'''
	Sdate = datetime.datetime.strptime(startDate, "%Y%m%d").date()
	Edate = datetime.datetime.strptime(endDate, "%Y%m%d").date()
	d = Sdate
	result = []
	all_count = 0
	while d <=Edate:
		all_count +=1
		if d.weekday() in [5,6]:#如果是周末就不加入DateList
			d += datetime.timedelta(days=1)
			continue
		datestr = d.strftime("%Y%m%d")
		result.append(datestr)
		d += datetime.timedelta(days=1)
	return result,all_count




class MktConf:
	open_index = -1
	high_index = -1
	low_index = -1
	close_index = -1
	bid_index = -1
	ask_index = -1
	last_index=  -1
	time_index = -1


def initMktConf():
	if "future"=="future":
		for line in open("./future.conf"):
			if not line.strip():
				continue
			parts = line.strip().split(",")
			if parts[2]=="open":
				MktConf.open_index = int(parts[0])
			if parts[2] =="close":
				MktConf.close_index = int(parts[0])
			if parts[2] == "high":
				MktConf.high_index = int(parts[0])
			if parts[2] =="low":
				MktConf.low_index = int(parts[0])
			if parts[2] == "code":
				MktConf.code_index= int(parts[0])
			if parts[2] == "time":
				MktConf.time_index = int(parts[0])
			if parts[2]== "new":
				MktConf.new_index = int(parts[0])
			if parts[2]=="bid":
				MktConf.bid_index = int(parts[0])
			if parts[2]=="ask":
				MktConf.ask_index = int(parts[0])
			if parts[2]=="time":
				MktConf.time_index = int(parts[0])


def getMkt(line):
	'''
	function：
	    获取制定品种的行情信息（目前只支持期货）
	参数：
		品种名称
	返回值：
		品种的行情字典
	'''
	mkt_dict = {}#mkt_dict[date]=[open,high,low,close]
	open_index,high_index,low_index,close_index = (1,1,1,1)
	code_index,time_index = (0,0)
	
	for line in open("./mktdata/instrument"):
		if not line.strip():
			continue
		parts = line.strip().split(',')
		cur_date = parts[time_index].strip()
		cur_open = float(parts[open_index])
		cur_high = float(parts[high_index])
		cur_low = float(parts[low_index])
		cur_close = float(parts[close_index])
		mkt_dict[cur_date]=[cur_open,cur_high,cur_low,cur_close]
	return mkt_dict
		

def getTradeDate():
	'''
	function:
		获取交易日期，用于生成每日权益（应该只用于股票吧，期货貌似不需要）
	'''
	pass




