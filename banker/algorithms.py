#!/usr/bin/python
# -*- coding: utf-8 -*- 
# @File Name: algorithms.py
# @Created:   2017-11-08 21:24:09  seo (simon.seo@nyu.edu) 
# @Updated:   2017-11-12 22:38:09  Simon Seo (simon.seo@nyu.edu)
from banker import DEBUG

class FIFO():
	"""Simulates the optimistic resource management algorithm in FIFO manner"""
	def __init__(self, *args):
		self.arg = args
		self.name = 'FIFO'

	def run(self, tm):
		# if all tasks are terminated, print summary and exit
		if tm.isAllTerminated():
			tm.printSummary()
			return

		# go through blocked tasks: allocate if rejected request is acceptable, else keep blocking
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

		# go through running tasks
		runningTasks = tm.getTaskByState('running')
		releaseQueue = []
		for task in runningTasks:
			if DEBUG: print('Taking care of running tasks')
			# skip if task is computing
			if task.isComputing():
				task.compute()
				continue
			act = task.getActivity()
			assert(act.name in 'request compute release terminate'.split())
			# if allocatable, alloc. if not, block.
			if act.name == 'request':
				if tm.canAlloc(act.resourceId, act.requested):
					tm.alloc(task, act.resourceId, act.requested)
					task.run()
				else:
					if DEBUG: print('Request for {} of resource {} cannot be granted at cycle {}'.format(act.requested, act.resourceId, task.currCycle))
					task.block(act)
			# enter compute state
			elif act.name == 'compute':
				task.compute(act.computeCycleLength)
			# queue tasks of which resources will be released later
			elif act.name == 'release':
				releaseQueue.append([task, act.resourceId, act.released]) #release at the end of cycle
				task.run()
			# enter terminated state
			elif act.name == 'terminate':
				task.terminate()
		for args in releaseQueue:
			tm.release(*args)

		# initiate and restart from block
		unstartedTasks = tm.getTaskByState('unstarted')
		for task in unstartedTasks:
			if task.nextActivity() == 'initiate':
				act = task.getActivity()
				assert(act.name == 'initiate')
				task.setClaim(act.resourceId, act.claim)
			task.run()
			if task.nextActivity() == 'initiate':
				task.unstart()

		# abort tasks until not deadlocked
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
			if tm.isSafe(task):
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
					# abort if hold + request > claim
					if task.getClaim(act.resourceId) < task.res(act.resourceId) + act.requested:
						print('During cycle {}-{} of Banker\'s algorithms\n\tTask {}\'s request exceeds its claim; aborted;'.format(task.currCycle, task.currCycle + 1, task.id))
						task.abort()
						tm.release(task)
					# allocate resources if safe
					elif tm.isSafe(task):
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
					print('Banker aborts task {} before run begins:\n\tclaim for resource {} ({}) exceeds number of units present ({})'.format(task.id, act.resourceId, act.claim, tm.res(act.resourceId)))
					task.abort()
					continue
			task.run()
			if task.nextActivity() == 'initiate':
				task.unstart()


		self.run(tm)
	
		