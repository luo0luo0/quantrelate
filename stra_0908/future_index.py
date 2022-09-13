#coding:utf-8

'''
function:
   技术指标相关计算
'''
import sys

import matplotlib.pyplot as plt
import os



def gen_RSV(win_list,i):
	return 100*(win_list[i]-min(win_list))/(max(win_list)- min(win_list))

def gen_K(win_list,i):
	if i == 0:
		return (2.0/3.0)*50 + (1.0/3.0)*gen_RSV(win_list,0)
	else:
		return (2.0/3.0)*gen_K(win_list,i-1)+(1.0/3.0)*gen_RSV(win_list,i)






def gen_all_RSV(win_list):
	RSV_list = []
	min_v = min(win_list)
	max_v = max(win_list)
	for i in range(len(win_list)):
		RSV_list.append((win_list[i] - min_v)/(max_v - min_v))
	return RSV_list

def gen_all_K(win_list,RSV_list):
	k_list = []
	for i in range(len(win_list)):
		if i == 0:
			k_list.append(50)
			continue
		cur_k = (2.0/3.0)*k_list[-1] + (1.0/3.0)*RSV_list[i]
		k_list.append(cur_k)
	#print len(win_list),len(k_list)
	return k_list


def gen_all_D(win_list,k_list):
	#print len(win_list),len(k_list)
	d_list = []
	for i in range(len(win_list)):
		if i == 0:
			d_list.append(50)
			continue
		cur_d = (2.0/3.0) * d_list[-1] + (1.0/3.0) * k_list[i]
		d_list.append(cur_d)
	return d_list

def gen_all_J(k_list,d_list):
	k_list =[3*x for x in k_list]
	return list(map(lambda x:x[0]-x[1],zip(k_list,d_list)))


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


def plot_kdj():
	#fn = "/Users/luoaoxue/Dev/backtest/rb1610_20160830.txt"
	fn = "/Users/luoaoxue/Dev/backtest/rb1610_2016082_train"
	#fn = "/Users/luoaoxue/Dev/stock_minite/trans/sh/sh600009.txt"
	win = 3600
	fn = open(fn)
	p_list = []
	for line in fn:
		if not line.strip():
			continue
		p = line.strip().split(",")[6]
		#p = line.strip().split()[9]
		p_list.append(float(p))
	k_list = []
	d_list = []
	j_list = []
	RSV_list = []
	RSI_list = []
	dev_1_list = [0]
	last_k = 50
	last_d = 50
	last_j = 50
	'''
	strategy variables
	'''
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
		if i >0:
			dev_1_list.append(p_list[i]-p_list[i-1])
		if i<win:
			k_list.append(50)
			d_list.append(50)
			j_list.append(50)
			RSV_list.append(50)
			RSI_list.append(50)
			continue
		win_list = p_list[i-win:i]
		RSV = gen_RSV(win_list,-1)
		cur_k = (2.0/3.0)*last_k + (1.0/3.0)*RSV
		cur_d = (2.0/3.0)*last_d + (1.0/3.0)*cur_k
		cur_j = 3*cur_k - 2*cur_d
		last_k = cur_k
		last_d = cur_d
		#print RSV,cur_k,cur_d,cur_j
		k_list.append(cur_k)
		d_list.append(cur_d)
		j_list.append(cur_j)
		RSV_list.append(RSV)
		RSI = gen_RSI(win_list)
		RSI_list.append(RSI)
		'''
		下述为策略相关：
		
		if hold_price != 0:
			max_hold_p = max(p_list[i],max_hold_p)
			min_hold_p = min(p_list[i],min_hold_p)
		if hold_price > 0 and max_hold_p - p_list[i]> 3:
			print "Sell2cover",hold_price,p_list[i],max_hold_p,hold_index,p_list[i]-hold_price
			hold_x.append(i)
			hold_y.append(p_list[i])
			hold_price = 0
			continue
		if hold_price < 0 and p_list[i] - min_hold_p > 3:
			print "Buy2cover",hold_price,p_list[i],min_hold_p,hold_index,abs(hold_price) - p_list[i]
			hold_x.append(i)
			hold_y.append(p_list[i])
			hold_price = 0
			continue
		if j_list[i] > 80 and sum(p_list[i-60:i])/len(p_list[i-60:i]) < sum(p_list[i-win:i])/len(p_list[i-win:i]):
		#if p_list[i] >sum(p_list[i-60:i])/len(p_list[i-60:i])  and sum(p_list[i-60:i])/len(p_list[i-60:i]) < sum(p_list[i-win:i])/len(p_list[i-win:i]):
			if hold_price == 0:
				print "Sell",p_list[i]
				hold_price = -p_list[i]
				max_hold_p = abs(hold_price)
				min_hold_p = abs(hold_price)
				hold_index = d_list[i]
				hold_x.append(i)
				hold_y.append(p_list[i])
				hold_sell_x.append(i)
				hold_sell_y.append(p_list[i])
				continue
		if  j_list[i] < 10 and  sum(p_list[i-60:i])/len(p_list[i-60:i]) > sum(p_list[i-win:i])/len(p_list[i-win:i]):
		#if p_list[i] < sum(p_list[i-60:i])/len(p_list[i-60:i])  and  sum(p_list[i-60:i])/len(p_list[i-60:i]) > sum(p_list[i-win:i])/len(p_list[i-win:i]):
			if hold_price == 0:
				print "Buy",p_list[i]
				hold_price = p_list[i]
				max_hold_p = abs(hold_price)
				min_hold_p = abs(hold_price)
				hold_index = d_list[i]
				hold_x.append(i)
				hold_y.append(p_list[i])
				hold_buy_x.append(i)
				hold_buy_y.append(p_list[i])
				continue
		'''
		#break
	#print k_list[-30:]
	#print d_list[-30:]
	#print j_list[-30:]
	
	fig = plt.figure(1)
	plt.subplot(511)
	plt.plot(p_list)
	#plt.plot(hold_x,hold_y,'r')
	#plt.plot(hold_sell_x,hold_sell_y,"*")
	plt.subplot(512)
	plt.plot(k_list)
	#plt.plot(d_list,'r')
	plt.subplot(513)
	plt.plot(RSI_list)
	plt.subplot(514)
	plt.plot(dev_1_list)
	plt.subplot(515)
	plt.plot(RSV_list)
	plt.show()
	

