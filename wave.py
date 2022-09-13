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
		i_price = 9
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

def index_cut(index_list,thr):
	'''
	功能：
	    用于指标的切割，用于做成Z图，就是上涨和下跌必是交替出现的！
	参数：
	    index_list:  指标数组
	    thr       ： 变换Z字形的阈值（用于过滤噪声）
	返回：
	    插值后的序列
	    高低序列［
	    new_index_list:x=range(len)后，z状图的点
	    z_info_list：[beginpoint,endpoint,len］,[beginpoint,endpoint,len]]
	    z_list：[［begin_point,begin_index］...]
	'''
	up_flag = 0#上涨还是下跌的标志
	z_info_list = []
	z_list = []
	t_list = []
	win_list = []
	new_index_list = []
	debug_last_flag = 0
	for p in index_list:
		win_list.append(p)
		if len(win_list)==1:
			up_flag = 0
			continue
		if up_flag == 0 :#or len(win_list)==2:
			if win_list[-1]>win_list[0]:
				up_flag = 1
			elif win_list[-1]<win_list[0]:
				up_flag = -1
			#continue
		#print win_list,up_flag

		if up_flag == 1 and max(win_list)> p + thr:
			max_value = max(win_list)
			max_value_i = -1
			for i in range(1,len(win_list)+1,1):
				j = 0-i
				if max_value == win_list[j]:
					max_value_i = j
					break
			cut_win_list = win_list[:max_value_i+1]
			if up_flag == debug_last_flag:
				print "problem 1",win_list
			cut_win_list = range_insert(cut_win_list[0],cut_win_list[-1],len(cut_win_list))
			z_info_list.append([cut_win_list[0],cut_win_list[-1],len(cut_win_list)])
			z_list.append([cut_win_list[0],len(new_index_list)])
			'''
			if len(cut_win_list)==1:
				z_list.append(cut_win_list[0])
				print 1,cut_win_list[0]
			else:
				print 1,cut_win_list[0],cut_win_list[-1]
				z_list.append(cut_win_list[0])
				z_list.append(cut_win_list[-1])
			'''
			new_index_list += cut_win_list[:-1]
			debug_last_flag = up_flag
			win_list = win_list[max_value_i:]
			up_flag = -1
		elif up_flag == -1 and min(win_list) < p - thr:
			min_value = min(win_list)
			min_value_i = -1
			for i in range(1,len(win_list)+1,1):
				j = 0-i
				if min_value == win_list[j]:
					min_value_i = j
					break
			cut_win_list = win_list[:min_value_i+1]
			#print min_value_i,min_value,win_list,cut_win_list
			if up_flag == debug_last_flag:
				print "problem -1",win_list
			cut_win_list = range_insert(cut_win_list[0],cut_win_list[-1],len(cut_win_list))
			z_info_list.append([cut_win_list[0],cut_win_list[-1],len(cut_win_list)])
			z_list.append([cut_win_list[0],len(new_index_list)])
			'''
			if len(cut_win_list)==1:
				z_list.append(cut_win_list[0])
				print -1,cut_win_list[0]
			else:
				print -1,cut_win_list[0],cut_win_list[-1]
				z_list.append(cut_win_list[0])
				z_list.append(cut_win_list[-1])
			'''
			new_index_list += cut_win_list[:-1]
			debug_last_flag = up_flag
			win_list = win_list[min_value_i:]
			up_flag = 1
	cut_win_list = range_insert(win_list[0],win_list[-1],len(win_list))
	z_info_list.append([cut_win_list[0],cut_win_list[-1],len(cut_win_list)])
	'''
	if len(cut_win_list)==1:
		z_list.append(cut_win_list[0])
	else:
		z_list.append(cut_win_list[0])
		z_list.append(cut_win_list[-1])
	'''
	z_list.append([cut_win_list[0],len(new_index_list)])
	new_index_list += cut_win_list
	z_list.append([cut_win_list[-1],len(new_index_list)-1])
	print len(new_index_list),len(z_list)
	return new_index_list,z_info_list,z_list






