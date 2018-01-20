import operator
from enum import Enum
from typing import Iterable

import wx
import wx.grid


class Position(Enum):
    LEAD_ENGINEER = 0
    SENIOR_RESEARCHER = 1
    LEAD_RESEARCHER = 2
    SECTOR_HEAD = 3
    DEP_HEAD = 4
    COMPLEX_HEAD = 5
    DIRECTOR = 6


class Degree(Enum):
    SPECIALIST = 0
    PhD = 1
    Ph_P_D = 2
    ACADEMICIAN = 3


class Expert(object):
    MAX_RATE = 100
    __competency_map = {
        (Position.LEAD_ENGINEER, Degree.SPECIALIST): 1,

        (Position.SENIOR_RESEARCHER, Degree.SPECIALIST): 1,
        (Position.SENIOR_RESEARCHER, Degree.PhD): 1.5,

        (Position.LEAD_RESEARCHER, Degree.PhD): 2.25,
        (Position.LEAD_RESEARCHER, Degree.Ph_P_D): 3,

        (Position.SECTOR_HEAD, Degree.SPECIALIST): 2,
        (Position.SECTOR_HEAD, Degree.PhD): 3,
        (Position.SECTOR_HEAD, Degree.Ph_P_D): 4,
        (Position.SECTOR_HEAD, Degree.ACADEMICIAN): 6,

        (Position.DEP_HEAD, Degree.SPECIALIST): 2.5,
        (Position.DEP_HEAD, Degree.PhD): 3.75,
        (Position.DEP_HEAD, Degree.Ph_P_D): 5,
        (Position.DEP_HEAD, Degree.ACADEMICIAN): 7.5,

        (Position.COMPLEX_HEAD, Degree.SPECIALIST): 3,
        (Position.COMPLEX_HEAD, Degree.PhD): 4.5,
        (Position.COMPLEX_HEAD, Degree.Ph_P_D): 6,
        (Position.COMPLEX_HEAD, Degree.ACADEMICIAN): 9,

        (Position.DIRECTOR, Degree.SPECIALIST): 4,
        (Position.DIRECTOR, Degree.Ph_P_D): 8,
        (Position.DIRECTOR, Degree.PhD): 6,
        (Position.DIRECTOR, Degree.ACADEMICIAN): 12,

    }

    def __init__(self, name: str, position: Position, degree: Degree):
        try:
            self.competency_index = self.__competency_map[(position, degree)]
        except KeyError as e:
            raise ValueError("An expert with such position({}) can not have such degree({}).".format(position, degree))

        self.degree = degree
        self.position = position
        self.name = name
        self.rate_count = self.MAX_RATE

    def __str__(self):
        return "{}: {}, {}".format(self.name, self.degree, self.position)


class ExpertProject(object):
    def __init__(self, alternatives: Iterable[str], experts: Iterable[Expert], name: str, target: str):
        self.target = target
        self.name = name
        self.__alternatives = list(alternatives)
        self.__experts = experts
        self.__votes = {exp: {alt: 0 for alt in alternatives} for exp in experts}
        self.votes = {exp: {alt: 0 for alt in alternatives} for exp in experts}
        self.__relative_competencies = {exp: exp.competency_index / self.__get_competencies_sum() for exp in experts}

    def get_alternatives(self) -> tuple:
        return tuple(self.__alternatives)

    def get_experts(self) -> tuple:
        return tuple(self.__experts)

    def vote(self, expert: Expert, alternative: str, rate: int):
        if not isinstance(rate, int):
            raise ValueError("Illegal coeficient value: {} (must be int in range 0-10).".format(rate))

        if expert.rate_count == 0 and self.__sum_votes(expert) < Expert.MAX_RATE:
            expert.rate_count = Expert.MAX_RATE - self.__sum_votes(expert)

        if rate < expert.rate_count:
            self.__votes[expert][alternative] = rate / Expert.MAX_RATE
            self.votes[expert][alternative] = rate
            expert.rate_count -= rate
        else:
            self.__votes[expert][alternative] = expert.rate_count / Expert.MAX_RATE
            self.votes[expert][alternative] = expert.rate_count
            expert.rate_count = 0

    def __get_competencies_sum(self) -> float:
        return sum(x.competency_index for x in self.__experts)

    def __sum_votes(self, expert):
        return sum(self.votes[expert].values)

    def get_result(self):
        return {alt: sum(self.__votes[exp][alt] * self.__relative_competencies[exp] for exp in self.__experts) for alt
                in self.__alternatives}


