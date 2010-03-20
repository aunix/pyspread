"""
pyspread config file
====================

"""

"""
Program info
============

"""

# The current version of pyspread
VERSION = "0.1" 


"""
Command line defaults
=====================

"""

default_dimensions = (1000, 100, 3) # Used for empty sheet at start-up


"""
Paths
=====

Provides paths for libraries and icons

"""

import os.path

import wx
import wx.stc  as  stc

ICONPREFIX = os.path.dirname(os.path.realpath(__file__)) + '/'

"""
GPG key parameters
==================

"""

GPG_KEY_PARMS = \
"""<GnupgKeyParms format="internal">
    Key-Type: DSA
    Key-Length: 2048
    Subkey-Type: ELG-E
    Subkey-Length: 2048
    Name-Real: pyspread
    Name-Comment: Pyspread savefile signature keys
    Name-Email: pyspread@127.0.0.1
    Passphrase: pyspread
    Expire-Date: 0
    </GnupgKeyParms>
    """
    
GPG_KEY_UID = 'pyspread'
GPG_KEY_PASSPHRASE = "pyspread" # Set this individually!

"""
System info
===========
"""

# Some system config checks are needed before 
# the real application is instanciated.
# These checks need a wx.App in order to work.

dpi = map(lambda (pixels, length_mm): pixels * 25.6 / length_mm, 
          zip(wx.GetDisplaySize(), wx.GetDisplaySizeMM()))

"""
Grid lines
==========
"""

GRID_LINE_PEN = wx.Pen("Gray80", 1)

"""
CSV
===

CSV import options

"""

# Number of bytes for the sniffer (should be larger than 1st+2nd line)
SNIFF_SIZE = 65536 


"""
Key press behavior
==================

Defines, what actions are mapped on which key for the main window

"""

KEYFUNCTIONS = {"Ctrl+A": "MainGrid.SelectAll",
                "\x7f": "MainGrid.delete", # Del key
                "Shift+\x7f": "MainGrid.purge", # Shift+Del key
                } 

# Not needed because of menu:
#            "not_Shift+Ctrl+C": "OnCopy", \
#            "Shift+Ctrl+C": "OnCopyResult",\
#            "Ctrl+V": "OnPaste",\
#            "Ctrl+X": "OnCut",\


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

if wx.Platform == '__WXMSW__':
    DEFAULT_FONT = wx.Font(faces['size'], wx.NORMAL, wx.NORMAL, 
                           wx.NORMAL, False, faces['helv'])
    DEFAULT_FONT.SetPointSize(faces['size'])
else:
    DEFAULT_FONT = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)

FONT_SIZES = range(3, 14) + range(16, 32, 2) + range(36, 99, 4)

selected_cell_brush = wx.Brush(wx.Colour(127, 127, 255), wx.SOLID)

default_color = wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW)

