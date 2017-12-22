import operator
from collections import Iterable
from fractions import Fraction
from functools import reduce
from typing import Union

import wx
import wx.grid
import wx.propgrid as pg
from matplotlib import pyplot


class ComparisonMatrix(object):
    def __init__(self, items):
        super().__init__()
        self.size = len(items)

        if self.size < 3 or self.size > 10:
            raise ValueError("There should be more than 2 and less then 11 items, given {0}".format(self.size))

        for it in items:
            if not isinstance(it, str):
                raise TypeError("Only str items allowed.")

        self.items = list(items)

        self._matrix = {(c1, c2): Fraction(1) for c1 in items for c2 in items}

    def _get_priority_vector(self):
        return [pow(reduce(lambda x, y: x * y, [self._matrix[(col, row)] for row in self.items]), 1 / self.size)
                for col in
                self.items]

    def _get_col_sums(self):
        return [sum([self._matrix[(col, row)] for col in self.items]) for row in self.items]

    def get_items(self) -> tuple:
        return tuple(self.items)

    def get_normalized_vector(self) -> dict:

        s = sum(self._get_priority_vector())
        v = self._get_priority_vector()

        return {self.items[i]: float(v[i] / s) for i in range(0, self.size)}

    def get_lmax(self):
        v = self.get_normalized_vector()
        sums = self._get_col_sums()
        return float(sum(map(lambda i: v[self.items[i]] * sums[i], range(0, self.size))))

    def get_coherence_relation(self) -> float:
        return int(10000 * (self.get_lmax() - self.size) / (self.size - 1) / self._get_coherence_index()) / 100

    def _get_coherence_index(self):
        return {1: 0, 2: 0, 3: .58, 4: .9, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}[self.size]

    def add(self, item: str) -> None:
        if self.size >= 10: raise IndexError("There are already 10 items")
        self.items.append(item)
        self.size += 1

        for i in range(0, self.size):
            self._matrix[(item, self.items[i])] = Fraction(1)
            self._matrix[(self.items[i], item)] = Fraction(1)

    def remove(self, item: str) -> None:
        if self.size <= 3: raise IndexError("At least 3 items must remain.")
        for i in range(0, self.size):
            del self._matrix[(item, self.items[i])]

        self.items.remove(item)
        self.size -= 1

        for i in range(0, self.size):
            del self._matrix[(self.items[i], item)]

    def __str__(self):
        result = "Comparison matrix:\n"

        for i in range(0, self.size):
            for j in range(0, self.size):
                result += "[{0}]".format(str(self._matrix[(self.items[i], self.items[j])]))

            result += "\n"

        return result

    def set(self, name1: str, name2: str, value: Union[Fraction, int, float, str]):
        if not (isinstance(value, Fraction) or isinstance(value, str) or isinstance(value, int) or isinstance(value,
                                                                                                              float)):
            raise ValueError("Value must be Fraction, str, int, or float, got: {0}".format(value.__class__))

        value = Fraction(value)

        self._check_value(value)

        if (name1, name2) not in self._matrix:
            raise IndexError("No comparison: {0} -> {1}".format(name1, name2))

        if name2 == name1:
            self._matrix[(name1, name2)] = 1
            return

        self._matrix[(name1, name2)] = value
        self._matrix[(name2, name1)] = Fraction(value.denominator, value.numerator)

    def get(self, name1: str, name2: str):
        if (name1, name2) not in self._matrix:
            raise IndexError("No comparison: {0} -> {1}".format(name1, name2))

        return str(self._matrix[(name1, name2)])

    def _check_value(self, value: Fraction) -> None:
        if value.numerator not in range(1, 10) or value.denominator not in range(1, 10):
            raise ValueError("Invalid fractional value: {0}.".format(value))
        # TODO Улучшить метод проверки Fraction.


