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



import pickle


#model_fn = open("./train.model")

global fn

fn=open("./tmp.log"+str(datetime.datetime.now().day),'w+')



global p_list
global win_list
win_list = []
p_list = []
#交易参数
global min_after_hold
global max_after_hold
global hold_price
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
	parts = line.split(",")
	if len(parts) < 4:
                return ""
	InstrumentID = parts[3]
	mdRecvTime   = parts[0]
	newPrice = float(parts[6])
	checkCode1 = "ToJeactpTrader_ModelResult"
	checkCode2 = "+*LAX_2399"
	p_list.append(newPrice)
	if len(p_list)<win:
		return ""
	win_list = p_list[-win:]
	mean_win = sum(win_list)/len(win_list)
	narr = np.array(win_list)
	narr2 = narr*narr
	sum2 = narr2.sum()
	var_win = (sum2/len(win_list)) - mean_win**2
	#boll_mid = mean_win
	#boll_up = boll_mid + 2*var_win
	#boll_down = boll_mid - 2*var_win
	begin_line = sum(p_list)/len(p_list)
	print begin_line,newPrice,var_win,boll_up,boll_down
	if hold_price != 0:
		'''
		如果有持仓，检查是否需要止盈或者止损平仓
		'''
		max_after_hold = max(max_after_hold,newPrice)
		min_after_hold = min(min_after_hold,newPrice)
		#if hold_price > 0 and (max_after_hold - newPrice)/max_after_hold > drawback_thr5:
		if hold_price > 0 and (newPrice < begin_line - 4 or hold_price - newPrice > 15 )and var_win>=4 :
			cur_gain = newPrice - hold_price
			fn.write("Sell2cover"+"\t"+str(newPrice)+"\t"+str(hold_price)+"\t"+str(cur_gain)+"\n")
			last_hold = hold_price
			hold_price = 0
			modelResult = 3
			print "Sell2cover",newPrice,hold_price,cur_gain
			return "%s\t%s\t%d\t%s\t%s\t%s" %(checkCode1, checkCode2, modelResult, InstrumentID, mdRecvTime,str(newPrice))
		#if hold_price < 0 and (newPrice - min_after_hold)/min_after_hold > drawback_thr5:
		if hold_price < 0 and (newPrice > begin_line + 4 or newPrice - abs(hold_price)>15 ) and var_win>=4:
			cur_gain =  abs(hold_price) - newPrice
			fn.write( "Buy2cover"+"\t"+str(newPrice)+"\t"+str(hold_price)+"\t"+str(cur_gain)+"\n")
			print "Buy2cover",newPrice,hold_price,cur_gain
			last_hold = hold_price
			hold_price = 0
			modelResult = 3
			return "%s\t%s\t%d\t%s\t%s\t%s" %(checkCode1, checkCode2, modelResult, InstrumentID, mdRecvTime,str(newPrice))
	#print predict_gain
	if hold_price==0 and newPrice > begin_line + 4 and last_hold <=0:#and predict_win < thr4:
		fn.write( "Buy\t"+str(newPrice)+"\n")
		print "Buy",newPrice
		hold_price = newPrice
		max_after_hold = hold_price
		min_after_hold = hold_price
		modelResult = 1
		return "%s\t%s\t%d\t%s\t%s\t%s" %(checkCode1, checkCode2, modelResult, InstrumentID, mdRecvTime,str(newPrice))
	if hold_price == 0 and newPrice < begin_line - 4 and last_hold <=0:
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

