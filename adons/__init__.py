#!/usr/bin/env python
# -*- coding: utf-8 -*-

import traceback
import hashlib

class ModuleInfo:
    def __init__(self, name, obj, md5sum=None, filename=None):
        self.name = name
        self.submodules = []
        self.init_fcn = None
        self.obj = obj
        self.disabled = False
        self.load_error = False
        self.md5sum = md5sum
        self.filename = filename
        self.parent = None
    def add_submodule(self, submodule):
        self.submodules.append(submodule)
        submodule.parent = self
    def set_init_fcn(self, fcn):
        self.init_fcn = fcn
    def print_modules(self, tab = 0):
        print ' '*tab, "name:", self.name
        if self.init_fcn != None:
            print ' '*tab , "init fcn:",self.init_fcn
        for m in self.submodules:
            m.print_modules(tab + 4)
    def get_disabled_adons(self):
        l = []
        if self.disabled:
            l.append(self.name)
        for m in self.submodules:
            l1 = m.get_disabled_adons()
            if len(l1)>0:
                for l2 in l1:
                    l3 = []
                    l3.append(self.name)
                    if isinstance(l2, str):
                        l3.append(l2)
                    else:
                        l3.extend(l2)
                    l.append(l3)
        return l
    def build_full_python_name(self):
        return self.parent.parent.name+"."+self.parent.name+"."+self.name
    def reload(self, manager, gui):
        if (None != self.obj or self.load_error) and self.filename!=None and self.md5sum!=None:
            try:
                md5sum = hashlib.md5(open(self.filename, 'rb').read()).digest()
                if md5sum!=self.md5sum:
                    self.md5sum = md5sum
                    print "Reloading module", self.name
                    if not self.load_error or None!=self.obj:
                        print "\tRemoving handlers..."
                        manager.remove_module_handlers(self.obj.__name__)
                        print "\tImporting module..."
                        self.obj = reload(self.obj)
                    else:
                        print "\tImporting as not loaded yet..."
                        self.obj = __import__(self.build_full_python_name(), globals(), locals(), self.name)
                    init_fcn = self.obj.init_module
                    print "\tInitialising module..."
                    init_fcn(manager, gui)
                    self.load_error = False
                    print "\tModule reloaded"
            except:
                self.load_error = True
                print "Сбой при перезагрузке пакета "+self.name
                print traceback.format_exc()
        for m in self.submodules:
            m.reload(manager, gui)

    def check_md5(self):
        if (None != self.obj or self.load_error) and self.filename!=None and self.md5sum!=None:
            md5sum = hashlib.md5(open(self.filename, 'rb').read()).digest()
            if md5sum!=self.md5sum:
                return False
        return True


def adons_init(check_adond_disabled):
    tree = ModuleInfo('adons', None)
    global __all__
    import os
    import os.path
    import copy
    local_path = os.path.dirname(os.path.realpath(__file__))
    
    adon_groups = [o for o in os.listdir(local_path) if os.path.isdir(os.path.join(local_path,o))]
    for adon_group in adon_groups:
        group_mi = ModuleInfo(adon_group, None)
        tree.add_submodule(group_mi)
        if check_adond_disabled(['adons', adon_group]):
            group_mi.disabled = True
            continue
        group_path = os.path.join(local_path, adon_group)
        submodules = [o for o in os.listdir(group_path) if os.path.isdir(os.path.join(group_path,o)) and o!=".hg"]
        submodules.sort()
        try:
            __all__.extend(copy.deepcopy(submodules))
        except:
            __all__ = copy.deepcopy(submodules)
        
        for a in submodules:
            adon_mi = ModuleInfo(a, None)
            group_mi.add_submodule(adon_mi)
            if check_adond_disabled(['adons', adon_group, a]):
                adon_mi.disabled = True
                continue
            try:
                adg = __import__(adon_group+"."+a, globals(), locals(), '__init__')
                for mname in adg.__all__:
                    if check_adond_disabled(['adons', adon_group,a, mname]):
                        mi = ModuleInfo(mname, None)
                        adon_mi.add_submodule(mi)
                        mi.disabled = True
                        continue
                    try:
                        ad = __import__(adon_group+"."+a+"."+mname, globals(), locals(), mname)
                        obj = ad
                        filename = obj.__file__.replace('.pyc', '.py')
                        md5sum = hashlib.md5(open(filename, 'rb').read()).digest()
                        fcn = obj.init_module
                        mi = ModuleInfo(mname, obj, filename = filename, md5sum = md5sum)
                        mi.set_init_fcn(fcn)
                        adon_mi.add_submodule(mi)
                    except:
                        print "Сбой при загрузке модуля "+mname+" из пакета "+adon_group+"."+a
                        print traceback.format_exc()
                        try:
                            #Настоящего имени файла у нас нет, попробуем его сформировать и посчитать контрольную сумму
                            filename = adg.__file__.replace('__init__.pyc', mname+".py")
                            md5sum = hashlib.md5(open(filename, 'rb').read()).digest()
                            mi = ModuleInfo(mname, None, filename = filename, md5sum = md5sum)
                            adon_mi.add_submodule(mi)
                            mi.load_error = True
                        except:
                            print traceback.format_exc()
                            mi = ModuleInfo(mname, None)
                            adon_mi.add_submodule(mi)
                            mi.load_error = True
                        continue
                            
            except:
                print "Сбой при загрузке пакета "+a+" из "+adon_group
                print traceback.format_exc()
                continue
    return tree

def load_user_adon(tree, adon_module_name):
    def get_user_group(tree):
        for m in tree.submodules:
            if m.name=='adons-external':
                return m
        m = ModuleInfo('adons-external', None)
        tree.add_submodule(m)
        return m
    ug = get_user_group(tree)
    try:
        ad = __import__(adon_module_name, globals(), locals())
        obj = ad
        filename = obj.__file__.replace('.pyc', '.py')
        md5sum = hashlib.md5(open(filename, 'rb').read()).digest()
        fcn = obj.init_module
        mi = ModuleInfo(adon_module_name, obj, filename = filename, md5sum = md5sum)
        mi.set_init_fcn(fcn)
        ug.add_submodule(mi)
    except:
        print "Сбой при загрузке пакета "+adon_module_name+" из adons-external"
        print traceback.format_exc()
        mi = ModuleInfo(adon_module_name, None)
        ug.add_submodule(mi)
        mi.load_error = True

