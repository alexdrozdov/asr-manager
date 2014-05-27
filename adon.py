#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os
import pickle
import traceback

class AdonsManager:
	def __init__(self, manager, gui):
		self.man = manager
		self.gui = gui
		self.tree = None
		self.disabled_adons = []
		self.load_disabled_adons()
		self.scan_adons()
		self.objects = []

	def load_disabled_adons(self):
		try:
			with open(os.path.dirname(__file__) + "/disabled-adons.txt", 'r') as f:
				self.disabled_adons = pickle.load(f)
		except:
			pass

	def store_disabled_adons(self):
		try:
			self.disabled_adons = self.tree.get_disabled_adons()
			with open(os.path.dirname(__file__) + "/disabled-adons.txt", 'w') as f:
				pickle.dump(self.disabled_adons, f)
		except:
			print traceback.format_exc()

	def adon_disabled(self, adon_path):
		for p in self.disabled_adons:
			if cmp(p, adon_path)==0:
				return True
		return False

	def scan_adons(self):
		try:
		    self.ad = __import__("adons", globals(), locals(), "*")
		    self.tree = self.ad.adons_init(self.adon_disabled)
		except:
			print "Фатальный бой при загрузке каталога подключаемых модулей."
			print "Использование модулей невозможно из-за нарушения структуры каталога. Устраните причину и перезапустите программу"
			print "Возможно, приведенная ниже информация может помочь в решении проблемы"
			print traceback.format_exc()

	def load_adons(self, tree = None):
	    if None == tree:
	    	tree = self.tree
	    if None == tree:
	    	print "Модули не были инициализированы"
	    	return
	    if tree.init_fcn != None:
	    	print "Loading ", tree.name
	    	try:
	        	tree.init_fcn(self.man, self.gui)
	    	except:
	        	tree.load_error = True
	        	print "Loading failed!"
	        	print traceback.format_exc()
	    for m in tree.submodules:
	        self.load_adons(m)

	def reload(self):
		self.tree.reload(self.man, self.gui)

	def print_adons(self):
		if None != self.tree:
			self.tree.print_modules()
        

