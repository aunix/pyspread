import os
from sys import path

test_path = os.path.dirname(os.path.realpath(__file__))
path.insert(0, test_path + "/../..")

import wx
app = wx.App()

from gui._main_window import MainWindow
from gui._grid import Grid
from gui._grid import Grid
import actions._grid_actions
import lib.vartypes as vartypes
from lib._interfaces import PysInterface
from model._data_array import DataArray

from gui._events import *

class TestFileActions(object):
    """File actions test class"""

    def setup_method(self, method):
        self.main_window = MainWindow(None, -1)
        self.grid = self.main_window.grid
        
    def test_validate_signature(self):
        """Tests signature validation"""
        
        # Test wrong file name

        filename_wrong = "test-1.pys"
        class Event(object):
            attr = {"interface": PysInterface}
        event = Event()
        event.attr["filepath"] = filename_wrong
        
        assert self.grid.actions.open(event) == 0
        
        # Test non-existent sig files
        filename_no_sig = "test2.pys"
        
        post_command_event(self.main_window, GridActionOpenMsg, 
            attr={"filepath": filename_no_sig, "interface": PysInterface})
        
        assert self.grid.data_array.safe_mode
        
        # Test valid sig files
        filename_valid_sig = "test1.pys"
        post_command_event(self.main_window, GridActionOpenMsg, 
            attr={"filepath": filename_valid_sig, "interface": PysInterface})
            
        assert not self.grid.data_array.safe_mode
        
        # Test invalid sig files
        filename_invalid_sig = "test3.pys"
        post_command_event(self.main_window, GridActionOpenMsg, 
            attr={"filepath": filename_invalid_sig, "interface": PysInterface})
        assert self.grid.data_array.safe_mode

    def test_approve(self):
        
        # Test if safe_mode is correctly set for invalid sig
        
        # Test if safe_mode is correctly set for valid sig
        
        # Test if safe_mode is correctly set for missing sig
        
        # Test if safe_mode is correctly set for io-error sig
        
        pass
        
    def test_open(self):
        """Tests open functionality"""
        
        # Test missing event attributes
        
        # Test wrong event attribute types
        
        # Test missing file
        
        # Test unaccessible file
        
        # Test empty file
        
        # Test file with sig
        
        # Test file without sig
        
        # Test grid size for valid file
        
        # Test grid content for valid file
        
        pass
    
    def test_save(self):
        """Tests save functionality"""
        
        # Test normal save
        
        # Test double filename
        
        # Test io error
        
        # Test invalid file name
        
        # Test sig creation is happening
        
        pass    
    
    def test_open_save(self):
        """Tests open save round trip"""
        
        # Test normal save open round trip
        
        pass

    def test_sign_file(self):
        """Tests signing functionality"""
        
        # Test signing user id
        
        # Test normal signing
        
        # Test double filename signing
        
        # Test io error signing
        
        # Test invalid file name signing
        
        pass


class TestGridActions(object):
    """Grid level grid actions test class"""
    
    def setup_method(self, method):
        main_window = MainWindow(None, -1)
        self.grid = main_window.grid
        
        class Event(object):
            pass
            
        self.event = Event()
        
    def test_new(self):
        """Tests creation of a new spreadsheets"""
        no_tests = 10
        
        dims = vartypes.getints(1, 1000000, no_tests*3)
        dims = zip(dims[::3], dims[1::3], dims[2::3])
        
        for dim in dims:
            print dim, self.grid.GetTable().data_array.shape
            data_array = DataArray(dim)
            self.event.data_array = data_array
            self.grid.actions.new(self.event)
            assert self.grid.GetTable().data_array.shape == dim
    
