####
#    用于执行所有程序的脚本
#    	  回测品种：   rb
#      回测开始时间：   20160701
#      回测结束时间：   20160930
#      交易类型：白天日内（day）; 夜盘日内（night）; 日间交易（iter）／／现在默认为白天日内
#      回测类型：日（day），月(month)，全部（all）
#
#
####


#日内交易，按天输出相关结果
python context.py rb1701 20161021 20161021 day 3000 day
#python context.py rb1701 20160817 20160901 day 3000 day
#日内交易，按整体输出相关结果
#不需要输出每天的结果

