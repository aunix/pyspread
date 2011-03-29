import os
from sys import path

test_path = os.path.dirname(os.path.realpath(__file__))
path.insert(0, test_path + "/../..")

import wx
app = wx.App()

from gui._grid import Grid
from gui._grid import Grid
import actions._grid_actions
import lib.vartypes as vartypes

class TestGridActions(object):
    """Grid level grid actions test class"""
    def setup_method(self, method):
        main_window = wx.Frame(None, -1)
        self.grid = Grid(main_window, -1)
        self.grid_actions = actions._grid_actions.AllGridActions(self.grid)
        
    def test_new(self):
        """Tests creation of a new spreadsheets"""
        no_tests = 100
        
        dims = vartypes.getints(1, 1000000, no_tests*3)
        dims = zip(dims[::3], dims[1::3], dims[2::3])
        
        for dim in dims:
            print dim
            self.grid_actions.new(dim)
            assert self.grid.GetTable().data_array.shape == dim
    
