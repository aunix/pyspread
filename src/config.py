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

from sysvars import get_program_path, get_color_string, get_font_string

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
        
        self.help_window_position = "(15, 15)"
        self.help_window_size = "(wx.GetDisplaySize()[0] * 7 /10," + \
                                " wx.GetDisplaySize()[1] * 7 /10)"
        

    def set_grid_config(self):
        """Grid configuration"""
        
        self.grid_shape = "(1000, 100, 3)"
        self.max_unredo = "5000"
        
        # Colors
        
        self.grid_color = repr(get_color_string(wx.SYS_COLOUR_ACTIVEBORDER))
        self.selection_color = repr(get_color_string(wx.SYS_COLOUR_HIGHLIGHT))
        self.background_color = repr(get_color_string(wx.SYS_COLOUR_WINDOW))
        self.text_color = repr(get_color_string(wx.SYS_COLOUR_WINDOWTEXT))
        
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
        return eval(getattr(self.data, key))
    
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



    

"""
System info
===========
"""

# Some system config checks are needed before 
# the real application is instanciated.
# These checks need a wx.App in order to work.

try:
    displaysize = wx.GetDisplaySize()
except wx.PyNoAppError:
    app = wx.App()
    displaysize = wx.GetDisplaySize()

dpi = map(lambda (pixels, length_mm): pixels * 25.6 / length_mm, 
          zip(displaysize, wx.GetDisplaySizeMM()))


"""
Grid lines
==========
"""

GRID_LINE_PEN = wx.Pen("Gray80", 1)


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


selected_cell_color = wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT)

default_color = wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW)
default_text_color = wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOWTEXT)


default_cell_attributes = {
    "borderwidth_bottom": 1,
    "borderwidth_right": 1,
    "bordercolor_bottom": wx.Colour(200, 200, 200).GetRGB(),
    "bordercolor_right": wx.Colour(200, 200, 200).GetRGB(),
    "bgcolor": default_color.GetRGB(),
    "textfont": wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT).\
                                  GetFaceName(),
    "pointsize": 10,
    "fontweight": wx.NORMAL,
    "fontstyle": wx.NORMAL,
    "textcolor": default_text_color.GetRGB(),
    "underline": False,
    "strikethrough": False,
    "angle": 0.0,
    "column-width": 150,
    "row-height": 26,
    "vertical_align": "top",
    "justification": "left",
    "frozen": False,
}



"""
Icontheme
=========

Provides the dict 'icons' with paths to the toolbar icons.

"""

if wx.Platform == '__WXMAC__':
    # Mac does not support "uncommon" icon sizes
    icon_size = (24, 24)
    wide_icon = ""
else:
    icon_size = (36, 36)
    wide_icon = "_w"
    
small_icon_size = (24, 24)

theme = "Tango"

_action_path = get_program_path() + "share/icons/" + theme + "/" + \
               str(icon_size[0]) + "x" + str(icon_size[1]) + \
               "/actions/"
               
_action_path_small = get_program_path() + "share/icons/" + theme + "/" + \
                     str(small_icon_size[0]) + "x" + str(small_icon_size[1]) + \
                     "/actions/"
               
_toggle_path = get_program_path() + "share/icons/" + theme + "/" + \
               str(small_icon_size[0]) + "x" + str(small_icon_size[1]) + \
               "/toggles/"

icons = {"FileNew": _action_path + "filenew.png", 
         "FileOpen": _action_path + "fileopen.png", 
         "FileSave": _action_path + "filesave.png", 
         "FilePrint": _action_path + "fileprint.png", 
         "EditCut": _action_path + "edit-cut.png", 
         "EditCopy": _action_path + "edit-copy.png", 
         "EditCopyRes": _action_path + "edit-copy-results.png", 
         "EditPaste": _action_path + "edit-paste.png",
         "Undo": _action_path + "edit-undo.png",
         "Redo": _action_path + "edit-redo.png",
         "Find": _action_path + "edit-find.png",
         "FindReplace": _action_path + "edit-find-replace.png",
         "FormatTextBold": _action_path_small + "format-text-bold.png",
         "FormatTextItalic": _action_path_small + "format-text-italic.png",
         "FormatTextUnderline": _action_path_small + \
                                            "format-text-underline.png",
         "FormatTextStrikethrough": _action_path_small + \
                                            "format-text-strikethrough.png",
         "JustifyRight": _action_path_small + "format-justify-right.png",
         "JustifyCenter": _action_path_small + "format-justify-center.png",
         "JustifyLeft": _action_path_small + "format-justify-left.png",
         "AlignTop": _action_path_small + "format-text-aligntop.png",
         "AlignCenter": _action_path_small + "format-text-aligncenter.png", 
         "AlignBottom": _action_path_small + "format-text-alignbottom.png", 
         "Freeze": _action_path_small + "frozen_small.png",
         "AllBorders": _toggle_path + "border_all.xpm",
         "LeftBorders": _toggle_path + "border_left.xpm",
         "RightBorders": _toggle_path + "border_right.xpm",
         "TopBorders": _toggle_path + "border_top.xpm",
         "BottomBorders": _toggle_path + "border_bottom.xpm",
         "InsideBorders": _toggle_path + "border_inside.xpm",
         "OutsideBorders": _toggle_path + "border_outside.xpm",
         "TopBottomBorders": _toggle_path + "border_top_n_bottom.xpm",
         "SearchDirectionUp": _toggle_path + "go-down.png",
         "SearchDirectionDown": _toggle_path + "go-up.png",
         "SearchCaseSensitive": _toggle_path + "aA" + wide_icon + ".png",
         "SearchRegexp": _toggle_path + "regex" + wide_icon + ".png",
         "SearchWholeword": _toggle_path + "wholeword" + wide_icon + ".png",
         }



# Bitmap and position of cell overflow rects
               
overflow_rects = { \
  "RIGHT": [wx.Bitmap(_toggle_path + "arrow_right.xpm", wx.BITMAP_TYPE_XPM),
          lambda x, y, w, h: (x - 6, y + h / 2 - 5)], 
  "LEFT": [wx.Bitmap(_toggle_path + "arrow_left.xpm", wx.BITMAP_TYPE_XPM), 
          lambda x, y, w, h: (x + w + 1, y + h / 2 - 5)], 
  "UP": [wx.Bitmap(_toggle_path + "arrow_up.xpm", wx.BITMAP_TYPE_XPM), 
          lambda x, y, w, h: (x + w / 2 - 5, y + h + 1)], 
  "DOWN": [wx.Bitmap(_toggle_path + "arrow_down.xpm", wx.BITMAP_TYPE_XPM), 
          lambda x, y, w, h: (x + w / 2 - 5, y - 6)], 
}




