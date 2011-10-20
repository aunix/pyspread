#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from sys import path

test_path = os.path.dirname(os.path.realpath(__file__))
path.insert(0, test_path + "/../..")

class TestCellActions(object):
    """Cell actions test class"""
    
    def setup_method(self, method):
        self.main_window = MainWindow(None, -1)
        self.grid = self.main_window.grid
    
    def test_set_code(self):
        pass
    
    def test_delete_cell(self):
        pass
    
    def test_get_absolute_reference(self):
        pass
    
    def test_get_relative_reference(self):
        pass
    
    def test_append_reference_code(self):
        pass
    
    def test_set_cell_attr(self):
        pass
    
    def test_set_attr(self):
        pass
    
    def test_set_border_attr(self):
        pass
    
    def test_toggle_attr(self):
        pass
    
    def test_change_frozen_attr(self):
        pass
    
    def test_get_new_cell_attr_state(self):
        pass
    
    def test_get_new_selection_attr_state(self):
        pass
    
    def test_refresh_selected_frozen_cells(self):
        pass
        