def range_insert(begin_point,end_point,point_len):
	'''
	功能：
	    将首尾之间用直线相连
	参数：
	   begin_point : 起始点数值
	   end_point ： 结束点数值
	   point_len ： 整个数组的长度
	'''
	if point_len == 1:
		return [end_point]
	point_list =[]
	g = (end_point - begin_point)/(point_len -1)
	for i in range(point_len-1):
		point_list.append(begin_point+i*g)
	point_list.append(end_point)
	return point_list




def find_most_likely(ori_z_list,pair_list,alpha,beta):
	'''
	function:
	     从一系列数据中，找出和给定列表相似的形状
	parmas：
	    ori_z_list: 原始所有的大Z状图[[v1,i1],[v2,i2]...]
	    pair_list : 需要匹配的形状[[v1,i1],[v2,i2],[v3,i3]]
	Return：
	     返回匹配成功的形状列表
	'''
	win = len(pair_list)
	likely_wave = []
	dis_list = []
	for i in range(len(ori_z_list)-win+1):
		cur_wave = ori_z_list[i:i+win]
		cur_dis = wave_cor(cur_wave,pair_list,alpha,beta)
		likely_wave.append([cur_wave,cur_dis])
		dis_list.append(cur_dis)
	#dis_list.remove(0.0)
	print "distence",min(dis_list),sum(dis_list)/len(dis_list),max(dis_list),dis_list.count(100)
	return likely_wave




def wave_cor(z_list_1,z_list_2,alpha,beta):
	'''
	function:
	      对z型图做相似性判断
	params:
	    z_list_1: [up,down,up,down...]
	    z_list_2: [up,down,up,down...]
	'''
	z_list_1_up,z_list_1_down = split_up_down(z_list_1)
	index_1_up= get_sorted_index(z_list_1_up)
	index_1_down= get_sorted_index(z_list_1_down)

	z_list_2_up,z_list_2_down = split_up_down(z_list_2)
	index_2_up = get_sorted_index(z_list_2_up)
	index_2_down = get_sorted_index(z_list_2_down)


	if index_1_up != index_2_up or index_1_down != index_2_down:
		#print index_1_up,index_2_up
		#print index_1_down,index_2_down
		return 100
	return get_dis_list(z_list_1,z_list_2,alpha,beta)


def get_dis_list(z_list_1,z_list_2,alpha,beta):
	'''
	function:
	    测算两个列表的距离
	parmas：
	    z_list_1 : 原始的z列表数据［［v1,t1］,[v2,t2],[v3,t3]］
	    z_list_2 : 同上
	附注：
	     用于
	'''
	if len(z_list_2)!=len(z_list_1) or len(z_list_1)<=2:
		print "length not equal"
		return -1
	alpha_part = 0
	beta_part = 0 
	for i in range(len(z_list_1)-1):
		dis_v = abs(abs(z_list_1[i+1][0]-z_list_1[i][0])-abs(z_list_2[i+1][0]-z_list_2[i][0]))
		alpha_part += dis_v
		dis_k = abs(abs(z_list_1[i+1][1]-z_list_1[i][1])-abs(z_list_2[i+1][1]-z_list_2[i][1]))
		beta_part += dis_k
	return (alpha * alpha_part + beta * beta_part)/(len(z_list_1)-1)






def get_sorted_index(z_list):
	'''
	function:
	    将z列表按第一列的排序，给出下标列表
	'''
	sort_z_list = sorted(z_list,key = lambda x:x[1])
	index_up = zip(*sort_z_list)[1]
	#index_up = [x-min(index_up) for x in index_up]
	return index_up


def split_up_down(z_list):
	'''
	function:
	    将一个列表中的元素按照奇偶分成两列
	'''
	split_up =[] 
	split_down =[] 
	split_0 = []
	split_1 = []
	min_value = z_list[0][1]
	#print min_value
	for i in range(len(z_list)):
		if i%2==0:
			split_0.append([z_list[i][0],z_list[i][1]-min_value])
		else:
			split_1.append([z_list[i][0],z_list[i][1]-min_value])
	if z_list[1]>z_list[0]:
		split_down  = split_0
		split_up = split_1
	else:
		split_down = split_1
		split_up = split_0
	return split_up,split_down



