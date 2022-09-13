#coding:utf-8


import sys

import os
import math
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
	return str(100 * RS /(1+RS)),str(float(len(up_list))-len(down_list))

def comp_index(cur_date,p_list):
  mean_win = sum(p_list)/len(p_list)
  narr = np.array(p_list)
  narr2 = narr * narr
  sum2 = narr2.sum()
  var_win = (sum2/len(p_list)) - mean_win**2
  var_win = math.sqrt(abs(var_win))
  print cur_date,"\t",max(p_list)-min(p_list),'\t',var_win,"\t",'\t'.join(gen_RSI(p_list))


def gen_index_before():
  dir = "/data/jeactp_data/rb1701/"
  for fn in os.listdir(dir):
    cur_date = fn.split("_")[1]
    fn = dir+fn
    p_list = []
    for line in open(fn):
      if not line.strip():
        continue
      parts = line.strip().split(",")
      hour = int(parts[0].split()[1].strip().split(":")[0])
      if hour < 9:
        continue
      p_list.append(float(parts[6]))
      if len(p_list) == 3600:
        comp_index(cur_date,p_list)
        break
      

if __name__ == "__main__":
  gen_index_before()
