import os
from sys import path
import csv

test_path = os.path.dirname(os.path.realpath(__file__))
path.insert(0, test_path + "/../..")

import wx
app = wx.App()

from gui._main_window import MainWindow
from gui._grid import Grid
import lib.vartypes as vartypes
from lib._interfaces import PysInterface
from model._data_array import DataArray

import actions._main_window_actions as main_window_actions

class TestCsvGenerator(object):
    def setup_method(self, method):
        test_filename = "test.csv"
        test_file = open(test_filename)
        dialect = csv.Sniffer().sniff(test_file.read(1024))
        test_file.close()
        
        digest_types = [type(1)]
        has_header = False

        self.csv_gen = main_window_actions.CsvGenerator( \
            test_filename, dialect, digest_types, has_header)


    def test_get_csv_cells_gen(self):
        """Tests generator from csv content"""
        
        column = xrange(100)
        
        cell_gen = self.csv_gen._get_csv_cells_gen(column)
        
        for i, cell in enumerate(cell_gen):
            assert str(i) == cell
        

    def test_iter(self):
        """Tests csv generator"""
        

        
        assert [list(col) for col in self.csv_gen] == [['1', '2'], ['3', '4']]
                
        
        
class TestExchangeActions(object):
    pass
