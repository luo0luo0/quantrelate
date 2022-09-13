#coding:utf-8

'''
function:
   技术指标相关计算
'''
import sys
import os
import matplotlib.pyplot as plt


import numpy as np



def plot_kdj(p_list):
	#fn = "/Users/luoaoxue/Dev/backtest/rb1610_20160830.txt"
	#fn = "/Users/luoaoxue/Dev/stock_minite/trans/sh/sh600009.txt"
	win = 3600
	'''
	strategy variables
	'''
	gain_list = []
	hold_price = 0
	max_hold_p = 0
	min_hold_p = 0
	hold_index = 0
	hold_x =[]
	hold_y = []
	hold_buy_x = []
	hold_buy_y = []
	hold_sell_x = []
	hold_sell_y =[]
	for i in range(len(p_list)):
		if i<win:
			continue
		win_list = p_list[i-win:i]
		mean_win = sum(win_list)/len(win_list)
		narr = np.array(win_list)
		narr2 = narr*narr
		sum2 = narr2.sum()
		var_win = (sum2/len(win_list)) - mean_win**2
		boll_mid = mean_win
		boll_up = boll_mid + 2*var_win
		boll_down = boll_mid - 2*var_win
		begin_line = sum(p_list)/len(p_list)
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
		if hold_price > 0 and p_list[-1] < boll_down:
			print "Sell2cover",hold_price,p_list[i],max_hold_p,p_list[i]-hold_price
			gain_list.append(p_list[i] - hold_price)
			hold_x.append(i)
			hold_y.append(p_list[i])
			hold_price = 0
			continue
		if hold_price < 0 and p_list[-1] > boll_up:
			print "Buy2cover",hold_price,p_list[i],min_hold_p,abs(hold_price) - p_list[i]
			gain_list.append(abs(hold_price)-p_list[i])
			hold_x.append(i)
			hold_y.append(p_list[i])
			hold_price = 0
			continue
		'''
		入场相关
		'''
		#if j_list[i] > 90 and sum(p_list[i-60:i])/len(p_list[i-60:i]) < sum(p_list[i-win:i])/len(p_list[i-win:i]) and abs(p_list[i] - p_list[i-60]) <2:
		#if p_list[i] >sum(p_list[i-60:i])/len(p_list[i-60:i])  and sum(p_list[i-60:i])/len(p_list[i-60:i]) < sum(p_list[i-win:i])/len(p_list[i-win:i]):
		if p_list[-1] < begin_line - var_win:
			if hold_price == 0:
				print "Sell",p_list[i]
				hold_price = -p_list[i]
				max_hold_p = abs(hold_price)
				min_hold_p = abs(hold_price)
				hold_x.append(i)
				hold_y.append(p_list[i])
				hold_sell_x.append(i)
				hold_sell_y.append(p_list[i])
				continue
		#if  j_list[i] < 10 and  sum(p_list[i-60:i])/len(p_list[i-60:i]) > sum(p_list[i-win:i])/len(p_list[i-win:i]) and abs(p_list[i]-p_list[i-60]) < 2:
		#if p_list[i] < sum(p_list[i-60:i])/len(p_list[i-60:i])  and  sum(p_list[i-60:i])/len(p_list[i-60:i]) > sum(p_list[i-win:i])/len(p_list[i-win:i]):
		if p_list[-1] > begin_line + var_win:
			if hold_price == 0:
				print "Buy",p_list[i]
				hold_price = p_list[i]
				max_hold_p = abs(hold_price)
				min_hold_p = abs(hold_price)
				hold_x.append(i)
				hold_y.append(p_list[i])
				hold_buy_x.append(i)
				hold_buy_y.append(p_list[i])
				continue
	if hold_price >0 :
		print "Time2over",hold_price,p_list[-1],max_hold_p,p_list[-1]-hold_price
		gain_list.append(p_list[i] - hold_price)
	if hold_price < 0:
		print "Time2cover",hold_price,p_list[-1],min_hold_p,abs(hold_price)-p_list[-1]
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
	dir = "./test/"
	dir = "/data/jeactp_data/IF1612/"
	dir = "./test_1/"
	for fn in os.listdir(dir):
		fn = dir+fn
		p_list = []
		gain_list = []
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
		gain_list = plot_kdj(p_list)
		if gain_list == []:
			continue
		print "gain_list",gain_list
		print "gain_list",10*min(gain_list),10*max(gain_list),10*sum(gain_list)
		print ""
		print ""

if __name__ == "__main__":
	stra_backtest()













