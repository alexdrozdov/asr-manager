#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pickle

class ExcNodeExists(Exception):
	def __init__(self, message):
		Exception.__init__(self, message)

class ExcWrongPersistance(Exception):
	def __init__(self, message):
		Exception.__init__(self, message)

class ExcPersistanceViolantion(Exception):
	def __init__(self, message):
		Exception.__init__(self, message)

class ExcInitializeFailure(Exception):
	def __init__(self, message):
		Exception.__init__(self, message)

class ExcNodeNotFound(Exception):
	def __init__(self, message):
		Exception.__init__(self, message)

class DbNodePersistance:
	persistent = 0  #Значение узла сохраняется при каждом изменении и доступно при каждом запуске программы
	writeonce  = 1  #Параметры узла могут быть заданы только один раз. Изменить значение узла невозможно, но можно создавать вложенные узлы 
	temporary  = 2  #Значение узла не сохраняется при перезапуске, может быть изменено или удалено

#Для pickle. Будет содержать только постоянные элементы узла
class DbNodeState(object):
	def __init__(self, dbnode):
		self.persistance = dbnode.persistance
		self.name = dbnode.name
		self.description = dbnode.description
		self.node_value = dbnode.node_value
		self.node_type = dbnode.node_type
		self.subnodes = {}
		for k in dbnode.subnodes.keys():
			if dbnode.subnodes[k].get_persistance() != DbNodePersistance.temporary:
				self.subnodes[k]=dbnode.subnodes[k]

class DbNode(object):
	def __init__(self, name, persistance = DbNodePersistance.temporary, description=None, node_value=None):
		self.persistance = persistance
		self.name = name
		self.description = description
		self.subnodes = {}
		self.node_value = node_value
		self.mounted_db = None
		if None == self.node_value:
			self.node_type = None
			return
		self.node_type = type(node_value)
	def __getstate__(self):
		return DbNodeState(self)
	def __setstate__(self, state):
		self.persistance = state.persistance
		self.name = state.name
		self.description = state.description
		self.node_value = state.node_value
		self.node_type = state.node_type
		self.subnodes = state.subnodes
		self.mounted_db = None
	def add_subnode(self, node):
		if self.subnodes.has_key(node.get_name()):
			raise ExcNodeExists(u"Узел "+node.get_name()+u" уже зарегистрирован в базе данных")
		self.subnodes[node.get_name()] = node
	def subnode_exists(self, name):
		return self.subnodes.has_key(name)
	def insert_subnode(self, path, node):
		if None == self.mounted_db:
			if self.persistance==DbNodePersistance.temporary and node.persistance!=DbNodePersistance.temporary:
				raise ExcWrongPersistance(u"Постоянный узел "+node.get_name()+ u" не может быть встроен во временный")
			root_name = path[0]
			if len(path)==1:
				#Новый узел должен стать дочерним по отношению к этому узлу
				if not self.subnode_exists(node.get_name()):
					self.add_subnode(node) #Узел еще не существует - добавляем его
				else:
					self.subnodes[node.get_name()].update_from_node(node) #Узел уже существует, обновляем его значение
				return
			#Узел расположен где-то дальше
			if not self.subnode_exists(root_name):
				self.subnodes[root_name] = DbNode(root_name, persistance=node.persistance)
			self.subnodes[root_name].insert_subnode(path[1:], node)
		else:
			#На это узел смонтирована другая база данных, передаем ей эстафету на вставку узла
			mounted_node = self.mounted_db.root_node
			while mounted_node!=None and mounted_node.mounted_db!=None:
				mounted_node = mounted_node.mounted_db.root_node
			if None == mounted_node:
				raise ExcNodeNotFound(u"Невозможно обновить значение узла в смонтированной базе данных т.к. не инициализирован ее корневой элемент")
			mounted_node.insert_subnode(path, node)
	def update_from_node(self, node):
		if None == self.mounted_db:
			#Собственный узел базы данных. Просто обновляем его состояние если это допустимо
			if self.persistance == DbNodePersistance.writeonce:
				if self.node_value==node.node_value and self.persistance==node.persistance and self.node_type==node.node_type:
					return #Пытались обновить значение неизменяемого узла, при этом сами значения не изменлись. Все в порядке
				raise ExcPersistanceViolantion(u"Попытка изменить однократно перезаписываемый узел "+self.get_name())
			self.persistance = node.persistance
			self.node_value = node.node_value
			if None == self.node_value:
				self.node_type = None
				return
			self.node_type = type(node.node_value)
		else:
			#На этот узел смонтирована другая база данных. Ищем последнюю смонтированную базу данных и вызываем соответсвующий метод ее корневого узла
			mounted_node = self.mounted_db.root_node
			while mounted_node!=None and mounted_node.mounted_db!=None:
				mounted_node = mounted_node.mounted_db.root_node
			if None == mounted_node:
				raise ExcNodeNotFound(u"Невозможно обновить значение узла в смонтированной базе данных т.к. не инициализирован ее корневой элемент")
			mounted_node.update_from_node(node)

	def get_name(self):
		return self.name
	def mount_db(self, db):
		if None == mounted_db:
			self.mounted_db = db
		else:
			self.mounted_db.root_node.mount_db(db) #Если в этот узел уже что-то примонтировано, то надо монтировать поверх его корневого узла
	def get_node(self, path):
		if isinstance(path, str):
			path = [path]
		if None != self.mounted_db:
			mounted_node = self.mounted_db.root_node
			while mounted_node!=None and mounted_node.mounted_db!=None:
				mounted_node = mounted_node.mounted_db.root_node
			if None == mounted_node:
				raise ExcNodeNotFound(u"Невозможно обновить значение узла в смонтированной базе данных т.к. не инициализирован ее корневой элемент")
			if len(path)==1:
				return mounted_node
			return mounted_node.get_node(path[1:])
		root_name = path[0]
		if not self.subnodes.has_key(root_name):
			raise ExcNodeNotFound(root_name)
		if len(path)==1:
			return self.subnodes[root_name]
		try:
			node = self.subnodes[root_name].get_node(path[1:])
		except ExcNodeNotFound as e:
			raise ExcNodeNotFound(self.get_name()+"/"+e.msg)
		return node
	def get_value(self):
		return self.node_value
	def get_type(self):
		return self.node_type
	def get_persistance(self):
		return self.persistance
	def list_subnodes(self):
		return self.subnodes.keys()

