#coding:utf-8
import sys

from util import *
from strategy import *
import matplotlib.pyplot as plt
import os

import sys
import math

'''
1.回测平台：
   用于支撑（1）期货的回测 （2）股票的回测

（1）期货回测：
   区间为日期：beginTime,endTime
   不需要position类，需要每日的交易总结
   需要品种类：涉及品种的保证金，品种的手续费(GlobalVar 里的tax等信息取决于不同的品种)
   对比品种：空

（2）股票回测：
   区间为日期：beginTime,endTime
   Position: 最新当前持仓，并输出到持仓文件中，用于下一轮的解析
'''









	



OrderType = {
	"Buy":1,
	"Sell":2,
	"Buy2Cover":3,
	"Sell2Cover":4
}

PriceType = {
	"Limited":1,#限价单
	"Market":2#市价单
}



import time
'''
'''




class ContextVar:
	initCash = 100000
	compInstru = "rb1701"
	beginDate = 20160101
	endDate  = 20160701
	commission = 0
	tax = 0
	instrument = "rb1701"
	priceDict = {}#需要读区
	isStock = False
	isFuture = True





class GlobalBackVar:
	hold_price = 0#多次买入均价
	left_ratio = 1
	hold_max = 0 #持有期的最大值
	hold_min = 0 #持有期的最小值
	profit_list = [] #日内交易的每笔交易的盈利列表
	buy_index_list = []
	sell_index_list = []
	over_index_list = []

class MktData:
	open_list = []
	close_list = []
	high_list = []
	low_list = []
	bid_list = []
	ask_list = []
	new_list = []
	time_list = []
	new_dict = {}

def initBackVar():
	GlobalBackVar.hold_price = 0
	GlobalBackVar.left_ratio = 0
	GlobalBackVar.hold_max = 0
	GlobalBackVar.hold_min = 0
	GlobalBackVar.profit_list = []
	MktData.open_list = []
	MktData.high_list = []
	MktData.low_list = []
	MktData.close_list = []
	MktData.bid_list = []
	MktData.ask_list = []
	MktData.new_list = []
	MktData.time_list = []


def positionMgr(op,op_p,op_r):
	if op == "buy":
		GlobalBackVar.hold_price = op_p
		GlobalBackVar.left_ratio += op_r
		GlobalBackVar.hold_max = op_p
		GlobalBackVar.hold_min = op_p
		GlobalBackVar.buy_index_list.append(MktData.time_list[-1])
		print "buy@",op_p
		return
	if op == "sell":
		GlobalBackVar.hold_price = -op_p
		GlobalBackVar.left_ratio += op_r
		GlobalBackVar.hold_max = op_p
		GlobalBackVar.hold_min = op_p
		GlobalBackVar.sell_index_list.append(MktData.time_list[-1])
		print "sell@",op_p
		return
	if op == "buy2cover":
		if GlobalBackVar.hold_price >= 0 or GlobalBackVar.left_ratio <=0:
			print "Err: No short Position hold"
			return
		if GlobalBackVar.hold_price <0:
			GlobalBackVar.left_ratio -= op_r
			profit = op_r * (abs(GlobalBackVar.hold_price)-op_p)
			GlobalBackVar.profit_list.append(profit)
			print "buy2cover@",op_p,"profit:",profit,"left_ratio:",GlobalBackVar.left_ratio
			GlobalBackVar.over_index_list.append(MktData.time_list[-1])
			if GlobalBackVar.left_ratio == 0:
				GlobalBackVar.hold_price = 0
	if op == "sell2cover":
		if GlobalBackVar.hold_price <=0 or GlobalBackVar.left_ratio <=0:
			print "Err: No long position hold"
			return
		GlobalBackVar.left_ratio -= op_r
		profit = op_r * (op_p - abs(GlobalBackVar.hold_price))
		GlobalBackVar.profit_list.append(profit)
		print "sell2cover@",op_p,"profit:",profit,"left_ratio:",GlobalBackVar.left_ratio
		GlobalBackVar.over_index_list.append(MktData.time_list[-1])
		if GlobalBackVar.left_ratio == 0:
			GlobalBackVar.hold_price = 0
	if op == "clear":
		if GlobalBackVar.hold_price > 0:
			profit = GlobalBackVar.left_ratio * (op_p - GlobalBackVar.hold_price)
			GlobalBackVar.left_ratio = 0
			GlobalBackVar.hold_price = 0
			GlobalBackVar.profit_list.append(profit)
			print "clear opeartion for Sell2Cover:",profit
		if GlobalBackVar.hold_price < 0:
			profit = GlobalBackVar.left_ratio * (abs(GlobalBackVar.hold_price) - op_p)
			GlobalBackVar.left_ratio = 0
			GlobalBackVar.hold_price = 0
			GlobalBackVar.profit_list.append(profit)
			print "clear opeartion for Sell2Cover:",profit



	

def procOneTick():
	'''
	处理当前tick
	'''
	
	res = handle_data(MktData,GlobalBackVar)#支持后续的可以按1分钟／5分钟的Bar来执行
	if res:
		op,op_p,op_r = res
		positionMgr(op,op_p,op_r)

	