#def stra_backtest():





def plot_fun():
	data_dir = "/Users/luoaoxue/Dev/future_data/rb1701/"
	for fn in os.listdir(data_dir):
		if not "rb" in fn:
			continue
		fn = data_dir + fn
		p_list = []
		for line in open(fn):
			if not line.strip():
				continue
			parts = line.strip().split(",")
			p = float(parts[6])
			p_list.append(p)
		plot_index(p_list)




def plot_index(p_list):
	win = 3600
	k_list = []
	d_list = []
	j_list =[]
	RSV_list = []
	RSI_list = []
	last_k = 50
	last_d = 50
	last_j = 50
	MA_list＝ []
	for i in range(len(p_list)):
		if i<win:
			k_list.append(50)
			d_list.append(50)
			j_list.append(50)
			RSV_list.append(50)
			RSI_list.append(50)
			MA_list.append(0)
			continue
		win_list = p_list[i-win:i]
		RSV = gen_RSV(win_list,-1)
		cur_k = (2.0/3.0)*last_k + (1.0/3.0)*RSV
		cur_d = (2.0/3.0)*last_d + (1.0/3.0)*cur_k
		cur_j = 3*cur_k - 2*cur_d
		last_k = cur_k
		last_d = cur_d
		cur_MA = sum(p_list[i-win:i])/len(p_list[i-win:i])
		#print RSV,cur_k,cur_d,cur_j
		k_list.append(cur_k)
		d_list.append(cur_d)
		j_list.append(cur_j)
		RSV_list.append(RSV)
		MA_list.append(cur_MA)
		RSI = gen_RSI(win_list)
		RSI_list.append(RSI)
	fig = plt.figure(1)
	plt.subplot(511)
	plt.plot(p_list)
	plt.plot(MA_list)
	#plt.plot(hold_x,hold_y,'r')
	#plt.plot(hold_sell_x,hold_sell_y,"*")
	plt.subplot(512)
	plt.plot(k_list)
	plt.plot(d_list)
	plt.plot(j_list)
	#plt.plot(d_list,'r')
	plt.subplot(513)
	plt.plot(RSI_list)
	plt.subplot(514)
	plt.plot(RSV_list)
	plt.show()

if __name__ == "__main__":
	plot_fun()













