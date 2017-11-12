#!/usr/bin/python
# -*- coding: utf-8 -*- 
# @File Name: taskmanager.py
# @Created:   2017-11-08 22:01:56  seo (simon.seo@nyu.edu) 
# @Updated:   2017-11-12 03:57:58  Simon Seo (simon.seo@nyu.edu)
import os
import banker.algorithms as algorithms
from banker import DEBUG

class TaskManager(list):
	"""Holds all tasks and processes them with banker or fifo algorithms.
	Also keeps track of resources"""
	def __init__(self, algo):
		super(TaskManager, self).__init__()
		if algo == 'fifo':
			self.algo = algorithms.FIFO()
		elif algo == 'banker':
			self.algo = algorithms.Banker()
		self.R = 0 #number of resource types
		self.availRes = [] #resources that are currently available
		self.totalRes = [] #total amount of resource in the system

	def main(self):
		self.algo.run(self)

	def addTask(self, *specs):
		self.append(Task(*specs, self.R))

	def getTaskById(self, taskId):
		return self[taskId - 1]

	def getTaskByState(self, taskState):
		assert(taskState in 'unstarted running blocked terminated aborted'.split())
		result = []
		for task in self:
			if task.state == taskState:
				result.append(task)
		return result

	def addActivity(self, *specs):
		activity = Activity(*specs)
		self.getTaskById(activity.taskId).addActivity(activity)

	def isAllTerminated(self):
		numTerminated = len(self.getTaskByState('terminated'))
		numAborted = len(self.getTaskByState('aborted'))
		return False if numAborted + numTerminated < len(self) else True

	def res(self, resourceId, count=-1):
		'''get AND set function for available resources. 
		assumes passed count is non-negative'''
		assert(resourceId - 1 < len(self.availRes))
		if count >= 0:
			self.availRes[resourceId - 1] = count
		return self.availRes[resourceId - 1]

	def canAlloc(self, resourceId, count):
		assert(count > 0)
		return True if self.res(resourceId) - count >= 0 else False

	def alloc(self, task, resourceId, count):
		assert(task in self)
		tmResCount = self.res(resourceId)
		taskResCount = task.res(resourceId)
		self.res(resourceId, tmResCount - count)
		task.res(resourceId, taskResCount + count)
		if DEBUG: print('Allocated {} resource {} to task {} at cycle {}'.format(count, resourceId, task.id, task.currCycle))

	def release(self, task, resourceId=None, count=None):
		if resourceId is not None and count is not None:
			tmResCount = self.res(resourceId)
			taskResCount = task.res(resourceId)
			self.res(resourceId, tmResCount + count)
			task.res(resourceId, taskResCount - count)
			if DEBUG: print('Released {} resource {} from task {} at cycle {}'.format(count, resourceId, task.id, task.currCycle))
		else:
			[self.res(i, self.res(i) + task.res(i)) for i in range(1, 1+self.R)] #release all
			if DEBUG: print('Released all resources from task {} at cycle {}'.format(task.id, task.currCycle))

	def isDeadlocked(self):
		blockedTasks = self.getTaskByState('blocked')
		runningTasks = self.getTaskByState('running')
		if len(blockedTasks) == 0 or len(runningTasks) > 0:
			return False
		for task in blockedTasks:
			act = task.getActivity()
			assert(act.name == 'request')
			if self.canAlloc(act.resourceId, act.requested):
				return False
			else:
				task.block(act)
		if DEBUG: print('Deadlock found at cycle {}'.format(task.currCycle))
		return True

	def parseInput(self, filename):
		"""returns list of task specs"""
		if not os.path.isfile(filename):
			raise Exception('The input file does not exist. The input filename should be the last argument.')
		with open(filename, 'r') as f:
			tokens = []
			for l in f:
				tokens += [int(el) if el.isnumeric() else el for el in l.strip().split()]
		T = tokens.pop(0) #the number of tasks
		R = tokens.pop(0) #the number of resource types
		self.R = R
		units = tokens[:R] #units/number of each resource
		tokens = tokens[R:]

		[self.addTask(id) for id in range(1,T+1)]
		self.availRes = units
		self.totalRes = units

		while len(tokens) > 0:
			self.addActivity(*tokens[:4])
			tokens = tokens[4:]

	def printSummary(self):
		print(self.algo.name)
		totalCycle = 0
		totalWaiting = 0
		for task in self:
			print('Task {}: {}'.format(task.id, task.state if task.state == 'aborted' else \
				'{}   {}   {}%'.format(task.currCycle, task.waitingTime, round(task.waitingTime / task.currCycle * 100))))
			totalCycle += task.currCycle
			totalWaiting += task.waitingTime
		print('Total: {}   {}.  {}%'.format(totalCycle, totalWaiting, round(totalWaiting / totalCycle * 100)))

class Task():
	"""model for a task. holds information about state of task and activities it will process"""
	def __init__(self, *args):
		self.id = args[0] #task-number
		self.state = 'unstarted' #unstarted, running, blocked, terminated, aborted
		self.waitingTime = 0 #keeps track of how long task waited
		self.currCycle = 0 #keeps track of how long task ran
		self.compCycle = 0 #keeps track of how many computing cycles are left

		self.claims = [0] * args[-1] #list of claims that task has for each resource
		self.holds = [0] * args[-1] #list of resources that task currently holds
		self.activityList = [] #queue of commands/activities that task will execute

	def addActivity(self, activity):
		self.activityList.append(activity)

	def getActivity(self):
		'''returns the next activity in queue'''
		return self.activityList.pop(0)

	def nextActivity(self):
		assert(len(self.activityList) > 0)
		return self.activityList[0].name

	def _tick(self):
		self.currCycle += 1

	def _wait(self):
		self.waitingTime += 1
		self._tick()

	def run(self):
		self.state = 'running'
		self._tick()

	def block(self, activity=None):
		if activity is not None:
			self.activityList.insert(0, activity)
		self.state = 'blocked'
		self._wait()

	def terminate(self):
		self.state = 'terminated'

	def abort(self):
		if DEBUG: print('Aborting task #{} at cycle {}'.format(self.id, self.currCycle))
		self.state = 'aborted'

	def compute(self, computeCycleLength=None):
		if computeCycle is not None:
			self.compCycle = computeCycleLength
		self.compCycle -= 1
		self._tick()

	def isComputing(self):
		return self.compCycle > 0

	def getClaim(self, resourceId):
		return self.claims[resourceId - 1]

	def setClaim(self, resourceId, count):
		self.claims[resourceId - 1] = count

	def res(self, resourceId, count=-1):
		'''function that taskmanager will use to allocate resources'''
		if count >= 0:
			if self.res(resourceId) + count <= self.getClaim(resourceId):
				self.holds[resourceId - 1] = count
			else:
				if DEBUG: print('Cannot allocate {} of {} because the claim is {}'.format(count, resourceId, self.getClaim(resourceId)))
		return self.holds[resourceId - 1]

class Activity():
	"""represents the activities a task can process"""
	def __init__(self, *args):
		self.name = args[0] #initiate, request, compute, release, terminate
		if self.name == 'initiate':
			self.taskId, self.resourceId, self.claim = args[1:]
		elif self.name == 'request':
			self.taskId, self.resourceId, self.requested = args[1:]
		elif self.name == 'release':
			self.taskId, self.resourceId, self.released = args[1:]
		elif self.name == 'compute':
			self.taskId, self.computeCycleLength, _ = args[1:]
		elif self.name == 'terminate':
			self.taskId, _, __ = args[1:]




