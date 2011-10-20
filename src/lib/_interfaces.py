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
_interfaces
===========

Provides
--------

 * EVT_STATUSBAR_TEXT: Event for updating the main statusbar
 
 * SafeUnpickler: Basic security for loading pys files
 
 * sorted_keys:  Generator for sorting keys
 
 * textfont_from_string: wx textfont from given font string
 
 * sniff: Sniffs CSV dialect and header info
 * fill_numpyarray: Fills the target array
 * fill_wxgrid: Fills the target grid
 
 * is_pyme_present: Checks if pyme is installed
 * genkey: Generates gpg key
 * sign: Returns detached signature for file
 * verify: verifies stream against signature
 
 * make_string
 * make_unicode
 * make_slice
 * make_boolean
 * make_int
 * make_float
 * make_object
 * make_repr
 
 * Clipboard: Clipboard access
 * Commandline: Gets command line options and parameters
 * Digest: Converts any object to target type as goog as possible
 * Validator: Validator for text and digit TextCtrl

"""

import bz2
import cPickle as pickle
import csv
import datetime
from itertools import ifilter
import optparse
import re
import sys
import string
import types
import cStringIO as StringIO

import numpy
import wx
import wx.lib.newevent


try:
    from pyme import core, pygpgme
    import pyme.errors
except ImportError:
    pass

from config import config
from sysvars import get_default_font

def sorted_keys(keys, startkey, reverse=False):
    """Generator that yields sorted keys starting with startkey

    Parameters
    ----------

    keys: Iterable of tuple/list
    \tKey sequence that is sorted
    startkey: Tuple/list
    \tFirst key to be yielded
    reverse: Bool
    \tSort direction reversed if True

    """

    tuple_key = lambda t: t[::-1]
    if reverse:
        tuple_cmp = lambda t: t[::-1] > startkey[::-1]
    else:
        tuple_cmp = lambda t: t[::-1] < startkey[::-1]
        
    searchkeys = sorted(keys, key=tuple_key, reverse=reverse)
    searchpos = sum(1 for _ in ifilter(tuple_cmp, searchkeys))
    
    searchkeys = searchkeys[searchpos:] + searchkeys[:searchpos]
    
    for key in searchkeys:
        yield key


def sniff(csvfilepath):
    """
    Sniffs CSV dialect and header info from csvfilepath
    
    Returns a tuple of dialect and has_header
    
    """
    
    csvfile = open(csvfilepath, "rb")
    sample = csvfile.read(config["sniff_size"])
    csvfile.close()
    
    sniffer = csv.Sniffer()
    dialect = sniffer.sniff(sample)()
    has_header = sniffer.has_header(sample)
    
    return dialect, has_header

def fill_wxgrid(target, src_it, digest_types, key=(0, 0)):
    """
    Fills the target array with data from src_it at position key
    
    Parameters
    ----------
    target: numpy.array
    src_it: Iterable object
    \tThe source of the data that shall be pasted has to be iterable.
    \tThe iterable can yield iterables but iterables that are strings
    \tare always treated as values.
    digest_types: tuple of types
    \tTypes of data for each col
    key: 3-tuple of int
    \tInsertion point
    has_header: bool
    \t True if the first line shall be treated as a header line
    
    """
    
    for i, line in enumerate(src_it):
        row = i + key[0]
        if row > target.shape[0] - 1:
            break
        for j, value in enumerate(line):
            col = j + key[1]
            try:
                digest_key = digest_types[j]
            except IndexError:
                digest_key = digest_types[0]
            
            digest = Digest(acceptable_types=[digest_key])
            try:
                digest_res = repr(digest(value))
            except Exception, err:
                digest_res = str(err)
            target.SetCellValue(row, col, digest_res)

# GPG handling functions

def is_pyme_present():
    """Returns True if pyme can be imported else false"""
    
    try:
        from pyme import core
        return True
    except ImportError:
        return False

def _passphrase_callback(hint='', desc='', prev_bad=''): 
    """Callback function needed by pyme"""
    
    return config["gpg_key_passphrase"]

def _get_file_data(filename):
    """Returns pyme.core.Data object of file."""
    
    # Required because of unicode bug in pyme
    
    infile = open(filename, "rb")
    infile_content = infile.read()
    infile.close()
    
    return core.Data(string=infile_content)


def genkey():
    """Creates a new standard GPG key"""
    
    # Initialize our context.
    core.check_version(None)

    c = core.Context()
    c.set_armor(1)
    #c.set_progress_cb(callbacks.progress_stdout, None)
    
    # Check if standard key is already present
    keyname = config["gpg_key_uid"]
    c.op_keylist_start(keyname, 0)
    key = c.op_keylist_next()
    if key is None:
        # Key not present --> Create new one
        print "Generating new GPG key", keyname, \
              ". This may take some time..."
        c.op_genkey(config["gpg_key_parameters"], None, None)
        print c.op_genkey_result().fpr



def sign(filename):
    """Returns detached signature for file"""
    
    plaintext = _get_file_data(filename)
    
    ciphertext = core.Data()
    
    ctx = core.Context()

    ctx.set_armor(1)
    ctx.set_passphrase_cb(_passphrase_callback)
    
    ctx.op_keylist_start(config["gpg_key_uid"], 0)
    sigkey = ctx.op_keylist_next()
    ##print sigkey.uids[0].uid
    
    ctx.signers_clear()
    ctx.signers_add(sigkey)
    
    ctx.op_sign(plaintext, ciphertext, pygpgme.GPGME_SIG_MODE_DETACH)
    
    ciphertext.seek(0, 0)
    signature = ciphertext.read()
    
    return signature

def verify(sigfilename, filefilename=None):
    """Verifies a signature, returns True if successful else False."""
    
    c = core.Context()

    # Create Data with signed text.
    __signature = _get_file_data(sigfilename)
    
    if filefilename:
        __file = _get_file_data(filefilename)
        __plain = None
    else:
        __file = None
        __plain = core.Data()

    # Verify.
    try:
        c.op_verify(__signature, __file, __plain)
    except pyme.errors.GPGMEError:
        return False
    
    result = c.op_verify_result()
    
    # List results for all signatures. Status equal 0 means "Ok".
    validation_sucess = False
    
    for sign in result.signatures:
        if (not sign.status) and sign.validity:
            validation_sucess = True
    
    return validation_sucess

def get_font_from_data(fontdata):
    """Returns wx.Font from fontdata string"""
    
    textfont = get_default_font()
    
    if fontdata != "":
        nativefontinfo = wx.NativeFontInfo()
        nativefontinfo.FromString(fontdata)
        textfont.SetNativeFontInfo(nativefontinfo)
    
    return textfont

def get_pen_from_data(pendata):
    """Returns wx.Pen from pendata attribute list"""

    pen_color = wx.Colour()
    pen_color.SetRGB(pendata[0])
    pen = wx.Pen(pen_color, *pendata[1:])
    pen.SetJoin(wx.JOIN_MITER)
    
    return pen

def get_font_list():
    """Returns a sorted list of all system font names"""
    
    font_enum = wx.FontEnumerator()
    font_enum.EnumerateFacenames(wx.FONTENCODING_SYSTEM)
    font_list = font_enum.GetFacenames()
    font_list.sort()
    
    return font_list

def string_match(datastring, findstring, flags=None):
    """
    Returns position of findstring in datastring or None if not found.
    Flags is a list of strings. Supported strings are:
     * "MATCH_CASE": The case has to match for valid find
     * "WHOLE_WORD": The word has to be surrounded by whitespace characters
                     if in the middle of the string
     * "REG_EXP":    A regular expression is evaluated.
    
    """
    
    if type(datastring) is types.IntType: # Empty cell
        return None
    
    if flags is None:
        flags = []
    
    if "REG_EXP" in flags:
        match = re.search(findstring, datastring)
        if match is None:
            pos = -1
        else:
            pos = match.start()
    else:
        if "MATCH_CASE" not in flags:
            datastring = datastring.lower()
            findstring = findstring.lower()
        
        if "WHOLE_WORD" in flags:
            pos = -1
            for match in re.finditer(r'\b' + findstring + r'+\b', datastring):
                pos = match.start()
                break # find 1st occurrance
        else:
            pos = datastring.find(findstring)
    
    if pos == -1:
        return None
    else:
        return pos

class Clipboard(object):
    """Clipboard access

    Provides:
    ---------
    get_clipboard: Get clipboard content
    set_clipboard: Set clipboard content
    grid_paste: Inserts data into grid target

    """

    clipboard = wx.TheClipboard

    def _convert_clipboard(self, datastring=None, sep='\t'):
        """Converts data string to iterable.

        Parameters:
        -----------
        datastring: string, defaults to None
        \tThe data string to be converted.
        \tself.get_clipboard() is called if set to None
        sep: string
        \tSeparator for columns in datastring

        """

        if datastring is None:
            datastring = self.get_clipboard()

        data_it = ((ele for ele in line.split(sep)) \
                            for line in datastring.splitlines())
        return data_it

    def get_clipboard(self):
        """Returns the clipboard text content"""

        textdata = wx.TextDataObject()
        if self.clipboard.Open():
            self.clipboard.GetData(textdata)
            self.clipboard.Close()
        else:
            wx.MessageBox("Can't open the clipboard", "Error")
        return textdata.GetText()

    def set_clipboard(self, data):
        """Writes data to the clipboard"""

        error_log = []

        textdata = wx.TextDataObject()
        try:
            textdata.SetText(data)
        except UnboundLocalError, err:
            error_log.append([err, "Error converting to string"])
        if self.clipboard.Open():
            self.clipboard.SetData(textdata)
            self.clipboard.Close()
        else:
            wx.MessageBox("Can't open the clipboard", "Error")
        return error_log

# end of class Clipboard


class Commandlineparser(object):
    """
    Command line handling

    Methods:
    --------

    parse: Returns command line options and arguments as 2-tuple

    """
    
    def __init__(self):
        usage = "usage: %prog [options] [filename]"
        version = "%prog " + unicode(config["version"])

        self.parser = optparse.OptionParser(usage=usage, version=version)

        self.parser.add_option("-d", "--dimensions", type="int", nargs=3,
            dest="dimensions", default=config["grid_shape"], \
            help="Dimensions of empty grid (works only without filename) "
                 "rows, cols, tables [default: %default]")

    def parse(self):
        """
        Returns a a tuple (options, filename)

        options: The command line options
        filename: String (defaults to None)
        \tThe name of the file that is loaded on start-up

        """
        options, args = self.parser.parse_args()

        if min(options.dimensions) < 1:
            raise ValueError, "The number of cells in each dimension " + \
                              "has to be greater than 0"

        if len(args) > 1:
            raise ValueError, "Only one file may be opened at a time"
        elif len(args) == 1:
            filename = args[0]
        else:
            filename = None

        return options, filename

# end of class Commandlineparser


class Digest(object):
    """
    Maps types to types that are acceptable for target class

    The Digest class handles data of unknown type. Its objects are
    callable. They return an acceptable data type, which may be the fallback
    data type if everything else fails.

    The Digest class is intended to be subclassed by the target class.

    Parameters:
    -----------

    acceptable_types: list of types, defaults to None
    \tTypes that are acceptable for the target_class.
    \tThey are ordered highest preference first
    \tIf None, the string representation of the object is returned

    fallback_type: type, defaults to types.UnicodeType
    \t

    """

    def __init__(self, acceptable_types=None, fallback_type=None):

        if acceptable_types is None:
            acceptable_types = [None]

        self.acceptable_types = acceptable_types
        self.fallback_type = fallback_type
        
        # Type conversion functions
        
        def make_string(obj):
            """Makes a string object from any object"""
            
            if type(obj) is types.StringType:
                return obj
            
            if obj is None:
                return ""
            try:
                return str(obj)
            except Exception:
                return repr(obj)
        
        def make_unicode(obj):
            """Makes a unicode object from any object"""
            
            if type(obj) is types.UnicodeType:
                return obj
            
            if obj is None:
                return u""
            
            return unicode(obj)
        
        def make_slice(obj):
            """Makes a slice object from slice or int"""
            
            if isinstance(obj, slice):
                return obj
            
            return slice(obj, obj + 1, None)
        
        def make_date(obj):
            """Makes a date from comparable types"""
            
            from dateutil.parser import parse
            return parse(obj).date()
        
        def make_datetime(obj):
            """Makes a datetime from comparable types"""
            
            from dateutil.parser import parse
            return parse(obj)
        
        def make_time(obj):
            """Makes a time from comparable types"""
            
            from dateutil.parser import parse
            return parse(obj).time()
        
        
        def make_object(obj):
            """Returns the object"""
            
            return obj

        self.typehandlers = { \
            None: make_repr, \
            types.StringType: make_string, \
            types.UnicodeType: make_unicode, \
            types.SliceType: make_slice, \
            types.BooleanType: bool, \
            types.ObjectType: make_object, \
            types.IntType: int, \
            types.FloatType: float, \
            types.CodeType: make_object, \
            datetime.date: make_date, \
            datetime.datetime: make_datetime, \
            datetime.time: make_time, \
            }

        if self.fallback_type is not None and \
           self.fallback_type not in self.typehandlers:

            err_msg = " ".join(["Fallback type", \
                                str(self.fallback_type), \
                                "unknown."])
            raise NotImplementedError, err_msg

    def __call__(self, orig_obj):
        """Returns acceptable object"""

        errormessage = ""
        
        type_found = False
        
        for target_type in self.acceptable_types:
            if target_type in self.typehandlers:
                type_found = True
                break
        if not type_found:
            target_type = self.fallback_type
        
        try:
            acceptable_obj = self.typehandlers[target_type](orig_obj)
            return acceptable_obj
        except TypeError, err:
            errormessage += str(err)
        
        try:
            acceptable_obj = self.typehandlers[self.fallback_type](orig_obj)
            return acceptable_obj
        except TypeError, err:
            errormessage += str(err)
        
        return errormessage

# end of class Digest

ALPHA_ONLY = 1
DIGIT_ONLY = 2

class Validator(wx.PyValidator):
    def __init__(self, flag=None, pyVar=None):
        wx.PyValidator.__init__(self)
        self.flag = flag
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def TransferToWindow(self):
            return True
    def TransferFromWindow(self):
            return True

    def Clone(self):
        return Validator(self.flag)

    def Validate(self, win):
        tc = self.GetWindow()
        val = tc.GetValue()
        
        if self.flag == ALPHA_ONLY:
            for x in val:
                if x not in string.letters:
                    return False

        elif self.flag == DIGIT_ONLY:
            for x in val:
                if x not in string.digits:
                    return False

        return True


    def OnChar(self, event):
        key = event.GetKeyCode()

        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return

        if self.flag == ALPHA_ONLY and chr(key) in string.letters:
            event.Skip()
            return

        if self.flag == DIGIT_ONLY and chr(key) in string.digits:
            event.Skip()
            return

        if not wx.Validator_IsSilent():
            wx.Bell()

        # Returning without calling even.Skip eats the event
        #  before it gets to the text control
        return


# end of class Validator
