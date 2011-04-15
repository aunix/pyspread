import os
from sys import path

test_path = os.path.dirname(os.path.realpath(__file__))
path.insert(0, test_path + "/../..")

import wx
app = wx.App()

from gui._main_window import MainWindow
from gui._grid import Grid
import actions._grid_actions
import lib.vartypes as vartypes
from lib._interfaces import PysInterface
from model._data_array import DataArray

class TestCsvGenerator(object):
    def setup_method(self, method):
        self.main_window = MainWindow(None, -1)
        self.grid = self.main_window.grid

    def test_get_csv_cells_gen(self):
        """Tests generator from csv content"""
        
        
        
    def test_get_csv_lines_gen(self):
        pass
        
        
class TestExchangeActions(object):
    pass
