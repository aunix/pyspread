"""
pyspread config file
====================

"""

"""
Program info
============

"""

# The current version of pyspread
VERSION = "0.1.3" 


class Config(object):
    """Configuration class for the application pyspread
    
    ## TODO: Implement wx.Python based config 
    """
    
    default_config = { \
        "default_dim": "1000 100 3",
        "icon_theme": "Stock", # Stock icon theme is "Tango" for Windows
        "max_undo": "5000",
    }
    
    # Main configuration 
    
    config = default_config
    
    # Helper functions for parsing
    
    read_maps = { \
        "default_dim": lambda s: tuple(int(num) for num in s.split),
        "icon_theme": lambda s: s,
        "max_undo": lambda s: int(s),
    }

    write_maps = { \
        "default_dim": lambda s: " ".join(s),
        "icon_theme": lambda s: s,
        "max_undo": lambda s: repr(s),
    }

    config_filename = ".pyspreadrc"
    
    def __init__(self):
        
        self.cfg_file = wx.Config('myconfig')
        
        self.load()
    
    def load(self):
        """Loads configuration file"""
        
        for key in self.default_config:
            if self.cfg_file.Exists(key):
                self.config[key] = self.read_maps(self.cfg_file.Read(key))
            else:
                self.config[key] = self.read_maps(self.default_config[key])
                        
    def save(self):
        """Saves configuration file"""
        
        for key in self.config:
            self.cfg_file.Write(key, self.write_maps[key](self.config[key]))


"""
Command line defaults
=====================

"""

DEFAULT_DIM = (1000, 100, 3) # Used for empty sheet at start-up

DEFAULT_FILENAME = "unnamed.pys"

"""
Paths
=====

Provides paths for libraries and icons

"""

import getpass
import os.path

import wx
import wx.stc  as  stc

PROG_DIR = os.path.dirname(os.path.realpath(__file__)) + '/../'
HELP_DIR = PROG_DIR + "doc/help/"

"""
GPG key parameters
==================

"""

GPG_KEY_UID = 'pyspread_' + getpass.getuser()
GPG_KEY_PASSPHRASE = "pyspread" # Set this individually!

GPG_KEY_PARMS = \
"""<GnupgKeyParms format="internal">
    Key-Type: DSA
    Key-Length: 2048
    Subkey-Type: ELG-E
    Subkey-Length: 2048
    Name-Real: """ + GPG_KEY_UID + """
    Name-Comment: Pyspread savefile signature keys
    Name-Email: pyspread@127.0.0.1
    Passphrase: """ + GPG_KEY_PASSPHRASE + """
    Expire-Date: 0
    </GnupgKeyParms>
    """
    

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

Main window styling
===================

"""

MAIN_WINDOW_ICON = wx.Bitmap(PROG_DIR + 'share/icons/pyspread.png', \
                             wx.BITMAP_TYPE_ANY)

MAIN_WINDOW_SIZE = (int(displaysize[0] * 0.9), int(displaysize[1] * 0.9))
HELP_SIZE = (int(displaysize[0] * 0.7), int(displaysize[1] * 0.7))

"""
Grid lines
==========
"""

GRID_LINE_PEN = wx.Pen("Gray80", 1)

"""
Zoom increase and decrease factor on zoom in and zoom out
"""

ZOOM_FACTOR = 0.05

MINIMUM_ZOOM = 0.25
MAXIMUM_ZOOM = 8.0

"""
CSV
===

CSV import options

"""

# Number of bytes for the sniffer (should be larger than 1st+2nd line)
SNIFF_SIZE = 65536 

# Maximum undo / redo size

MAX_UNREDO = 10000


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
Fold symbols
------------

The following styles are pre-defined:
  "arrows"      Arrow pointing right for contracted folders,
                arrow pointing down for expanded
  "plusminus"   Plus for contracted folders, minus for expanded
  "circletree"  Like a flattened tree control using circular headers 
                and curved joins
  "squaretree"  Like a flattened tree control using square headers

"""

