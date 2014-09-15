 #!/usr/bin/env python
# -*- coding: utf-8 -*-


import wx, interface_adonstree
import adon_window
#import daemons


class Frame_AdonsTree(interface_adonstree.AdonsTree, adon_window.AdonWindow):
    def __init__(self):
        interface_adonstree.AdonsTree.__init__(self, None, -1, "")
        adon_window.AdonWindow.__init__(self, window_id='wnd_adons_tree', window_caption='', default_size=(410,500))
        self.ok = False
        self.tree = None
        self.reload = False
        #self.Bind(wx.EVT_CLOSE, self.btnClose_handler, self)
    def btnOk_handler(self, event):  # wxGlade: AdonsTree.<event_handler>
        self.ok = True
        self.Close()

    def btnCancel_handler(self, event):  # wxGlade: AdonsTree.<event_handler>
        self.SetReturnCode(wx.ID_CANCEL)
        self.Close()

    def btnEnable_handler(self, event):  # wxGlade: AdonsTree.<event_handler>
        for itm in self.tree_ctrl_1.GetSelections():
            tree = self.tree_ctrl_1.GetItemPyData(itm)
            tree.disabled = False
            self.tree_ctrl_1.SetItemBold(itm, True)
        event.Skip()

    def btnDisable_handler(self, event):  # wxGlade: AdonsTree.<event_handler>
        for itm in self.tree_ctrl_1.GetSelections():
            tree = self.tree_ctrl_1.GetItemPyData(itm)
            tree.disabled = True
            self.tree_ctrl_1.SetItemBold(itm, False)
        event.Skip()

    def btnMd5_handler(self, event):
        pass

    def btnReload_handler(self, event):
        self.reload = True

    def _set_adons_tree(self, tree, parent_item = None):
        name = tree.name
        change_color = False
        if not tree.check_md5():
            name += u" (изменен)"
            change_color = True
        if tree.load_error:
            name += u" (сбой при загрузке)"
            change_color = True
        if None == parent_item:
            parent_item = self.tree_ctrl_1.AddRoot(name)
            itm = parent_item
        else:
            itm = self.tree_ctrl_1.AppendItem(parent_item, name)
        self.tree_ctrl_1.SetItemPyData(itm, tree)
        if change_color:
            self.tree_ctrl_1.SetItemTextColour(itm, wx.Colour(200,0,0))
        if tree.disabled:
            return
        self.tree_ctrl_1.SetItemBold(itm, True)
        for m in tree.submodules:
            self._set_adons_tree(m, itm)
        self.tree_ctrl_1.Expand(itm)

    def set_adons_tree(self, adons_tree):
        try:
            self.tree_ctrl_1.DeleteAllItems()
        except:
            pass
        self.tree = adons_tree.tree
        self._set_adons_tree(adons_tree.tree)
        self.tree_ctrl_1.Expand(self.tree_ctrl_1.GetRootItem())


if __name__ == "__main__":
    app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    frame_1 = Frame_AdonsTree()
    app.SetTopWindow(frame_1)
    frame_1.Show()
    app.MainLoop()
