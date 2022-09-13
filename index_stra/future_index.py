#coding:utf-8

'''
function:
   技术指标相关计算
'''
import sys
import os
import matplotlib.pyplot as plt



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



def plot_kdj(p_list):
	#fn = "/Users/luoaoxue/Dev/backtest/rb1610_20160830.txt"
	#fn = "/Users/luoaoxue/Dev/stock_minite/trans/sh/sh600009.txt"
	win = 1200
	k_list = []
	d_list = []
	j_list = []
	RSV_list = []
	last_k = 50
	last_d = 50
	last_j = 50
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
			k_list.append(50)
			d_list.append(50)
			j_list.append(50)
			RSV_list.append(50)
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
		'''
		下述为策略相关：
		'''
		if hold_price != 0:
			max_hold_p = max(p_list[i],max_hold_p)
			min_hold_p = min(p_list[i],min_hold_p)
		if hold_price > 0 and (max_hold_p - p_list[i]> 1 or p_list[i]-hold_price >2):
			print "Sell2cover",hold_price,p_list[i],max_hold_p,hold_index,p_list[i]-hold_price
			gain_list.append(p_list[i] - hold_price)
			hold_x.append(i)
			hold_y.append(p_list[i])
			hold_price = 0
			continue
		if hold_price < 0 and (p_list[i] - min_hold_p > 1 or abs(hold_price) - p_list[i] > 2):
			print "Buy2cover",hold_price,p_list[i],min_hold_p,hold_index,abs(hold_price) - p_list[i]
			gain_list.append(abs(hold_price)-p_list[i])
			hold_x.append(i)
			hold_y.append(p_list[i])
			hold_price = 0
			continue
		if j_list[i] > 90 and sum(p_list[i-60:i])/len(p_list[i-60:i]) < sum(p_list[i-win:i])/len(p_list[i-win:i]) and abs(p_list[i] - p_list[i-60]) <2:
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
		if  j_list[i] < 10 and  sum(p_list[i-60:i])/len(p_list[i-60:i]) > sum(p_list[i-win:i])/len(p_list[i-win:i]) and abs(p_list[i]-p_list[i-60]) < 2:
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
	dir = "/data/jeactp_data/ag1612/"
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
		#print len(p_list)
		gain_list = plot_kdj(p_list)
		if gain_list == []:
			continue
		print "gain_list",gain_list
		print "gain_list",10*min(gain_list),10*max(gain_list),10*sum(gain_list)
		print ""
		print ""

if __name__ == "__main__":
	stra_backtest()