fold_symbol_styles = { \
  "arrows": \
  [ \
    (stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_ARROWDOWN, "black", "black"), \
    (stc.STC_MARKNUM_FOLDER, stc.STC_MARK_ARROW, "black", "black"), \
    (stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_EMPTY, "black", "black"), \
    (stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_EMPTY, "black", "black"), \
    (stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_EMPTY, "white", "black"), \
    (stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_EMPTY, "white", "black"), \
    (stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_EMPTY, "white", "black"), \
  ], \
  "plusminus": \
  [ \
    (stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_MINUS, "white", "black"), \
    (stc.STC_MARKNUM_FOLDER, stc.STC_MARK_PLUS,  "white", "black"), \
    (stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_EMPTY, "white", "black"), \
    (stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_EMPTY, "white", "black"), \
    (stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_EMPTY, "white", "black"), \
    (stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_EMPTY, "white", "black"), \
    (stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_EMPTY, "white", "black"), \
  ], \
  "circletree":
  [ \
    (stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_CIRCLEMINUS, "white", "#404040"), \
    (stc.STC_MARKNUM_FOLDER, stc.STC_MARK_CIRCLEPLUS, "white", "#404040"), \
    (stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_VLINE, "white", "#404040"), \
    (stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_LCORNERCURVE,
                                                    "white", "#404040"), \
    (stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_CIRCLEPLUSCONNECTED, 
                                                    "white", "#404040"), \
    (stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_CIRCLEMINUSCONNECTED, 
                                                    "white", "#404040"), \
    (stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNERCURVE, 
                                                    "white", "#404040"), \
  ], \
  "squaretree": 
  [ \
    (stc.STC_MARKNUM_FOLDEROPEN, stc.STC_MARK_BOXMINUS, "white", "#808080"), \
    (stc.STC_MARKNUM_FOLDER, stc.STC_MARK_BOXPLUS, "white", "#808080"), \
    (stc.STC_MARKNUM_FOLDERSUB, stc.STC_MARK_VLINE, "white", "#808080"), \
    (stc.STC_MARKNUM_FOLDERTAIL, stc.STC_MARK_LCORNER, "white", "#808080"), \
    (stc.STC_MARKNUM_FOLDEREND, stc.STC_MARK_BOXPLUSCONNECTED, 
                                                      "white", "#808080"), \
    (stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_BOXMINUSCONNECTED, 
                                                      "white", "#808080"), \
    (stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNER, 
                                                      "white", "#808080"), \
  ] \
}

fold_symbol_style = fold_symbol_styles["circletree"]



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

_action_path = PROG_DIR + "share/icons/" + theme + "/" + \
               str(icon_size[0]) + "x" + str(icon_size[1]) + \
               "/actions/"
               
_action_path_small = PROG_DIR + "share/icons/" + theme + "/" + \
                     str(small_icon_size[0]) + "x" + str(small_icon_size[1]) + \
                     "/actions/"
               
_toggle_path = PROG_DIR + "share/icons/" + theme + "/" + \
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

"""
Border toggles
==============

Toggles for border changes, points to (top, bottom, left, right, inner, outer)

"""

border_toggles = [ \
    ("AllBorders",       (1, 1, 1, 1, 1, 1)),
    ("LeftBorders",      (0, 0, 1, 0, 1, 1)),
    ("RightBorders",     (0, 0, 0, 1, 1, 1)),
    ("TopBorders",       (1, 0, 0, 0, 1, 1)),
    ("BottomBorders",    (0, 1, 0, 0, 1, 1)),
    ("InsideBorders",    (1, 1, 1, 1, 1, 0)),
    ("OutsideBorders",   (1, 1, 1, 1, 0, 1)),
    ("TopBottomBorders", (1, 1, 0, 0, 0, 1)),
]

bordermap = { \
    "AllBorders":      ("top", "bottom", "left", "right"),
    "LeftBorders":     ("left"),
    "RightBorders":    ("right"),
    "TopBorders":      ("top"),
    "BottomBorders":   ("bottom"),
    "InsideBorders":   (""),
    "OutsideBorders":  (""),
    "TopBottomBorders":("top", "bottom"),
}

"""
ODF tags
========

The tags that identify recognizable attributes in ODF files

"""

