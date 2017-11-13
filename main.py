#!/usr/bin/python
# -*- coding: utf-8 -*- 
# @File Name: main.py
# @Created:   2017-11-08 20:52:00  seo (simon.seo@nyu.edu) 
# @Updated:   2017-11-12 22:42:59  Simon Seo (simon.seo@nyu.edu)

import banker
from banker import DEBUG
from banker.taskmanager import TaskManager
import sys

def main():
	if DEBUG:
		for i in range(1, 13):
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
	else:
		assert(len(sys.argv) > 1), 'input file is required.'
		filename = sys.argv[1]
		tm = TaskManager('fifo')
		tm.parseInput(filename)
		tm.main()

		tm = TaskManager('banker')
		tm.parseInput(filename)
		tm.main()

if __name__ == '__main__':
	main()