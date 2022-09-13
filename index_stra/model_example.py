#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import tcp_client
from wave import *
import datetime

'''
保存全局变量
'''


#global train data


#train_wave_win[i] = win
global train_price_list
global train_z_list


import pickle


model_fn = open("./train.model")
train_z_list = pickle.load(model_fn)
train_price_list = pickle.load(model_fn)


global fn

fn=open("./tmp.log"+str(datetime.datetime.now().day),'w+')



global test_price_list
global test_z_list

test_price_list = []
test_z_list = []

#交易参数
global min_after_hold
global max_after_hold
global hold_price
min_after_hold = 0
hold_price = 0
max_after_hold = 0


#一些阈值参数
global thr1
global thr2
global thr3
global thr4
global drawback_thr5
global dis_thr
global win
win = 4
thr1 = 0.6
thr2 = 1
dis_thr = 0.1
thr3 = 1
thr4 = 10
#drawback_thr5 = 0.001
drawback_thr5 = 2





'''
定义自己的数据处理函数
完成自己的数据存储，模型计算等逻辑
@return 
    返回一个字符串（一行），作为模型结果返回给TcpTrader
    如果返回的是空串，则不返回给TcpTrader
'''
def my_data_processor(line):
	global fn
	global train_price_list
	global train_z_list
	global thr1
	global thr2
	global thr3
	global thr4
	global drawback_thr5
	global dis_thr
	global win
	global test_price_list
	global test_z_list
	#交易参数
	global min_after_hold
	global max_after_hold
	global hold_price
	parts = line.split(",")
	if len(parts) < 4:
                return ""
	InstrumentID = parts[3]
	mdRecvTime   = parts[0]
	newPrice = float(parts[6])
	checkCode1 = "ToJeactpTrader_ModelResult"
	checkCode2 = "+*LAX_2399"
	test_price_list.append(newPrice)
	if hold_price != 0:
		'''
		如果有持仓，检查是否需要止盈或者止损平仓
		'''
		max_after_hold = max(max_after_hold,newPrice)
		min_after_hold = min(min_after_hold,newPrice)
		#if hold_price > 0 and (max_after_hold - newPrice)/max_after_hold > drawback_thr5:
		if hold_price > 0 and (max_after_hold - newPrice) > drawback_thr5:
			cur_gain = newPrice - hold_price
			fn.write("Sell2cover"+"\t"+str(newPrice)+"\t"+str(hold_price)+"\t"+str(cur_gain)+"\n")
			hold_price = 0
			modelResult = 3
			print "Sell2cover",newPrice,hold_price,cur_gain
			return "%s\t%s\t%d\t%s\t%s\t%s" %(checkCode1, checkCode2, modelResult, InstrumentID, mdRecvTime,str(newPrice))
		#if hold_price < 0 and (newPrice - min_after_hold)/min_after_hold > drawback_thr5:
		if hold_price < 0 and (newPrice - min_after_hold) > drawback_thr5:
			cur_gain =  abs(hold_price) - newPrice
			fn.write( "Buy2cover"+"\t"+str(newPrice)+"\t"+str(hold_price)+"\t"+str(cur_gain)+"\n")
			print "Buy2cover",newPrice,hold_price,cur_gain
			hold_price = 0
			modelResult = 3
			return "%s\t%s\t%d\t%s\t%s\t%s" %(checkCode1, checkCode2, modelResult, InstrumentID, mdRecvTime,str(newPrice))
	test_b_list = get_boll_index(test_price_list)
	test_b_z_list,test_z_info_list,test_z_list = index_cut(test_b_list,thr1)
	predict_value_list = predict_value(train_price_list,train_z_list,test_price_list,test_z_list,win,thr2,dis_thr)
	if not predict_value_list :
		return ""
	predict_value_list = zip(*predict_value_list)
	predict_gain = sum(predict_value_list[0])/len(predict_value_list[0])
	predict_win = sum(predict_value_list[1])/len(predict_value_list[1])
	#print predict_gain
	if hold_price * predict_gain > 0:
		fn.write("Hold already\n")
		return ""
	if abs(predict_gain) > thr3 :#and predict_win < thr4:
		if predict_gain > 0:
			if hold_price <0:
				cur_gain =  abs(hold_price) - newPrice
				fn.write( "Buy2cover"+"\t"+str(newPrice)+"\t"+str(hold_price)+"\t"+str(cur_gain)+"\n")
			fn.write( "Buy\t"+str(newPrice)+"\n")
			print "Buy",newPrice
			hold_price = newPrice
			max_after_hold = hold_price
			min_after_hold = hold_price
			modelResult = 1
			return "%s\t%s\t%d\t%s\t%s\t%s" %(checkCode1, checkCode2, modelResult, InstrumentID, mdRecvTime,str(newPrice))
		if predict_gain < 0 :
			if hold_price > 0:
				cur_gain = newPrice - hold_price
				print "Sell2Cover",newPrice, cur_gain
				fn.write("Sell2cover"+"\t"+str(newPrice)+"\t"+str(hold_price)+"\t"+str(cur_gain)+"\n")
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

