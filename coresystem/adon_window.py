#!/usr/bin/env python
# -*- #coding: utf8 -*-

import wx
import traceback
import localdb

class AdonWindow(object):
    def __init__(self, window_id=None, window_caption=None, add_to_adon_list=False, default_size=None, default_pos=None, default_top_most=False):
        self.window_id = window_id
        self.window_caption = window_caption
        self.pos = default_pos
        self.size = default_size
        self.top_most = default_top_most
        self.auto_open = False
        self.pos_db_path = '/db/persistent/adon_window/'+self.window_id+'/pos'
        self.size_db_path = '/db/persistent/adon_window/'+self.window_id+'/size'
        self.autoopen_db_path = '/db/persistent/adon_window/'+self.window_id+'/auto_open'
        self.topmost_db_path = '/db/persistent/adon_window/'+self.window_id+'/top_most'
        self.__load_defaults()
        self.restore_pos_and_size()
        try:
            localdb.db.write_persistent(self.topmost_db_path, self.top_most)
        except:
            print traceback.format_exc()
        self.Bind(wx.EVT_MOVE, self.on_form_move)
        self.Bind(wx.EVT_SIZE, self.on_form_size)
        self.Bind(wx.EVT_CLOSE, self.on_form_close, self)
        self.Bind(wx.EVT_SHOW,  self.on_form_show, self)
    def __load_defaults(self):
        try:
            self.pos = localdb.db.read_value(self.pos_db_path)
        except:
            pass
        try:
            self.size = localdb.db.read_value(self.size_db_path)
        except:
            pass
        try:
            self.auto_open = localdb.db.read_value(self.autoopen_db_path)
        except:
            pass
        try:
            self.top_most = localdb.db.read_value(self.topmost_db_path)
        except:
            pass
    def on_form_move(self, event):
        try:
            self.pos = event.GetPosition()
            localdb.db.write_persistent(self.pos_db_path, self.pos)
        except:
            print traceback.format_exc()
        event.Skip()
    def on_form_size(self, event):
        try:
            self.size = event.GetSize()
            localdb.db.write_persistent(self.size_db_path, self.size)
        except:
            print traceback.format_exc()
        event.Skip()
    def on_form_show(self, event):
        try:
            show = event.GetShow()
            localdb.db.write_persistent(self.autoopen_db_path, show)
        except:
            print traceback.format_exc()
        event.Skip()
    def on_form_close(self, event):
        self.Hide()
    def restore_pos_and_size(self):
        if None != self.pos:
            self.SetPosition(wx.Point(self.pos[0], self.pos[1]))
        if None != self.size:
            self.SetSize(wx.Size(self.size[0], self.size[1]))
        if self.top_most:
            self.SetWindowStyle(self.GetWindowStyle() | (wx.STAY_ON_TOP))
        else:
            self.SetWindowStyle(self.GetWindowStyle() & (~wx.STAY_ON_TOP))   
        if self.auto_open:
            self.Show()