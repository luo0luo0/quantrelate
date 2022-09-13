#coding:utf-8

import sys

import numpy as np
import matplotlib.pyplot as plt

'''
  用于构造波形匹配相关代码
'''
import math


def read_data(fn="",i_price=1):
	if i_price ==-1:
		i_price = 6
	price_list = []
	if fn=="":
		fn = "/Users/luoaoxue/Dev/stock_minite/trans/sh/sh600009.txt"
		fn = "/Users/luoaoxue/Dev/backtest/rb1610_2016082_train"
	for line in open(fn):
		if not line.strip():
			continue
		parts = line.strip().split(',')
		cur_price = float(parts[i_price])
		price_list.append(cur_price)
	return price_list




def get_boll_index(price_list,boll_win = 60):
	win_price = []
	b_index_list = []
	b_index_list += [0]*(boll_win-1)
	for p in price_list:
		win_price.append(p)
		if len(win_price)>boll_win:
			win_price.pop(0)
		if len(win_price)==boll_win:
			mean = sum(win_price)/len(win_price)
			narr = np.array(win_price)
			narr2 = narr*narr
			sum2 = narr2.sum()
			var = (sum2/boll_win) - mean**2
			#print sum2/boll_win,mean**2, var
			if abs(var) < 10**(-7):
				var = 0
			up = mean + 2* math.sqrt(var)
			down = mean - 2* math.sqrt(var)
			if up == down:
				cur_b = 0
			else:
				cur_b = (p-down)/(up-down)
			#print "b%",cur_b
			b_index_list.append(cur_b)
	#print len(price_list),len(b_index_list)
	return b_index_list

def get_ln_index(price_list):
	last_p = 0
	ln_index_list = []
	for p in price_list:
		if last_p != 0:
			ln_index_list.append(p/last_p)
		last_p = p
	return ln_index_list






def cell_test():
	'''
	单元测试
	'''
	#price_list = read_data(fn="/Users/luoaoxue/Dev/stock_minite/trans/sh/sh600009.txt",i_price = 9)
	price_list = read_data(fn =  "/Users/luoaoxue/Dev/backtest/rb1610_20160830.txt",i_price = 6)
	#price_list = get_ma_list(price_list,240)
	b_index_list = get_boll_index(price_list)
	for i in range(len(price_list)):
		if b_index_list[i] > 1:
			print "Sell",price_list[i]	
	#ln_index_list = get_ln_index(price_list)
	#new_index_list = index_cut(price_list,0.0005)
	print len(price_list),len(new_index_list)
	i_list = zip(*z_list)[1]
	new_price_list =[]
	for i in range(len(price_list)):
		if i in i_list:
			new_price_list.append(price_list[i])
	pair_wave = z_list[-200:-196]
	print "test",pair_wave,len(z_list)
	pair_wave_pred = z_list[-200:-195]
	near_wave_list = find_most_likely(z_list,pair_wave,0.6,0.4)
	near_sort_list = sorted(near_wave_list,key = lambda x:x[1])
	most_near = near_sort_list[0][0]
	for s in near_sort_list:
		if s[1]==0:
			continue
		most_near = s[0]
		print "most_near",s[1]
		break
	print "near_wave_list:",len(near_wave_list)

	fig = plt.figure(1)
	plt.subplot(611)
	plt.title("price")
	plt.plot(price_list[-3000:])
	plt.subplot(612)
	plt.title("b_index")
	plt.plot(b_index_list[-3000:])
	plt.subplot(613)
	plt.plot(new_index_list[-3000:])
	plt.title("ln_index")
	#绘制相似波型
	plt.subplot(614)
	xy = zip(*pair_wave)
	x = [t-xy[1][0] for t in xy[1]]
	x = [i-min(i_list[-500:]) for i in i_list[-500:]]
	i_value_begin = len(price_list)-500
	x = []
	for s in i_list:
		if s > i_value_begin:
			x.append(s)
	x = [i-min(x) for i in x]
	print "map to price list",len(x),len(new_price_list[-len(x):])
	plt.plot(x,new_price_list[-len(x):])


	plt.subplot(615)
	print most_near
	xy = zip(*most_near)
	x = [t-xy[1][0] for t in xy[1]]
	plt.plot(x,xy[0])



	plt.subplot(616)
	xy = zip(*pair_wave_pred)
	x = [t-xy[1][0] for t in xy[1]]
	plt.plot(x,xy[0],"*")

	most_near_pred = most_near
	most_near_pred.append(z_list[z_list.index(most_near_pred[-1])+1])
	xy = zip(*most_near_pred)
	x =  [t-xy[1][0] for t in xy[1]]
	plt.plot(x,xy[0],'r')
	for i in range(5):
		most_near_comp = near_sort_list[i+2][0]
		most_near_comp_pack = z_list[z_list.index(most_near_comp[-1])+1]
		most_near_comp.append(most_near_comp_pack)
		print "pack",most_near_comp
		#print near_sort_list[i+2][1]
		xy = zip(*most_near_comp)
		x = [t-xy[1][0] for t in xy[1]]
		plt.plot(x,xy[0],'b')
	plt.show()
	fig.savefig("test.jpg")



'''
function:
   1,  
'''

def stra_predict():
	'''
	策略相关
	'''
	pass



