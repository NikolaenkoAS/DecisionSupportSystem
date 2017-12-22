from enum import Enum
from fractions import Fraction
from typing import Union, Collection


class Competency(object):
    __type = Union[Fraction, str, int]

    def __init__(self, value: __type):
        """
        :param value: fraction in range 1, 1/2, 1/3, 1/4, 1/5, 1/6, 1/7, 1/8, 1/9, where 1 - best competency, 1/9 - lowest competency.
        """
        if isinstance(value, int):
            self.__value = Fraction(1, value)

        self.__value = Fraction(value)

        if self.__value.numerator != 1 or self.__value.denominator not in range(1, 10):
            raise ValueError("Invalid competency value: {}".format(self.__value))

    def __str__(self):
        return "{}".format(self.__value)

    def value_of(self):
        return self.__value.__copy__()


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
    __competency_matr = {
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
            self.competency_index = self.__competency_matr[(position, degree)] / 12.5
        except KeyError as e:
            raise KeyError("An expert with such position({}) can not have such degree({}).".format(position, degree))

        self.degree = degree
        self.position = position
        self.name = name


class ExpertProject(object):
    def __init__(self, alternatives: Collection):
        self.alternatives = list(alternatives)
        self.experts = {}

    def add_expert(self, name: str, competency: Competency) -> None:
        self.experts[name] = competency

    def remove_expert_by_name(self, name: str) -> None:
        try:
            del self.experts[name]
        except KeyError as e:
            raise KeyError("There is no expert: {}".format(name))


if __name__ == "__main__":
    print(Competency("2/8"))

    print(Expert("e1", Position.DIRECTOR, Degree.Ph_P_D).competency_index)
