#!/usr/bin/python
# -*- coding: utf-8 -*- 
# @File Name: fifo.py
# @Created:   2017-11-08 21:24:16  seo (simon.seo@nyu.edu) 
# @Updated:   2017-11-08 21:25:08  Simon Seo (simon.seo@nyu.edu)

class Banker():
	"""Simulates the optimistic resource management algorithm in FIFO manner"""
	def __init__(self, arg):
		self.arg = arg
		