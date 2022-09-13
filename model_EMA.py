#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import tcp_client
import datetime

'''
保存全局变量
'''

import numpy as np
#global train data
import pickle

import math
#model_fn = open("./train.model")
global fn
fn=open("./tmp.log"+str(datetime.datetime.now().day),'w+')





global p_list
global win_list


win_list = []

p_fn="/data/jeactp_data/rb1701/rb1701_"+datetime.date.today().strftime("%Y%m%d")+".txt"

p_list = []

begin_line = 0
last_begin_line  = 0
'''
for line in open(p_fn):
	if not line.strip():
		continue
	parts = line.strip().split(",")
	time = int(parts[0].split()[1].strip().split(":")[0])
	if time < 9:
		continue
	if len(parts) < 12:
		continue
	p_list.append(float(parts[6]))
	if len(p_list) == 1:
		begin_line = p_list[0]
	else:
		begin_line = (float(len(p_list)-1)/float(len(p_list)+1))*last_begin_line + (2.0/(len(p_list)+1))*p_list[-1]

last_begin_line = begin_line
'''
#交易参数
global min_after_hold
global max_after_hold
global hold_price
global strategy_type
strategy_type = 1
min_after_hold = 0
hold_price = 0
max_after_hold = 0


#一些阈值参数
global win
win = 3600



last_hold = 0

