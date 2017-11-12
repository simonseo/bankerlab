#!/usr/bin/python
# -*- coding: utf-8 -*- 
# @File Name: algorithms.py
# @Created:   2017-11-08 21:24:09  seo (simon.seo@nyu.edu) 
# @Updated:   2017-11-12 03:58:25  Simon Seo (simon.seo@nyu.edu)
from banker import DEBUG

class FIFO():
	"""Simulates the optimistic resource management algorithm in FIFO manner"""
	def __init__(self, *args):
		self.arg = args
		self.name = 'FIFO'

	def run(self, tm):
		if tm.isAllTerminated():
			tm.printSummary()
			return

		blockedTasks = tm.getTaskByState('blocked')
		for task in blockedTasks:
			if DEBUG: print('Taking care of blocked tasks')
			act = task.getActivity()
			assert(act.name == 'request')
			if tm.canAlloc(act.resourceId, act.requested):
				tm.alloc(task, act.resourceId, act.requested)
				task.run()
			else:
				task.block(act)

		runningTasks = tm.getTaskByState('running')
		releaseQueue = []
		for task in runningTasks:
			if DEBUG: print('Taking care of running tasks')
			if task.isComputing():
				task.compute()
			else:
				act = task.getActivity()
				assert(act.name in 'request compute release terminate'.split())

				if act.name == 'request':
					if tm.canAlloc(act.resourceId, act.requested):
						tm.alloc(task, act.resourceId, act.requested)
						task.run()
					else:
						task.block(act)
				elif act.name == 'compute':
					task.compute(act.computeCycleLength)
				elif act.name == 'release':
					releaseQueue.append([task, act.resourceId, act.released]) #release at the end of cycle
					task.run()
				elif act.name == 'terminate':
					task.terminate()
		for args in releaseQueue:
			tm.release(*args)

		unstartedTasks = tm.getTaskByState('unstarted')
		for task in unstartedTasks:
			while task.nextActivity() == 'initiate':
				act = task.getActivity()
				assert(act.name == 'initiate')
				task.setClaim(act.resourceId, act.claim)
			task.run()

		while tm.isDeadlocked():
			sacrifice = tm.getTaskByState('blocked')[0]
			sacrifice.abort()
			tm.release(sacrifice)

		self.run(tm)



class Banker():
	"""Simulates the banker algorithm resource manager"""
	def __init__(self, *args):
		self.arg = args
		self.name = 'Banker\'s'

	def run(self, tm):
		pass
	
		