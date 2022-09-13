#coding:utf-8

'''
function:
   震荡短线策略，不同于趋势策略，需要上升一定点位开多，这里是下降一定点位开多；上升一定点位开空
'''


import matplotlib.pyplot as plt
import sys
import numpy as np


import math


def get_boll(win_price):
	mean = sum(win_price)/len(win_price)
	narr = np.array(win_price)
	narr2 = narr*narr
	sum2 = narr2.sum()
	boll_win = len(win_price)
	var = (sum2/boll_win) - mean**2
	#print sum2/boll_win,mean**2, var
	if abs(var) < 10**(-7):
		var = 0
	p = win_price[-1]
	up = mean + 2* math.sqrt(var)
	down = mean - 2* math.sqrt(var)
	if up == down:
		cur_b = 0
	else:
		cur_b = (p-down)/(up-down)
	return cur_b

def gen_eval(price_index = 6):
	win = 50
	win_long = 500
	RSI_long_thr = 10
	RSI_short_thr = 90
	price_list = []
	RSI_list = []
	boll_list = []
	hold_price = 0
	max_after_hold = 0
	min_after_hold = 0
	hold_tick = -1
	for line in sys.stdin:
		if not line.strip():
			continue
		parts = line.strip().split(",")
		cur_price = float(parts[price_index])
		price_list.append(cur_price)
		if hold_price > 0 or hold_price < 0:
			hold_tick +=1
		if len(price_list) > win:
			win_price = price_list[-win:]
			cur_boll = get_boll(win_price)
			win_price_a = [win_price[i+1]-win_price[i] for i in range(len(win_price)-1)]
			up_price = sum([x for x in win_price_a if x > 0])
			down_price = abs(sum([x for x in win_price_a if x<0]))
			if up_price + down_price == 0:
				cur_RSI = 0
			else:
				cur_RSI = (100 * up_price)/(up_price + down_price)
			RSI_list.append(cur_RSI)
			boll_list.append(cur_boll)
			'''
			止盈止损部分
			'''
			if hold_price > 0 and max_after_hold - cur_price >1:
				print "Sell2cover for lost:",hold_price,cur_price,cur_price-hold_price
				hold_price = 0
				max_after_hold = 0
				min_after_hold = 0
				hold_tick = -1
			if hold_price < 0 and cur_price - min_after_hold > 1:
				print "Buy2cover for lost:",hold_price,cur_price,abs(hold_price)-cur_price
				hold_price = 0
				max_after_hold = 0
				min_after_hold = 0
				hold_tick = -1
			'''
			入场部分
			'''
			#if cur_RSI > RSI_short_thr and len(price_list) > win_long and sum(price_list[-win_long:])/win_long > sum(price_list[-win:])/win:
			if cur_boll > 1 and len(price_list) > win_long and sum(price_list[-win_long:])/win_long > sum(price_list[-win:])/win:
				if hold_price > 0 and hold_tick > win:
					print "Sell2cover",hold_price,cur_price,cur_price - hold_price
					hold_tick = -1
					hold_price = 0
					max_after_hold = 0
					min_after_hold = 0
				if hold_price < 0 :
					continue
				print "Sell",cur_price
				hold_tick +=1
				hold_price = cur_price
				max_after_hold = cur_price
				min_after_hold = cur_price
			#if cur_RSI < RSI_long_thr and len(price_list) > win_long and sum(price_list[-win_long:])/win_long < sum(price_list[-win:])/win:
			if cur_boll < -1 and len(price_list) > win_long and sum(price_list[-win_long:])/win_long < sum(price_list[-win:])/win:
				if hold_price < 0 and hold_tick > win:
					print "Buy2cover",hold_price,cur_price,abs(hold_price) - cur_price
					hold_price = 0
					max_after_hold = 0
					min_after_hold = 0
					hold_tick = -1
				if hold_price > 0:
					continue
				print "Buy",cur_price
				hold_tick += 1
				hold_price  = -cur_price
				max_after_hold = cur_price
				min_after_hold = cur_price
		else:
			RSI_list.append(0)
			boll_list.append(0)
	plt.figure(1)
	plt.subplot(311)
	plt.plot(price_list[-10000:])
	plt.subplot(312)
	plt.plot(RSI_list[-10000:])
	plt.subplot(313)
	plt.plot(boll_list[-10000:])
	plt.show()
	pass




if __name__ == "__main__":
	gen_eval()