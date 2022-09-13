# coding:utf-8

import sys
import os
import datetime
#import pandas as pd



colnames = [
        'RecvTime'           ,
        'NoUse'              ,        
        'TradingDay'         ,  # 交易日 
        'InstrumentID'       ,  # 合约代码
        'ExchangeID'         ,  # 交易所代码
        'ExchangeInstID'     ,  # 合约在交易所的代码
        'LastPrice'          ,  # 最新价
        'PreSettlementPrice' ,  # 上次结算价
        'PreClosePrice'      ,  # 昨收盘
        'PreOpenInterest'    ,  # 昨持仓量
        'OpenPrice'          ,  # 今开盘
        'HighestPrice'       ,  # 最高价 
        'LowestPrice'        ,  # 最低价
        'Volume'             ,  # 数量
        'Turnover'           ,  # 成交金额
        'OpenInterest'       ,  # 持仓量
        'ClosePrice'         ,  # 今收盘
        'SettlementPrice'    ,  # 本次结算价
        'UpperLimitPrice'    ,  # 涨停板价
        'LowerLimitPrice'    ,  # 跌停板价
        'PreDelta'           ,  # 昨虚实度
        'CurrDelta'          ,  # 今虚实度
        'UpdateTime'         ,  # 最后修改时间
        'UpdateMillisec'     ,  # 最后修改毫秒
        'BidPrice1'          ,  # 申买价一
        'BidVolume1'         ,  # 申买量一
        'AskPrice1'          ,  # 申卖价一
        'AskVolume1'         ,  # 申卖量一
        'BidPrice2'          ,  # 申买价二
        'BidVolume2'         ,  # 申买量二
        'AskPrice2'          ,  # 申卖价二 
        'AskVolume2'         ,  # 申卖量二
        'BidPrice3'          ,  # 申买价三
        'BidVolume3'         ,  # 申买量三
        'AskPrice3'          ,  # 申卖价三
        'AskVolume3'         ,  # 申卖量三
        'BidPrice4'          ,  # 申买价四
        'BidVolume4'         ,  # 申买量四
        'AskPrice4'          ,  # 申卖价四
        'AskVolume4'         ,  # 申卖量四
        'BidPrice5'          ,  # 申买价五
        'BidVolume5'         ,  # 申买量五
        'AskPrice5'          ,  # 申卖价五
        'AskVolume5'         ,  # 申卖量五
        'AveragePrice'       ,  # 当日均价
        'ActionDay'             # 业务日期
    ];

def GetDateList(start_date, end_date):
    Sdate = datetime.datetime.strptime(start_date, "%Y%m%d").date()
    Edate = datetime.datetime.strptime(end_date, "%Y%m%d").date()
    d = Sdate
    result = []
    while d <= Edate:
        datestr = d.strftime("%Y%m%d")
        result.append(datestr)
        d += datetime.timedelta(days=1)
    return result

def ReadCtpData(id, start_date, end_date):
    data = pd.DataFrame()
    datelist = GetDateList(start_date, end_date)
    for datestr in datelist:
        filename = "/data/jeactp_data/%s/%s_%s.txt" %(id, id, datestr)
        if os.path.exists(filename):
            print "Reading file: %s" %filename
            d1 = pd.read_csv(filename, header=None, names=colnames);
            data = data.append(d1)
    return data 

def GetTopTradeInstrumentID(code, datestr):

    if "rb" == code:
        if   datestr <= "20160731":
            return 'rb1610'
        elif datestr <= "20160930":
            return 'rb1701'
    if "jd" == code:
        return "jd1701"
    else:
        return code+"1701"








