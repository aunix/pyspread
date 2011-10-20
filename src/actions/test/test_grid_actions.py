#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        
        # Filenames
        # ---------
        
        # File with valid signature
        self.filename_valid_sig = "test1.pys"
        
        # File without signature
        self.filename_no_sig = "test2.pys"
        
        # File with invalid signature
        self.filename_invalid_sig = "test3.pys"
        
        # File for grid size test
        self.filename_gridsize = "test4.pys"
        
        # Empty file
        self.filename_empty = "test5.pys"
        
        # File name that cannot be accessed
        self.filename_not_permitted = "test6.pys"
        
        # File name without file
        self.filename_wrong = "test-1.pys"
        
        # File for testing save
        self.filename_save = "test_save.pys"
        
    def test_validate_signature(self):
        """Tests signature validation"""
        
        # Test missing sig file
        assert not self.grid.actions.validate_signature(self.filename_no_sig)
        
        # Test valid sig file
        assert self.grid.actions.validate_signature(self.filename_valid_sig)
        
        # Test invalid sig file
        assert not \
            self.grid.actions.validate_signature(self.filename_invalid_sig)
        
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
        self.grid.actions.approve(self.filename_invalid_sig)
        
        assert self.grid.GetTable().data_array.safe_mode
        
        # Test if safe_mode is correctly set for valid sig
        
        self.grid.actions.approve(self.filename_valid_sig)
            
        assert not self.grid.GetTable().data_array.safe_mode
        
        # Test if safe_mode is correctly set for missing sig
        self.grid.actions.approve(self.filename_no_sig)
        
        assert self.grid.GetTable().data_array.safe_mode
        
        # Test if safe_mode is correctly set for io-error sig
        
        os.chmod(self.filename_not_permitted, 0200)
        os.chmod(self.filename_not_permitted + ".sig", 0200)
        
        self.grid.actions.approve(self.filename_not_permitted)
        
        assert self.grid.GetTable().data_array.safe_mode
        
        os.chmod(self.filename_not_permitted, 0644)
        os.chmod(self.filename_not_permitted + ".sig", 0644)
    
    def test_get_file_version(self):
        """Tests infile version string."""
        
        infile = bz2.BZ2File(self.filename_valid_sig)
        assert self.grid.actions._get_file_version(infile) == "0.1.3"
        infile.close()
    
    def test_open(self):
        """Tests open functionality"""

        class Event(object):
            attr = {"interface": PysInterface}
        event = Event()
        
        # Test missing file
        event.attr["filepath"] = self.filename_wrong
        
        assert not self.grid.actions.open(event)
        
        # Test unaccessible file
        os.chmod(self.filename_not_permitted, 0200)
        event.attr["filepath"] = self.filename_not_permitted
        assert not self.grid.actions.open(event)
        
        os.chmod(self.filename_not_permitted, 0644)
        
        # Test empty file
        event.attr["filepath"] = self.filename_empty
        assert not self.grid.actions.open(event)
        
        assert self.grid.GetTable().data_array.safe_mode # sig is also empty
        
        # Test invalid sig files
        event.attr["filepath"] = self.filename_invalid_sig
        self.grid.actions.open(event)
        
        assert self.grid.GetTable().data_array.safe_mode
        
        # Test file with sig
        event.attr["filepath"] = self.filename_valid_sig
        self.grid.actions.open(event)
            
        assert not self.grid.GetTable().data_array.safe_mode
        
        # Test file without sig
        event.attr["filepath"] = self.filename_no_sig
        self.grid.actions.open(event)
        
        assert self.grid.GetTable().data_array.safe_mode
        
        # Test grid size for valid file
        event.attr["filepath"] = self.filename_gridsize
        self.grid.actions.open(event)
        
        assert not self.grid.GetTable().data_array.safe_mode
        assert self.grid.GetTable().data_array.shape == (1111, 2222, 3333)
        
        # Test grid content for valid file
        
        assert self.grid.GetTable().data_array[0, 0, 0] == "test4"
    
    def test_save(self):
        """Tests save functionality"""
        
        class Event(object):
            attr = {"interface": PysInterface}
        event = Event()
        
        # Test normal save
        event.attr["filepath"] = self.filename_save
        
        self.grid.actions.save(event)
        
        savefile = open(self.filename_save)
        
        assert savefile
        savefile.close()
        
        # Test double filename
        
        self.grid.actions.save(event)
        
        # Test io error
        
        os.chmod(self.filename_save, 0200)
        try:
            self.grid.actions.save(event)
            raise IOError, "No error raised even though target not writable"
        except IOError:
            pass
        os.chmod(self.filename_save, 0644)
        
        # Test invalid file name
        
        event.attr["filepath"] = None
        try:
            self.grid.actions.save(event)
            raise TypeError, "None accepted as filename"
        except TypeError:
            pass
        
        # Test sig creation is happening
        
        sigfile = open(self.filename_save + ".sig")
        assert sigfile
        sigfile.close()
        
        os.remove(self.filename_save)
        os.remove(self.filename_save + ".sig")

    def test_sign_file(self):
        """Tests signing functionality"""
        
        # Test signing user id
        
        # Test normal signing
        
        # Test double filename signing
        
        # Test io error signing
        
        # Test invalid file name signing
        
        pass

class TestTableRowActionsMixins(object):
    def test_set_row_height(self):
        pass
        
    def test_insert_rows(self):
        pass
        
    def test_delete_rows(self):
        pass
        

class TestTableColumnActionsMixin(object):
    def test_set_col_width(self):
        pass
        
    def test_insert_cols(self):
        pass
        
    def test_delete_cols(self):
        pass
        
    
class TestTableTabActionsMixin(object):
    def test_insert_tabs(self):
        pass
        
    def test_delete_tabs(self):
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
    
    def test_on_key(self):
        pass
        
    def test_change_grid_shape(self):
        pass


class TestUnRedoActions(object):
    def test_undo(self):
        pass
        
    def test_redo(self):
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
            
    def test_get_visible_area(self):
        pass
        
    def test_switch_to_table(self):
        pass
        
    def test_get_cursor(self):
        pass
        
    def test_set_cursor(self):
        pass
        

class TestSelectionActions(object):
    """Selection actions test class"""
    
    def test_get_selection(self):
        pass
        
    def test_select_cell(self):
        pass
        
    def test_select_slice(self):
        pass
        
    def test_delete_selection(self):
        pass
    
    
class TestFindActions(object):
    """FindActions test class"""
    
    def test_find(self):
        pass
        
    def test_replace(self):
        pass

    
    
