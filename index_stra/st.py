#coding:utf-8


import sys


cur_date = ""
cur_size = 0

for line in sys.stdin:
  if line.strip() == "":
    cur_date = ""
    continue
  if "begin" in line:
    cur_date = line.strip().split("/")[-1].split(".")[0]
    continue
  if cur_date!="" and "gain_list" in line and (not "[" in line):
    if 1 or cur_size > 2500:
      print cur_date,"\t",line.strip().split()[-1]
      continue
  if (not "gain_list" in line) and len(line.strip().split())==2:
    cur_size = int(line.strip().split()[0])
