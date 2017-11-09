#!/usr/bin/python
# -*- coding: utf-8 -*- 
# @File Name: banker.py
# @Created:   2017-11-08 21:24:09  seo (simon.seo@nyu.edu) 
# @Updated:   2017-11-08 21:25:19  Simon Seo (simon.seo@nyu.edu)

class Banker():
	"""Simulates the Banker algorithm resource manager"""
	def __init__(self, arg):
		self.arg = arg
		