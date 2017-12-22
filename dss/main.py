import os
import pickle

import wx

from ahpproject import AHPDialog, AHPWindow, AHPProject


class MainFrame(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title="Система принятия решений", pos=wx.DefaultPosition,
                          size=wx.Size(765, 56), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        self.main_menu = wx.MenuBar(0)
        self.file_menu = wx.Menu()
        self.m_menu2 = wx.Menu()
        self.ahp_mi = wx.MenuItem(self.m_menu2, wx.ID_ANY, "МАИ проэкт", wx.EmptyString, wx.ITEM_NORMAL)
        self.m_menu2.Append(self.ahp_mi)

        self.expert_mi = wx.MenuItem(self.m_menu2, wx.ID_ANY, "Анализ экспертных оценок", wx.EmptyString,
                                     wx.ITEM_NORMAL)
        self.m_menu2.Append(self.expert_mi)

        self.markov_mi = wx.MenuItem(self.m_menu2, wx.ID_ANY, "Марковский процесс", wx.EmptyString, wx.ITEM_NORMAL)
        self.m_menu2.Append(self.markov_mi)

        self.tree_mi = wx.MenuItem(self.m_menu2, wx.ID_ANY, "Дерево принятия решений", wx.EmptyString, wx.ITEM_NORMAL)
        self.m_menu2.Append(self.tree_mi)

        self.uncertainty_des_mi = wx.MenuItem(self.m_menu2, wx.ID_ANY, "Решение при неопределенности", wx.EmptyString,
                                              wx.ITEM_NORMAL)
        self.m_menu2.Append(self.uncertainty_des_mi)

        self.know_base = wx.MenuItem(self.m_menu2, wx.ID_ANY, "База знаний", wx.EmptyString, wx.ITEM_NORMAL)
        self.m_menu2.Append(self.know_base)

        self.file_menu.AppendSubMenu(self.m_menu2, "Новый")

        self.open_mi = wx.MenuItem(self.file_menu, wx.ID_ANY, "Открыть" + "\t" + "Ctrl+O", wx.EmptyString,
                                   wx.ITEM_NORMAL)
        self.file_menu.Append(self.open_mi)

        self.save_mi = wx.MenuItem(self.file_menu, wx.ID_ANY, "Сохранить" + "\t" + "Ctrl+S", wx.EmptyString,
                                   wx.ITEM_NORMAL)
        self.file_menu.Append(self.save_mi)

        self.close_mi = wx.MenuItem(self.file_menu, wx.ID_ANY, "Закрыть" + "\t" + "Ctrl+C", wx.EmptyString,
                                    wx.ITEM_NORMAL)
        self.file_menu.Append(self.close_mi)

        self.exit_mi = wx.MenuItem(self.file_menu, wx.ID_ANY, "Выход" + "\t" + "Ctrl+Q", wx.EmptyString,
                                   wx.ITEM_NORMAL)
        self.file_menu.Append(self.exit_mi)

        self.main_menu.Append(self.file_menu, "Файл")

        self.about_menu = wx.Menu()
        self.author_mi = wx.MenuItem(self.about_menu, wx.ID_ANY, "Автор", wx.EmptyString, wx.ITEM_NORMAL)
        self.about_menu.Append(self.author_mi)

        self.about_mi = wx.MenuItem(self.about_menu, wx.ID_ANY, "О приложении", wx.EmptyString, wx.ITEM_NORMAL)
        self.about_menu.Append(self.about_mi)

        self.main_menu.Append(self.about_menu, "Справка")

        self.SetMenuBar(self.main_menu)

        self.Bind(wx.EVT_MENU, self.new_ahp, id=self.ahp_mi.GetId())
        self.Bind(wx.EVT_MENU, self.new_expert, id=self.expert_mi.GetId())
        self.Bind(wx.EVT_MENU, self.layout_markov, id=self.markov_mi.GetId())
        self.Bind(wx.EVT_MENU, self.layout_tree, id=self.tree_mi.GetId())
        self.Bind(wx.EVT_MENU, self.layout_uncertainty, id=self.uncertainty_des_mi.GetId())
        self.Bind(wx.EVT_MENU, self.layout_know_base, id=self.know_base.GetId())
        self.Bind(wx.EVT_MENU, self.open, id=self.open_mi.GetId())
        self.Bind(wx.EVT_MENU, self.save, id=self.save_mi.GetId())
        self.Bind(wx.EVT_MENU, self.close, id=self.close_mi.GetId())
        self.Bind(wx.EVT_MENU, self.exit, id=self.exit_mi.GetId())
        self.Bind(wx.EVT_MENU, self.show_author, id=self.author_mi.GetId())
        self.Bind(wx.EVT_MENU, self.show_about, id=self.about_mi.GetId())
        self.Bind(wx.EVT_CLOSE, self.accept_exit)

        self.open_hk = wx.NewId()
        self.save_hk = wx.NewId()
        self.close_hk = wx.NewId()
        self.exit_hk = wx.NewId()
        self.RegisterHotKey(self.open_hk, wx.MOD_CMD, ord("O") | ord("Щ"))
        self.RegisterHotKey(self.save_hk, wx.MOD_CMD, ord("S") | ord("Ы"))
        self.RegisterHotKey(self.close_hk, wx.MOD_CMD, ord("C") | ord("С"))
        self.RegisterHotKey(self.exit_hk, wx.MOD_CMD, ord("Q") | ord("Й"))
        self.Bind(wx.EVT_HOTKEY, self.open, id=self.open_hk)
        self.Bind(wx.EVT_HOTKEY, self.save, id=self.save_hk)
        self.Bind(wx.EVT_HOTKEY, self.close, id=self.close_hk)
        self.Bind(wx.EVT_HOTKEY, self.exit, id=self.exit_hk)

        self.proj_opened = False
        self.proj_saved = True
        self.proj = None
        self.proj_win = None

    def new_ahp(self, event):
        self.close(None)

        dlg = AHPDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.proj = AHPProject(dlg.proj_name, dlg.target, dlg.criteria, dlg.alternatives)
            self.proj_win = AHPWindow(self, self.proj)
            self.proj_opened = True
            self.proj_saved = False
            self.proj_win.Show()

    def new_expert(self, event):
        event.Skip()

    def layout_markov(self, event):
        event.Skip()

    def layout_tree(self, event):
        event.Skip()

    def layout_uncertainty(self, event):
        event.Skip()

    def layout_know_base(self, event):
        event.Skip()

    def open(self, event):
        self.close(None)
        dlg = wx.FileDialog(self, "Открыть файл", os.path.curdir, style=wx.FD_OPEN, )
        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        try:
            if dlg.GetPath():
                f = open(dlg.GetPath(), "rb")
                self.proj = pickle.load(f)
                f.close()

                if type(self.proj) == AHPProject:
                    self.proj_win = AHPWindow(self, self.proj)
                    self.proj_opened = True
                    self.proj_saved = True
                    self.proj_win.Show()
                else:
                    wx.MessageBox("Неверный формат файла.")
                    return
        except Exception as e:
            wx.MessageBox("Ошибка: {}.".format(e))

    def save(self, event):
        if self.proj is not None:
            if self.proj_saved:
                f = open(self.saved_filename, "wb")
                pickle.dump(self.proj, f, 3)
                self.proj_saved = True
            else:
                dlg = wx.FileDialog(self, "Сохранение проэкта", style=wx.FD_SAVE, defaultFile=self.proj.name + ".ds")

                if dlg.ShowModal() == wx.ID_CANCEL:
                    return
                try:
                    if dlg.GetPath():
                        f = open(dlg.GetPath(), "wb")
                        pickle.dump(self.proj, f, 3)
                        self.proj_saved = True
                        self.saved_filename = dlg.GetPath()
                except:
                    wx.MessageBox("Ошибка сохранения.", style=wx.OK | wx.CENTRE | wx.ICON_ERROR)

    def close(self, event):
        if self.proj_opened:
            self._accept_save()
            self.proj_win.Destroy()
            self.proj_win = None
            self.proj = None
            self.proj_opened = False
            self.proj_saved = True

    def exit(self, event):
        self._accept_save()
        self.Destroy()

    def show_author(self, event):
        event.Skip()

    def show_about(self, event):
        event.Skip()

    def _accept_save(self):
        if self.proj_opened and not self.proj_saved:
            if wx.MessageDialog(self, "Текущий проэкт не сохранен. Сохранить?",
                                style=wx.YES_NO).ShowModal() == wx.ID_YES:
                self.save(None)

    def accept_exit(self, event):
        self._accept_save()
        if self.proj_win:
            self.proj_win.Destroy()
        self.Destroy()


if __name__ == "__main__":
    app = wx.App()
    m_frame = MainFrame(None)
    m_frame.Show()
    app.MainLoop()