def procOneDay(fn):
	initBackVar()#每天重新初始化
	initstraGlobal()
	for line in open(fn):
		try:
			parts = line.strip().split(",")
			RecvTime = parts[MktConf.time_index]
			HourMinute = RecvTime[11: 16]
			iMinuteCnt = int(HourMinute[0: 2]) * 60 + int(HourMinute[3: 5])
			bid_price = float(parts[MktConf.bid_index])
			ask_price = float(parts[MktConf.ask_index])
			new_price = float(parts[MktConf.new_index])
			if iMinuteCnt < 9 * 60:
				continue
			if iMinuteCnt > 15*60:
				positionMgr("clear",new_price,1)
				return GlobalBackVar.profit_list
			MktData.time_list.append(iMinuteCnt)
			#MktData.open_list.append(float(parts[MktConf.open_index]))
			#MktData.high_list.append(float(parts[MktConf.high_index]))
			#MktData.low_list.append(float(parts[MktConf.low_index]))
			#print MktConf.close_index,parts[MktConf.close_index]
			#MktData.close_list.append(float(parts[MktConf.close_index]))
			MktData.bid_list.append(bid_price)
			MktData.ask_list.append(ask_price)
			MktData.new_list.append(new_price)
			MktData.new_dict[iMinuteCnt] = new_price
		except:
			continue
		procOneTick()
	return GlobalBackVar.profit_list






def gen_voltility(NetList):
	'''
	生成收益波动率
	'''
	newList = NetList[1:]
	u_list = map(lambda x,y:math.log(x/y),NetList[1:],NetList[:-1])
	u_std = gen_std(u_list)
	return u_std*math.sqrt(252)




'''
期货策略需要设定是不是日内策略，或者是其他
'''
if __name__ == "__main__":
	'''
	回测需要指定的环境变量：
	  回测品种：   rb
      回测开始时间：   20160701
      回测结束时间：   20160930
      交易类型：白天日内（day）; 夜盘日内（night）; 日间交易（iter）／／现在默认为白天日内
      回测类型：日（day），月(month)，全部（all）
    function：
      回测区间内的 品种的 主力合约相关内容
	'''
	instru = sys.argv[1]
	beginDate = sys.argv[2]
	endDate = sys.argv[3]
	tradeType = sys.argv[4]
	depositCash = float(sys.argv[5])
	backType = sys.argv[6]
	print instru,beginDate,endDate,tradeType,depositCash,backType
	dateList,all_days = getDateList(beginDate,endDate)#获取回测期间的日期列表
	print dateList
	initMktConf()#将需要读取行情文件的相应列下标进行设置
	NetList = [depositCash]#净值曲线由每天生成一次（日间），初始值为交易一手所需的保证金   
	srcDir = "/Users/luoaoxue/Dev/future_data/"
	dayProfit = []
	for d in dateList:
		fn = srcDir + instru + "/" + instru+"_"+d+".txt"
		print ""
		print ""
		print d
		if not os.path.exists(fn):
			print "Not exist:"+d
			continue
		gain = procOneDay(fn)
		if len(gain)==0:
			print "Gain@",d,0
		else:
			print "Gain@",d,sum(gain),min(gain),max(gain)
		if backType=="day":
			plt.figure(1)
			plt.plot(MktData.time_list,MktData.new_list,"y")
			ave_list = [sum(MktData.new_list[:i+1])/len(MktData.new_list[:i+1]) for i in range(len(MktData.new_list))]
			plt.plot(MktData.time_list,ave_list)
			title_str = "["+d+"]"+u"交易"+str(len(gain))+u"次   盈利"+str(len([i for i in gain if i>0]))+u"次 亏损"+str(len([i for i in gain if i<0]))+u"次"
			plt.title(title_str)
			buy_y = [MktData.new_dict[x] for x in GlobalBackVar.buy_index_list]
			sell_y = [MktData.new_dict[x] for x in GlobalBackVar.sell_index_list]
			over_y = [MktData.new_dict[x] for x in GlobalBackVar.over_index_list]
			buy =plt.scatter(GlobalBackVar.buy_index_list,buy_y,s=50,c="red")
			sell = plt.scatter(GlobalBackVar.sell_index_list,sell_y,s=50,c="green")
			over = plt.scatter(GlobalBackVar.over_index_list,over_y,s=50,c="blue")
			plt.legend((buy, sell, over), (u'开多', u'开空', u'平仓'), loc=2)
			plt.show()
		NetList.append(NetList[-1]+sum(gain))
		dayProfit.append(sum(gain))
	plt.figure(1)
	plt.title(u"日净值曲线如下")
	group_labels = ['20160911']+dateList
	plt.plot(range(len(NetList)),NetList)
	plt.xticks(range(len(NetList)),group_labels, rotation=0) 
	plt.show()
	print ""
	print ""
	print "================== 策略回测期间指标================="
	print ""
	print "回测天数：      ",len(dayProfit)
	print "最高日盈利：    ",max(dayProfit)
	print "最低日盈利：    ",min(dayProfit)
	print "日均赢利：      ",sum(dayProfit)/len(dayProfit)
	print "总收益：        ",NetList[-1]-NetList[0]
	print "区间最大回撤：   ",genMaxDrawBack(NetList)
	print "交易日净值列表:  ",NetList
	print "年化收益：      ",all_days,str(100*365*((NetList[-1]-NetList[0])/NetList[0])/all_days)+"%"
	print "年化收益波动率： ",str(100*gen_voltility(NetList))+"%"
	#https://www.zhihu.com/question/19770602
	print "=================================================="
	print ""
	'''
	可视化区域：
	（1）全局绘制，净值曲线NetList
	（2）某一天，绘制交易时间点和入场的线
	'''




	



