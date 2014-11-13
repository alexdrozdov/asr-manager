#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import wx, loader_interface
import wx.grid 
import manager as ms
import test_adons_tree as at
import adon
import adon_window
import time

class FrameInfo:
    def __init__(self, frame, description, iden_wind):
        self.frame = frame
        self.description = description
        self.iden = iden_wind


class GuiInfo:
    def __init__(self):
        self.frames = []
    def register_window(self, frame, description, iden_wind):
        for f in self.frames:
            if f.iden==iden_wind:
                f.frame = frame
                f.description = description
                return
        self.frames.append(FrameInfo(frame, description, iden_wind))
    def show_wnd_by_iden(self, iden_wind):
        for i in range(len(self.frames)):
            try:
                if self.frames[i].iden == iden_wind:
                    self.frames[i].frame.Show()
                    return
            except:
                break
        wx.MessageBox(u"Модуль с иден-ром " + iden_wind + u" не найден. Проверьте дерево загруженных модулей", u"Ошибка", wx.OK)

class Frame(loader_interface.LoaderFrame, adon_window.AdonWindow):
    def __init__(self):
        loader_interface.LoaderFrame.__init__(self, None, -1, "")
        adon_window.AdonWindow.__init__(self, window_id='wnd_main_gui', window_caption='', default_size=(410,500), default_pos=(60,60), default_top_most=True)
        self.Bind(wx.EVT_CLOSE, self.on_form_close, self)
        self.listModules.InsertColumn(0, u'Компоненты')
        self.listModules.SetColumnWidth(0, 400)
        self.gui_count = 0
        self.gui_frames = []
        self.adons = adon.AdonsManager(man, gui)
        self.adons.load_adons()
    def listModules_on_activate(self, event):
        try:
            itm = self.listModules.GetFirstSelected()
            if itm < 0:
                return
            if self.gui_frames[itm].IsShown():
                self.gui_frames[itm].Hide()
                self.gui_frames[itm].Show()
            else: self.gui_frames[itm].Show()
            self.gui_frames[itm].frames = self.gui_frames
        except:
            pass
    
    def add_gui(self, frame, description):
        self.listModules.InsertStringItem(self.gui_count, description)
        self.gui_count += 1
        self.gui_frames.append(frame)

    def btnLoadedModules_on_click(self, event):
        adons_tree_gui = at.Frame_AdonsTree()
        adons_tree_gui.set_adons_tree(self.adons)
        adons_tree_gui.ShowModal()
        if adons_tree_gui.ok:
            self.adons.store_disabled_adons()                
            wx.MessageBox(u"Изменения в списке подключаемых модулей будет применены при следующем запуске программы. Закройте программу и запустите ее заново.", u"Перезапустите программу", wx.OK)
        else:
            self.adons.load_disabled_adons()
        event.Skip()
        
    def on_form_close(self, event):
        exit()
    def btnUpdateModules_on_click(self, event):
        self.adons.reload()
        self.listModules.DeleteAllItems()
        for g in gui.frames:
            loader_frame.add_gui(g.frame, g.description)

def def_params(localdb):
    localdb.write_once("/db", None)

def init_database():
    sys.path.append('./manager')
    import localdb
    import adon_window
    localdb.init_localdb("localdb.pickle", def_params)


def init_coresystem_events(manager):
    manager.add_data_id("core::load_complete", u"Coresystem initialization complete, all adons loaded", tag="undefined")
    manager.add_data_id("core::idle", u"Coresystem main loop executed all pending events", tag="undefined")
    manager.add_data_id("core::exception", u"Coresystem encountered exception while running user code", tag="exception")

def run():
    app = wx.App(0)
    if wx.__version__ < "2.9":
        wx.InitAllImageHandlers()

    global man
    global gui
    global loader_frame

    if '--no-gui' in sys.argv:
        no_gui = True
    else:
        no_gui = False

    man = ms.manager
    init_coresystem_events(man)
    if not no_gui:
        gui = GuiInfo()
        loader_frame = Frame()
        app.SetTopWindow(loader_frame)
        loader_frame.Show()
        for g in gui.frames:
            loader_frame.add_gui(g.frame, g.description)
    else:
        gui = None
        loader_frame = None
        nongui_adons = adon.AdonsManager(man, gui)
        nongui_adons.load_adons()
    man.push_ticket(man.ticket("core::load_complete", "Coresystem load is complete", description="Load complete"))
    man.start_async_operation()

    if not no_gui:
        app.MainLoop()
    else:
        while True:
            time.sleep(1000)


