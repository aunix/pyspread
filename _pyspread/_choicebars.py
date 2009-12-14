#!/usr/bin/env python
# -*- coding: utf-8 -*-
# generated by wxGlade 0.6 on Sun May 25 23:31:23 2008

# Copyright 2008 Martin Manns
# Distributed under the terms of the GNU General Public License
# generated by wxGlade 0.6 on Mon Mar 17 23:22:49 2008

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
_choicebars
===========

Provides choice bars such as toolbars and menubars

Provides:
---------
  1. ContextMenu: Context menu for main grid
  2. MainMenu: Main menu of pyspread
  3. MainToolbar: Main toolbar of pyspread
  4. FindToolbar: Toolbar for Find operation
  5. AttributesToolbar: Toolbar for editing cell attributes

"""
import wx
import wx.lib.colourselect as csel

from _pyspread.config import icons, odftags, FONT_SIZES

from _pyspread._interfaces import get_font_list
import _widgets

class _filledMenu(wx.Menu):
    """Menu that fills from the attribute menudata.

    Parameters:
    parent: object
    \tThe parent object that hosts the event handler methods
    menubar: wx.Menubar, defaults to parent
    \tThe menubar to which the menu is attached

    menudata has the following structure:
    [
        [wx.Menu, "Menuname", [\
            [wx.MenuItem, ["Methodname", "Itemlabel", "Help"]] , \
            ...
            "Separator" , \
            ...
            [wx.Menu, ...], \
            ...
        ] , \
    ...
    ]
    """

    menudata = []

    def _add_submenu(self, parent, data):
        """Adds items in data as a submenu to parent"""

        for item in data:
            obj = item[0]
            if obj == wx.Menu:
                menuname = item[1]
                submenu = item[2]
                menu = obj()
                self._add_submenu(menu, submenu)
                if parent == self:
                    self.menubar.Append(menu, menuname)
                else:
                    parent.AppendMenu(wx.NewId(), menuname, menu)
            elif obj == wx.MenuItem:
                methodname = item[1][0]
                method = self.parent.__getattribute__(methodname)
                if len(item) == 3:
                    style = item[2]
                else:
                    style = wx.ITEM_NORMAL
                params = [parent, wx.NewId()] + item[1][1:] + [style]
                menuitem = obj(*params)
                parent.AppendItem(menuitem)
                self.parent.Bind(wx.EVT_MENU, method, menuitem)
            elif obj == "Separator":
                parent.AppendSeparator()
            else:
                raise TypeError, "Menu item unknown"


    def __init__(self, *args, **kwargs):
        self.parent = kwargs.pop('parent')
        try:
            self.menubar = kwargs.pop('menubar')
        except KeyError:
            self.menubar = self.parent
        wx.Menu.__init__(self, *args, **kwargs)
        self._add_submenu(self, self.menudata)

# end of class _filledMenu


class ContextMenu(_filledMenu):
    """Context menu for grid operations"""

    item = wx.MenuItem
    menudata = [ \
    [item, ["OnCut", "Cu&t\tCtrl+x", "Cut cell to clipboard"]], \
    [item, ["OnCopy", "&Copy\tCtrl+c", "Copy input strings to clipboard"]], \
    [item, ["OnPaste", "&Paste\tCtrl+v", "Paste cell from clipboard"]], \
    [item, ["OnInsertRows", "Insert &rows\tShift+Ctrl+i", 
        "Insert rows at cursor"]], \
    [item, ["OnInsertColumns", "&Insert columns\tCtrl+i", 
        "Insert columns at cursor"]], \
    [item, ["OnDeleteRows", "Delete rows\tShift+Ctrl+d", "Delete rows" ]], \
    [item, ["OnDeleteColumns", "Delete columns\tCtrl+Alt+d", "Delete columns"]]]


# end of class ContextMenu


class MainMenu(_filledMenu):
    """Main application menu"""
    item = wx.MenuItem
    menudata = [ \
        [wx.Menu, "&File", [\
            [item, ["OnFileNew", "&New\tCtrl+n", 
                "Create a new, empty spreadsheet"]], \
            [item, ["OnFileOpen", "&Open\tCtrl+o", 
                "Open spreadsheet from file"]], \
            [item, ["OnFileSave", "&Save\tCtrl+s", "Save spreadsheet"]], \
            [item, ["OnFileSaveAs", "Save &As\tShift+Ctrl+s", 
                "Save spreadsheet to a new file"]], \
            ["Separator"], \
            [item, ["OnFileImport", "&Import", "Import a file " + \
                "(Supported formats: CSV, Tab separated text)"]], \
            [item, ["OnFileExport", "&Export", 
                "Export a file (Supported formats: None"]], \
            ["Separator"], \
            [item, ["OnPageSetup", "Page setup", 
                "Setup page for printing"]], \
            [item, ["OnFilePrintPreview", "Page preview", 
                "Setup page for printing"]], \
            [item, ["OnFilePrint", "&Print...\tCtrl+p", 
                "Print current spreadsheet"]], \
            ["Separator"], \
            [item, ["OnExit", "E&xit\tCtrl+q", "Exit Program"]]] \
        ], \
        [wx.Menu, "&Edit", [\
            [item, ["OnUndo", "&Undo\tCtrl+z", "Undo last step"]], \
            [item, ["OnRedo", "&Redo\tShift+Ctrl+z", 
                "Redo last undone step"]], \
            ["Separator"], \
            [item, ["OnCut", "Cu&t\tCtrl+x", "Cut cell to clipboard"]], \
            [item, ["OnCopy", "&Copy\tCtrl+c", 
                "Copy the input strings of the cells to clipboard"]], \
            [item, ["OnCopyResult", "Copy &Results\tShift+Ctrl+c", 
                "Copy the result strings of the cells to the clipboard"]], \
            [item, ["OnPaste", "&Paste\tCtrl+v", 
                "Paste cells from clipboard"]], \
            ["Separator"], \
            [item, ["OnShowFind", "&Find\tCtrl+f", "Find cell by content"]], \
            [item, ["OnShowFindReplace", "Replace\tCtrl+Shift+f", 
                "Replace strings in cells"]], \
            ["Separator"], \
            [item, ["OnInsertRows", "Insert &rows\tShift+Ctrl+i", 
                "Insert rows at cursor"]], \
            [item, ["OnInsertColumns", "&Insert columns\tCtrl+i", 
                "Insert columns at cursor"]], \
            [item, ["OnInsertTable", "Insert &table", 
                "Insert table before current table"]], \
            ["Separator"], \
            [item, ["OnDeleteRows", "Delete rows\tShift+Ctrl+d", 
                "Delete rows"]], \
            [item, ["OnDeleteColumns", "Delete columns\tCtrl+Alt+d", 
                "Delete columns"]], \
            [item, ["OnDeleteTable", "Delete table", 
                "Delete current table"]], \
            ["Separator"], \
            [item, ["OnResizeGrid", "Resize grid", "Resize the grid. " + \
                    "The buttom right lowermost cells are deleted first."]]] \
        ], \
        [wx.Menu, "&View", [ \
            [wx.Menu, "Zoom", [ \
                [item, ["OnZoom", str(int(zoom)) + "%", 
                        "Zoom " + str(int(zoom)) + "%"] \
                ] for zoom in xrange(50, 350, 10)]
                ] \
            ], \
        ], \
        [wx.Menu, "&Macro", [\
            [item, ["OnMacroList", "&Macro list\tCtrl+m", 
                        "Choose, fill in, manage, and create macros"]], \
            [item, ["OnMacroListLoad", "&Load macro list\tShift+Ctrl+m", 
                        "Load macro list"]], \
            [item, ["OnMacroListSave", "&Save macro list\tShift+Alt+m", 
                        "Save macro list"]]]], \
        [wx.Menu, "&Help", [\
            [item, ["OnAbout", "&About", "About this program"]]] \
        ] \
    ]

# end of class MainMenu


class MainToolbar(wx.ToolBar):
    """Main application toolbar, built from attribute toolbardata

    toolbardata has the following structure:
    [[toolobject, "Methodname", "Label",
                  "Iconname", "Tooltip", "Help string"] , \
    ...
    ["Separator"] ,\
    ...
    ]

    """

    tool = wx.ITEM_NORMAL

    toolbardata = [
    [tool, "OnFileNew", "New", "FileNew", "New spreadsheet", 
        "Create a new, empty spreadsheet"], \
    [tool, "OnFileOpen", "Open", "FileOpen", "Open spreadsheet", 
        "Open spreadsheet from file"], \
    [tool, "OnFileSave", "Save", "FileSave", "Save spreadsheet", 
        "Save spreadsheet to file"], \
    ["Separator"] , \
    [tool, "OnUndo", "Undo", "Undo", "Undo", "Undo last operation"], \
    [tool, "OnRedo", "Redo", "Redo", "Redo", "Redo next operation"], \
    ["Separator"] , \
    [tool, "OnShowFind", "Find", "Find", "Find", "Find cell by content"], \
    [tool, "OnShowFindReplace", "Replace", "FindReplace", "Replace", 
        "Replace strings in cells"], \
    ["Separator"] , \
    [tool, "OnCut", "Cut", "EditCut", "Cut", "Cut cells to clipboard"], \
    [tool, "OnCopy", "Copy", "EditCopy", "Copy", 
        "Copy the input strings of the cells to clipboard"], \
    [tool, "OnCopyResult", "Copy Results", "EditCopyRes", "Copy Results", 
        "Copy the result strings of the cells to the clipboard"], \
    [tool, "OnPaste", "Paste", "EditPaste", "Paste", 
        "Paste cell from clipboard"], \
    ["Separator"] , \
    [tool, "OnFilePrint", "Print", "FilePrint", "Print current spreadsheet", 
        "Print current spreadsheet"], \
    ]

    def _add_tools(self):
        """Adds tools from self.toolbardata to self"""
        
        for tool in self.toolbardata:
            obj = tool[0]
            if obj == "Separator":
                self.AddSeparator()
            elif obj == self.tool:
                methodname = tool[1]
                method = self.parent.__getattribute__(methodname)
                label = tool[2]
                icon = wx.Bitmap(icons[tool[3]], wx.BITMAP_TYPE_ANY)
                icon2 = wx.NullBitmap
                tooltip = tool[4]
                helpstring = tool[5]
                toolid = wx.NewId()
                self.AddLabelTool(toolid, label, icon, icon2, obj, 
                                  tooltip, helpstring)
                self.parent.Bind(wx.EVT_TOOL, method, id=toolid)
            else:
                raise TypeError, "Toolbar item unknown"

    def __init__(self, *args, **kwargs):
        wx.ToolBar.__init__(self, *args, **kwargs)
        self.parent = args[0]
        self._add_tools()


# end of class MainToolbar


class FindToolbar(wx.ToolBar):
    """Toolbar for find operations (replaces wxFindReplaceDialog)"""
    
    # Search flag buttons
    search_options_buttons = { \
      "matchcase_tb": { \
        "ID": wx.NewId(), 
        "iconname": "SearchCaseSensitive", 
        "shorthelp": "Case sensitive",
        "longhelp": "Case sensitive search",
        "flag": "MATCH_CASE",
      },
      "regexp_tb": { 
        "ID": wx.NewId(), 
        "iconname": "SearchRegexp", 
        "shorthelp": "Regular expression",
        "longhelp": "Treat search string as regular expression",
        "flag": "REG_EXP",
      },
      "wholeword_tb": { \
        "ID": wx.NewId(), 
        "iconname": "SearchWholeword", 
        "shorthelp": "Whole word",
        "longhelp": "Search string is surronted by whitespace characters",
        "flag": "WHOLE_WORD",
      },
    }
    
    def __init__(self, *args, **kwargs):
        kwargs["style"] = wx.TB_FLAT | wx.TB_NODIVIDER
        wx.ToolBar.__init__(self, *args, **kwargs)
        
        self.parent = args[0]
        
        # Search entry control
        self.search_history = []
        self.search = wx.SearchCtrl(self, size=(150, -1), \
                        style=wx.TE_PROCESS_ENTER | wx.NO_BORDER)
        self.search.SetToolTip(wx.ToolTip("Enter search string for " + \
                                "searching in the grid cell source code"))
        self.menu = self.make_menu()
        self.search.SetMenu(self.menu)
        self.SetToolBitmapSize(self.search.GetSize())
        self.AddControl(self.search)
        
        # Search direction toggle button
        self.search_options = ["DOWN"]
        self.setup_searchdirection_togglebutton()
        
        # Search flags buttons
        sfbs = self.search_options_buttons
        for name in sfbs:
            iconname = sfbs[name]["iconname"]
            __id = sfbs[name]["ID"]
            shorthelp = sfbs[name]["shorthelp"]
            longhelp = sfbs[name]["longhelp"]
            
            bmp = wx.Bitmap(icons[iconname], wx.BITMAP_TYPE_PNG)
            self.SetToolBitmapSize(bmp.GetSize())
            self.AddCheckLabelTool(__id, name, bmp, 
                shortHelp=shorthelp, longHelp=longhelp)
            
        # Event bindings
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch, self.search)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnSearch, self.search)
        self.Bind(wx.EVT_MENU_RANGE, self.OnSearchFlag)
        self.Bind(wx.EVT_BUTTON, self.OnSearchDirectionButton, 
                                 self.search_direction_tb)
        self.Bind(wx.EVT_MENU, self.OnMenu)
        self.Realize()
    
    def setup_searchdirection_togglebutton(self):
        """Setup of search direction toggle button for searching up and down"""
        
        iconnames = ["SearchDirectionUp", "SearchDirectionDown"]
        bmplist = [wx.Bitmap(icons[iconname]) for iconname in iconnames]
        self.search_direction_tb = _widgets.BitmapToggleButton(self, bmplist)
        
        self.search_direction_tb.SetInitialSize()
        self.search_direction_tb.SetToolTip( \
            wx.ToolTip("Search direction"))
        self.SetToolBitmapSize(bmplist[0].GetSize())
        self.AddControl(self.search_direction_tb)
        
    
    def make_menu(self):
        """Creates the search menu"""
        
        menu = wx.Menu()
        item = menu.Append(-1, "Recent Searches")
        item.Enable(False)
        
        for __id, txt in enumerate(self.search_history):
            menu.Append(__id, txt)
        return menu
    
    def OnMenu(self, event):
        """Search history has been selected"""
        
        __id = event.GetId()
        try:
            menuitem = event.GetEventObject().FindItemById(__id)
            selected_text = menuitem.GetItemLabel()
            self.search.SetValue(selected_text)
        except AttributeError:
            # Not called by menu
            event.Skip()
    
    def OnSearch(self, event):
        """Event handler for starting the search"""
        
        search_string = self.search.GetValue()
        
        if search_string not in self.search_history:
            self.search_history.append(search_string)
        if len(self.search_history) > 10:
            self.search_history.pop(0)
            
        self.menu = self.make_menu()
        self.search.SetMenu(self.menu)
        
        search_flags = self.search_options + ["FIND_NEXT"]
        findpos = self.parent.find_position(search_string, search_flags)
        self.parent.find_gui_feedback(event, search_string, findpos)
        self.search.SetFocus()
    
    def OnSearchDirectionButton(self, event):
        """Event handler for search direction toggle button"""
        
        if "DOWN" in self.search_options:
            flag_index = self.search_options.index("DOWN")
            self.search_options[flag_index] = "UP"
        elif "UP" in self.search_options:
            flag_index = self.search_options.index("UP")
            self.search_options[flag_index] = "DOWN"
        else:
            raise AttributeError, "Neither UP nor DOWN in search_flags"
        event.Skip()
    
    def OnSearchFlag(self, event):
        """Event handler for search flag toggle buttons"""
        
        sfbs = self.search_options_buttons
        for name in sfbs:
            if sfbs[name]["ID"] == event.GetId():
                if event.IsChecked():
                    self.search_options.append(sfbs[name]["flag"])
                else:
                    flag_index = self.search_options.index(sfbs[name]["flag"])
                    self.search_options.pop(flag_index)
        event.Skip()

# end of class FindToolbar


class AttributesToolbar(wx.ToolBar):
    """Toolbar for editing cell attributes"""
        
    def __init__(self, *args, **kwargs):
        kwargs["style"] = wx.TB_FLAT | wx.TB_NODIVIDER
        self.parent = args[0]
        
        wx.ToolBar.__init__(self, *args, **kwargs)
        
        self._create_font_choice_combo()
        self._create_font_size_combo()
        self._create_font_face_buttons()
        self._create_justification_button()
        self._create_alignment_button()
        self._create_penwidth_combo()
        self._create_color_buttons()
        self._create_textrotation_spinctrl()
        
        self.Realize()
    
    # Create toolbar widgets
    # ----------------------
    
    def _create_font_choice_combo(self):
        """Creates font choice combo box"""
        
        self.fonts = get_font_list()
        self.font_choice_combo = _widgets.FontChoiceCombobox(self, \
                                    choices=self.fonts, style=wx.CB_READONLY,
                                    size=(125, -1))
        self.SetToolBitmapSize(self.font_choice_combo.GetSize())
        self.AddControl(self.font_choice_combo)
        self.Bind(wx.EVT_COMBOBOX, self.parent.OnTextFont, 
                  self.font_choice_combo)
    
    def _create_font_size_combo(self):
        """Creates font size combo box"""
        
        self.std_font_sizes = FONT_SIZES
        self.font_size_combo = wx.ComboBox(self, -1, 
                         value="10",
                         size=(60, -1),
                         choices=map(unicode, self.std_font_sizes),
                         style=wx.CB_DROPDOWN|wx.TE_PROCESS_ENTER)
        self.SetToolBitmapSize(self.font_size_combo.GetSize())
        self.AddControl(self.font_size_combo)
        self.Bind(wx.EVT_COMBOBOX, self.parent.OnTextSize, 
                  self.font_size_combo)
    
    def _create_font_face_buttons(self):
        """Creates font face buttons"""
        
        font_face_buttons = [
            ("bold_button", wx.FONTWEIGHT_BOLD, "FormatTextBold", "Bold"),
            ("italic_button", wx.FONTSTYLE_ITALIC, "FormatTextItalic", 
                "Italic"),
            ("underline_button", wx.FONTFLAG_UNDERLINED, "FormatTextUnderline", 
                "Underline"),
            ("strikethrough_button", wx.FONTFLAG_STRIKETHROUGH, 
                "FormatTextStrikethrough", "Strikethrough"),
            ("freeze_button", wx.FONTFLAG_MASK, "Freeze", "Freeze"),
            ]
            
        for name, __id, iconname, buttonname in font_face_buttons:
            bmp = wx.Bitmap(icons[iconname])
            self.SetToolBitmapSize(bmp.GetSize())
            self.AddCheckLabelTool(__id, name, bmp, shortHelp=buttonname)
            self.Bind(wx.EVT_TOOL, self.parent.OnToolClick, id=__id)
    
    def _create_justification_button(self):
        """Creates horizontal justification button"""
        
        iconnames = ["JustifyLeft", "JustifyRight"]
        bmplist = [wx.Bitmap(icons[iconname]) for iconname in iconnames]
        self.justify_tb = _widgets.BitmapToggleButton(self, bmplist)
        self.Bind(wx.EVT_BUTTON, self.parent.OnToolClick, 
                    self.justify_tb)
        self.AddControl(self.justify_tb)
    
    def _create_alignment_button(self):
        """Creates vertical alignment button"""
        
        iconnames = ["AlignTop", "AlignCenter", "AlignBottom"]
        bmplist = [wx.Bitmap(icons[iconname]) for iconname in iconnames]
        
        self.alignment_tb = _widgets.BitmapToggleButton(self, bmplist)
        self.Bind(wx.EVT_BUTTON, self.parent.OnToolClick, 
                    self.alignment_tb)
        self.AddControl(self.alignment_tb)
    
    def _create_penwidth_combo(self):
        """Create pen width combo box"""
        
        self.pen_width_combo = _widgets.PenWidthComboBox(self, 
                                choices=map(unicode, xrange(12)), \
                                style=wx.CB_READONLY, size=(50, -1))
        self.AddControl(self.pen_width_combo)
        self.Bind(wx.EVT_COMBOBOX, self.parent.OnLineWidth, 
                    self.pen_width_combo)

    
    def _create_color_buttons(self):
        """Create color choice buttons"""
        
        color_button_data = [
          ("OnLineColor", "linecolor_choice", (0, 0, 0), (30, 30), 
                                                         unichr(0x2500)),
          ("OnBGColor", "bgcolor_choice", (255, 255, 255), (30, 30), u""),
          ("OnTextColor", "textcolor_choice", (0, 0, 0), (30, 30), u"A")]
        
        for methodname, name, color, size, label in color_button_data:
            setattr(self, name, 
                csel.ColourSelect(self, -1, label, color, size = size, 
                                  style=wx.NO_BORDER))
            self.AddControl(getattr(self, name))
            method = getattr(self.parent, methodname)
            getattr(self, name).Bind(csel.EVT_COLOURSELECT, method)
    
    def _create_textrotation_spinctrl(self):
        """Create text rotation spin control"""
        
        self.rotation_spinctrl = wx.SpinCtrl(self, -1, "", size=(50, -1))
        self.rotation_spinctrl.SetRange(-179, 180)
        self.rotation_spinctrl.SetValue(0)
        
        # For compatibility with toggle buttons
        self.rotation_spinctrl.GetToolState = lambda x: None
        
        self.AddControl(self.rotation_spinctrl)
        
        self.Bind(wx.EVT_SPINCTRL, self.parent.OnToolClick, 
                    self.rotation_spinctrl)
    
    
    # Update widget state methods
    # ---------------------------
    
    def _update_textfont(self, textfont):
        """Updates text font widgets"""
        
        if textfont is None:
            textfont = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        
        font_face = textfont.FaceName
        font_size = textfont.PointSize
        font_weight = textfont.GetWeight()
        font_style = textfont.GetStyle()
        font_is_underlined = textfont.GetUnderlined()
        
        fontface_id = self.fonts.index(font_face)
        self.font_choice_combo.Select(fontface_id)
        
        try:
            fontsize_id = self.std_font_sizes.index(font_size)
        except:
            ## This is ugly. The size choice should be replaced by a combo
            fontsize_id = 0
        self.font_size_combo.Select(fontsize_id)
        
        if font_weight == wx.FONTWEIGHT_NORMAL:
            # Toggle up
            self.ToggleTool(wx.FONTWEIGHT_BOLD, 0)
        elif font_weight == wx.FONTWEIGHT_BOLD:
            # Toggle down
            self.ToggleTool(wx.FONTWEIGHT_BOLD, 1)
        else:
            print "Unknown fontweight"
        
        if font_style == wx.FONTSTYLE_NORMAL:
            # Toggle up
            self.ToggleTool(wx.FONTSTYLE_ITALIC, 0)
        elif font_style == wx.FONTSTYLE_ITALIC:
            # Toggle down
            self.ToggleTool(wx.FONTSTYLE_ITALIC, 1)
        else:
            print "Unknown fontstyle"
    
    def _update_bgbrush(self, bgbrush_data):
        """Updates background color"""
        
        try:
            brush_color = wx.Colour(255, 255, 255, 0)
            brush_color.SetRGB(bgbrush_data[0])
        except KeyError:
            brush_color = wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW)
        
        self.bgcolor_choice.SetColour(brush_color)
    
    def _update_borderpen(self, borderpen_data):
        """Updates background color"""
        
        try:
            borderpen_color = wx.Colour(255, 255, 255, 0)
            borderpen_color.SetRGB(borderpen_data[0])
            borderpen_width = borderpen_data[1]
        except KeyError:
            borderpen_color = wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW)
            borderpen_width = 0
        
        self.linecolor_choice.SetColour(borderpen_color)
        self.pen_width_combo.SetSelection(borderpen_width)
    
    def _update_frozencell(self):
        """Updates frozen cell button"""
        
        # Frozen cell information is not in the sgrid because the
        # stored results may not be pickleable.
        
        # Get selected cell's key
        
        key = self.parent.MainGrid.key
        
        # Check if cell is frozen and adjust frozen cell button
        
        if key in self.parent.MainGrid.pysgrid.frozen_cells:
            # Toggle down
            self.ToggleTool(wx.FONTFLAG_MASK, 1)
        else:
            # Toggle up
            self.ToggleTool(wx.FONTFLAG_MASK, 0)
    
    def _update_underline(self, textattributes):
        """Updates underline cell button"""
        
        try:
            underline_tag = odftags["underline"]
            underline_mode = textattributes[underline_tag]
        except KeyError:
            underline_mode = "none"
        
        if underline_mode == "continuous":
            # Toggle down
            self.ToggleTool(wx.FONTFLAG_UNDERLINED, 1)
        else:
            # Toggle up
            self.ToggleTool(wx.FONTFLAG_UNDERLINED, 0)
    

    
    def _update_justification(self, textattributes):
        """Updates horizontal text justification button"""
        
        justification_tag = odftags["justification"]
        try:
            justification = textattributes[justification_tag]
        except:
            justification = "left"
        
        if justification == "left":
            self.justify_tb.state = 1
        elif justification == "right":
            self.justify_tb.state = 0
        else:
            self.justify_tb.state = 1
        
        self.justify_tb.toggle(None)
        self.justify_tb.Refresh()
    
    def _update_alignment(self, textattributes):
        """Updates vertical text alignment button"""
        
        vert_align_tag = odftags["verticalalign"]
        try:
            vertical_align = textattributes[vert_align_tag]
        except:
            vertical_align = "top"
        
        if vertical_align == "top":
            self.alignment_tb.state = 2
        elif vertical_align == "middle":
            self.alignment_tb.state = 0
        elif vertical_align == "bottom":
            self.alignment_tb.state = 1
        else:
            self.alignment_tb.state = 2
            ##print "Vertical align tag " + vertical_align + " unknown"
        self.alignment_tb.toggle(None)
        self.alignment_tb.Refresh()
    
    def _update_fontcolor(self, textattributes):
        """Updates text font color button"""
        
        try:
            fontcolortag = odftags["fontcolor"]
            textcolor = textattributes[fontcolortag]
        except KeyError:
            textcolor = wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOWTEXT)
        self.textcolor_choice.SetColour(textcolor)
    
    def _update_strikethrough(self, textattributes):
        """Updates text strikethrough button"""
        
        try:
            strikethrough_tag = odftags["strikethrough"]
            strikethrough = textattributes[strikethrough_tag]
        except KeyError:
            strikethrough = "transparent"
        
        if strikethrough == "solid":
            self.ToggleTool(wx.FONTFLAG_STRIKETHROUGH, 1)
        else:
            self.ToggleTool(wx.FONTFLAG_STRIKETHROUGH, 0)
    
    def _update_textrotation(self, textattributes):
        """Updates text rotation spin control"""
        
        try:
            rot_angle_tag = odftags["rotationangle"]
            angle = float(textattributes[rot_angle_tag])
        except KeyError:
            angle = 0.0
        
        self.rotation_spinctrl.SetValue(angle)
    
    def update(self, borderpen_data=None, bgbrush_data=None, 
                     textattributes=None, textfont=None):
        """Updates all widgets
        
        Parameters
        ----------
        
        borderpen: wx.Pen (defaults to None)
        \tPen for cell borders
        bgbrush: wx.Brush (defaults to None), 
        \tBrush for cell background
        textattributes: Dict (defaults to None)
        \tAdditional text attributes
        textfont: wx.Font (defaults to None)
        \tText font
        
        """
        
        if textattributes is None:
            textattributes = {}
        
        self._update_textfont(textfont)
        self._update_bgbrush(bgbrush_data)
        self._update_borderpen(borderpen_data)
        
        self._update_frozencell()
        
        # Text attributes
        
        self._update_underline(textattributes)
        self._update_justification(textattributes)
        self._update_alignment(textattributes)
        self._update_fontcolor(textattributes)
        self._update_strikethrough(textattributes)
        self._update_textrotation(textattributes)
        
# end of class AttributesToolbar