def get_ma_list(ori_list,win):
	ma_list = []
	for i in range(len(ori_list)):
		begin_i = i+1-win
		if begin_i <0:
			ma_list.append(sum(ori_list[:i+1])/len(ori_list[:i+1]))
		else:
			ma_list.append(sum(ori_list[begin_i:i+1])/len(ori_list[begin_i:i+1]))
	return ma_list



def predict_and_eval():
	'''
	训练单元测试
	'''
	fn="/Users/luoaoxue/Dev/stock_minite/trans/sh/sh600009.txt"
	fn = "/Users/luoaoxue/Dev/backtest/rb1610_2016082_train"
	price_index = 6
	thr1 = 0.6#切割b％的阈值0.4,0.6
	thr2 = 1#形状匹配的触发点，需要切割对应的价格反弹值
	dis_thr = 0.1 #两个匹配波形的距离必须小于该阈值
	thr3 = 1 #匹配后的波形，预测的涨跌值的阈值
	thr4 = 10 #匹配后的波形，预测的涨跌所需的最长／短的持仓时间（过了该时间会跌）
	#drawback_thr5 = 0.001
	drawback_thr5 = 2
	#drawback_thr5 = 1
	win = 4
	'''
	不用b% 做为判断标准，适用价格做为切割标的
	'''
	train_price_list = read_data(fn=fn,i_price = 6)
	#train_price_list = get_ma_list(train_price_list,120)#适用分钟线
	train_b_list = get_boll_index(train_price_list)
	train_b_z_list,train_z_info_list,train_z_list= index_cut(train_b_list,thr1)
	#train_b_z_list,train_z_info_list,train_z_list = index_cut(train_price_list,3)
	test_price_list = []
	hold_price = 0
	max_after_hold = 0
	min_after_hold = 0
	gain_list = []
	for line in sys.stdin:
		if not line.strip():
			continue
		parts = line.strip().split(",")
		cur_price = float(parts[price_index])
		test_price_list.append(cur_price)
		if hold_price!=0:
			max_after_hold = max(max_after_hold,cur_price)
			min_after_hold = min(min_after_hold,cur_price)
			print hold_price,cur_price,max_after_hold,min_after_hold,(max_after_hold - cur_price)/max_after_hold, (cur_price - min_after_hold)/min_after_hold
			#if hold_price >0 and (max_after_hold - cur_price)/max_after_hold > drawback_thr5:
			if hold_price >0 and (max_after_hold - cur_price)> drawback_thr5:
				cur_gain = cur_price - hold_price
				print "Sell2Cover",cur_price, cur_gain
				gain_list.append(cur_gain)
				hold_price = 0
			#if hold_price < 0 and (cur_price - min_after_hold)/min_after_hold > drawback_thr5:
			if hold_price < 0 and (cur_price - min_after_hold)> drawback_thr5:
				cur_gain =  abs(hold_price) - cur_price
				print "Buy2cover", cur_price, cur_gain
				gain_list.append(cur_gain)
				hold_price = 0
		#test_price_list =get_ma_list(test_price_list,120)
		test_b_list = get_boll_index(test_price_list)
		pair_b_z_list,pair_z_info_list,test_z_list = index_cut(test_b_list,thr1)
		predict_value_list = predict_value(train_price_list,train_z_list,test_price_list,test_z_list,win,thr2,dis_thr)
		if not predict_value_list :
			continue
		'''
		策略相关参数如下：
		predict_value_list 返回的值中一列是匹配上的涨跌值，一列是这么多的涨跌值下所需要持有的窗口期，进行取平均后，用如下阈值过滤，看是否入场 
		thr3 : 涨跌阈值
		thr4 : 窗口阈值
		'''
		predict_value_list = zip(*predict_value_list)
		predict_gain = sum(predict_value_list[0])/len(predict_value_list[0])
		predict_win = sum(predict_value_list[1])/len(predict_value_list[1])
		#print predict_gain
		if hold_price * predict_gain > 0:
			print "Hold already"
			continue
		if abs(predict_gain) > thr3 :#and predict_win < thr4:
			if predict_gain > 0:
				if hold_price <0:
					cur_gain =  abs(hold_price) - cur_price
					print "Buy2cover",cur_price,hold_price,cur_gain
					gain_list.append(cur_gain)
				print "Buy",cur_price
				hold_price = cur_price
				max_after_hold = hold_price
				min_after_hold = hold_price
			if predict_gain < 0 :
				if hold_price > 0:
					cur_gain = cur_price - hold_price
					print "Sell2Cover",cur_price, cur_gain
					gain_list.append(cur_gain)
				print "Sell",cur_price
				hold_price = 0 - cur_price
				max_after_hold = abs(hold_price)
				min_after_hold = abs(hold_price)
	if gain_list:
		print sum(gain_list)/float(len(gain_list)),sum([x>0 for x in gain_list]),sum([x<0 for x in gain_list])



if __name__=="__main__":
	#cell_test()
	#predict_and_eval()
	cmd = sys.argv[1]
	if cmd == "plot":
		cell_test()
	elif cmd == "eval":
		predict_and_eval()
	elif cmd == "model":
		model_fn = sys.argv[2]
		gen_train_model(model_fn)

