#coding:utf-8

'''
  策略部分功能：
     直接使用实盘部分的代码，即可对响应策略进行回测
     保持回测和实盘代码 可以无缝接通
'''

import context



class GlobalStraVar:
	'''
	全局变量可以在任何地方修改使用
	'''
	hold_bar_cnt = 0
	hold_max = 0
	hold_min = 0
	pass


def initstraGlobal():
	'''
	将全局变量设置下
	策略部分
	'''
	pass



def proc_bar_hold(GlobalBackVar,cur_open,cur_high,cur_low,cur_close):
	GlobalStraVar.hold_bar_cnt +=1
	GlobalStraVar.hold_max = max(GlobalStraVar.hold_max,cur_close)
	GlobalStraVar.hold_min = min(GlobalStraVar.hold_min,cur_close)
	if GlobalBackVar.hold_price > 0:
		if cur_close - GlobalBackVar.hold_price > 20:
			return -1
		if GlobalStraVar.hold_max - cur_close > 6:
			return -1
	if GlobalBackVar.hold_price < 0 :
		if GlobalBackVar.hold_price - cur_close > 20:
			return 1
		if GlobalBackVar.hold_price - GlobalStraVar.hold_min > 6:
			return 1
	return 0



def proc_bar_sig(GlobalBackVar,cur_open,cur_high,cur_low,cur_close):
	if cur_close > cur_open +1 and cur_high > cur_close+2:
		return 1
	if cur_close < cur_open -1 and cur_low < cur_close -2:
		return -1
	return 0



def pro_bar_frame(MktData,GlobalBackVar,bar_len):
	if len(MktData.new_list)%bar_len == 0:
		'''
		基于Bar的操作策略
		'''
		cur_open = MktData.new_list[-bar_len]
		cur_close = MktData.new_list[-1]
		cur_high = max(MktData.new_list[-bar_len:])
		cur_low = min(MktData.new_list[-bar_len:])
		if GlobalBackVar.hold_price !=0:
			'''
			如果有持仓，相关止盈止损控制如下
			'''
			GlobalStraVar.hold_bar_cnt +=1
			res = proc_bar_hold(GlobalBackVar,cur_open,cur_high,cur_low,cur_close)
			if res == 1:
				return "buy2cover",MktData.ask_list[-1],1
			if res == -1:
				return "sell2cover",MktData.bid_list[-1],1
		res = proc_bar_sig(GlobalBackVar,cur_open,cur_high,cur_low,cur_close)#模型信号相关内容
		if GlobalBackVar.hold_price == 0 and res ==1:
			GlobalStraVar.hold_bar_cnt =1 
			return "buy",MktData.ask_list[-1],1
		if GlobalBackVar.hold_price < 0 and res == 1:
			GlobalStraVar.hold_bar_cnt = 1
			return "buy2cover",MktData.ask_list[-1],1
		if GlobalBackVar.hold_price == 0 and res == -1:
			return "sell",MktData.bid_list[-1],1
		if GlobalBackVar.hold_price > 0 and res == -1:
			return  "sell2cover",MktData.bid_list[-1],1

def pro_bar_frame_1(MktData,GlobalBackVar,bar_len):
	if len(MktData.new_list)%bar_len == 0:
		'''
		基于Bar的操作策略
		'''
		cur_open = MktData.new_list[-bar_len]
		cur_close = MktData.new_list[-1]
		cur_high = max(MktData.new_list[-bar_len:])
		cur_low = min(MktData.new_list[-bar_len:])
		#单纯用于找横盘点位，找到后的方向比较难判断。
		if abs(cur_close- cur_open)/(cur_high - cur_low) < 0.1 and  len(MktData.new_list) > 2400:
			#print "cross",len(MktData.new_list),MktData.new_list[-2400],MktData.new_list[-1],GlobalBackVar.hold_price
			if  MktData.new_list[-2400]>MktData.new_list[-1] +4 and GlobalBackVar.hold_price == 0:
				GlobalStraVar.hold_bar_cnt = 1
				return "buy",MktData.ask_list[-1],1
			if MktData.new_list[-2400]<MktData.new_list[-1] -4 and GlobalBackVar.hold_price == 0:
				GlobalStraVar.hold_bar_cnt = 1
				return "sell",MktData.bid_list[-1],1
			if GlobalBackVar.hold_price> 0 and GlobalStraVar.hold_bar_cnt > 20:
				return "sell2cover",MktData.bid_list[-1],1
			if GlobalBackVar.hold_price < 0 and GlobalStraVar.hold_bar_cnt > 20:
				return "buy2cover",MktData.ask_list[-1],1




def pro_tick_frame(MktData,GlobalBackVar):
	if len(MktData.new_list) < 6000:
		return ""
	ma1 =sum( MktData.new_list[-3000:])/len(MktData.new_list[-3000:])
	ma2 = sum(MktData.new_list[-6000:])/len(MktData.new_list[-6000:])
	if ma1 > ma2 and GlobalBackVar.hold_price < 0:
		return "buy2cover",MktData.bid_list[-1],1
	elif ma1 < ma2 and GlobalBackVar.hold_price > 0:
		return "sell2cover",MktData.bid_list[-1],1
	if ma1 > ma2 and GlobalBackVar.hold_price == 0:
		return "buy",MktData.ask_list[-1],1
	elif ma1 < ma2 and GlobalBackVar.hold_price ==0:
		return "sell",MktData.bid_list[-1],1

	pass

def handle_data(MktData,GlobalBackVar):
	'''
	策略部分
	参数：
	    MktDadta 为目前为止的行情数据
	返回：
	    “” 不操作
	    [instru],buy/sell／buy2cover/sell2cover,amount,price ={限价：价格＋最久成交时间 ｜ 对价：买一价／卖一价 ｜ 最新价 } ＃现只支持对价
	    eg: buy,ask,1
	    eg: sell2cover,bid,ratio
	'''
	#return pro_bar_frame(MktData,GlobalBackVar,1200)
	return pro_tick_frame(MktData,GlobalBackVar)
	#return pro_bar_frame_1(MktData,GlobalBackVar,120)


