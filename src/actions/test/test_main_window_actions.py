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
from model.model import DataArray

import actions._main_window_actions as main_window_actions


class TestCsvInterface(object):
    def setup_method(self, method):
        self.test_filename = "actions/test/test.csv"
        self.test_filename2 = "actions/test/test_one_col.csv"
        self.test_filename3 = "actions/test/test_write.csv"
        
        
    def _get_csv_gen(self, filename, digest_types=None):
        test_file = open(filename)
        dialect = csv.Sniffer().sniff(test_file.read(1024))
        test_file.close()
        
        if digest_types is None:
            digest_types = [type(1)]
            
        has_header = False

        return main_window_actions.CsvInterface( \
            filename, dialect, digest_types, has_header)

    def test_get_csv_cells_gen(self):
        """Tests generator from csv content"""
        
        csv_gen = self._get_csv_gen(self.test_filename)
        
        column = xrange(100)
        
        cell_gen = csv_gen._get_csv_cells_gen(column)
        
        for i, cell in enumerate(cell_gen):
            assert str(i) == cell
        

    def test_iter(self):
        """Tests csv generator"""
        
        csv_gen = self._get_csv_gen(self.test_filename)
        
        assert [list(col) for col in csv_gen] == [['1', '2'], ['3', '4']]
        
        csv_gen = self._get_csv_gen(self.test_filename2, digest_types = [type("")])
        
        
        for i, col in enumerate(csv_gen):
            list_col = list(col)
            if i < 6:
                assert list_col == ["'" + str(i + 1) + "'", "''"]
            else:
                assert list_col == ["''", "''"]
    
    def test_write(self):
        """Tests writing csv file"""
        
        csv_gen = self._get_csv_gen(self.test_filename)
        csv_gen.path = self.test_filename3
        
        csv_gen.write(xrange(100) for _ in xrange(100))
        
        infile = open(self.test_filename3)
        content = infile.read()
        assert content[:10] == "0\t1\t2\t3\t4\t"
        infile.close()


class TestTxtGenerator(object):
    """Tests generating txt files"""
    
    def test_iter(self):
        pass


class TestExchangeActions(object):
    def test_import_csv(self):
        pass
        
    def test_import_txt(self):
        pass
    
    def test_import_file(self):
        pass
    
    def test_export_csv(self):
        pass
    
    def test_export_file(self):
        pass

class TestPrintActions(object):
    def test_print_preview(self):
        pass
        
    def test_printout(self):
        pass
    
class TestClipboardActions(object):
    def test_cut(self):
        pass
        
    def test_copy(self):
        pass
        
    def test_copy_result(self):
        pass
        
    def test_paste(self):
        pass
        
class TestMacroActions(object):
    def test_replace_macros(self):
        pass

    def test_execute_macros(self):
        pass
        
    def test_open_macros(self):
        pass
        
    def test_save_macros(self):
        pass

class TestHelpActions(object):
    def test_launch_help(self):
        pass
    
