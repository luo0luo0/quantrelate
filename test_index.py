#coding:utf-8
import sys




def read_data():
	data_dir = ""
	for fn in os.listdir(data_dir):
		fn = data_dir = fn
		p_list = []
		for line in open(fn):
			if not line.strip():
				continue
			parts = line.strip().split(",")
			p = float(parts[6])
			p_list.append(p)
		plot_index(p_list)




def plot_index(p_list):
	pass 