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
pyspread config file
====================

"""

from copy import copy
from os import path
from getpass import getuser

import wx

from sysvars import get_program_path, get_color, get_font_string

"""
Program info
============

"""


class DefaultConfig(object):
    def __init__(self):
        # The current version of pyspread
        self.version = '"0.1.3"'
        
        self.set_paths()
        self.set_window_config()
        self.set_grid_config()
        self.set_gpg_config()
        self.set_csv_config()
        
    def set_paths(self):
        """User defined paths"""
        
        standardpaths = wx.StandardPaths.Get()
        self.work_path = standardpaths.GetDocumentsDir()
        
    def set_window_config(self):
        """Window configuration"""

        self.window_position = "(10, 10)"
        self.window_size = "(wx.GetDisplaySize()[0] * 9 /10," + \
                           " wx.GetDisplaySize()[1] * 9 /10)"
                           
        self.icon_theme ="'Tango'" 
        
        self.help_window_position = "(wx.GetDisplaySize()[0] * 7 / 10, 15)"
        self.help_window_size = "(wx.GetDisplaySize()[0] * 3 /10," + \
                                " wx.GetDisplaySize()[1] * 7 /10)"
        

    def set_grid_config(self):
        """Grid configuration"""
        
        self.grid_shape = "(1000, 100, 3)"
        self.max_unredo = "5000"
        
        # Colors
        self.grid_color = repr(get_color(wx.SYS_COLOUR_3DSHADOW))
        self.selection_color = repr(get_color(wx.SYS_COLOUR_HIGHLIGHT))
        self.background_color = repr(get_color(wx.SYS_COLOUR_WINDOW))
        self.text_color = repr(get_color(wx.SYS_COLOUR_WINDOWTEXT))
        
        # Fonts
        
        self.font = repr(get_font_string(wx.SYS_DEFAULT_GUI_FONT))
        
        # Zoom        
        
        self.minimum_zoom = "0.25"
        self.maximum_zoom = "8.0"
        
        # Increase and decrease factor on zoom in and zoom out
        self.zoom_factor = "0.05"
        
    def set_gpg_config(self):
        """GPG parameters"""
        
        self.gpg_key_uid = repr('pyspread_' + getuser())
        self.gpg_key_passphrase = repr("pyspread") # Set this individually!
        
        self.gpg_key_parameters = \
            '<GnupgKeyParms format="internal">\n' + \
            'Key-Type: DSA\n' + \
            'Key-Length: 2048\n' + \
            'Subkey-Type: ELG-E\n' + \
            'Subkey-Length: 2048\n' + \
            'Name-Real: ' + eval(self.gpg_key_uid) + '\n' + \
            'Name-Comment: Pyspread savefile signature keys\n' + \
            'Name-Email: pyspread@127.0.0.1\n' + \
            'Passphrase: ' + eval(self.gpg_key_passphrase) + '\n' + \
            'Expire-Date: 0\n' + \
            '</GnupgKeyParms>'

    def set_csv_config(self):
        """CSV parameters for import and export"""
        
        # Number of bytes for the sniffer (should be larger than 1st+2nd line)
        self.sniff_size = "65536"


class Config(object):
    """Configuration class for the application pyspread"""
    
    # Only keys in default_config are config keys
    
    config_filename = "pyspreadrc"
    
    def __init__(self, defaults=None):
        if defaults is None:
            self.defaults = DefaultConfig()
            
        else:
            self.defaults = defaults()
        
        self.data = DefaultConfig()
        
        self.cfg_file = wx.Config(self.config_filename)
        
        self.load()
    
    def __getitem__(self, key):
        """Main config element read access"""
        
        return eval(getattr(self.data, key))
    
    def __setitem__(self, key, value):
        """Main config element write access"""
        
        setattr(self.data, key, value)
    
    def load(self):
        """Loads configuration file"""
        
        # Reset data
        self.data.__dict__.update(self.defaults.__dict__)
        
        for key in self.defaults.__dict__:
            if self.cfg_file.Exists(key):
                setattr(self.data, key, self.cfg_file.Read(key))
                        
    def save(self):
        """Saves configuration file"""
        
        for key in self.defaults.__dict__:
            self.cfg_file.Write(key, getattr(self.data, key))


config = Config()
    

"""
StyledTextCtrl layout
=====================

Provides layout for the StyledTextCtrl widget that is used in the macro dialog

Platform dependent layout is specified here.

"""

"""
Font faces
----------

"""

if wx.Platform == '__WXMSW__':
    faces = { 'times': 'Times New Roman',
              'mono' : 'Courier New',
              'helv' : 'Arial',
              'other': 'Comic Sans MS',
              'size' : 10,
              'size2': 8,
             }
elif wx.Platform == '__WXMAC__':
    faces = { 'times': 'Times New Roman',
              'mono' : 'Monaco',
              'helv' : 'Arial',
              'other': 'Comic Sans MS',
              'size' : 10,
              'size2': 8,
             }
else:
    faces = { 'times': 'Times',
              'mono' : 'Courier',
              'helv' : wx.SystemSettings.GetFont( \
                       wx.SYS_DEFAULT_GUI_FONT).GetFaceName(),
              'other': 'new century schoolbook',
              'size' : 10,
              'size2': 8,
             }

"""
Default cell font size
----------------------

"""

FONT_SIZES = range(3, 14) + range(16, 32, 2) + range(36, 99, 4)