default_cell_attributes = {
    "borderpen_bottom": \
        lambda: [wx.Colour(200, 200, 200).GetRGB(), 1, int(wx.SOLID)],
    "borderpen_right": \
        lambda: [wx.Colour(200, 200, 200).GetRGB(), 1, int(wx.SOLID)],
    "bgbrush": lambda: [int(default_color.GetRGB()), int(wx.SOLID)],
    "textattributes": lambda: {},
    "textfont": lambda: unicode(wx.Font(faces['size'], wx.DEFAULT, wx.NORMAL, 
                        wx.NORMAL, False, faces['helv']).GetNativeFontInfo()),
    "column-width": lambda: 150,
    "row-height": lambda: 25,
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
Text styles
-----------

The lexer defines what each style is used for, we just have to define
what each style looks like.  The Python style set is adapted from Scintilla
sample property files.

"""

text_styles = [ \
  (stc.STC_STYLE_DEFAULT, "face:%(helv)s,size:%(size)d" % faces), \
  (stc.STC_STYLE_LINENUMBER, "back:#C0C0C0,face:%(helv)s,"
                             "size:%(size2)d" % faces), \
  (stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % faces), \
  (stc.STC_STYLE_BRACELIGHT, "fore:#FFFFFF,back:#0000FF,bold"), \
  (stc.STC_STYLE_BRACEBAD, "fore:#000000,back:#FF0000,bold"), \
  # Python styles
  # Default 
  (stc.STC_P_DEFAULT, "fore:#000000,face:%(helv)s,size:%(size)d" % faces), \
  # Comments
  (stc.STC_P_COMMENTLINE, "fore:#007F00,face:%(other)s,"
                          "size:%(size)d" % faces), \
  # Number
  (stc.STC_P_NUMBER, "fore:#007F7F,size:%(size)d" % faces), \
  # String
  (stc.STC_P_STRING, "fore:#7F007F,face:%(helv)s,size:%(size)d" % faces), \
  # Single quoted string
  (stc.STC_P_CHARACTER, "fore:#7F007F,face:%(helv)s,size:%(size)d" % faces), \
  # Keyword
  (stc.STC_P_WORD, "fore:#00007F,bold,size:%(size)d" % faces), \
  # Triple quotes
  (stc.STC_P_TRIPLE, "fore:#7F0000,size:%(size)d" % faces), \
  # Triple double quotes
  (stc.STC_P_TRIPLEDOUBLE, "fore:#7F0000,size:%(size)d" % faces), \
  # Class name definition
  (stc.STC_P_CLASSNAME, "fore:#0000FF,bold,underline,size:%(size)d" % faces), \
  # Function or method name definition
  (stc.STC_P_DEFNAME, "fore:#007F7F,bold,size:%(size)d" % faces), \
  # Operators
  (stc.STC_P_OPERATOR, "bold,size:%(size)d" % faces), \
  # Identifiers
  (stc.STC_P_IDENTIFIER, "fore:#000000,face:%(helv)s,size:%(size)d" % faces), \
  # Comment-blocks
  (stc.STC_P_COMMENTBLOCK, "fore:#7F7F7F,size:%(size)d" % faces), \
  # End of line where string is not closed
  (stc.STC_P_STRINGEOL, "fore:#000000,face:%(mono)s,"
                        "back:#E0C0E0,eol,size:%(size)d" % faces), \
]

"""
Icontheme
=========

Provides the dict 'icons' with paths to the toolbar icons.

"""

icon_size = (36, 36)
_action_path = ICONPREFIX + "icons/actions/"
_toggle_path = ICONPREFIX + "icons/toggles/"

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
         "FormatTextBold": _action_path + "format-text-bold.png",
         "FormatTextItalic": _action_path + "format-text-italic.png",
         "FormatTextUnderline": _action_path + "format-text-underline.png",
         "FormatTextStrikethrough": _action_path + \
                                            "format-text-strikethrough.png",
         "JustifyRight": _action_path + "format-justify-right.png",
         "JustifyLeft": _action_path + "format-justify-left.png",
         "AlignTop": _action_path + "format-text-aligntop.png",
         "AlignCenter": _action_path + "format-text-aligncenter.png", 
         "AlignBottom": _action_path + "format-text-alignbottom.png", 
         "Freeze": _action_path + "frozen_small.png",
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
         "SearchCaseSensitive": _toggle_path + "aA.png",
         "SearchRegexp": _toggle_path + "regex.png",
         "SearchWholeword": _toggle_path + "wholeword.png",
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

# brush_styles not yet implemented

pen_styles = [wx.SOLID, wx.TRANSPARENT, wx.DOT, wx.LONG_DASH, wx.SHORT_DASH,
              wx.DOT_DASH, wx.BDIAGONAL_HATCH, wx.CROSSDIAG_HATCH, 
              wx.FDIAGONAL_HATCH, wx.CROSS_HATCH, wx.HORIZONTAL_HATCH, 
              wx.VERTICAL_HATCH]

brush_styles = { \
    "": wx.TRANSPARENT,
    "": wx.SOLID,
    "": wx.STIPPLE,
    "": wx.BDIAGONAL_HATCH,
    "": wx.CROSSDIAG_HATCH,
    "": wx.FDIAGONAL_HATCH,
    "": wx.CROSS_HATCH,
    "": wx.HORIZONTAL_HATCH,
    "": wx.VERTICAL_HATCH,
}

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