def predict_value(train_price_list,train_z_list,pair_price_list,pair_z_list,win,thr1,thr2):
	'''
	function:
	     从训练数据集合中找出和pair_wave相似的波形，并将这些相似波形后续的走势统计返回
	params:
	     train_list: 训练数据集合
	     pair_wave: 需要匹配的波形
	     thr1: %b 切割后对应会价格曲线的，反弹值大于某个阈值。该阈值为事件触发点
	     thr2: 寻找相似b%的z状图波形时，两个匹配的波形之间距离的阈值
	'''
	#pair_boll_list = get_boll_index(pair_price_list)
	#pair_b_z_list,pair_z_info_list,pair_z_list = index_cut(pair_boll_list,0.2)
	#pair_b_z_list,pair_z_info_list,pair_z_list = index_cut(pair_price_list,3)
	if len(pair_z_list) < win:
		return 0
	pair_i = zip(*pair_z_list)[1]
	#print "pair price index",pair_i[-2],pair_i[-1]
	if abs(pair_price_list[pair_i[-2]] - pair_price_list[pair_i[-1]]) < thr1:
		'''
		step－0: 寻找触发点，触发条件是反弹一定阈值
		'''
		return 0
	pair_i = pair_i[-1-win:-1]
	pair_z_list = pair_z_list[-win:]
	near_wave_list = find_most_likely(train_z_list,pair_z_list,0.6,0.4)#在b％指标中寻找相似的Z状图
	near_wave_list = sorted(near_wave_list,key = lambda x:x[1])
	predict_index_list = []#[z_list_index]
	for n in near_wave_list:
		cur_wave = n[0]
		cur_dis = n[1]
		print cur_dis,cur_wave
		if cur_dis > thr2:
			break
		predict_index_list.append(train_z_list.index(cur_wave[-1]))
		
	predict_value_list = []
	for i in predict_index_list:
		cur_polor_price = train_price_list[train_z_list[i][1]]
		last_polor_price = train_price_list[train_z_list[i-1][1]]
		if len(train_z_list) <= i+1:
			continue
		next_polor_price = train_price_list[train_z_list[i+1][1]]#
		#print "predict train z list",train_z_list[i+1],train_z_list[i]
		predict_value_list.append([next_polor_price-cur_polor_price,train_z_list[i+1][1]-train_z_list[i][1]])
	if not predict_value_list:
		return 0
	print "predict_value_list",predict_value_list 
	return predict_value_list


import pickle

def gen_train_model(model_fn):
	'''
	把训练数据训练出来的模型存储下来
	'''
	fn="/Users/luoaoxue/Dev/stock_minite/trans/sh/sh600009.txt"
	fn = "/Users/luoaoxue/Dev/backtest/rb1610_2016082_train"
	price_index = 6
	thr1 = 0.6#切割b％的阈值0.4,0.6
	thr2 = 1#形状匹配的触发点，需要切割对应的价格反弹值
	dis_thr = 0.1 #两个匹配波形的距离必须小于该阈值
	thr3 = 1 #匹配后的波形，预测的涨跌值的阈值
	thr4 = 10 #匹配后的波形，预测的涨跌所需的最长／短的持仓时间（过了该时间会跌）
	drawback_thr5 = 0.001
	#drawback_thr5 = 1
	win = 4
	'''
	不用b% 做为判断标准，适用价格做为切割标的
	'''
	train_price_list = read_data(fn=fn,i_price = 6)
	train_b_list = get_boll_index(train_price_list)
	train_b_z_list,train_z_info_list,train_z_list= index_cut(train_b_list,thr1)
	with open(model_fn,'wb') as f:
		pickle.dump(train_z_list,f)
		pickle.dump(train_price_list,f)





def train_z_list(price_list):
	'''
	训练出来的模型应该是一个模式
	'''
	b_index_list = get_boll_index(price_list)
	new_index_list,z_info_list,z_list = index_cut(b_index_list,0.2)
	return z_list



def cell_test():
	'''
	单元测试
	'''
	#price_list = read_data(fn="/Users/luoaoxue/Dev/stock_minite/trans/sh/sh600009.txt",i_price = 9)
	price_list = read_data(fn =  "/Users/luoaoxue/Dev/backtest/rb1610_20160830.txt",i_price = 6)
	#price_list = get_ma_list(price_list,240)
	b_index_list = get_boll_index(price_list)
	#ln_index_list = get_ln_index(price_list)
	new_index_list,z_info_list,z_list = index_cut(b_index_list,0.5)
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

