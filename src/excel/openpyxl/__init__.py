# Copyright (c) 2010-2019 openpyxl


from .compat.numbers import NUMPY, PANDAS
from .xml import DEFUSEDXML, LXML
from .workbook import Workbook
from .reader.excel import load_workbook as open
from .reader.excel import load_workbook
import ._constants as constants

# Expose constants especially the version number

__author__ = constants.__author__
__author_email__ = constants.__author_email__
__license__ = constants.__license__
__maintainer_email__ = constants.__maintainer_email__
__url__ = constants.__url__
__version__ = constants.__version__
