#!/usr/bin/python
# -*- #coding: utf8 -*-

import copy
import traceback
import thread
import time

class NoId(ValueError):
    pass

class DataIdInfo:
    def __init__(self, iden, name, description = None, tag = None):
        self.iden = iden
        self.name = name
        if not description:
            description = "description not defined"
        self.description = description
        if not tag:
            tag = "uncategorised"
        self.tag = tag
        self.id_track = None
    def add_id_track(self, id_track):
        self.id_track = id_track


class DataIdStorage:
    def __init__(self):
        self._ids = {}
        self._last_data_id = 0
        
    def add_data_id(self, name, description, tag = None, iden = None):
        if None == tag:
            tag = "undefined"
        if self._ids.has_key(name):
            original_id = self._ids[name].iden
            data_info = DataIdInfo(original_id, name, description, tag) 
            self._ids[name] = data_info
            return
        if  None == iden:
            self._last_data_id += 1
            new_id = self._last_data_id
        else:
            new_id = iden
        data_info = DataIdInfo(new_id, name, description, tag) 
        self._ids[name] = data_info

    def get_tag_by_id(self, data_id):
        for di in self._ids.values():
            if data_id == di.iden:
                return di.tag
        return "undefined"

    def get_name_by_id(self, data_id):
        for di in self._ids.values():
            if data_id == di.iden:
                return di.name
        return "undefined"
    
    def get_id_name(self, data_id):
        return self.get_name_by_id(data_id)
            
    def get_data_id(self, name):
        if self._ids.has_key(name):
            return self._ids[name].iden
        else:
            self._last_data_id += 1
            new_id = self._last_data_id
            data_info = DataIdInfo(new_id, name, "default description", "undefined") 
            self._ids[name] = data_info
            return self._ids[name].iden
    def list_tags(self):
        tags = []
        for dii in self._ids.values():
            tags.append(dii.tag)
        return list(set(tags))
    
    def list_names(self):
        return self._ids.keys()
    
    def get_by_tag(self, tag):
        ids = []
        for dii in self._ids.values():
            if dii.tag == tag:
                ids.append(dii)
        return ids
    
    def get_id_info(self, data_id):
        for di in self._ids.values():
            if di.iden == data_id:
                return di
        raise NoId()

class TicketIdStore:
    def __init__(self):
        self.last_id = 0
    def get_id(self):
        id = self.last_id
        self.last_id += 1
        return id

global_ticket_id_store = TicketIdStore()

class Ticket(object):
    def __init__(self, manager, data_id, data, parent_ticket = None, id=None, description = None):
        self.man = manager
        self.data_id = self.man.get_data_id(data_id)
        self.parent_ticket = parent_ticket
        self.children = []
        self.tis = TicketIdStore()
        if None==id:
            self.id = global_ticket_id_store.get_id()
        else:
            self.id = id
        if None == self.parent_ticket:
            self.id_track = []
        else:
            self.id_track = copy.deepcopy(self.parent_ticket.id_track)
            self.parent_ticket.children.append(self)
        self.id_track.append(self.id)
        self.data = data
        self.description = description
    def create_ticket(self, data_id, data, id = None, description = None):
        if None==description:
            description = self.description
        if None==id:
            id = self.tis.get_id()
        t = Ticket(self.man, data_id, data, self, id, description)
        return t
    def get_data(self):
        return self.data
    def get_full_id(self):
        return str(self.id_track)
    def get_root_id(self):
        return self.id_track[0]
    def get_id_track(self):
        return copy.deepcopy(self.id_track)
    def get_data_id(self):
        return self.data_id
    def get_data_name(self):
        return self.man.dis.get_id_name(self.data_id)
    def get_data_tag(self):
        return self.man.dis.get_id_info(self.data_id).tag
    def export_standalone_ticket(self):
        st = StanaloneTicket(self)
        return st
    def get_parent(self):
        return self.parent_ticket
    def find_parent_by_data_id(self, data_id):
        data_id = self.man.get_data_id(data_id)
        p = self.parent_ticket
        while None != p:
            if p.data_id == data_id:
                return p
            p = p.parent_ticket
        return None

class StanaloneTicket(Ticket):
    def __init__(self, ticket):
        self.man = None
        self.data_id = ticket.data_id
        self.parent_ticket = None
        self.tis = None
        self.id = ticket.id
        self.id_track = copy.deepcopy(ticket.id_track)
        self.data = copy.deepcopy(ticket.data)
        self.description = copy.deepcopy(ticket.description)
        self.data_name = ticket.get_data_name()
        self.data_tag = ticket.get_data_tag()
    def create_ticket(self, data_id, data, id = None, description = None):
        raise u"StanaloneTicket не поддерживает создание других тикетов"
    def get_data(self):
        return self.data
    def get_full_id(self):
        return str(self.id_track)
    def get_root_id(self):
        return self.id_track[0]
    def get_id_track(self):
        return copy.deepcopy(self.id_track)
    def get_data_id(self):
        return self.data_id
    def get_data_name(self):
        return self.data_name
    def get_data_tag(self):
        return self.data_tag

