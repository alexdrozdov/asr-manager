#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

class FolderScan:
    def __init__(self, path):
        self.path = path
        self.subitems = {}
        self.files = []
        self.name = os.path.basename(path)
        self._scan()
    def get_name(self):
        return self.name
    def _scan(self):
        subfolders = os.listdir(self.path)
        for s in subfolders:
            full_path = os.path.join(self.path, s)
            if os.path.isdir(full_path):
                fs = self.create_subitem(full_path)
                self.subitems[fs.get_name()] = fs
            elif os.path.isfile(full_path):
                self.files.append(s)
        self.on_folder_loaded()
    def on_folder_loaded(self):
        pass
    
    def create_subitem(self, path):
        return FolderScan(path)
    
    def print_fs(self, tab = 0):
        print 'F', '    '*tab, self.get_name()
        for f in self.files:
            print 'L', '    '*(tab+1), f
        for sf in self.subitems.values():
            sf.print_fs(tab+1)
            
    def get_subitems(self, pattern = None):
        if None == pattern:
            return self.subitems
        selected_subitems = {}
        pattern = pattern.replace('.', '\\.').replace('*', '.*')
        rex = re.compile(pattern)
        for k in self.subitems.keys():
            if None==rex.match(k):
                continue
            selected_subitems[k] = self.subitems[k]
        return selected_subitems
    def get_subitem(self, name):
        return self.subitems[name]
    
    def get_files(self, pattern = None, expand_names = True):
        if None == pattern:
            selected_files = self.files
        else:
            selected_files = []
            pattern = pattern.replace('.', '\\.').replace('*', '.*')
            rex = re.compile(pattern)
            for f in self.files:
                if None==rex.match(f):
                    continue
                selected_files.append(f)
        if expand_names:
            expanded_files = []
            for f in selected_files:
                expanded_files.append(os.path.join(self.path, f))
            selected_files = expanded_files
        return selected_files
    def get_file(self, name, expand_name = True):
        if not name in self.files:
            raise KeyError(u"Файл "+name+u" отсутствует в каталоге " + self.path)
        if expand_name:
            return os.path.join(self.path, name)
        return name
