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
from model.model import CodeArray

from gui._events import *

class TestFileActions(object):
    """File actions test class"""

    def setup_method(self, method):
        self.main_window = MainWindow(None, -1)
        self.grid = self.main_window.grid
        
    def test_validate_signature(self):
        """Tests signature validation"""
        
        # Test missing sig file
        filename_no_sig = "test2.pys"
        assert not self.grid.actions.validate_signature(filename_no_sig)
        
        # Test valid sig file
        filename_valid_sig = "test1.pys"
        assert self.grid.actions.validate_signature(filename_valid_sig)
        
        # Test invalid sig file
        filename_invalid_sig = "test3.pys"
        assert not self.grid.actions.validate_signature(filename_invalid_sig)
        
    def test_enter_safe_mode(self):
        """Tests safe mode entry"""
        
        self.grid.actions.leave_safe_mode()
        self.grid.actions.enter_safe_mode()
        assert self.grid.code_array.safe_mode

    def test_leave_safe_mode(self):
        """Tests save mode exit"""
        
        self.grid.actions.enter_safe_mode()
        self.grid.actions.leave_safe_mode()
        assert not self.grid.code_array.safe_mode

    def test_approve(self):
        
        # Test if safe_mode is correctly set for invalid sig
        filename_invalid_sig = "test3.pys"
        
        self.grid.actions.approve(filename_invalid_sig)
        
        assert self.grid.GetTable().data_array.safe_mode
        
        # Test if safe_mode is correctly set for valid sig
        
        filename_valid_sig = "test1.pys"
        
        self.grid.actions.approve(filename_valid_sig)
            
        assert not self.grid.GetTable().data_array.safe_mode
        
        # Test if safe_mode is correctly set for missing sig
        filename_no_sig = "test2.pys"
        
        self.grid.actions.approve(filename_no_sig)
        
        assert self.grid.GetTable().data_array.safe_mode
        
        # Test if safe_mode is correctly set for io-error sig
        
        filename_not_permitted = "test6.pys"
        
        os.chmod(filename_not_permitted, 0200)
        os.chmod(filename_not_permitted + ".sig", 0200)
        
        self.grid.actions.approve(filename_not_permitted)
        
        assert self.grid.GetTable().data_array.safe_mode
        
        os.chmod(filename_not_permitted, 0644)
        os.chmod(filename_not_permitted + ".sig", 0644)
        
    def test_open(self):
        """Tests open functionality"""

        class Event(object):
            attr = {"interface": PysInterface}
        event = Event()
        
        # Test missing file

        filename_wrong = "test-1.pys"

        event.attr["filepath"] = filename_wrong
        
        assert not self.grid.actions.open(event)
        
        # Test unaccessible file
        
        filename_not_permitted = "test6.pys"
        os.chmod(filename_not_permitted, 0200)
        
        event.attr["filepath"] = filename_not_permitted
        assert not self.grid.actions.open(event)
        
        os.chmod(filename_not_permitted, 0644)
        
        # Test empty file
        filename_empty = "test5.pys"
        
        event.attr["filepath"] = filename_empty
        assert not self.grid.actions.open(event)
        
        assert self.grid.GetTable().data_array.safe_mode # sig is also empty
        
        # Test invalid sig files
        filename_invalid_sig = "test3.pys"
        
        event.attr["filepath"] = filename_invalid_sig
        self.grid.actions.open(event)
        
        assert self.grid.GetTable().data_array.safe_mode
        
        # Test file with sig
        filename_valid_sig = "test1.pys"
        
        event.attr["filepath"] = filename_valid_sig
        self.grid.actions.open(event)
            
        assert not self.grid.GetTable().data_array.safe_mode
        
        # Test file without sig
        filename_no_sig = "test2.pys"
        
        event.attr["filepath"] = filename_no_sig
        self.grid.actions.open(event)
        
        assert self.grid.GetTable().data_array.safe_mode
        
        # Test grid size for valid file
        filename_gridsize = "test4.pys"
        
        event.attr["filepath"] = filename_gridsize
        self.grid.actions.open(event)
        
        assert not self.grid.GetTable().data_array.safe_mode
        assert self.grid.GetTable().data_array.shape == (1111, 2222, 3333)
        
        # Test grid content for valid file
        
        assert self.grid.GetTable().data_array[0, 0, 0] == "test4"
    
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

class TestMacroActions(object):
    pass


class TestUnRedoActions(object):
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
            code_array = CodeArray(dim)
            self.event.code_array = code_array
            self.grid.actions.new(self.event)
            assert self.grid.GetTable().data_array.shape == dim
    
class TestSelection(object):
    """Selection class test class"""
    
    def setup_method(self, method):
        self.SelectionCls = actions._grid_actions.Selection

    def test_contains(self):
        """Tests __contains__ functionality of selection class"""
        
        # Test block selection
        
        selection = self.SelectionCls([(4, 5)], [(100, 200)], [], [], [])
        cells_in_selection = ((i, j) for i in xrange(4, 100, 5) 
                                     for j in xrange(5, 200, 5))
        
        for cell in cells_in_selection:
            assert cell in selection
        
        cells_not_in_selection = \
            [(0, 0), (0, 1), (1, 0), (1, 1), (4, 4), (3, 5),
             (100, 201), (101, 200), (101, 201), (10**10, 10**10),
             [0, 0]]
        
        for cell in cells_not_in_selection:
            assert cell not in selection
        
        # Test row selection
        
        # Test column selection
        
        # Test cell selection
    
    def test_get_bbox(self):
        """Tests bounding boxes of selection class"""
        
        sel_tl, sel_br = [(4, 5)], [(100, 200)]
        
        selection = self.SelectionCls(sel_tl, sel_br, [], [], [])
        bbox_tl, bbox_br = selection.get_bbox() 
        assert bbox_tl == sel_tl[0]
        assert bbox_br == sel_br[0]
    
    
class TestSelectionActions(object):
    pass
    
    
class TestTableActions(object):
    def setup_method(self, method):
        self.main_window = MainWindow(None, -1)
        self.grid = self.main_window.grid
        
    def test_paste(self):
        """Tests paste into grid"""
        
        # Test 1D paste of strings
        tl_cell = 0, 0, 0
        data = [map(str, [1, 2, 3, 4]), [""] * 4]
        
        self.grid.actions.paste(tl_cell, data)
        
        assert self.grid.code_array[tl_cell] == 1
        assert self.grid.code_array(tl_cell) == '1'
        assert self.grid.code_array[0, 1, 0] == 2
        assert self.grid.code_array[0, 2, 0] == 3
        assert self.grid.code_array[0, 3, 0] == 4
        
        # Test row overflow
        ##TODO
        
        # Test col overflow
        ##TODO
