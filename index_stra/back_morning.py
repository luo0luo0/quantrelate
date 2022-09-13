
# coding:utf-8

#from sklearn.datasets import load_iris

import os
import sys
#import pandas as pd
#import numpy as np
#from sklearn.ensemble import RandomForestClassifier

import ctp_data_util as cutil
#from all_features import GenFeatures 
import cPickle 
#from dataset import  GenDataSet
import time
import numpy as np
import math

class GlobalVar:
    test_time_interval_beg = None  # 测试时间段的起始时间，以一天内的第几分钟计算
    test_time_interval_end = None # 测试时间段的起始时间，以一天内的第几分钟计算

    dayProfitSum = 0 # 日内累积利润

    is_hold = False;
    hold_direction = ""
    last_direction = ""
    open_price = 0

    price_sum = 0
    price_cnt = 0
    left_ratio = 1
    today_first_price = 0

    price_list = []
    OpenBegin = False
    buy_sell_threadhold = 0

    price_max = 0
    price_min = 999999 

    trade_cnt = 0   # 交易次数

    stratety_type = 1 # 策略风格类型

    stratety_type1_profitSum = 0
    stratety_type2_profitSum = 0
    stratety_type999_profitSum = 0
    
    enable_stop_loss = False
    enable_stop_profit = False
    stop_profit = 26

    is_strategy_first_trade = True 

    going_to_direction = 'buy'
    '''
    新策略相关变量 
    '''
    last_EMA = 0
    EMA = 0
    enable_part = False
    hold_max = 0
    hold_min = 0

def GlobalVar_Reset():
    GlobalVar.dayProfitSum = 0 # 日内累积利润

    GlobalVar.is_hold = False;
    GlobalVar.hold_direction = ""
    GlobalVar.last_direction = ""
    GlobalVar.open_price = 0

    GlobalVar.price_sum = 0
    GlobalVar.price_cnt = 0

    GlobalVar.today_first_price = 0

    GlobalVar.price_list = []
    GlobalVar.OpenBegin = True
    GlobalVar.buy_sell_threadhold = 0

    GlobalVar.price_max = 0
    GlobalVar.price_min = 999999 

    GlobalVar.trade_cnt = 0

    GlobalVar.stratety_type = 1 # 策略风格类型

    #GlobalVar.stratety_type1_profitSum = 0
    #GlobalVar.stratety_type2_profitSum = 0
    
    GlobalVar.enable_stop_loss = False
    GlobalVar.enable_stop_profit = False
    GlobalVar.stop_profit = 26

    GlobalVar.is_strategy_first_trade = True 

    GlobalVar.going_to_direction = 'buy'



# 取交易反方向
def GetOppositDirection(direction):
    if "buy" == direction:
        return "sell"
    elif "sell" == direction:
        return "buy"
    else:
        print "GetOppositDirection() Error: 方向值错误"

# 开仓
def OpenPosition(RecvTime, direction, open_price):
    if GlobalVar.is_hold:
        print "OpenPosition() Error: 已经持仓，不能再开仓"
        return

    GlobalVar.is_hold = True
    GlobalVar.hold_direction = direction 
    GlobalVar.last_direction = direction 
    GlobalVar.open_price = open_price
    GlobalVar.trade_cnt += 1
    GlobalVar.left_ratio = 1
    print "[%s] Open  (　　) %-4s ---- Price: %-5.0f" %(RecvTime, direction, open_price)

# 平仓
def ClosePosition(RecvTime, CloseReason, BidPrice1, AskPrice1,ratio):
    if not GlobalVar.is_hold or GlobalVar.left_ratio<=0:
        print "Error: 未持仓，无法平仓!",GlobalVar.left_ratio,ratio
        return

    if "buy" == GlobalVar.hold_direction:
        close_price = BidPrice1
    elif 'sell' == GlobalVar.hold_direction:
        close_price = AskPrice1
    else:
        print "ClosePosition() Error: 持仓方向值错误: %s" %(GlobalVar.hold_direction)
        return 

    HandlingFee = 10  # 一次手续费
    if "" == CloseReason:
        CloseReason = "　　"

    thisProfit =ratio * GetProfit(GlobalVar.hold_direction, GlobalVar.open_price, close_price)
    GlobalVar.dayProfitSum += (thisProfit - HandlingFee)
    print "[%s] Close (%s) %-4s  Price: %-5.0f  本次利润: %-6.0f , 日内累积利润: %-6.0f, 部分: %f" \
        %(RecvTime, CloseReason, GetOppositDirection(GlobalVar.hold_direction), close_price, thisProfit, GlobalVar.dayProfitSum, ratio)
    GlobalVar.left_ratio = GlobalVar.left_ratio - ratio
    if GlobalVar.left_ratio == 0:
      GlobalVar.is_hold = False
      GlobalVar.hold_direction = ""
      GlobalVar.open_price = 0
    if 1 == GlobalVar.stratety_type:
        GlobalVar.stratety_type1_profitSum += (thisProfit - HandlingFee) 
    elif 2 == GlobalVar.stratety_type:
        GlobalVar.stratety_type2_profitSum += (thisProfit - HandlingFee)
    else:
        GlobalVar.stratety_type999_profitSum += (thisProfit - HandlingFee)
        print "未知策略类型!!!!!!"

    GlobalVar.is_strategy_first_trade = False

    
    #if thisProfit < 0:
    #    GlobalVar.OpenBegin = False
    if 1 == GlobalVar.trade_cnt and  thisProfit < 0:
    #if   thisProfit < 0:
        GlobalVar.stratety_type = 2
        GlobalVar.enable_stop_loss = True
        GlobalVar.enable_stop_profit = True
        print "[%s] 切换到策略２" %RecvTime
        GlobalVar.is_strategy_first_trade = True


    #if thisProfit < 0:
    #    GlobalVar.going_to_direction = GetOppositDirection(GlobalVar.hold_direction)
    #else: 
    #    GlobalVar.going_to_direction = GlobalVar.hold_direction

    #if thisProfit < 0:
    #    GlobalVar.OpenBegin = False