class AlternativesMaster(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Параметры проэкта", pos=wx.DefaultPosition,
                           size=wx.Size(560, 410), style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer4 = wx.BoxSizer(wx.VERTICAL)

        fgSizer1 = wx.FlexGridSizer(0, 4, 0, 0)
        fgSizer1.SetFlexibleDirection(wx.BOTH)
        fgSizer1.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        fgSizer1.SetMinSize(wx.Size(-1, 25))
        self.m_staticText2 = wx.StaticText(self, wx.ID_ANY, u"Имя", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText2.Wrap(-1)
        fgSizer1.Add(self.m_staticText2, 0, wx.ALL, 5)

        self.name_field = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        fgSizer1.Add(self.name_field, 0, wx.ALL, 5)

        self.m_staticText3 = wx.StaticText(self, wx.ID_ANY, u"Цель", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText3.Wrap(-1)
        fgSizer1.Add(self.m_staticText3, 0, wx.ALL, 5)

        self.target_field = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        fgSizer1.Add(self.target_field, 0, wx.ALL, 5)

        bSizer4.Add(fgSizer1, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND, 0)

        fgSizer3 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer3.SetFlexibleDirection(wx.BOTH)
        fgSizer3.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        fgSizer3.SetMinSize(wx.Size(-1, 300))
        fgSizer4 = wx.FlexGridSizer(0, 1, 0, 0)
        fgSizer4.SetFlexibleDirection(wx.BOTH)
        fgSizer4.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_button1 = wx.Button(self, wx.ID_ANY, u"+", wx.DefaultPosition, wx.Size(50, -1), 0)
        fgSizer4.Add(self.m_button1, 0, wx.ALL, 3)

        self.m_button2 = wx.Button(self, wx.ID_ANY, u"-", wx.DefaultPosition, wx.Size(50, -1), 0)
        fgSizer4.Add(self.m_button2, 0, wx.ALL, 3)

        fgSizer3.Add(fgSizer4, 1, wx.EXPAND, 5)

        self.alt_grid = wx.grid.Grid(self, wx.ID_ANY, wx.DefaultPosition, wx.Size(-1, 300), 0)

        # Grid
        self.alt_grid.CreateGrid(3, 1)
        self.alt_grid.EnableEditing(True)
        self.alt_grid.EnableGridLines(True)
        self.alt_grid.EnableDragGridSize(False)
        self.alt_grid.SetMargins(0, 0)

        # Columns
        self.alt_grid.SetColSize(0, 400)
        self.alt_grid.EnableDragColMove(False)
        self.alt_grid.EnableDragColSize(True)
        self.alt_grid.SetColLabelSize(30)
        self.alt_grid.SetColLabelValue(0, u"Альтернативы")
        self.alt_grid.SetColLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Rows
        self.alt_grid.EnableDragRowSize(True)
        self.alt_grid.SetRowLabelSize(80)
        self.alt_grid.SetRowLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Label Appearance

        # Cell Defaults
        self.alt_grid.SetDefaultCellAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
        fgSizer3.Add(self.alt_grid, 0, wx.ALL, 5)

        bSizer4.Add(fgSizer3, 1, wx.EXPAND, 0)

        m_sdbSizer2 = wx.StdDialogButtonSizer()
        self.m_sdbSizer2OK = wx.Button(self, wx.ID_OK)
        m_sdbSizer2.AddButton(self.m_sdbSizer2OK)
        self.m_sdbSizer2Cancel = wx.Button(self, wx.ID_CANCEL)
        m_sdbSizer2.AddButton(self.m_sdbSizer2Cancel)
        m_sdbSizer2.Realize()

        bSizer4.Add(m_sdbSizer2, 1, wx.EXPAND, 0)

        self.SetSizer(bSizer4)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.m_button1.Bind(wx.EVT_BUTTON, self.add_alt)
        self.m_button2.Bind(wx.EVT_BUTTON, self.del_alt)
        self.m_sdbSizer2OK.Bind(wx.EVT_BUTTON, self.submit)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def add_alt(self, event):
        if self.alt_grid.GetNumberRows() >= 15:
            pass
        else:
            self.alt_grid.AppendRows()

    def del_alt(self, event):
        if self.alt_grid.GetNumberRows() <= 3:
            pass
        else:
            if self.alt_grid.GetSelectedRows():
                self.alt_grid.DeleteRows(self.alt_grid.GetSelectedRows()[0])
            else:
                self.alt_grid.DeleteRows(pos=self.alt_grid.GetNumberRows() - 1)

    def submit(self, event):
        if self.name_field.IsEmpty() or self.target_field.IsEmpty():
            wx.MessageBox("Не все поля заполнены")
        else:
            self.target = self.target_field.GetLabelText()
            self.name = self.target_field.GetLabelText()
            self.alternatives = []

            for i in range(self.alt_grid.GetNumberRows()):
                if self.alt_grid.GetCellValue(i, 0) == "":
                    self.alternatives.append("Альтернатива {}".format(i))
                else:
                    self.alternatives.append(self.alt_grid.GetCellValue(i, 0))

            self.Destroy()


class ExpertDialog(wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Определение єкспертов", pos=wx.DefaultPosition,
                           size=wx.Size(642, 474), style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer2 = wx.BoxSizer(wx.VERTICAL)

        self.m_staticText3 = wx.StaticText(self, wx.ID_ANY, u"Эксперты", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText3.Wrap(-1)
        bSizer2.Add(self.m_staticText3, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        fgSizer4 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer4.SetFlexibleDirection(wx.BOTH)
        fgSizer4.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        bSizer3 = wx.BoxSizer(wx.VERTICAL)

        self.add_btn = wx.Button(self, wx.ID_ANY, u"+", wx.DefaultPosition, wx.Size(40, -1), 0)
        bSizer3.Add(self.add_btn, 0, wx.ALL, 5)

        self.del_btn = wx.Button(self, wx.ID_ANY, u"-", wx.DefaultPosition, wx.Size(40, -1), 0)
        bSizer3.Add(self.del_btn, 0, wx.ALL, 5)

        fgSizer4.Add(bSizer3, 1, wx.EXPAND, 5)

        self.exp_grid = wx.grid.Grid(self, wx.ID_ANY, wx.DefaultPosition, wx.Size(-1, 360), 0)

        # Grid
        self.exp_grid.CreateGrid(3, 4)
        self.positions = {
            "Ведущий инженер": Position.LEAD_ENGINEER, "Научный сотрудник": Position.SENIOR_RESEARCHER,
            "Главный Н.С.": Position.LEAD_RESEARCHER, "Зав. сектора": Position.SECTOR_HEAD,
            "Зав. отдела": Position.DEP_HEAD, "Зав. Комплекса": Position.COMPLEX_HEAD,
            "Директор": Position.DIRECTOR}

        self.degrees = {"Без степени": Degree.SPECIALIST, "Кандидат наук": Degree.PhD, "Доктор наук": Degree.Ph_P_D,
                        "Академик": Degree.ACADEMICIAN}

        for x in range(self.exp_grid.GetNumberCols()):
            for y in range(self.exp_grid.GetNumberRows()):
                if x == 2:
                    self.exp_grid.SetCellEditor(y, x, wx.grid.GridCellChoiceEditor(tuple(self.positions.keys())))
                if x == 3:
                    self.exp_grid.SetCellEditor(y, x, wx.grid.GridCellChoiceEditor(tuple(self.degrees.keys())))

        self.exp_grid.EnableEditing(True)
        self.exp_grid.EnableGridLines(True)
        self.exp_grid.EnableDragGridSize(False)
        self.exp_grid.SetMargins(0, 0)

        # Columns
        self.exp_grid.SetColSize(0, 130)
        self.exp_grid.SetColSize(1, 140)
        self.exp_grid.SetColSize(2, 120)
        self.exp_grid.SetColSize(3, 140)
        self.exp_grid.EnableDragColMove(False)
        self.exp_grid.EnableDragColSize(True)
        self.exp_grid.SetColLabelSize(30)
        self.exp_grid.SetColLabelValue(0, u"Имя")
        self.exp_grid.SetColLabelValue(1, u"Фамилия")
        self.exp_grid.SetColLabelValue(2, u"Должность")
        self.exp_grid.SetColLabelValue(3, u"Научная степень")
        self.exp_grid.SetColLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Rows
        self.exp_grid.EnableDragRowSize(True)
        self.exp_grid.SetRowLabelSize(35)
        self.exp_grid.SetRowLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Label Appearance

        # Cell Defaults
        self.exp_grid.SetDefaultCellAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)

        fgSizer4.Add(self.exp_grid, 0, wx.ALL, 5)

        bSizer2.Add(fgSizer4, 1, wx.EXPAND, 5)

        m_sdbSizer2 = wx.StdDialogButtonSizer()
        self.m_sdbSizer2OK = wx.Button(self, wx.ID_OK)
        m_sdbSizer2.AddButton(self.m_sdbSizer2OK)
        self.m_sdbSizer2Cancel = wx.Button(self, wx.ID_CANCEL)
        m_sdbSizer2.AddButton(self.m_sdbSizer2Cancel)
        m_sdbSizer2.Realize()

        bSizer2.Add(m_sdbSizer2, 1, wx.EXPAND, 5)

        self.SetSizer(bSizer2)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.add_btn.Bind(wx.EVT_BUTTON, self.add_exp)
        self.del_btn.Bind(wx.EVT_BUTTON, self.del_exp)
        self.m_sdbSizer2OK.Bind(wx.EVT_BUTTON, self.submit)

        self.experts = []

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def add_exp(self, event):
        if self.exp_grid.GetNumberRows() <= 15:
            self.exp_grid.AppendRows()

    def del_exp(self, event):
        if self.exp_grid.GetNumberRows() > 1:
            if self.exp_grid.GetSelectedRows():
                self.exp_grid.DeleteRows(self.exp_grid.GetSelectedRows()[0])
            else:
                self.exp_grid.DeleteRows()

    def submit(self, event):
        for i in range(self.exp_grid.GetNumberRows()):
            name = self.exp_grid.GetCellValue(i, 0)
            surname = self.exp_grid.GetCellValue(i, 1)

            if self.exp_grid.GetCellValue(i, 2) == "":
                wx.MessageBox("Для єксперта {} необходимо выбрать должность".format(i))
                self.experts.clear()
                return
            else:
                position = self.positions[self.exp_grid.GetCellValue(i, 2)]

            if self.exp_grid.GetCellValue(i, 3) == "":
                wx.MessageBox("Для єксперта {} нееобходимо выбрать научную степень".format(i))
                self.experts.clear()
                return
            else:
                degree = self.degrees[self.exp_grid.GetCellValue(i, 3)]

            if name == "" and surname == "":
                name = "Эксперт {}".format(i)

            try:
                if surname == "":
                    self.experts.append(Expert(name, position, degree))
                else:
                    self.experts.append(Expert("{} {}".format(name, surname), position, degree))

            except ValueError as e:
                wx.MessageBox("Ошибка при создании эксперта {}: {}".format(i, e))
                self.experts.clear()
                return

        self.Destroy()


class ExpertWindow(wx.Frame):

    def __init__(self, parent, proj: ExpertProject):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"Анализ экспертных оценок", pos=wx.DefaultPosition,
                          size=wx.Size(1124, 636), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        self.proj = proj
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        fgSizer6 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer6.SetFlexibleDirection(wx.BOTH)
        fgSizer6.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.nb = wx.Notebook(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_panel1 = wx.Panel(self.nb, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        fgSizer7 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer7.SetFlexibleDirection(wx.BOTH)
        fgSizer7.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.vote_board = VoteBoard(proj, self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.Size(1000, 550), 0)

        fgSizer7.Add(self.vote_board, 0, wx.ALL, 0)

        bSizer4 = wx.BoxSizer(wx.VERTICAL)

        self.submit_btn = wx.Button(self.m_panel1, wx.ID_ANY, u"Завершить", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer4.Add(self.submit_btn, 0, wx.ALL, 5)

        self.reset_btn = wx.Button(self.m_panel1, wx.ID_ANY, u"Очистить", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer4.Add(self.reset_btn, 0, wx.ALL, 5)

        fgSizer7.Add(bSizer4, 1, wx.EXPAND, 5)

        self.m_panel1.SetSizer(fgSizer7)
        self.m_panel1.Layout()
        fgSizer7.Fit(self.m_panel1)
        self.nb.AddPage(self.m_panel1, u"Голосование", True)
        self.m_panel2 = wx.Panel(self.nb, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        bSizer5 = wx.BoxSizer(wx.VERTICAL)

        self.result_grid = wx.grid.Grid(self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)

        # Grid
        self.result_grid.CreateGrid(self.proj.get_alternatives().__len__(), 2)
        self.result_grid.EnableEditing(True)
        self.result_grid.EnableGridLines(True)
        self.result_grid.EnableDragGridSize(False)
        self.result_grid.SetMargins(0, 0)

        # Columns
        self.result_grid.SetColSize(0, 200)
        self.result_grid.SetColSize(1, 200)
        self.result_grid.EnableDragColMove(False)
        self.result_grid.EnableDragColSize(True)
        self.result_grid.SetColLabelSize(30)
        self.result_grid.SetColLabelValue(0, u"Альтернатива")
        self.result_grid.SetColLabelValue(1, u"Оценка")
        self.result_grid.SetColLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Rows
        self.result_grid.EnableDragRowSize(True)
        self.result_grid.SetRowLabelSize(80)
        self.result_grid.SetRowLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # Label Appearance

        # Cell Defaults
        self.result_grid.SetDefaultCellAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)

        for i in range(self.result_grid.GetNumberRows()):
            self.result_grid.SetReadOnly(i, 0, True)
            self.result_grid.SetReadOnly(i, 1, True)

        bSizer5.Add(self.result_grid, 0, wx.ALL, 5)

        bSizer6 = wx.BoxSizer(wx.HORIZONTAL)

        self.stt1 = wx.StaticText(self.m_panel2, wx.ID_ANY, u"Лучшая альтернатива: ", wx.DefaultPosition,
                                  wx.DefaultSize, 0)
        self.stt1.Wrap(-1)
        self.stt1.SetFont(wx.Font(16, 70, 93, 92, False, wx.EmptyString))

        bSizer6.Add(self.stt1, 0, wx.ALL, 5)

        self.result = wx.StaticText(self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        self.result.Wrap(-1)
        self.result.SetFont(wx.Font(16, 70, 93, 92, False, wx.EmptyString))
        self.result.SetForegroundColour(wx.Colour(255, 0, 0))

        bSizer6.Add(self.result, 0, wx.ALL, 5)

        bSizer5.Add(bSizer6, 1, wx.EXPAND, 5)

        self.m_panel2.SetSizer(bSizer5)
        self.m_panel2.Layout()
        bSizer5.Fit(self.m_panel2)
        self.nb.AddPage(self.m_panel2, u"Результаты", False)

        fgSizer6.Add(self.nb, 1, wx.EXPAND | wx.ALL, 0)

        self.SetSizer(fgSizer6)
        self.Layout()
        self.m_menubar1 = wx.MenuBar(0)
        self.m_menu1 = wx.Menu()
        self.update_mi = wx.MenuItem(self.m_menu1, wx.ID_ANY, u"Обновить", wx.EmptyString, wx.ITEM_NORMAL)
        self.m_menu1.AppendItem(self.update_mi)

        self.m_menubar1.Append(self.m_menu1, u"Правка")

        self.SetMenuBar(self.m_menubar1)

        self.Centre(wx.BOTH)

        # Connect Events
        self.Bind(wx.EVT_CLOSE, self.close)
        self.submit_btn.Bind(wx.EVT_BUTTON, self.submit)
        self.reset_btn.Bind(wx.EVT_BUTTON, self.clear)
        self.Bind(wx.EVT_MENU, self.update, id=self.update_mi.GetId())

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def close(self, event):
        self.GetParent().close(None)

    def submit(self, event):
        max_ = max(self.proj.get_result().items(), key=operator.itemgetter(1))[0]

        for i, (alt, val) in enumerate(self.proj.get_result().items()):
            if alt == max_:
                self.result_grid.SetCellBackgroundColour(i, 0, wx.Colour("red"))
                self.result_grid.SetCellBackgroundColour(i, 1, wx.Colour("red"))
                self.result.SetLabel(alt)
            self.result_grid.SetCellValue(i, 0, alt)
            self.result_grid.SetCellValue(i, 1, str(val))

    def clear(self, event):
        self.vote_board.clear()

    def update(self, event):
        self.vote_board.update()


class VoteBoard(wx.grid.Grid):
    def __init__(self, proj: ExpertProject, *args, **kw):
        super().__init__(*args, **kw)
        self.proj = proj
        self.num_rows = proj.get_experts().__len__()
        self.num_cols = proj.get_alternatives().__len__()
        self.CreateGrid(self.num_rows, self.num_cols)

        self.AppendCols()
        self.SetColLabelValue(self.GetNumberCols() - 1, "Очков осталось")

        for i in range(self.GetNumberRows()):
            self.SetReadOnly(i, self.GetNumberCols() - 1, True)

        for i, it in enumerate(self.proj.get_experts()):
            self.SetRowLabelValue(i, it.name)

        for i, it in enumerate(self.proj.get_alternatives()):
            self.SetColLabelValue(i, it)

        self.SetColSize(self.GetNumberCols() - 1, 150)
        self.GetParent().Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.cell_changed)

        self.update()

    def clear(self):
        self.update(True)

    def update(self, reset=False):
        for i, exp in enumerate(self.proj.get_experts()):
            for j, alt in enumerate(self.proj.get_alternatives()):
                if not reset:
                    self.SetCellValue(i, j, self.proj.votes[exp][alt].__str__())
                else:
                    self.SetCellValue(i, j, '0')
                    exp.rate_count = Expert.MAX_RATE
                    self.proj.vote(exp, alt, 0)

        for i, exp in enumerate(self.proj.get_experts()):
            self.SetCellValue(i, self.GetNumberCols() - 1, exp.rate_count.__str__())

    def cell_changed(self, event):
        x = event.GetRow()
        y = event.GetCol()

        try:
            self.proj.vote(self.proj.get_experts()[x], self.proj.get_alternatives()[y], int(self.GetCellValue(x, y)))
            self.update()
        except Exception:
            self.SetCellValue(x, y, event.GetString())
