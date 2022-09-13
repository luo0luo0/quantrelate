#coding:utf-8

import sys


import matplotlib.pyplot as plt
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



win_list = []
loss_list = []
hold_price = 0


price_list = []
ave_list= []
MA_list = []
var_up_list = []
var_down_list = []
low_win_list = []
high_win_list =[]
RSI_list = []
win = 3600
for line in sys.stdin:
	if not line.strip():
		continue
	parts = line.strip().split(",")
	cur_time = int(parts[0].split()[1].split(":")[0])
	if cur_time <9:
		continue
	if cur_time > 15:
		break
	price = float(parts[6])
	price_list.append(price)
	ave = sum(price_list)/len(price_list)
	up_price = ave*1.001087
	down_price = ave*(1-0.001087)
	
	var_up_list.append(up_price)
	var_down_list.append(down_price)
	ave_list.append(ave)
	if price > up_price and hold_price<=0:
		hold_price = price
	if price < down_price and hold_price >= 0:
		hold_price = -price
	if hold_price > 0:
		win_list.append(hold_price + 26)
		loss_list.append(hold_price - 40)
	if hold_price < 0 :
		win_list.append(abs(hold_price) - 26)
		loss_list.append(abs(hold_price)+40)
	if hold_price == 0 :
		win_list.append(price)
		loss_list.append(price)

	'''
	if len(price_list) < win:
		MA_list.append(price)
		#var_up_list.append(ave)
		#var_down_list.append(ave)
		low_win_list.append(min(price_list))
		high_win_list.append(max(price_list))
		#RSI_list.append(50)
	else:
		win_list = price_list[-win:]
		mean_win = sum(win_list)/len(win_list)
		#narr = np.array(win_list)
		#narr2 = narr*narr
		#sum2 = narr2.sum()
		#var_win = (sum2/len(win_list)) - mean_win**2
		#var_win = abs(var_win)
		#var_up_list.append(ave+var_win)
		#var_down_list.append(ave-var_win)
		low_win_list.append(min(price_list))
		high_win_list.append(max(price_list))
		#MA_list.append(sum(win_list)/len(win_list))
		#RSI_list.append(gen_RSI(win_list))
	'''



print "Finish"
print len(price_list)
plt.figure(1)
#plt.subplot(211)
plt.plot(price_list)
plt.plot(ave_list)
plt.plot(var_up_list)
plt.plot(var_down_list)
plt.plot(win_list,'r')
plt.plot(loss_list,'b')
#plt.plot(MA_list)
#plt.plot(high_win_list)
#plt.plot(low_win_list)
#plt.subplot(212)
#plt.plot(RSI_list)
#plt.plot(var_up_list)
#plt.plot(var_down_list)
plt.show()