class LocalDb:
	def __init__(self, filename, default_values_callback=None):
		self.filename = filename
		self.root_node = None
		try:
			with open(filename, "r") as f:
				self.root_node = pickle.load(f)
		except:
			if None == default_values_callback:
				raise ExcInitializeFailure(u"Не удалось загрузить базу данных из файла, нет функции для построения структуры по-умолчанию")
			default_values_callback(self)
	def write_value(self, path, value, persistance=DbNodePersistance.temporary, description=None):
		separated_path=path.split('/')
		separated_path.remove('')
		if len(separated_path) < 1:
			return
		root_node_name=separated_path[0]
		if None==self.root_node and len(separated_path)==1:
			self.root_node = DbNode(root_node_name, persistance=persistance, node_value=value, description=description)
		elif None==self.root_node:
			self.root_node=DbNode(root_node_name, persistance=DbNodePersistance.writeonce)
			node = DbNode(separated_path[-1], persistance=persistance, node_value=value, description=description)
			self.root_node.insert_subnode(separated_path[1:], node)
		else:
			node = DbNode(separated_path[-1], persistance=persistance, node_value=value, description=description)
			self.root_node.insert_subnode(separated_path[1:], node)
		if persistance == DbNodePersistance.temporary:
			return # Временное значение, ничего не надо сохранять
		self.store()

	def store(self):
		with open(self.filename, "w") as f:
			pickle.dump(self.root_node, f)
	def write_temporary(self, path, value, description=None):
		self.write_value(path, value, DbNodePersistance.temporary, description)
	def write_persistent(self, path, value, description=None):
		self.write_value(path, value, DbNodePersistance.persistent, description)
	def write_once(self, path, value, description=None):
		self.write_value(path, value, DbNodePersistance.writeonce, description)

	def get_node(self, path):
		if None == self.root_node:
			raise ExcNodeNotFound(u"В базе данных отсутствует корневой элемент")
		if isinstance(path, str):
			separated_path=path.split('/')
			separated_path.remove('')
		else:
			separated_path = path
		if len(separated_path) < 1:
			return None
		if separated_path[0] != self.root_node.get_name():
			raise ExcNodeNotFound(u"Узел /"+separated_path[0]+u"не найден")
		if len(separated_path)==1:
			node = self.root_node
		else:
			try:
				node = self.root_node.get_node(separated_path[1:])
			except ExcNodeNotFound as e:
				raise ExcNodeNotFound(u"Узел /"+e.msg+u"не найден")
		return node
	def read_value(self, path):
		return self.get_node(path).get_value()
	def read_persistance(self, path):
		return self.get_node(path).get_persistance()
	def read_type(self, path):
		return self.get_node(path).get_type()
	def list_subnodes(self, path):
		node = self.get_node(path)
		return node.subnodes.keys()

def init_localdb(filename, default_values_callback=None):
	global db
	db = LocalDb(filename, default_values_callback)

#def def_params(localdb):
#	localdb.write_value("/db/temporary/t1", 1, DbNodePersistance.persistent)
#	localdb.write_value("/db/temporary/t2", 2, DbNodePersistance.temporary)

#db = LocalDb("db.pickle", def_params)
#db.write_persistent("/db/temporary/t1", 5)
#db.write_value("/db/temporary/t2", 3, DbNodePersistance.temporary)

#print "/db/temporary/t1=", db.read_value("/db/temporary/t1")
#print "/db/temporary/t2=", db.read_value("/db/temporary/t2")
#print "/db/temporary=", db.read_value("/db/temporary")

