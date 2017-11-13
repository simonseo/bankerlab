#!/usr/bin/python
# -*- coding: utf-8 -*- 
# @File Name: taskmanager.py
# @Created:   2017-11-08 22:01:56  seo (simon.seo@nyu.edu) 
# @Updated:   2017-11-12 21:59:56  Simon Seo (simon.seo@nyu.edu)
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
		'''create new task with given specifications and add to task manager'''
		self.append(Task(*specs, self.R))

	def getTaskById(self, taskId):
		'''return the task with given id'''
		return self[taskId - 1]

	def getTaskByState(self, taskState):
		'''returns all tasks that are in the specified state'''
		assert(taskState in 'unstarted running blocked terminated aborted'.split())
		result = []
		for task in self:
			if task.state == taskState:
				result.append(task)
		return result

	def addActivity(self, *specs):
		'''add activity commands to each task class'''
		activity = Activity(*specs)
		self.getTaskById(activity.taskId).addActivity(activity)

	def isAllTerminated(self):
		'''checks if every task has terminated'''
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
		'''check if resource manager is able to provide specified resource'''
		assert(count > 0)
		return True if self.res(resourceId) - count >= 0 else False

	def alloc(self, task, resourceId, count):
		'''allocates resource from the resource manager to specified task'''
		assert(task in self)
		tmResCount = self.res(resourceId)
		taskResCount = task.res(resourceId)
		self.res(resourceId, tmResCount - count)
		task.res(resourceId, taskResCount + count)
		if DEBUG: print('Allocated {} resource {} to task {} at cycle {}'.format(count, resourceId, task.id, task.currCycle))

	def release(self, task, resourceId=None, count=None):
		'''releases a specified resource from a task or all resources of a task'''
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
		'''checks if state is in deadlock: all unfinished tasks are blocked and no requests can be satisfied'''
		if DEBUG: print('Looking for deadlock')
		blockedTasks = self.getTaskByState('blocked')
		runningTasks = self.getTaskByState('running')
		if len(blockedTasks) == 0 or len(runningTasks) > 0:
			return False
		for task in blockedTasks:
			act = task.getActivity()
			assert(act.name == 'request')
			task.block(act, deadlockChecking=True)
			if self.canAlloc(act.resourceId, act.requested):
				return False
			else:
				pass
		if DEBUG: print('Deadlock found at cycle {}'.format(task.currCycle))
		return True

	def isSafe(self, task):
		'''checks if resource state is safe: no potential requests (claim - hold)
		 are greater than current resource'''
		for i in range(1, self.R+1):
			if task.getClaim(i) - task.res(i) > self.res(i):
				return False
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
			if task.state == 'aborted':
				print('Task {}: {}'.format(task.id, task.state))
			else:
				print('Task {}: {}   {}   {}%'.format(task.id, task.currCycle, task.waitingTime, round(task.waitingTime / task.currCycle * 100)))
				totalCycle += task.currCycle
				totalWaiting += task.waitingTime
		print('Total: {}   {}   {}%'.format(totalCycle, totalWaiting, round(totalWaiting / totalCycle * 100)))

class Task():
	"""model for a task. holds information about state of task and activities it will process"""
	def __init__(self, *args):
		self.id = args[0] #task-number
		self.state = 'unstarted' #unstarted, running, blocked, terminated, aborted
		self.waitingTime = 0 #keeps track of how long task waited
		self.currCycle = 0 #keeps track of how long task ran
		self.compCycle = 0 #keeps track of how many computing cycles are left
		self.blockedCycle = -1 #when was the task blocked

		self.claims = [0] * args[-1] #list of claims that task has for each resource
		self.holds = [0] * args[-1] #list of resources that task currently holds
		self.activityList = [] #queue of commands/activities that task will execute

	def addActivity(self, activity):
		'''add activity commands to each task class'''
		self.activityList.append(activity)

	def getActivity(self):
		'''pops and returns the next activity in queue'''
		act = self.activityList.pop(0)
		if DEBUG: print('popping activity {}: {}'.format(act.name, [el.name for el in self.activityList]))
		return act

	def nextActivity(self):
		'''returns the name of the next activity'''
		assert(len(self.activityList) > 0)
		return self.activityList[0].name

	def _tick(self):
		'''count up total time'''
		if DEBUG: print('ticking for task {}'.format(self.id))
		self.currCycle += 1

	def _wait(self):
		'''count up waiting time and total time'''
		if DEBUG: print('task {} is waiting'.format(self.id))
		self.waitingTime += 1
		self._tick()

	def run(self):
		'''set task to running state and count up'''
		self.state = 'running'
		self.blockedCycle = -1
		self._tick()

	def unstart(self):
		'''set task to unstarted state'''
		self.state = 'unstarted'

	def block(self, activity=None, deadlockChecking=False):
		'''changes state to blocked and puts rejected request back into the queue'''
		if activity is not None:
			self.activityList.insert(0, activity)
			if DEBUG: print('reinserting activity {}: {}'.format(activity.name, [el.name for el in self.activityList]))
		if not deadlockChecking:
			self.state = 'blocked'
			if self.blockedCycle < 0:
				self.blockedCycle = self.currCycle
			self._wait()

	def terminate(self):
		'''sets task state to terminated'''
		self.state = 'terminated'

	def abort(self):
		'''sets task state to aborted'''
		if DEBUG: print('Aborting task #{} at cycle {}'.format(self.id, self.currCycle))
		self.state = 'aborted'

	def compute(self, computeCycleLength=None):
		'''count down compute time and count up total time'''
		if computeCycleLength is not None:
			self.compCycle = computeCycleLength
		self.compCycle -= 1
		self._tick()

	def isComputing(self):
		return self.compCycle > 0

	def getClaim(self, resourceId):
		'''returns the claim of a task for given resource'''
		return self.claims[resourceId - 1]

	def setClaim(self, resourceId, count):
		'''set claim of task for given resource'''
		self.claims[resourceId - 1] = count

	def res(self, resourceId, count=-1):
		'''get AND set function for resources that a task holds'''
		if count >= 0:
			if count <= self.getClaim(resourceId):
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




