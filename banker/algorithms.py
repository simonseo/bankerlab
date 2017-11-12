#!/usr/bin/python
# -*- coding: utf-8 -*- 
# @File Name: algorithms.py
# @Created:   2017-11-08 21:24:09  seo (simon.seo@nyu.edu) 
# @Updated:   2017-11-12 07:01:48  Simon Seo (simon.seo@nyu.edu)
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
		blockedTasks.sort(key=lambda task: task.blockedCycle)
		for task in blockedTasks:
			if DEBUG: print('Taking care of blocked task {}'.format(task.id))
			act = task.getActivity()
			assert(act.name == 'request'), 'blocked task\'s next act is {}'.format(act.name)
			if tm.canAlloc(act.resourceId, act.requested):
				tm.alloc(task, act.resourceId, act.requested)
				task.unstart()
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
						if DEBUG: print('Request for {} of resource {} cannot be granted at cycle {}'.format(act.requested, act.resourceId, task.currCycle))
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
			if task.nextActivity() == 'initiate':
				act = task.getActivity()
				assert(act.name == 'initiate')
				task.setClaim(act.resourceId, act.claim)
			task.run()
			if task.nextActivity() == 'initiate':
				task.unstart()

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
		if tm.isAllTerminated():
			tm.printSummary()
			return

		blockedTasks = tm.getTaskByState('blocked')
		blockedTasks.sort(key=lambda task: task.blockedCycle)
		for task in blockedTasks:
			if DEBUG: print('Taking care of blocked task {}'.format(task.id))
			act = task.getActivity()
			assert(act.name == 'request'), 'blocked task\'s next act is {}'.format(act.name)
			if tm.canAlloc(act.resourceId, act.requested):
				tm.alloc(task, act.resourceId, act.requested)
				task.unstart()
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
					# abort if request more than claim
					if task.getClaim(act.resourceId) < task.res(act.resourceId) + act.requested:
						task.abort()
						tm.release(task)
					# allocate resources if safe
					elif tm.isSafe(task, act.resourceId, act.requested):
						tm.alloc(task, act.resourceId, act.requested)
						task.run()
					# block if unsafe
					else:
						if DEBUG: print('Request for {} of resource {} cannot be granted at cycle {}'.format(act.requested, act.resourceId, task.currCycle))
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

		unstartedTasks = tm.getTaskByState('unstarted') #all uninitiated or unblocked tasks
		for task in unstartedTasks:
			if task.nextActivity() == 'initiate':
				act = task.getActivity()
				assert(act.name == 'initiate')
				if tm.canAlloc(act.resourceId, act.claim):
					task.setClaim(act.resourceId, act.claim)
				else:
					task.abort()
					continue
			task.run()
			if task.nextActivity() == 'initiate':
				task.unstart()


		self.run(tm)
	
		