class QueueTask:
    def __init__(self, data_id, data):
        self.data_id = data_id
        self.data = data


class Manager:
    def __init__(self):
        self.handlers = {}
        self.queue = []
        self.dump = []
        self.promiscuous_handlers = []
        self.dis = DataIdStorage()
        self.lock = thread.allocate_lock()
        self.daemons = []
        self.curr_takt = 0
        self.request_trimts = {}
        
    def register_daemon(self, callback):
        self.daemons.append(callback)
    
    def start_async_operation(self):
        self.man_thread = thread.start_new_thread(self._start_oper_cycle, ())

    def register_handler(self, data_id, callback):
        if None == data_id:
            #Передан обработчик сообщений любого типа. Проходим по всем зарегистрированным типам данных и добавляем к ним этот обработчик
            self.promiscuous_handlers.append(callback)
            for v in self.handlers.values():
                v.append(callback)
            return
        if not isinstance(data_id, int):
            data_id = self.dis.get_data_id(data_id)
        if self.handlers.has_key(data_id):
            self.handlers[data_id].append(callback)
        else:
            self.handlers[data_id] = [callback]
            #Все обработчики сообщений любого типа должны подписаться на этот тип данных
            for h in self.promiscuous_handlers:
                self.handlers[data_id].append(h)

    def remove_module_handlers(self, search_mask):
        for k in self.handlers.keys():
            handlers = self.handlers[k]
            new_handlers = []
            for h in handlers:
                cls = str(h.im_class)
                if search_mask in cls:
                    print "Removing", cls, h.func_name, "handler"
                    continue
                new_handlers.append(h)
            self.handlers[k] = new_handlers

        
    def push_data(self, data_id, data):
        if not isinstance(data_id, int):
            data_id = self.dis.get_data_id(data_id)
        qt = QueueTask(data_id, data)
        self.lock.acquire()
        self.queue.append(qt)
        self.lock.release()

    def add_data_id(self, name, description, tag = None, iden = None):
        self.dis.add_data_id(name, description, tag, iden)
        data_id = self.dis.get_data_id(name)
        if not self.handlers.has_key(data_id):
            self.handlers[data_id] = []
            for h in self.promiscuous_handlers:
                self.handlers[data_id].append(h)

    def get_data_id(self, data_id_or_name):
        if not isinstance(data_id_or_name, int):
            return self.dis.get_data_id(data_id_or_name)
        return data_id_or_name

    def push_ticket(self, ticket):
        data_id = self.get_data_id(ticket.data_id)
        qt = QueueTask(data_id, ticket)        
        self.lock.acquire()
        self.queue.append(qt)
        self.lock.release()

    def ticket(self, data_id, data, description = None):
        t = Ticket(self, data_id, data, description = description)
        return t

    def handle_once(self):
        if len(self.queue) > 0:
            self.lock.acquire();
            qt = self.queue[0]
            self.queue.pop(0)
            self.lock.release()
            if self.handlers.has_key(qt.data_id):
                for i in range(len(self.handlers[qt.data_id])):
                    try:
                        self.handlers[qt.data_id][i](qt.data)
                    except:
                        print "Exception while executing adon"
                        print traceback.format_exc()

    def print_handlers(self):
        for k in self.handlers.keys():
            ii = self.dis.get_id_info(k)
            info = u'Обработчики для name='+str(ii.name)+'; id='+str(ii.iden)+'; tag='+str(ii.tag)
            print info
            handlers = self.handlers[k]
            for h in handlers:
                try:
                    print "    "+str(h.im_class)+"."+str(h.func_name)
                except:
                    print "Unable to determine handler class for", h

    def has_tasks(self):
        return len(self.queue) > 0
    
    def pause(self):
        self.lock.acquire()
    
    def resume(self):
        self.lock.release()
    
    def _start_oper_cycle(self):
        while True:
            while self.has_tasks():
                try:
                    self.handle_once()
                except:
                    print "Exception while executing adon"
                    print traceback.format_exc()
            for daemon in self.daemons:
                try:
                    daemon()
                except:
                    print "Exception while executing daemon"
                    print traceback.format_exc()
            time.sleep(0.2)

    def reset(self):
        self.handlers = {}
        self.queue = []
        self.dump = []
        self.dis = DataIdStorage()
        self.promiscuous_handlers = []

manager = Manager()

