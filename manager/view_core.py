#!/usr/bin/env python
# -*- coding: utf-8 -*-

import localdb
import re

class PlotterWrapper(object):
    def __init__(self, path):
        self.path = path
        self.class_name = localdb.db.read_value(self.path + "/class")
        self.name = localdb.db.read_value(self.path + "/name")
        self.caption = localdb.db.read_value(self.path + "/caption")
        self.is_locked = False
        self.inst = None
    def lock(self):
        self.is_locked = True
    def locked(self):
        return self.is_locked
    def get_plotter_name(self):
        return self.name
    def get_plotter_instance(self):
        if None == self.inst:
            self.inst = self.class_name()
        return self.inst

class ViewerWrapper(object):
    def __init__(self, path):
        self.path = path
        self.class_name = localdb.db.read_value(self.path + "/class")
        self.id = localdb.db.read_value(self.path + "/id")
        self.caption = localdb.db.read_value(self.path + "/caption")
        self.tags = localdb.db.read_value(self.path + "/tags")
        self.plotter_name = localdb.db.read_value(self.path + "/plotter/name")
        self.multiplexable = localdb.db.read_value(self.path + "/plotter/multiplexable")
        self.inst = None

    def check_view_capability(self, ticket):
        """Функция проверки возможности отображения тикета. Вызывается классом
        ViewManager перед тем, как сопоставить тикет с этим классом отображения
        Вернуть True, если класс может отобразить такой тикет, вернуть False,
        если отображение такого тикета невозможно"""
        print "Метод проверки не реализован. По-умолчанию считаем, что отображать этот тикеть невозможно"
        return True
    def view(self, kwargs):
        pass
    def supported_tags(self):
        return self.tags
    def get_viewer_id_name(self):
        return self.id
    def get_viewer_caption(self):
        return self.caption
    def get_plotter_name(self):
        return self.plotter_name
    def get_plotter_wrapper(self):
        return PlotterWrapper("/db/temporary/plotters/" + self.plotter_name)
    def create_viewer_instance(self):
        return self.class_name()
    def is_multiplexable(self):
        return self.multiplexable


class ViewManager:
    def __init__(self):
        self.viewers_by_id = {}
    
    def register_viewer(self, inst, id_name, caption, default_tags=None, default_data_ids=None):
        self.viewers_by_id[id_name] = inst
    def get_ticket_capability_list(self, ticket):
        tag = ticket.get_data_tag()
        capability_list = []
        viewer_nodes = localdb.db.list_subnodes("/db/temporary/viewers")
        for vn in viewer_nodes:
            viewer_path = "/db/temporary/viewers/" + vn
            viewer_tags = localdb.db.read_value(viewer_path + "/tags")
            if tag in viewer_tags:
                v = ViewerWrapper(viewer_path)
                capability_list.append(v)
            else: #Точное название тэга не совпало, но, возможно, совпадет как регулярное выражение
                for vt in viewer_tags:
                    rex = re.compile(vt)
                    if None!=rex.match(tag):
                        v = ViewerWrapper(viewer_path)
                        capability_list.append(v)
                        break
        return capability_list
    def get_data_capability_list(self, data):
        pass
        
    def get_viewer_by_id(self, viewer_id):
        return self.viewers_by_id[viewer_id]

def YesNo(parent, question, caption = 'Yes or no?'):
    dlg = wx.MessageDialog(parent, question, caption, wx.YES_NO | wx.ICON_QUESTION)
    result = dlg.ShowModal() == wx.ID_YES
    dlg.Destroy()
    return result
    
class ResultsToView:
    def __init__(self, view_manager):
        self.view_manager = view_manager
        self.view_list = []
    def add_ticket(self, ticket, viewer_id=None):
        if None == viewer_id:
            viewers_list = self.view_manager.get_ticket_capability_list(ticket)
            if len(viewers_list) < 1:
                wx.MessageBox(u"Не удалось найти модуль для отображения, выберите модуль отображения из списка принудительно", u"Не модуля отображения", wx.OK)
                return
            v = viewers_list[0]
        else:
            v = self.view_manager.get_viewer_by_id(viewer_id)
            if not v.check_view_capability(ticket):
                wx.MessageBox(u"Выбранное средство просмотра не поддерживает тикеты такого типа", u"Отображение невозможно", wx.OK)
                return
        #Проверяем, что это билет не зарегистрирован на другой просмотровщик
        for itm in self.view_list:
            if itm[0]!=ticket:
                continue
            if itm[1]==v:
                return; #Этот тикет уже добавлен в список для отображения при помощи выбранного просмотровщика. И так все хорошо.
            if not YesNo(None, u"Этот тикет уже отображается другим просмотровщиком. Добавить тикет для отображения еще раз?", u"Смена просмотровщика"):
                return
        self.view_list.append([ticket, v])
    def update_ticket_viewer(self, ticket, viewer):
        for i in range(len(self.view_list)):
            if self.view_list[i][0]==ticket:
                self.view_list[i][1] = viewer
                break
    def remove_ticket(self, ticket):
        for itm in self.view_list:
            if ticket==itm[0]:
                self.view_list.remove(itm)
                break

    def store_for_view(self):
        pass
    def view(self):
        pass
    def move_up(self, index):
        if index < 1:
            return
        tmp = self.view_list[index-1]
        self.view_list[index-1] = self.view_list[index]
        self.view_list[index] = tmp
    def move_down(self, index):
        if index > len(self.view_list)-1:
            return
        tmp = self.view_list[index+1]
        self.view_list[index+1] = self.view_list[index]
        self.view_list[index] = tmp
        
    def update_view_widget(self, widget):
        widget.Clear()
        for itm in self.view_list:
            widget.Append(itm[0].description + " " + itm[0].get_data_name() + " " + itm[0].get_data_tag(), itm)
    def get_view_list(self):
        return self.view_list
    
    def show_results(self):
        #Создаем список плоттеров и направляем в них данные для отображения
        plotter_wrappers = []
        for itm in self.get_view_list():
            ticket = itm[0]
            viewer = itm[1]
            plotter_name = viewer.get_plotter_name()
            viewer_inst = viewer.create_viewer_instance()
            if not viewer.is_multiplexable():
                #Этот модуль отображения не может быть скомбинирован с другими модулями.
                #Просто создаем этот модуль отображения и его плоттер
                plotter = viewer.get_plotter_wrapper()
                plotter_inst = plotter.get_plotter_instance()
                viewer_inst.generate(ticket, plotter_inst)
                plotter.lock()
                plotter_wrappers.append(plotter)
            else:
                #Модуль может разделять плоттер совместно с другими модулями. Ищем первый плоттер с требуемым именем
                plotter = None
                for pw in plotter_wrappers:
                    print pw.get_plotter_name(), pw.locked()
                    if not pw.locked() and pw.get_plotter_name()==plotter_name:
                        plotter = pw
                        break
                if None == plotter:
                    plotter = viewer.get_plotter_wrapper()
                    plotter_inst = plotter.get_plotter_instance()
                    plotter_wrappers.append(plotter)
                viewer_inst.generate(ticket, plotter_inst)
        #Теперь отображаем все то, что было отправлено в плоттеры 
        for p in plotter_wrappers:
            p.get_plotter_instance().plot()
