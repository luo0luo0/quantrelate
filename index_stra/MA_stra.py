#coding:utf-8

'''
function:
   技术指标相关计算
'''
import sys
import os
import matplotlib.pyplot as plt

import math
import numpy as np



def gen_RSI(win_list):
	'''
	返回窗口期的相对强弱指数
	'''
	win_gain_list = [win_list[i+1]-win_list[i] for i in range(len(win_list)-1)]
	up_list = [i for i in win_gain_list if i>0]
	down_list = [i for i in win_gain_list if i<0]
	if up_list==[]:
		return 0
	if down_list==[]:
		return 100 
	RS = (sum(up_list)/len(up_list))/abs(sum(down_list)/len(down_list))
	return 100 * RS /(1+RS)






def plot_kdj(p_list,time_list):
	#fn = "/Users/luoaoxue/Dev/backtest/rb1610_20160830.txt"
	#fn = "/Users/luoaoxue/Dev/stock_minite/trans/sh/sh600009.txt"
	win = 3600
	short_win = 600
	long_win = 2400
	#win = 4000
	'''
	strategy variables
	'''
	gain_list = []
	hold_price = 0
	max_hold_p = 0
	last_hold = 0
	min_hold_p = 0
	hold_index = 0
	hold_x =[]
	hold_y = []
	hold_buy_x = []
	hold_buy_y = []
	hold_sell_x = []
	hold_sell_y =[]
	last_mean_win = 0
	last_begin_line = 0
	for i in range(len(p_list)):
		if i<=long_win:
			continue
		'''
		win_list = p_list[i-win:i]
		mean_win = sum(win_list)/len(win_list)
		narr = np.array(win_list)
		narr2 = narr*narr
		sum2 = narr2.sum()
		var_win = (sum2/len(win_list)) - mean_win**2
		var_win = math.sqrt(abs(var_win))
		begin_line = sum(p_list[:i])/len(p_list[:i])
		'''
		short_MA = sum(p_list[i-short_win:i])/len(p_list[i-long_win:i])
		long_MA = sum(p_list[i-long_win:i])/len(p_list[i-long_win:i])
		'''
		boll_mid = mean_win
		boll_up = boll_mid + 2*var_win
		boll_down = boll_mid - 2*var_win
		'''
		#print begin_line,p_list[i],var_win,boll_up,boll_down
		#print RSV,cur_k,cur_d,cur_j
		'''
		下述为策略相关：
		'''
		if hold_price != 0:
			'''
			持仓期间的相关变量更新
			'''
			max_hold_p = max(p_list[i],max_hold_p)
			min_hold_p = min(p_list[i],min_hold_p)
		'''
		止盈止损平仓
		'''
		#if hold_price > 0 and p_list[i] < boll_down:
		#if hold_price > 0 and (p_list[i] < mean_win or max_hold_p- p_list[i]>3):
		#if hold_price > 0 and ( max_hold_p- p_list[i]>3):
		#if hold_price > 0 and (p_list[i] < begin_line -max(3,var_win) or  max_hold_p- p_list[i]>min(9,max(4,var_win)) ):
		#if hold_price > 0 and (p_list[i] < begin_line -min(5,max(2,var_win))  or hold_price - p_list[i] > 15) and var_win >3:
		#if hold_price > 0 and (p_list[i] < begin_line -4  or hold_price - p_list[i] > 15) and var_win >3:
		#if hold_price > 0 and (p_list[i] < begin_line -4  or max_hold_p - p_list[i] > 15) and var_win >3:
		#if hold_price > 0 and (p_list[i] < boll_down  or max_hold_p - p_list[i] > 15) and var_win >3:
		if hold_price > 0 and  max_hold_p - p_list[i] > 15:
			print "Sell2cover@"+time_list[i],hold_price,p_list[i],max_hold_p,p_list[i]-hold_price
			gain_list.append(p_list[i] - hold_price)
			last_hold = hold_price
			hold_x.append(i)
			hold_y.append(p_list[i])
			hold_price = 0
			'''
			last_mean_win = mean_win
			last_begin_line = begin_line
			'''
			continue
		#if hold_price < 0 and p_list[i] > boll_up:
		#if hold_price < 0 and (p_list[i] > mean_win or p_list[i]-min_hold_p >3):
		#if hold_price < 0 and ( p_list[i]-min_hold_p >3):
		#if hold_price < 0 and ( p_list[i]-min_hold_p >3):
		#if hold_price < 0 and (p_list[i]-begin_line > 4 or p_list[i]- abs(hold_price)>15) and var_win>3:
		#if hold_price < 0 and (p_list[i]-begin_line > 4 or p_list[i]- min_hold_p >15) and var_win>3:
		if hold_price < 0 and  p_list[i]- min_hold_p >15:
			print "Buy2cover@"+time_list[i],hold_price,p_list[i],min_hold_p,abs(hold_price)-p_list[i]
			last_hold = hold_price
			gain_list.append(abs(hold_price)-p_list[i])
			hold_x.append(i)
			hold_y.append(p_list[i])
			hold_price = 0
			'''
			last_mean_win = mean_win
			last_begin_line = begin_line
			'''
			continue
		'''
		入场相关
		'''
		#if j_list[i] > 90 and sum(p_list[i-60:i])/len(p_list[i-60:i]) < sum(p_list[i-win:i])/len(p_list[i-win:i]) and abs(p_list[i] - p_list[i-60]) <2:
		#if p_list[i] >sum(p_list[i-60:i])/len(p_list[i-60:i])  and sum(p_list[i-60:i])/len(p_list[i-60:i]) < sum(p_list[i-win:i])/len(p_list[i-win:i]):
		#if p_list[i] < begin_line - var_win:
		#if p_list[i] < mean_win-1 and mean_win < begin_line-1 and last_mean_win >=last_begin_line-1:
		#if  p_list[i] < begin_line -4 and p_list[i-1] >=last_begin_line -4 and gen_RSI(p_list[i-win:i]) < 50 :
		#if  p_list[i] < begin_line -min(5,max(2,var_win))   and gen_RSI(p_list[i-win:i]) < 50 :
		if last_hold>=0 and  short_MA < long_MA:
			if hold_price == 0:
				#print "Sell@"+time_list[i],p_list[i],begin_line,var_win,last_mean_win,last_begin_line,mean_win,begin_line
				print "Sell@"+time_list[i],p_list[i]
				hold_price = -p_list[i]
				max_hold_p = abs(hold_price)
				min_hold_p = abs(hold_price)
				hold_x.append(i)
				hold_y.append(p_list[i])
				hold_sell_x.append(i)
				hold_sell_y.append(p_list[i])
				'''
				last_mean_win = mean_win
				last_begin_line = begin_line
				'''
				continue
		#if  j_list[i] < 10 and  sum(p_list[i-60:i])/len(p_list[i-60:i]) > sum(p_list[i-win:i])/len(p_list[i-win:i]) and abs(p_list[i]-p_list[i-60]) < 2:
		#if p_list[i] < sum(p_list[i-60:i])/len(p_list[i-60:i])  and  sum(p_list[i-60:i])/len(p_list[i-60:i]) > sum(p_list[i-win:i])/len(p_list[i-win:i]):
		#if p_list[i] > begin_line + var_win:
		#if p_list[i] >mean_win+1 and mean_win >begin_line + 1 and last_mean_win <= last_begin_line+1:
		#if  p_list[i] >begin_line + 4 and p_list[i-1]<=last_begin_line+4 and gen_RSI(p_list[i-win:i]) > 50:
		#if  p_list[i] >begin_line + min(5,max(2,var_win))  and gen_RSI(p_list[i-win:i]) > 50:
		if  last_hold<=0 and short_MA > long_MA:
			if hold_price == 0:
				#print "Buy@"+time_list[i],p_list[i],begin_line,var_win,last_mean_win,last_begin_line,mean_win,begin_line
				print "Buy@"+time_list[i],p_list[i]
				hold_price = p_list[i]
				max_hold_p = abs(hold_price)
				min_hold_p = abs(hold_price)
				hold_x.append(i)
				hold_y.append(p_list[i])
				hold_buy_x.append(i)
				hold_buy_y.append(p_list[i])
				'''
				last_mean_win = mean_win
				last_begin_line = begin_line
				'''
				continue
		'''
		last_mean_win = mean_win
		last_begin_line = begin_line
		'''
	if hold_price >0 :
		print "Time2over@",hold_price,p_list[i],max_hold_p,p_list[i]-hold_price
		gain_list.append(p_list[i] - hold_price)
	if hold_price < 0:
		print "Time2cover@",hold_price,p_list[i],min_hold_p,abs(hold_price)-p_list[i]
		gain_list.append(abs(hold_price)-p_list[i])
	return gain_list
		#break
	#print k_list[-30:]
	#print d_list[-30:]
	#print j_list[-30:]
	'''
	fig = plt.figure(1)
	plt.subplot(511)
	plt.plot(p_list)
	plt.plot(hold_x,hold_y,'r')
	plt.plot(hold_sell_x,hold_sell_y,"*")
	plt.subplot(512)
	plt.plot(k_list)
	plt.plot(d_list,'r')
	plt.subplot(513)
	plt.plot(d_list)
	plt.subplot(514)
	plt.plot(j_list)
	plt.subplot(515)
	plt.plot(RSV_list)
	plt.show()
	'''


def stra_backtest():
	dir = "/data/jeactp_data/rb1610/"
	#dir = "./test/"
	#dir = "/data/jeactp_data/IF1612/"
	#dir = "./test_1/"
	for fn in os.listdir(dir):
		fn = dir+fn
		p_list = []
		gain_list = []
		time_list = []
		print "begin",fn
		for line in open(fn):
			if not line.strip():
				continue
			parts = line.strip().split(",")
			time = int(parts[0].split()[1].strip().split(":")[0])
			if time <9:
				continue
			if time >15:
				break
			p_list.append(float(parts[6]))
			time_list.append(parts[0])
		print len(p_list),len(time_list)
		gain_list = plot_kdj(p_list,time_list)
		if gain_list == []:
			continue
		print "gain_list",gain_list
		print "gain_list",10*min(gain_list),10*max(gain_list),10*sum(gain_list)
		print ""
		print ""

if __name__ == "__main__":
	stra_backtest()













