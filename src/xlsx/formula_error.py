from typing import Optional

class FormulaError:
    def __init__(self, error: str):
        self._error = error

    @property
    def error(self) -> str:
        return self._error

    @staticmethod
    def get_error(error: str) -> 'FormulaError':
        for e in [DIV0, NA, NAME, NULL, NUM, REF, VALUE]:
            if e.error == error:
                return e
        return FormulaError(error)


DIV0 = FormulaError("#DIV/0!")
NA = FormulaError("#N/A")
NAME = FormulaError("#NAME?")
NULL = FormulaError("#NULL!")
NUM = FormulaError("#NUM!")
REF = FormulaError("#REF!")
VALUE = FormulaError("#VALUE!")