class AHPProject(object):
    def __init__(self, name: str, target: str, criteria, alternatives) -> None:
        self.criteria = list(criteria)
        self.alternatives = list(alternatives)
        self.target = target
        self.name = name

        self.criteria_comparison = ComparisonMatrix(criteria)
        self.alternatives_comparisons = {criterion: ComparisonMatrix(alternatives) for criterion in criteria}

    def add_criterion(self, crit: str) -> None:
        if not isinstance(crit, str):
            raise TypeError("Criterion must be str, got: {0}".format(crit.__class__))
        self.criteria_comparison.add(crit)
        self.alternatives_comparisons[crit] = ComparisonMatrix(self.alternatives)

    def get_global_vector(self) -> dict:
        crit_v = self.criteria_comparison.get_normalized_vector()
        alt_v = {k: v.get_normalized_vector() for k, v in self.alternatives_comparisons.items()}

        result = {}
        for a in self.alternatives:
            s = 0
            for c in self.criteria:
                s += crit_v[c] * alt_v[c][a]
            result[a] = s

        return result

    def add_alternative(self, alt: str):
        if not isinstance(alt, str):
            raise TypeError("ALternative must be str, got: {0}".format(alt.__class__))

    def __str__(self) -> str:
        res = "criteria: \n {0}".format(self.criteria_comparison)
        res += "Alternatives: \n"
        for k, v in self.alternatives_comparisons:
            res += "{0}:\n {1}".format(str(k), str(v))

        # TODO Улучшить строковое представление AHP.
        return res


