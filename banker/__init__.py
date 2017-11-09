#!/usr/bin/python
# -*- coding: utf-8 -*- 
# @File Name: __init__.py
# @Created:   2017-11-08 20:45:52  seo (simon.seo@nyu.edu) 
# @Updated:   2017-11-08 21:13:10  Simon Seo (simon.seo@nyu.edu)

def parseInput(filename):
	"""returns list of process specs"""
	result = []
	if not os.path.isfile(filename):
		raise Exception('The input file does not exist. The input filename should be the last argument.')
	with open(filename, 'r') as f:
		nums = []
		for l in f:
			nums += [int(el) for el in l.strip().split() if el.isnumeric()]
	psl = nums.pop(0) #processes (list) length
	for i in range(psl):
		result.append(nums[4*i:4*i+4])
	return result
