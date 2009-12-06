#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# Copyright (C) 2005 Dr. Ralf Schlatterbeck Open Source Consulting.
# Reichergasse 131, A-3411 Weidling.
# Web: http://www.runtux.com Email: office@runtux.com
# All rights reserved
# ****************************************************************************
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Library General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
# ****************************************************************************

from zipfile                 import ZipFile, ZIP_DEFLATED
from StringIO                import StringIO
try:
    from lxml.etree import ElementTree, fromstring

except ImportError :
    try :
        import xml.etree.cElementTree.ElementTree as ElementTree
        from xml.etree.cElementTree import fromstring
    except ImportError :
        try:
            import xml.etree.cElementTree as ElementTree
            from xml.etree.cElementTree import fromstring
        except ImportError :
            from elementtree.ElementTree import ElementTree, fromstring

from tempfile                import mkstemp
from Version                 import VERSION
import os

class _autosuper (type) :
    def __init__ (cls, name, bases, dict) :
        super   (_autosuper, cls).__init__ (name, bases, dict)
        setattr (cls, "_%s__super" % name, super (cls))
    # end def __init__
# end class _autosuper

class autosuper (object) :
    __metaclass__ = _autosuper
    pass
# end class autosuper

class OOoElementTree (autosuper) :
    """
        An ElementTree for OOo document XML members. Behaves like the
        orginal ElementTree (in fact it delegates almost everything to a
        real instance of ElementTree) except for the write method, that
        writes itself back to the OOo XML file in the OOo zip archive it
        came from.
    """
    def __init__ (self, ooopy, zname, root) :
        self.ooopy = ooopy
        self.zname = zname
        self.tree  = ElementTree (root)
    # end def __init__

    def write (self) :
        self.ooopy.write (self.zname, self.tree)
    # end def write

    def __getattr__ (self, name) :
        """
            Delegate everything to our ElementTree attribute.
        """
        if not name.startswith ('__') :
            result = getattr (self.tree, name)
            setattr (self, name, result)
            return result
        raise AttributeError, name
    # end def __getattr__

# end class OOoElementTree

class OOoPy (autosuper) :
    """
        Wrapper for OpenOffice.org zip files (all OOo documents are
        really zip files internally).

        from OOoPy import OOoPy
        >>> o = OOoPy (infile = 'test.sxw', outfile = 'out.sxw')
        >>> e = o.read ('content.xml')
        >>> o.mimetype
        'application/vnd.sun.xml.writer'
        >>> e.write ()
        >>> o.close ()
        >>> o = OOoPy (infile = 'test.odt')
        >>> o.mimetype
        'application/vnd.oasis.opendocument.text'
        >>> o.close ()
    """
    def __init__ \
        ( self
        , infile     = None
        , outfile    = None
        , write_mode = 'w'
        , mimetype   = None
        ) :
        """
            Open an OOo document, if no outfile is given, we open the
            file read-only. Otherwise the outfile has to be different
            from the infile -- the python ZipFile can't deal with
            read-write access. In case an outfile is given, we open it
            in "w" mode as a zip file, unless write_mode is specified
            (the only allowed case would be "a" for appending to an
            existing file, see pythons ZipFile documentation for
            details). If no infile is given, the user is responsible for
            providing all necessary files in the resulting output file.

            Note that both, infile and outfile can either be filenames
            or file-like objects (e.g. StringIO).

            The mimetype is automatically determined if an infile is
            given. If only writing is desired, the mimetype should be
            set.
        """
        assert (infile != outfile)
        self.izip = self.ozip = None
        if infile :
            self.izip    = ZipFile (infile,  'r',        ZIP_DEFLATED)
        if outfile :
            self.ozip    = ZipFile (outfile, write_mode, ZIP_DEFLATED)
            self.written = {}
        if mimetype :
            self.mimetype = mimetype
        elif self.izip :
            self.mimetype = self.izip.read ('mimetype')
    # end def __init__

    def read (self, zname) :
        """
            return an OOoElementTree object for the given OOo document
            archive member name. Currently an OOo document contains the
            following XML files::

             * content.xml: the text of the OOo document
             * styles.xml: style definitions
             * meta.xml: meta-information (author, last changed, ...)
             * settings.xml: settings in OOo
             * META-INF/manifest.xml: contents of the archive

            There is an additional file "mimetype" that always contains
            the string "application/vnd.sun.xml.writer" for OOo 1.X files
            and the string "application/vnd.oasis.opendocument.text" for
            OOo 2.X files.
        """
        assert (self.izip)
        return OOoElementTree (self, zname, fromstring (self.izip.read (zname)))
    # end def read

    def write (self, zname, etree) :
        assert (self.ozip)
        str = StringIO ()
        etree.write (str)
        self.ozip.writestr (zname, str.getvalue ())
        self.written [zname] = 1
    # end def write

    def close (self) :
        """
            Close the zip files. According to documentation of zipfile in
            the standard python lib, this has to be done to be sure
            everything is written. We copy over the not-yet written files
            from izip before closing ozip.
        """
        if self.izip and self.ozip :
            for f in self.izip.infolist () :
                if not self.written.has_key (f.filename) :
                    self.ozip.writestr (f, self.izip.read (f.filename))
        for i in self.izip, self.ozip :
            if i : i.close ()
    # end def close
# end class OOoPy
