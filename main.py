#!/usr/bin/python
# -*- coding: utf-8 -*- 
# @File Name: main.py
# @Created:   2017-11-08 20:52:00  seo (simon.seo@nyu.edu) 
# @Updated:   2017-11-12 22:00:22  Simon Seo (simon.seo@nyu.edu)

import banker
from banker import DEBUG
from banker.taskmanager import TaskManager
import sys

def main():
	sys.argv.append('input/input-01.txt')
	filename = sys.argv[1]
	for i in range(5, 13):
		num = ('0' + str(i))[-2:]
		filename = 'input/input-{}.txt'.format(num)
		print(filename)

		tm = TaskManager('fifo')
		tm.parseInput(filename)
		tm.main()

		tm = TaskManager('banker')
		tm.parseInput(filename)
		tm.main()
		print()

	# filename = 'input/input-04.txt'
	# tm = TaskManager('banker')
	# tm.parseInput(filename)
	# tm.main()
	print()


if __name__ == '__main__':
	main()