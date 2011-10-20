#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2008 Martin Manns
# Distributed under the terms of the GNU General Public License

# --------------------------------------------------------------------
# pyspread is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyspread is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyspread.  If not, see <http://www.gnu.org/licenses/>.
# --------------------------------------------------------------------

"""

UnRedo
======

UnRedo contains the UnRedo class that manages undo and redo operations.

"""

from config import config

class UnRedo(object):
    """Undo/Redo framework class.
    
    For each undo-able operation, the undo/redo framework stores the
    undo operation and the redo operation. For each step, a 4-tuple of:
    1) the function object that has to be called for the undo operation
    2) the undo function parameters as a list
    3) the function object that has to be called for the redo operation
    4) the redo function parameters as a list
    is stored.
    
    One undo step in the application can comprise of multiple operations.
    Undo steps are separated by the string "MARK".
    
    The attributes should only be written to by the class methods.

    Attributes
    ----------
    undolist: List
    \t
    redolist: List
    \t
    active: Boolean
    \tTrue while an undo or a redo step is executed.

    """
    
    def __init__(self):
        """[(undofunc, [undoparams, ...], redofunc, [redoparams, ...]), 
        ..., "MARK", ...]
        "MARK" separartes undo/redo steps
        
        """
        
        self.undolist = []
        self.redolist = []
        self.active = False
        
    def mark(self):
        """Inserts a mark in undolist and empties redolist"""
        
        if self.undolist != [] and self.undolist[-1] != "MARK":
            self.undolist.append("MARK")
    
    def undo(self):
        """Undos operations until next mark and stores them in the redolist"""
        
        self.active = True
        
        while self.undolist != [] and self.undolist[-1] == "MARK":
            self.undolist.pop()
            
        if self.redolist != [] and self.redolist[-1] != "MARK":
            self.redolist.append("MARK")
        
        while self.undolist != []:
            step = self.undolist.pop()
            if step == "MARK": 
                break
            self.redolist.append(step)
            step[0](*step[1])
        
        self.active = False
        
    def redo(self):
        """Redos operations until next mark and stores them in the undolist"""
        
        self.active = True
        
        while self.redolist and self.redolist[-1] == "MARK":
            self.redolist.pop()
        
        if self.undolist:
            self.undolist.append("MARK")
        
        while self.redolist:
            step = self.redolist.pop()
            if step == "MARK": 
                break
            self.undolist.append(step)
            step[2](*step[3])
            
        self.active = False

    def reset(self):
        """Empties both undolist and redolist"""
        
        self.__init__()

    def append(self, undo_operation, operation):
        """Stores an operation and its undo operation in the undolist
        
        undo_operation: (undo_function, [undo_function_attribute_1, ...])
        operation: (redo_function, [redo_function_attribute_1, ...])
        
        """
        
        if self.active:
            return False
        
        # If the lists grow too large they are emptied
        if len(self.undolist) > config["max_unredo"] or \
           len(self.redolist) > config["max_unredo"]:
            self.reset()
        
        # Check attribute types
        for unredo_operation in [undo_operation, operation]:
            iter(unredo_operation)
            assert len(unredo_operation) == 2
            assert hasattr(unredo_operation[0], "__call__")
            iter(unredo_operation[1])
        
        if not self.active:
            self.undolist.append(undo_operation + operation)

# End of class UnRedo
