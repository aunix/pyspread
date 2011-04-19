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
        pass
        
        
    def get_csv_gen(self, filename, digest_types=None):
        test_file = open(filename)
        dialect = csv.Sniffer().sniff(test_file.read(1024))
        test_file.close()
        
        if digest_types is None:
            digest_types = [type(1)]
            
        has_header = False

        return main_window_actions.CsvGenerator( \
            filename, dialect, digest_types, has_header)

    def test_get_csv_cells_gen(self):
        """Tests generator from csv content"""
        test_filename = "test.csv"
        csv_gen = self.get_csv_gen(test_filename)
        
        column = xrange(100)
        
        cell_gen = csv_gen._get_csv_cells_gen(column)
        
        for i, cell in enumerate(cell_gen):
            assert str(i) == cell
        

    def test_iter(self):
        """Tests csv generator"""
        
        test_filename = "test.csv"
        csv_gen = self.get_csv_gen(test_filename)
        
        assert [list(col) for col in csv_gen] == [['1', '2'], ['3', '4']]
        

        test_filename = "test_one_col.csv"
        csv_gen = self.get_csv_gen(test_filename, digest_types = [type("")])
        
        
        for i, col in enumerate(csv_gen):
            list_col = list(col)
            if i < 6:
                assert list_col == ["'" + str(i + 1) + "'", "''"]
            else:
                assert list_col == ["''", "''"]
        
        
class TestExchangeActions(object):
    pass