odftags = {
           "root": "document-content",
           "autostyle": "automatic-styles",
           "body": "body",
           "office": "office",
           "table": "table",
           "column": "table-column",
           "row": "table-row",
           "cell": "table-cell",
           "style": "style",
           "name": "name",
           "stylename": "style-name",
           "colwidth": "column-width",
           "rowheight": "row-height",
           "strikethrough": "{urn:oasis:names:tc:opendocument:" + \
                            "xmlns:style:1.0}text-line-through-style",
           "fontcolor":     "{urn:oasis:names:tc:opendocument:" + \
                            "xmlns:xsl-fo-compatible:1.0}color",
           "verticalalign": "{urn:oasis:names:tc:opendocument:" + \
                            "xmlns:style:1.0}vertical-align",
           "rotationangle": "{urn:oasis:names:tc:opendocument:" + \
                            "xmlns:style:1.0}rotation-angle",
           "justification": "{urn:oasis:names:tc:opendocument:" + \
                            "xmlns:xsl-fo-compatible:1.0}fo:text-align",
           "textalign":     "{urn:oasis:names:tc:opendocument:" + \
                            "xmlns:xsl-fo-compatible:1.0}text-align",
           "underline":     "{urn:oasis:names:tc:opendocument:" + \
                            "xmlns:xsl-fo-compatible:1.0}text-underline-mode",
}

repeated_tags = {
           "rowsrepeated":  "{urn:oasis:names:tc:opendocument:xmlns:" + \
                            "table:1.0}number-rows-repeated",
           "colsrepeated":  "{urn:oasis:names:tc:opendocument:xmlns:" + \
                            "table:1.0}number-columns-repeated"
}

column_width_tag = '{urn:oasis:names:tc:opendocument:xmlns:style:1.0}' + \
                   'column-width'
row_height_tag = '{urn:oasis:names:tc:opendocument:xmlns:style:1.0}' + \
                 'row-height'

# Font attributes: tag: 
# [getter, setter, assertionfunction, conversionfunction]

font_weight_styles = [ \
            ("normal", wx.FONTWEIGHT_NORMAL), 
            ("bold", wx.FONTWEIGHT_BOLD),
            ("lighter", wx.FONTWEIGHT_LIGHT),
]

font_styles = [ \
            ("normal", wx.FONTSTYLE_NORMAL),
            ("italic", wx.FONTSTYLE_ITALIC),
]

font_attributes = { \
    "font-size": {
        "getter": "GetPointSize",
        "setter": "SetPointSize",
        "assert_func": lambda size: size[-2:] == "pt",
        "convert_func": lambda size: int(size[:-2]),
    },
    "font-size-complex": {
        "getter": "GetPointSize",
        "setter": "SetPointSize",
        "assert_func": lambda size: size[-2:] == "pt",
        "convert_func": lambda size: int(size[:-2]),
    },
    "font-style": { \
        "getter": "GetStyle",
        "setter": "SetStyle",
        "assert_func": lambda style: style in ["normal", "italic"],
        "convert_func": lambda style: dict(font_styles)[style],
    },
    "font-style-complex": { \
        "getter": "GetStyle",
        "setter": "SetStyle",
        "assert_func": lambda style: style in ["normal", "italic"],
        "convert_func": lambda style: dict(font_styles)[style],
    },
    "font-weight": { \
        "getter": "GetWeight",
        "setter": "SetWeight",
        "assert_func": lambda weight: weight in \
            ["normal", "bold", "lighter"],
        "convert_func": lambda weight: dict(font_weight_styles)[weight],
    },
    "font-weight-complex": { \
        "getter": "GetWeight",
        "setter": "SetWeight",
        "assert_func": lambda weight: weight in \
            ["normal", "bold", "lighter"],
        "convert_func": lambda weight: dict(font_weight_styles)[weight],
    },
    "text-underline-style": { \
        "getter": "GetUnderlined",
        "setter": "SetUnderlined",
        "assert_func": lambda underlined: underlined == "solid",
        "convert_func": lambda underlined: 1,
    },
}



pen_styles = [wx.SOLID, wx.TRANSPARENT, wx.DOT, wx.LONG_DASH, wx.SHORT_DASH,
              wx.DOT_DASH, wx.BDIAGONAL_HATCH, wx.CROSSDIAG_HATCH, 
              wx.FDIAGONAL_HATCH, wx.CROSS_HATCH, wx.HORIZONTAL_HATCH, 
              wx.VERTICAL_HATCH]

file_approval_warning = \
u"""You are going to approve and trust a file that
you have received from an untrusted source.\n
After proceeding, the file is executed.
It can harm your system as any program can.
Unless you took precautions, it can delete your
files or send them away over the Internet.\n
CHECK EACH CELL BEFORE PROCEEDING.
Do not forget cells outside the visible range.
You have been warned. \n
Proceed and sign this file as trusted?"""