'''
定义自己的数据处理函数
完成自己的数据存储，模型计算等逻辑
@return 
    返回一个字符串（一行），作为模型结果返回给TcpTrader
    如果返回的是空串，则不返回给TcpTrader
'''
def my_data_processor(line):
	global fn
	global win
	#交易参数
	global min_after_hold
	global max_after_hold
	global hold_price
	global last_hold
	global begin_line
	global last_begin_line
	global p_list
	global strategy_type
	parts = line.split(",")
	if len(parts) < 46:
                return ""
	InstrumentID = parts[3]
	mdRecvTime   = parts[0]
	bidPrice = float(parts[24])
	askPrice = float(parts[26])
	hourminute = mdRecvTime[11:16]
	iminutecnt = int(hourminute[0:2])*60 + int(hourminute[3:5])
	newPrice = float(parts[6])
	checkCode1 = "ToJeactpTrader_ModelResult"
	checkCode2 = "+*LAX_2399"
	p_list.append(newPrice)
	if iminutecnt < 9*60  or iminutecnt > 15*60:
		print hourminute,"Not Open"
		return ""
	begin_line = (float(len(p_list)-1)/float(len(p_list)+1))*last_begin_line + (2.0/(len(p_list)+1))*p_list[-1]
	last_begin_line = begin_line
	print begin_line,newPrice
	#if len(p_list)<win and iminutecnt < 9*60+30:
	#	return ""
	#if len(p_list)<win:
	#	return ""
	win_list = p_list[-win:]
	ma = sum(p_list[-120:])*1.0 / 120.0
	mean_win = sum(win_list)/len(win_list)
	narr = np.array(win_list)
	narr2 = narr*narr
	sum2 = narr2.sum()
	var_win = (sum2/len(win_list)) - mean_win**2
	var_win = math.sqrt(var_win)
	#boll_mid = mean_win
	#boll_up = boll_mid + 2*var_win
	#boll_down = boll_mid - 2*var_win
	#begin_line = sum(p_list)/len(p_list)
	print var_win
	
	################################
	#  有仓位情况处理
	################################
	if hold_price != 0:
		'''
		如果有持仓，检查是否需要止盈或者止损平仓
		'''
		max_after_hold = max(max_after_hold,newPrice)
		min_after_hold = min(min_after_hold,newPrice)
		#if hold_price > 0 and (max_after_hold - newPrice)/max_after_hold > drawback_thr5:
		########################
		#    信号平仓
		########################
		if hold_price > 0 and ((ma < begin_line - 3 and strategy_type==1) or (strategy_type==2 and ma < begin_line-5)) and var_win> 5:
			cur_gain = newPrice - hold_price
			fn.write("Sell2cover"+"\t"+str(newPrice)+"\t"+str(hold_price)+"\t"+str(cur_gain)+"\n")
			last_hold = hold_price
			modelResult = 3
			print "Sell2cover",newPrice,hold_price,cur_gain
			hold_price = 0
			return "%s\t%s\t%d\t%s\t%s\t%s" %(checkCode1, checkCode2, modelResult, InstrumentID, mdRecvTime,str(newPrice))
		#if hold_price < 0 and (newPrice - min_after_hold)/min_after_hold > drawback_thr5:
		if hold_price < 0 and ((ma > begin_line + 3 and strategy_type==1) or (ma > begin_line + 5 and strategy_type==2) ) and var_win>5:
			cur_gain =  abs(hold_price) - newprice
			fn.write( "Buy2cover"+"\t"+str(newPrice)+"\t"+str(hold_price)+"\t"+str(cur_gain)+"\n")
			print "Buy2cover",newPrice,hold_price,cur_gain
			last_hold = hold_price
			hold_price = 0
			modelResult = 3
			return "%s\t%s\t%d\t%s\t%s\t%s" %(checkCode1, checkCode2, modelResult, InstrumentID, mdRecvTime,str(newPrice))
		###############################
		#   策略2:包含止盈止损
		###############################
		if strategy_type==2:
			if hold_price > 0 and (bidPrice - abs(hold_price) >= 26 or bidPrice -abs(hold_price)<= -40 ):
				cur_gain = newPrice - hold_price
				fn.write("Sell2cover for stop"+"\t"+str(newPrice)+"\t"+str(hold_price)+"\t"+str(cur_gain)+"\n")
				last_hold = hold_price
				modelResult = 3
				print "Sell2cover",newPrice,hold_price,cur_gain
				hold_price = 0
				return "%s\t%s\t%d\t%s\t%s\t%s" %(checkCode1, checkCode2, modelResult, InstrumentID, mdRecvTime,str(newPrice))
			if hold_price < 0 and (abs(hold_price)-askPrice >=26 or abs(hold_price) - askPrice <= -40):
				cur_gain =  abs(hold_price) - newprice
				fn.write( "Buy2cover"+"\t"+str(newPrice)+"\t"+str(hold_price)+"\t"+str(cur_gain)+"\n")
				print "Buy2cover",newPrice,hold_price,cur_gain
				last_hold = hold_price
				hold_price = 0
				modelResult = 3
				return "%s\t%s\t%d\t%s\t%s\t%s" %(checkCode1, checkCode2, modelResult, InstrumentID, mdRecvTime,str(newPrice))
	#print predict_gain
	if hold_price==0 and last_hold <=0 and ((strategy_type==1 and ma > begin_line +3) or (strategy_type==2 and ma > begin_line +5)):#and predict_win < thr4:
		fn.write( "Buy\t"+str(newPrice)+"\n")
		print "Buy",newPrice
		hold_price = newPrice
		max_after_hold = hold_price
		min_after_hold = hold_price
		modelResult = 1
		return "%s\t%s\t%d\t%s\t%s\t%s" %(checkCode1, checkCode2, modelResult, InstrumentID, mdRecvTime,str(newPrice))
	if hold_price == 0 and  last_hold <=0 and ((strategy_type==1 and ma < begin_line -3) or (strategy_type==2 and ma < begin_line - 5)):
		print "sell",newPrice
		fn.write( "Sell\t"+str(newPrice)+"\n")
		modelResult = 2
		hold_price = 0 - newPrice
		max_after_hold = abs(hold_price)
		min_after_hold = abs(hold_price)
		return "%s\t%s\t%d\t%s\t%s\t%s" %(checkCode1, checkCode2, modelResult, InstrumentID, mdRecvTime,str(newPrice))
	return ""


if __name__ == "__main__":
    tcpClient = tcp_client.TcpClient("127.0.0.1", 10120);
    tcpClient.SetDataProcessor(my_data_processor)  # 指定数据处理的回调函数
    tcpClient.Run()
    print "end."