def GetProfit(direction, open_price, close_price):
    if "buy" == direction:
        return (close_price - open_price) * 10
    elif "sell" == direction:
        return (open_price - close_price) * 10
    else:
        print "direction error!!!!!"
        exit(-1)

def ProcOneLine(line):

    #--------------------
    # 解析数据     
    #--------------------
    fields = line.split(",")
    if (len(fields) < 46):
        return 

    try:
        RecvTime           = fields[0]
        #NoUse              = fields[1]
        #TradingDay         = fields[2]  # 交易日 
        #InstrumentID       = fields[3]  # 合约代码
        #ExchangeID         = fields[4]  # 交易所代码
        #ExchangeInstID     = fields[5]  # 合约在交易所的代码
        LastPrice          = float(fields[6])  # 最新价
        #PreSettlementPrice = float(fields[7])  # 上次结算价
        PreClosePrice      = float(fields[8])  # 昨收盘
        #PreOpenInterest    = float(fields[9])  # 昨持仓量
        OpenPrice          = float(fields[10])  # 今开盘
        #HighestPrice       = float(fields[11])  # 最高价 
        #LowestPrice        = float(fields[12])  # 最低价
        #Volume             = float(fields[13])  # 数量
        #Turnover           = float(fields[14])  # 成交金额
        #OpenInterest       = float(fields[15])  # 持仓量
        #ClosePrice         = float(fields[16])  # 今收盘
        #SettlementPrice    = float(fields[17])  # 本次结算价
        #UpperLimitPrice    = float(fields[18])  # 涨停板价
        #LowerLimitPrice    = float(fields[19])  # 跌停板价
        #PreDelta           = float(fields[20])  # 昨虚实度
        #CurrDelta          = float(fields[21])  # 今虚实度
        #UpdateTime         = fields[22]  # 最后修改时间
        #UpdateMillisec     = fields[23]  # 最后修改毫秒
        BidPrice1          = float(fields[24])  # 申买价一
        #BidVolume1         = float(fields[25])  # 申买量一
        AskPrice1          = float(fields[26])  # 申卖价一
        #AskVolume1         = float(fields[27])  # 申卖量一
        #BidPrice2          = fields[28]  # 申买价二
        #BidVolume2         = fields[29]  # 申买量二
        #AskPrice2          = fields[30]  # 申卖价二 
        #AskVolume2         = fields[31]  # 申卖量二
        #BidPrice3          = fields[32]  # 申买价三
        #BidVolume3         = fields[33]  # 申买量三
        #AskPrice3          = fields[34]  # 申卖价三
        #AskVolume3         = fields[35]  # 申卖量三
        #BidPrice4          = fields[36]  # 申买价四
        #BidVolume4         = fields[37]  # 申买量四
        #AskPrice4          = fields[38]  # 申卖价四
        #AskVolume4         = fields[39]  # 申卖量四
        #BidPrice5          = fields[40]  # 申买价五
        #BidVolume5         = fields[41]  # 申买量五
        #AskPrice5          = fields[42]  # 申卖价五
        #AskVolume5         = fields[43]  # 申卖量五
        #AveragePrice       = fields[44]  # 当日均价
        #ActionDay          = fields[45]  # 业务日期
    except:
        #print "except: 解析数据异常. RecvTime: %s" %(RecvTime)
        return


    HourMinute = RecvTime[11: 16]
    iMinuteCnt = int(HourMinute[0: 2]) * 60 + int(HourMinute[3: 5])

    if iMinuteCnt < GlobalVar.test_time_interval_beg or iMinuteCnt > GlobalVar.test_time_interval_end:
        return

    #print HourMinute + "  iMinuteCnt %d" %iMinuteCnt

    #--------------------
    # 缓存历史序列数据     
    #--------------------
    GlobalVar.price_list.append(LastPrice)

    GlobalVar.price_sum += LastPrice
    GlobalVar.price_cnt += 1

    if len(GlobalVar.price_list)==120:
        if OpenPrice - PreClosePrice > 3:
            OpenPosition(RecvTime, "buy", AskPrice1)
            return 0
        elif PreClosePrice - OpenPrice >3:
            OpenPosition(RecvTime, "sell", BidPrice1)
            return 0
        else:
            modelDirection = "ignore"
            return 1
    #====================
    #如果有持仓
    #===================
    if GlobalVar.is_hold:
      GlobalVar.hold_max = max(GlobalVar.hold_max,LastPrice)
      GlobalVar.hold_min = min(GlobalVar.hold_min,LastPrice)
      #到时间出场
      if len(GlobalVar.price_list)>=7200:
         if GlobalVar.hold_direction == "buy":
           ClosePosition(RecvTime,"半点出场",BidPrice1,AskPrice1,GlobalVar.left_ratio)
           return 1
         elif GlobalVar.hold_direction == "sell":
           ClosePosition(RecvTime,"半点出场",BidPrice1,AskPrice1,GlobalVar.left_ratio)
           return 1
      if GlobalVar.hold_direction == "buy" and LastPrice - GlobalVar.open_price >15 and GlobalVar.left_ratio > 0.4:
         ClosePosition(RecvTime,"止盈",BidPrice1,AskPrice1,GlobalVar.left_ratio)
         return 1
      elif GlobalVar.hold_direction == "sell" and GlobalVar.open_price - LastPrice > 15 and GlobalVar.left_ratio > 0.4:
         ClosePosition(RecvTime,"止盈",BidPrice1,AskPrice1,GlobalVar.left_ratio)
         return 1

    #====================    
    # 时间到达平仓期
    #====================    
    
    if iMinuteCnt > GlobalVar.test_time_interval_end - 10:
        #print "收盘清仓时段，时间：%s" %(iMinuteCnt)
        if GlobalVar.is_hold: 
            ClosePosition(RecvTime, "收盘", BidPrice1, AskPrice1,GlobalVar.left_ratio)
        return;
    