class AHPDialog(wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Мастер МАИ проэкта", pos=wx.DefaultPosition,
                           size=wx.Size(556, 384), style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        bSizer3 = wx.BoxSizer(wx.VERTICAL)

        fgSizer1 = wx.FlexGridSizer(0, 4, 0, 0)
        fgSizer1.SetFlexibleDirection(wx.BOTH)
        fgSizer1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        fgSizer1.SetMinSize(wx.Size(-1, 210))
        self.m_staticText2 = wx.StaticText(self, wx.ID_ANY, u"Имя", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText2.Wrap(-1)
        fgSizer1.Add(self.m_staticText2, 0, wx.ALL, 5)

        self.name_ed = wx.TextCtrl(self, wx.ID_ANY, u"untitled", wx.DefaultPosition, wx.Size(160, -1), 0)
        fgSizer1.Add(self.name_ed, 0, wx.ALL, 5)

        self.m_staticText3 = wx.StaticText(self, wx.ID_ANY, u"Цель", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText3.Wrap(-1)
        fgSizer1.Add(self.m_staticText3, 0, wx.ALL, 5)

        self.target_ed = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(160, -1), 0)
        fgSizer1.Add(self.target_ed, 0, wx.ALL, 5)

        self.m_staticText4 = wx.StaticText(self, wx.ID_ANY, u"Критерии", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText4.Wrap(-1)
        fgSizer1.Add(self.m_staticText4, 0, wx.ALL, 5)

        self.crit_grid = wx.grid.Grid(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)

        # Grid
        self.crit_grid.CreateGrid(3, 1)
        self.crit_grid.EnableEditing(True)
        self.crit_grid.EnableGridLines(True)
        self.crit_grid.EnableDragGridSize(False)
        self.crit_grid.SetMargins(0, 0)

        # Columns
        self.crit_grid.SetColSize(0, 129)
        self.crit_grid.EnableDragColMove(False)
        self.crit_grid.EnableDragColSize(True)
        self.crit_grid.SetColLabelSize(30)
        self.crit_grid.SetColLabelValue(0, u"Name")
        self.crit_grid.SetColLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Rows
        self.crit_grid.EnableDragRowSize(True)
        self.crit_grid.SetRowLabelSize(30)
        self.crit_grid.SetRowLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Label Appearance

        # Cell Defaults
        self.crit_grid.SetDefaultCellAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
        self.crit_grid.SetMinSize(wx.Size(-1, 200))

        fgSizer1.Add(self.crit_grid, 0, wx.ALL, 5)

        self.m_staticText5 = wx.StaticText(self, wx.ID_ANY, u"Альтернативы", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText5.Wrap(-1)
        fgSizer1.Add(self.m_staticText5, 0, wx.ALL, 5)

        self.alt_grid = wx.grid.Grid(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)

        # Grid
        self.alt_grid.CreateGrid(3, 1)
        self.alt_grid.EnableEditing(True)
        self.alt_grid.EnableGridLines(True)
        self.alt_grid.EnableDragGridSize(False)
        self.alt_grid.SetMargins(0, 0)

        # Columns
        self.alt_grid.SetColSize(0, 129)
        self.alt_grid.EnableDragColMove(False)
        self.alt_grid.EnableDragColSize(True)
        self.alt_grid.SetColLabelSize(30)
        self.alt_grid.SetColLabelValue(0, u"Name")
        self.alt_grid.SetColLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Rows
        self.alt_grid.EnableDragRowSize(True)
        self.alt_grid.SetRowLabelSize(30)
        self.alt_grid.SetRowLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Label Appearance

        # Cell Defaults
        self.alt_grid.SetDefaultCellAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
        self.alt_grid.SetMinSize(wx.Size(-1, 200))

        fgSizer1.Add(self.alt_grid, 0, wx.ALL, 5)

        fgSizer1.AddSpacer(0)

        fgSizer3 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer3.SetFlexibleDirection(wx.BOTH)
        fgSizer3.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.crit_add = wx.Button(self, wx.ID_ANY, u"+", wx.DefaultPosition, wx.Size(70, -1), 0)
        fgSizer3.Add(self.crit_add, 0, wx.ALL, 5)

        self.crit_del_btn = wx.Button(self, wx.ID_ANY, u"-", wx.DefaultPosition, wx.Size(70, -1), 0)
        fgSizer3.Add(self.crit_del_btn, 0, wx.ALL, 5)

        fgSizer1.Add(fgSizer3, 1, wx.EXPAND, 5)

        fgSizer1.AddSpacer(0)

        fgSizer4 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer4.SetFlexibleDirection(wx.BOTH)
        fgSizer4.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.add_alt_btn = wx.Button(self, wx.ID_ANY, u"+", wx.DefaultPosition, wx.Size(70, -1), 0)
        fgSizer4.Add(self.add_alt_btn, 0, wx.ALL, 5)

        self.del_alt_btn = wx.Button(self, wx.ID_ANY, u"-", wx.DefaultPosition, wx.Size(70, -1), 0)
        fgSizer4.Add(self.del_alt_btn, 0, wx.ALL, 5)

        fgSizer1.Add(fgSizer4, 1, wx.EXPAND, 5)

        bSizer3.Add(fgSizer1, 1, wx.EXPAND, 5)

        m_sdbSizer4 = wx.StdDialogButtonSizer()
        self.m_sdbSizer4OK = wx.Button(self, wx.ID_OK)
        m_sdbSizer4.AddButton(self.m_sdbSizer4OK)
        self.m_sdbSizer4Cancel = wx.Button(self, wx.ID_CANCEL)
        m_sdbSizer4.AddButton(self.m_sdbSizer4Cancel)
        m_sdbSizer4.Realize()

        bSizer3.Add(m_sdbSizer4, 1, wx.EXPAND, 5)

        self.SetSizer(bSizer3)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.crit_add.Bind(wx.EVT_BUTTON, self.add_crit)
        self.crit_del_btn.Bind(wx.EVT_BUTTON, self.del_crit)
        self.add_alt_btn.Bind(wx.EVT_BUTTON, self.add_alt)
        self.del_alt_btn.Bind(wx.EVT_BUTTON, self.del_alt)
        self.m_sdbSizer4OK.Bind(wx.EVT_BUTTON, self.submit)

    def add_crit(self, event):
        if self.crit_grid.GetNumberRows() < 10:
            self.crit_grid.InsertRows(pos=self.crit_grid.GetNumberRows())

    def del_crit(self, event):
        if self.crit_grid.GetNumberRows() > 3:
            if self.crit_grid.GetSelectedRows():
                self.crit_grid.DeleteRows(self.crit_grid.GetSelectedRows()[0])
            else:
                self.crit_grid.DeleteRows(pos=self.crit_grid.GetNumberRows() - 1)

    def add_alt(self, event):
        if self.alt_grid.GetNumberRows() < 10:
            self.alt_grid.InsertRows(pos=self.alt_grid.GetNumberRows())

    def del_alt(self, event):
        if self.alt_grid.GetNumberRows() > 3:
            if self.alt_grid.GetSelectedRows():
                self.alt_grid.DeleteRows(self.alt_grid.GetSelectedRows()[0])
            else:
                self.alt_grid.DeleteRows(pos=self.alt_grid.GetNumberRows() - 1)

    def submit(self, event):
        if self._check_fields():
            self.proj_name = self.name_ed.GetValue()[:15]
            self.target = self.target_ed.GetValue()[:15]
            self.criteria = []
            self.alternatives = []

            self._read_criteria()

            self._read_alternatives()

            self.EndModal(wx.ID_OK)

    def _read_alternatives(self):
        for i in range(0, self.alt_grid.GetNumberRows()):
            val = self.alt_grid.GetCellValue(i, 0)
            if len(val) == 0:
                self.alternatives.append("Альтернатива {}".format(i))
            else:
                self.alternatives.append(val[:15])

    def _read_criteria(self):
        for i in range(0, self.crit_grid.GetNumberRows()):
            val = self.crit_grid.GetCellValue(i, 0)
            if len(val) == 0:
                self.criteria.append("Критерий {}".format(i))
            else:
                self.criteria.append(val[:15])

    def _check_fields(self):
        if self.name_ed.IsEmpty():
            wx.MessageBox("Поле 'имя' не может быть пустым.")
            self.name_ed.SetFocus()
            return False
        elif self.target_ed.IsEmpty():
            wx.MessageBox("Необходимо указать цель.")
            self.target_ed.SetFocus()
            return False

        return True


class AHPWindow(wx.Frame):

    def __init__(self, parent, proj):
        self.current_matrix = None
        self.model: AHPProject = proj

        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title="МАИ проэкт", pos=wx.DefaultPosition,
                          size=wx.Size(1285, 737), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER | wx.TAB_TRAVERSAL)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        self.main_menu = wx.MenuBar(0)
        self.edit_menu = wx.Menu()
        self.change_mi = wx.MenuItem(self.edit_menu, wx.ID_ANY, "Изменить", wx.EmptyString, wx.ITEM_NORMAL)
        self.edit_menu.Append(self.change_mi)

        self.update_ui = wx.MenuItem(self.edit_menu, wx.ID_ANY, "Обновить", wx.EmptyString, wx.ITEM_NORMAL)
        self.edit_menu.Append(self.update_ui)

        self.calc_memu = wx.Menu()
        self.calc_mi = wx.MenuItem(self.calc_memu, wx.ID_ANY, "Вычислить")

        self.gr_menu = wx.MenuItem(self.calc_memu, wx.ID_ANY, "Показать график")
        self.calc_memu.Append(self.calc_mi)
        self.calc_memu.Append(self.gr_menu)
        self.main_menu.Append(self.edit_menu, "Правка")
        self.main_menu.Append(self.calc_memu, "Расчеты")

        self.SetMenuBar(self.main_menu)

        bSizer2 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_notebook1 = wx.Notebook(self, wx.ID_ANY, wx.DefaultPosition, wx.Size(-1, -1), 0)
        self.m_notebook1.SetMaxSize(wx.Size(300, -1))

        self.m_panel1 = wx.Panel(self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.Size(-1, -1), wx.TAB_TRAVERSAL)
        bSizer5 = wx.BoxSizer(wx.VERTICAL)

        self.struct_view = wx.TreeCtrl(self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.Size(1000, 1000),
                                       wx.TR_DEFAULT_STYLE)
        bSizer5.Add(self.struct_view, 0, wx.ALL, 0)

        self.m_panel1.SetSizer(bSizer5)
        self.m_panel1.Layout()
        bSizer5.Fit(self.m_panel1)
        self.m_notebook1.AddPage(self.m_panel1, u"Структура", False)

        bSizer2.Add(self.m_notebook1, 1, wx.EXPAND | wx.ALL, 0)

        self.m_notebook2 = wx.Notebook(self, wx.ID_ANY, wx.DefaultPosition, wx.Size(675, -1), 0)
        self.matrix_edit = wx.ScrolledWindow(self.m_notebook2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                             wx.HSCROLL | wx.VSCROLL | wx.ALWAYS_SHOW_SB)
        self.matrix_edit.SetScrollRate(5, 5)
        self.m_notebook2.AddPage(self.matrix_edit, u"Изменение матриц", True)
        self.result_win = wx.ScrolledWindow(self.m_notebook2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                            wx.HSCROLL | wx.VSCROLL)
        self.result_win.SetScrollRate(5, 5)
        self.m_notebook2.AddPage(self.result_win, u"отчет", False)

        bSizer2.Add(self.m_notebook2, 1, wx.EXPAND | wx.ALL, 0)

        self.m_notebook3 = wx.Notebook(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_notebook3.SetMaxSize(wx.Size(300, -1))

        self.m_scrolledWindow7 = wx.ScrolledWindow(self.m_notebook3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                                   wx.HSCROLL | wx.VSCROLL)
        self.m_scrolledWindow7.SetScrollRate(5, 5)
        bSizer4 = wx.BoxSizer(wx.VERTICAL)

        self.props = pg.PropertyGrid(self.m_scrolledWindow7, wx.ID_ANY, wx.DefaultPosition, wx.Size(292, 647),
                                     wx.propgrid.PG_DEFAULT_STYLE | wx.propgrid.PG_TOOLTIPS)
        bSizer4.Add(self.props, 0, wx.ALL, 0)

        self.m_scrolledWindow7.SetSizer(bSizer4)
        self.m_scrolledWindow7.Layout()
        bSizer4.Fit(self.m_scrolledWindow7)
        self.m_notebook3.AddPage(self.m_scrolledWindow7, u"Свойства", False)

        bSizer2.Add(self.m_notebook3, 1, wx.EXPAND | wx.ALL, 0)

        self.SetSizer(bSizer2)
        self.Layout()

        self.Centre(wx.BOTH)

        self.Bind(wx.EVT_MENU, self.calculate, id=self.calc_mi.GetId())
        self.Bind(wx.EVT_MENU, self.update, id=self.update_ui.GetId())
        self.Bind(wx.EVT_MENU, self.show_chart, id=self.gr_menu.GetId())

        self.Bind(wx.EVT_CLOSE, self.accept_close)

        self.update(None)

    def calculate(self, event):
        m_sizer = wx.BoxSizer(wx.VERTICAL)

        gv = self.model.get_global_vector()

        glob_grid = wx.grid.Grid(self.result_win)
        glob_grid.SetColLabelSize(0)
        glob_grid.SetRowLabelSize(150)
        glob_grid.CreateGrid(len(gv), 1)

        max_ = max(gv.items(), key=operator.itemgetter(1))[0]

        for i, alt in enumerate(gv):
            glob_grid.SetRowLabelValue(i, alt)
            glob_grid.SetCellValue(i, 0, str(gv[alt]))
            glob_grid.SetReadOnly(i, 0)
            if alt == max_:
                glob_grid.SetCellBackgroundColour(i, 0, wx.Colour("red"))

        m_sizer.Add(glob_grid)

        c_btn = wx.Button(self.result_win, wx.ID_ANY, "График")
        self.result_win.Bind(wx.EVT_BUTTON, lambda e: (pyplot.plot(gv.values()), pyplot.show()), c_btn)

        label = wx.StaticText(self.result_win, wx.ID_ANY, "Лучшая альтернатива: {}".format(max_))
        label.SetFont(wx.Font(wx.FontInfo(16).Bold().Italic()))

        m_sizer.Add(label)
        m_sizer.Add(c_btn)

        if self.result_win.GetSizer():
            self.result_win.GetSizer().Clear()

        self.result_win.SetSizer(m_sizer)
        self.result_win.FitInside()

    def show_chart(self, event):
        if self.current_matrix is not None:
            pyplot.plot(self.current_matrix.matrix.get_normalized_vector().values())
            pyplot.show()

    def edit_alternatives(self, event):
        event.Skip()

    def update(self, event):
        if self.model is not None:
            self._update_structure()

            m_sizer = wx.BoxSizer(wx.VERTICAL)

            m_sizer.Add(wx.StaticText(self.matrix_edit, wx.ID_ANY, "Критерии"))
            m_sizer.Add(CMatrixView(self.model.criteria_comparison, self.matrix_edit), 1, wx.ALL, 5)

            t = wx.StaticText(self.matrix_edit, wx.ID_ANY, "Сравнения альтернатив по критериям")
            t.SetFont(wx.Font(wx.FontInfo(15).Bold().Italic()))

            m_sizer.Add(t, 0, wx.TOP, 5)
            for it in self.model.alternatives_comparisons:
                m_sizer.Add(wx.StaticText(self.matrix_edit, wx.ID_ANY, it))
                m_sizer.Add(CMatrixView(self.model.alternatives_comparisons[it], self.matrix_edit), 1, wx.ALL, 5)

            if self.matrix_edit.GetSizer():
                self.matrix_edit.GetSizer().Clear(True)

            self.matrix_edit.SetSizer(m_sizer)
            self.matrix_edit.FitInside()

    def _update_structure(self):
        self.struct_view.DeleteAllItems()
        root: wx.TreeItemId = self.struct_view.AddRoot(self.model.name)
        self.struct_view.AppendItem(root, self.model.target)

        crit = self.struct_view.AppendItem(root, "Критерии")
        alt = self.struct_view.AppendItem(root, "Альтернативы")

        for it in self.model.criteria:
            self.struct_view.AppendItem(crit, it)

        for it in self.model.alternatives:
            self.struct_view.AppendItem(alt, it)

    def accept_close(self, event):
        if self.GetParent():
            self.GetParent()._accept_save()
        else:
            self.Destroy()

    def update_props(self, names: tuple, props: tuple):
        if len(names) != len(props): raise ValueError("Количество имен групп должно совпадать с количеством групп")

        self.props.Clear()

        for i, n in enumerate(names):
            self.props.Append(wx.propgrid.PropertyCategory(n))
            for p in props[i]:
                self.props.Append(wx.propgrid.FloatProperty(p, value=props[i][p]))


class CMatrixView(wx.grid.Grid):
    def __init__(self, matrix: ComparisonMatrix, *args, **kw):
        super().__init__(*args, **kw)
        self.matrix = matrix
        self.GetParent().Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.cell_changed, self)
        self.GetParent().Bind(wx.grid.EVT_GRID_SELECT_CELL, self.focus_gain, self)
        self.CreateGrid(matrix.size, matrix.size)
        self.SetRowLabelSize(155)

        for i, it in enumerate(self.matrix.get_items()):
            self.SetColSize(i, 155)
            self.SetColLabelValue(i, it)
            self.SetRowLabelValue(i, it)
        self.update()

    def update(self):
        for i in range(self.matrix.size):
            for j in range(self.matrix.size):
                if i == j:
                    self.SetReadOnly(i, j)
                    self.SetCellValue(i, j, "1")
                    self.SetCellBackgroundColour(i, j, wx.Colour("yellow"))
                else:
                    self.SetCellValue(i, j, self.matrix.get(self.matrix.get_items()[i], self.matrix.get_items()[j]))

    def focus_gain(self, event):
        self.GetGrandParent().GetParent().update_props(("Нормализованный вектор", "Согласованность"), (
            self.matrix.get_normalized_vector(), {"": self.matrix.get_coherence_relation()}))

        if self.GetGrandParent().GetParent().current_matrix is not self:
            self.GetGrandParent().GetParent().current_matrix = self

    def cell_changed(self, event: wx.grid.GridEvent):
        try:
            self.matrix.set(self.matrix.items[event.GetRow()], self.matrix.items[event.GetCol()],
                            self.GetCellValue(event.GetRow(), event.GetCol()))
            self.update()
            self.focus_gain(None)
            self.GetGrandParent().GetParent().GetParent().proj_saved = False

        except Exception as e:
            self.SetCellValue(event.GetRow(), event.GetCol(), event.GetString())
