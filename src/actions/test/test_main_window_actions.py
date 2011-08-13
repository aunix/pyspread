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
from lib.selection import Selection

import actions._main_window_actions as main_window_actions

# test support code
def params(funcarglist):
    def wrapper(function):
        function.funcarglist = funcarglist
        return function
    return wrapper

def pytest_generate_tests(metafunc):
    for funcargs in getattr(metafunc.function, 'funcarglist', ()):
        metafunc.addcall(funcargs=funcargs)

# actual test code

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
        
        csv_gen = self._get_csv_gen(self.test_filename2, digest_types = \
                  [type("")])
        
        
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
    
    param_copy = [ \
        {'key': (0, 0, 0), 'value': "'Test'"},
        {'key': (999, 0, 0), 'value': "1"},
        {'key': (999, 99, 0), 'value': "$^%&$^&"},
    ]
    
    @params(param_copy)
    def test_copy(self, key, value):
        main_window = MainWindow(None, -1)
        code_array = main_window.grid.code_array
        
        row, col, tab = key
        code_array[row, col, tab] = value
        selection = Selection([], [], [], [], [key[:2]])
        assert main_window.actions.copy(selection) == value

    param_copy_result = [ \
        {'key': (0, 0, 0), 'value': "'Test'", 'result': "Test"},
        {'key': (999, 0, 0), 'value': "1", 'result': "1"},
        {'key': (999, 99, 0), 'value': "$^%&$^&", 
                'result': "invalid syntax (<string>, line 1)"},
    ]
    
    @params(param_copy_result)
    def test_copy_result(self, key, value, result):
        main_window = MainWindow(None, -1)
        code_array = main_window.grid.code_array
        
        row, col, tab = key
        code_array[row, col, tab] = value
        selection = Selection([], [], [], [], [key[:2]])
        assert main_window.actions.copy_result(selection) == result
        
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
    