g_trade_cnt = 0
def ProcOneDay(InstrumentID, datestr):
    dataFileName = "/data/jeactp_data/%s/%s_%s.txt" %(InstrumentID, InstrumentID, datestr)
    if not os.path.exists(dataFileName):
        print "文件不存在: %s" %dataFileName
        return 0

    GlobalVar_Reset()
    with open(dataFileName, 'r') as f:
        for line in f: 
            if ProcOneLine(line):
               break
    print "日期: %s  日利润: %f \n\n" %(datestr, GlobalVar.dayProfitSum)
    global g_trade_cnt
    g_trade_cnt += GlobalVar.trade_cnt 
    return GlobalVar.dayProfitSum

def ShowUsage():
    print "python %s <合约代码> <起始日期> <结束日期> <日盘/夜盘>" %(sys.argv[0])
    print "\n例：python %s rb 20160801 20160831 day\n" %(sys.argv[0])
    print "参数: 日盘/夜盘"
    print "   day   -- 日盘"
    print "   night -- 夜盘"

if __name__ == "__main__":

    if len(sys.argv) < 5:
        ShowUsage()
        exit(-1)

    # 参数
    InstrumentCode = sys.argv[1]
    BegDate        = sys.argv[2] 
    EndDate        = sys.argv[3] 
    TimeInterval   = sys.argv[4]

    if "day" == TimeInterval:
        GlobalVar.test_time_interval_beg =  9 * 60 + 0 # "09:00"
        GlobalVar.test_time_interval_end = 15 * 60 + 0 # "15:00"
    elif "night" == TimeInterval:
        GlobalVar.test_time_interval_beg = 21 * 60 + 0 # "21:00"
        GlobalVar.test_time_interval_end = 23 * 60 + 0 # "23:00"
    else:
        print "TimeInterval error!"
        exit(-1)


    # 计算
    profit_list = []
    month_profit_sum = {}
    datelist = cutil.GetDateList(BegDate, EndDate)
    for datestr in datelist:
        print "日期: %s" %datestr
        InstrumentID = cutil.GetTopTradeInstrumentID(InstrumentCode, datestr)
        profit = ProcOneDay(InstrumentID, datestr)
        profit_list.append(profit)

        month = datestr[0: 6]
        if month not in month_profit_sum.keys():
            month_profit_sum[month] = 0
        month_profit_sum[month] += profit

    profit_sum = sum(profit_list)
    print "测试区间总利润: %f" %profit_sum
    print "最大日利润: %f" %(max(profit_list))
    print "最小日利润: %f" %(min(profit_list))
    print "交易次数: %d" %(g_trade_cnt)

    print "\n各策略类型带来收益: "
    print "  策略1: %f" %(GlobalVar.stratety_type1_profitSum)
    print "  策略2: %f" %(GlobalVar.stratety_type2_profitSum)
    print "  策略其它: %f" %(GlobalVar.stratety_type999_profitSum)

    print "各月份利润："
    for m in sorted(month_profit_sum.keys()):
        print m + " : %d" %(month_profit_sum[m])


