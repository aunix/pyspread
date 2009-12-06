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

import time
import re
try :
    from xml.etree.ElementTree   import dump, SubElement, Element, tostring
except ImportError :
    from elementtree.ElementTree import dump, SubElement, Element, tostring
from OOoPy                   import OOoPy, autosuper
from Version                 import VERSION
from copy                    import deepcopy

files    = ['content.xml', 'styles.xml', 'meta.xml', 'settings.xml']
mimetypes = \
    [ 'application/vnd.sun.xml.writer'
    , 'application/vnd.oasis.opendocument.text'
    ]
namespace_by_name = \
  { mimetypes [0] :
      { 'chart'    : "http://openoffice.org/2000/chart"
      , 'config'   : "http://openoffice.org/2001/config"
      , 'dc'       : "http://purl.org/dc/elements/1.1/"
      , 'dr3d'     : "http://openoffice.org/2000/dr3d"
      , 'draw'     : "http://openoffice.org/2000/drawing"
      , 'fo'       : "http://www.w3.org/1999/XSL/Format"
      , 'form'     : "http://openoffice.org/2000/form"
      , 'math'     : "http://www.w3.org/1998/Math/MathML"
      , 'meta'     : "http://openoffice.org/2000/meta"
      , 'number'   : "http://openoffice.org/2000/datastyle"
      , 'office'   : "http://openoffice.org/2000/office"
      , 'script'   : "http://openoffice.org/2000/script"
      , 'style'    : "http://openoffice.org/2000/style"
      , 'svg'      : "http://www.w3.org/2000/svg"
      , 'table'    : "http://openoffice.org/2000/table"
      , 'text'     : "http://openoffice.org/2000/text"
      , 'xlink'    : "http://www.w3.org/1999/xlink"
      , 'manifest' : "http://openoffice.org/2001/manifest"
      }
  , mimetypes [1] :
      { 'chart'    : "urn:oasis:names:tc:opendocument:xmlns:chart:1.0"
      , 'config'   : "urn:oasis:names:tc:opendocument:xmlns:config:1.0"
      , 'dc'       : "http://purl.org/dc/elements/1.1/"
      , 'dr3d'     : "urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0"
      , 'draw'     : "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
      , 'fo'       : "urn:oasis:names:tc:opendocument:xmlns:"
                     "xsl-fo-compatible:1.0"
      , 'form'     : "urn:oasis:names:tc:opendocument:xmlns:form:1.0"
      , 'math'     : "http://www.w3.org/1998/Math/MathML"
      , 'meta'     : "urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
      , 'number'   : "urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
      , 'office'   : "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
      , 'script'   : "urn:oasis:names:tc:opendocument:xmlns:script:1.0"
      , 'style'    : "urn:oasis:names:tc:opendocument:xmlns:style:1.0"
      , 'svg'      : "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
      , 'table'    : "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
      , 'text'     : "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
      , 'xlink'    : "http://www.w3.org/1999/xlink"
      , 'manifest' : "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"
      # OOo 1.X tags and some others:
      , 'ooo'      : "http://openoffice.org/2004/office"
      , 'ooow'     : "http://openoffice.org/2004/writer"
      , 'oooc'     : "http://openoffice.org/2004/calc"
      , 'dom'      : "http://www.w3.org/2001/xml-events"
      , 'xforms'   : "http://www.w3.org/2002/xforms"
      , 'xsd'      : "http://www.w3.org/2001/XMLSchema"
      , 'xsi'      : "http://www.w3.org/2001/XMLSchema-instance"
      }
  }

namespace_by_url = {}
for mimetype in namespace_by_name.itervalues () :
    for k, v in mimetype.iteritems () :
        if v in namespace_by_url :
            assert (namespace_by_url [v] == k)
        namespace_by_url [v] = k

def OOo_Tag (namespace, name, mimetype) :
    """Return combined XML tag"""
    return "{%s}%s" % (namespace_by_name [mimetype][namespace], name)
# end def OOo_Tag

def split_tag (tag) :
    """ Split tag into symbolic namespace and name part -- inverse
        operation of OOo_Tag.
    """
    ns, t = tag.split ('}')
    return (namespace_by_url [ns [1:]], t)
# end def split_tag

class Transform (autosuper) :
    """
        Base class for individual transforms on OOo files. An individual
        transform needs a filename variable for specifying the OOo file
        the transform should be applied to and an optional prio.
        Individual transforms are applied according to their prio
        setting, higher prio means later application of a transform.

        The filename variable must specify one of the XML files which are
        part of the OOo document (see files variable above). As
        the names imply, content.xml contains the contents of the
        document (text and ad-hoc style definitions), styles.xml contains
        the style definitions, meta.xml contains meta information like
        author, editing time, etc. and settings.xml is used to store
        OOo's settings (menu Tools->Configure).
    """
    prio = 100
    textbody_names = \
        { mimetypes [0] : 'body'
        , mimetypes [1] : 'text'
        }
    paragraph_props = \
        { mimetypes [0] : 'properties'
        , mimetypes [1] : 'paragraph-properties'
        }
    font_decls = \
        { mimetypes [0] : 'font-decls'
        , mimetypes [1] : 'font-face-decls'
        }

    def __init__ (self, prio = None, transformer = None) :
        if prio is not None :
            self.prio    = prio
        self.transformer = None
        if transformer :
            self.register (transformer)
    # end def __init__

    def apply (self, root) :
        """ Apply myself to the element given as root """
        raise NotImplementedError, 'derived transforms must implement "apply"'
    # end def apply

    def apply_all (self, trees) :
        """ Apply myself to all the files given in trees. The variable
            trees contains a dictionary of ElementTree indexed by the
            name of the OOo File.
            The standard case is that only one file (namely
            self.filename) is used.
        """
        assert (self.filename)
        self.apply (trees [self.filename].getroot ())
    # end def apply_all

    def find_tbody (self, root) :
        """ Find the node which really contains the text -- different
            for different OOo versions.
        """
        tbody = root
        if tbody.tag != self.textbody_tag :
            tbody = tbody.find ('.//' + self.textbody_tag)
        return tbody
    # end def find_tbody

    def register (self, transformer) :
        """ Registering with a transformer means being able to access
            variables stored in the tranformer by other transforms.

            Also needed for tag-computation: The transformer knows which
            version of OOo document we are processing.
        """
        self.transformer     = transformer
        mt                   = self.mimetype = transformer.mimetype
        self.textbody_name   = self.textbody_names [mt]
        self.paragraph_props = self.paragraph_props [mt]
        self.properties_tag  = self.oootag ('style', self.paragraph_props)
        self.textbody_tag    = self.oootag ('office', self.textbody_name)
        self.font_decls_tag  = self.oootag ('office', self.font_decls [mt])
    # end def register

    def oootag (self, namespace, name) :
        """ Compute long tag version """
        return OOo_Tag (namespace, name, self.mimetype)
    # end def oootag

    def set (self, variable, value) :
        """ Set variable in our transformer using naming convention. """
        self.transformer [self._varname (variable)] = value
    # end def set

    def _varname (self, name) :
        """ For fulfilling the naming convention of the transformer
            dictionary (every entry in this dictionary should be prefixed
            with the class name of the transform) we have this
            convenience method.
            Returns variable name prefixed with own class name.
        """
        return ":".join ((self.__class__.__name__, name))
    # end def _varname

# end class Transform

class Transformer (autosuper) :
    """
        Class for applying a set of transforms to a given ooopy object.
        The transforms are applied to the specified file in priority
        order. When applying transforms we have a mechanism for
        communication of transforms. We give the transformer to the
        individual transforms as a parameter. The transforms may use the
        transformer like a dictionary for storing values and retrieving
        values left by previous transforms.
        As a naming convention each transform should use its class name
        as a prefix for storing values in the dictionary.
        >>> import Transforms
        >>> from Transforms import renumber_all, get_meta, set_meta, meta_counts
        >>> from StringIO import StringIO
        >>> sio = StringIO ()
        >>> o   = OOoPy (infile = 'test.sxw', outfile = sio)
        >>> m   = o.mimetype
        >>> c = o.read ('content.xml')
        >>> body = c.find (OOo_Tag ('office', 'body', mimetype = m))
        >>> body [-1].get (OOo_Tag ('text', 'style-name', mimetype = m))
        'Standard'
        >>> def cb (name) :
        ...     r = { 'street'     : 'Beispielstrasse 42'
        ...         , 'firstname'  : 'Hugo'
        ...         , 'salutation' : 'Frau'
        ...         }
        ...     if r.has_key (name) : return r [name]
        ...     return None
        ... 
        >>> p = get_meta (m)
        >>> t = Transformer (m, p)
        >>> t ['a'] = 'a'
        >>> t ['a']
        'a'
        >>> t.transform (o)
        >>> p.set ('a', 'b')
        >>> t ['Attribute_Access:a']
        'b'
        >>> t   = Transformer (
        ...       m
        ...     , Transforms.Autoupdate ()
        ...     , Transforms.Editinfo   ()  
        ...     , Transforms.Field_Replace (prio = 99, replace = cb)
        ...     , Transforms.Field_Replace
        ...         ( replace =
        ...             { 'salutation' : ''
        ...             , 'firstname'  : 'Erika'
        ...             , 'lastname'   : 'Musterfrau'
        ...             , 'country'    : 'D' 
        ...             , 'postalcode' : '00815'
        ...             , 'city'       : 'Niemandsdorf'
        ...             }
        ...         )
        ...     , Transforms.Addpagebreak_Style ()
        ...     , Transforms.Addpagebreak       ()
        ...     )
        >>> t.transform (o)
        >>> o.close ()
        >>> ov  = sio.getvalue ()
        >>> f   = open ("testout.sxw", "wb")
        >>> f.write (ov)
        >>> f.close ()
        >>> o = OOoPy (infile = sio)
        >>> c = o.read ('content.xml')
        >>> m = o.mimetype
        >>> body = c.find (OOo_Tag ('office', 'body', mimetype = m))
        >>> vset = './/' + OOo_Tag ('text', 'variable-set', mimetype = m)
        >>> for node in body.findall (vset) :
        ...     name = node.get (OOo_Tag ('text', 'name', m))
        ...     print name, ':', node.text
        salutation : None
        firstname : Erika
        lastname : Musterfrau
        street : Beispielstrasse 42
        country : D
        postalcode : 00815
        city : Niemandsdorf
        salutation : None
        firstname : Erika
        lastname : Musterfrau
        street : Beispielstrasse 42
        country : D
        postalcode : 00815
        city : Niemandsdorf
        >>> body [-1].get (OOo_Tag ('text', 'style-name', mimetype = m))
        'P2'
        >>> sio = StringIO ()
        >>> o   = OOoPy (infile = 'test.sxw', outfile = sio)
        >>> c = o.read ('content.xml')
        >>> t   = Transformer (
        ...       o.mimetype
        ...     , get_meta (o.mimetype)
        ...     , Transforms.Addpagebreak_Style ()
        ...     , Transforms.Mailmerge
        ...       ( iterator = 
        ...         ( dict (firstname = 'Erika', lastname = 'Nobody')
        ...         , dict (firstname = 'Eric',  lastname = 'Wizard')
        ...         , cb
        ...         )
        ...       )
        ...     , renumber_all (o.mimetype)
        ...     , set_meta (o.mimetype)
        ...     , Transforms.Fix_OOo_Tag ()
        ...     )
        >>> t.transform (o)
        >>> for i in meta_counts :
        ...     print i, t [':'.join (('Set_Attribute', i))]
        character-count 951
        image-count 0
        object-count 0
        page-count 3
        paragraph-count 113
        table-count 3
        word-count 162
        >>> name = t ['Addpagebreak_Style:stylename']
        >>> name
        'P2'
        >>> o.close ()
        >>> ov  = sio.getvalue ()
        >>> f   = open ("testout2.sxw", "wb")
        >>> f.write (ov)
        >>> f.close ()
        >>> o = OOoPy (infile = sio)
        >>> m = o.mimetype
        >>> c = o.read ('content.xml')
        >>> body = c.find (OOo_Tag ('office', 'body', m))
        >>> for n in body.findall ('.//*') :
        ...     zidx = n.get (OOo_Tag ('draw', 'z-index', m))
        ...     if zidx :
        ...         print ':'.join(split_tag (n.tag)), zidx
        draw:text-box 0
        draw:rect 1
        draw:text-box 3
        draw:rect 4
        draw:text-box 6
        draw:rect 7
        draw:text-box 2
        draw:text-box 5
        draw:text-box 8
        >>> for n in body.findall ('.//' + OOo_Tag ('text', 'p', m)) :
        ...     if n.get (OOo_Tag ('text', 'style-name', m)) == name :
        ...         print n.tag
        {http://openoffice.org/2000/text}p
        {http://openoffice.org/2000/text}p
        >>> vset = './/' + OOo_Tag ('text', 'variable-set', m)
        >>> for n in body.findall (vset) :
        ...     if n.get (OOo_Tag ('text', 'name', m), None).endswith ('name') :
        ...         name = n.get (OOo_Tag ('text', 'name', m))
        ...         print name, ':', n.text
        firstname : Erika
        lastname : Nobody
        firstname : Eric
        lastname : Wizard
        firstname : Hugo
        lastname : Testman
        firstname : Erika
        lastname : Nobody
        firstname : Eric
        lastname : Wizard
        firstname : Hugo
        lastname : Testman
        >>> for n in body.findall ('.//' + OOo_Tag ('draw', 'text-box', m)) :
        ...     print n.get (OOo_Tag ('draw', 'name', m)),
        ...     print n.get (OOo_Tag ('text', 'anchor-page-number', m))
        Frame1 1
        Frame2 2
        Frame3 3
        Frame4 None
        Frame5 None
        Frame6 None
        >>> for n in body.findall ('.//' + OOo_Tag ('text', 'section', m)) :
        ...     print n.get (OOo_Tag ('text', 'name', m))
        Section1
        Section2
        Section3
        Section4
        Section5
        Section6
        Section7
        Section8
        Section9
        Section10
        Section11
        Section12
        Section13
        Section14
        Section15
        Section16
        Section17
        Section18
        >>> for n in body.findall ('.//' + OOo_Tag ('table', 'table', m)) :
        ...     print n.get (OOo_Tag ('table', 'name', m))
        Table1
        Table2
        Table3
        >>> r = o.read ('meta.xml')
        >>> meta = r.find ('.//' + OOo_Tag ('meta', 'document-statistic', m))
        >>> for i in meta_counts :
        ...     print i, repr (meta.get (OOo_Tag ('meta', i, m)))
        character-count '951'
        image-count '0'
        object-count '0'
        page-count '3'
        paragraph-count '113'
        table-count '3'
        word-count '162'
        >>> o.close ()
        >>> sio = StringIO ()
        >>> o   = OOoPy (infile = 'test.sxw', outfile = sio)
        >>> t   = Transformer (
        ...       o.mimetype
        ...     , get_meta (o.mimetype)
        ...     , Transforms.Concatenate ('test.sxw', 'rechng.sxw')
        ...     , renumber_all (o.mimetype)
        ...     , set_meta (o.mimetype)
        ...     , Transforms.Fix_OOo_Tag ()
        ...     )
        >>> t.transform (o)
        >>> for i in meta_counts :
        ...     print i, repr (t [':'.join (('Set_Attribute', i))])
        character-count '1131'
        image-count '0'
        object-count '0'
        page-count '3'
        paragraph-count '168'
        table-count '2'
        word-count '160'
        >>> o.close ()
        >>> ov  = sio.getvalue ()
        >>> f   = open ("testout3.sxw", "wb")
        >>> f.write (ov)
        >>> f.close ()
        >>> o = OOoPy (infile = sio)
        >>> m = o.mimetype
        >>> c = o.read ('content.xml')
        >>> s = o.read ('styles.xml')
        >>> for n in c.findall ('./*/*') :
        ...     name = n.get (OOo_Tag ('style', 'name', m))
        ...     if name :
        ...         parent = n.get (OOo_Tag ('style', 'parent-style-name', m))
        ...         print '"%s", "%s"' % (name, parent)
        "Tahoma1", "None"
        "Bitstream Vera Sans", "None"
        "Tahoma", "None"
        "Nimbus Roman No9 L", "None"
        "Courier New", "None"
        "Arial Black", "None"
        "New Century Schoolbook", "None"
        "Helvetica", "None"
        "Table1", "None"
        "Table1.A", "None"
        "Table1.A1", "None"
        "Table1.E1", "None"
        "Table1.A2", "None"
        "Table1.E2", "None"
        "P1", "None"
        "fr1", "Frame"
        "fr2", "None"
        "fr3", "Frame"
        "Sect1", "None"
        "gr1", "None"
        "P2", "Standard"
        "Standard_Concat", "None"
        "Concat_P1", "Concat_Frame contents"
        "Concat_P2", "Concat_Frame contents"
        "P3", "Concat_Frame contents"
        "P4", "Concat_Frame contents"
        "P5", "Concat_Standard"
        "P6", "Concat_Standard"
        "P7", "Concat_Frame contents"
        "P8", "Concat_Frame contents"
        "P9", "Concat_Frame contents"
        "P10", "Concat_Frame contents"
        "P11", "Concat_Frame contents"
        "P12", "Concat_Frame contents"
        "P13", "Concat_Frame contents"
        "P15", "Concat_Standard"
        "P16", "Concat_Standard"
        "P17", "Concat_Standard"
        "P18", "Concat_Standard"
        "P19", "Concat_Standard"
        "P20", "Concat_Standard"
        "P21", "Concat_Standard"
        "P22", "Concat_Standard"
        "P23", "Concat_Standard"
        "T1", "None"
        "Concat_fr1", "Concat_Frame"
        "Concat_fr2", "Concat_Frame"
        "Concat_fr3", "Concat_Frame"
        "fr4", "Concat_Frame"
        "fr5", "Concat_Frame"
        "fr6", "Concat_Frame"
        "Concat_Sect1", "None"
        "N0", "None"
        "N2", "None"
        "P15_Concat", "Concat_Standard"
        >>> for n in s.findall ('./*/*') :
        ...     name = n.get (OOo_Tag ('style', 'name', m))
        ...     if name :
        ...         parent = n.get (OOo_Tag ('style', 'parent-style-name', m))
        ...         print '"%s", "%s"' % (name, parent)
        "Tahoma1", "None"
        "Bitstream Vera Sans", "None"
        "Tahoma", "None"
        "Nimbus Roman No9 L", "None"
        "Courier New", "None"
        "Arial Black", "None"
        "New Century Schoolbook", "None"
        "Helvetica", "None"
        "Standard", "None"
        "Text body", "Standard"
        "List", "Text body"
        "Table Contents", "Text body"
        "Table Heading", "Table Contents"
        "Caption", "Standard"
        "Frame contents", "Text body"
        "Index", "Standard"
        "Frame", "None"
        "OLE", "None"
        "Concat_Standard", "None"
        "Concat_Text body", "Concat_Standard"
        "Concat_List", "Concat_Text body"
        "Concat_Caption", "Concat_Standard"
        "Concat_Frame contents", "Concat_Text body"
        "Concat_Index", "Concat_Standard"
        "Horizontal Line", "Concat_Standard"
        "Internet link", "None"
        "Visited Internet Link", "None"
        "Concat_Frame", "None"
        "Concat_OLE", "None"
        "pm1", "None"
        "Concat_pm1", "None"
        "Standard", "None"
        "Concat_Standard", "None"
        >>> for n in c.findall ('.//' + OOo_Tag ('text', 'variable-decl', m)) :
        ...     name = n.get (OOo_Tag ('text', 'name', m))
        ...     print name
        salutation
        firstname
        lastname
        street
        country
        postalcode
        city
        date
        invoice.invoice_no
        invoice.abo.aboprice.abotype.description
        address.salutation
        address.title
        address.firstname
        address.lastname
        address.function
        address.street
        address.country
        address.postalcode
        address.city
        invoice.subscriber.salutation
        invoice.subscriber.title
        invoice.subscriber.firstname
        invoice.subscriber.lastname
        invoice.subscriber.function
        invoice.subscriber.street
        invoice.subscriber.country
        invoice.subscriber.postalcode
        invoice.subscriber.city
        invoice.period_start
        invoice.period_end
        invoice.currency.name
        invoice.amount
        invoice.subscriber.initial
        >>> for n in c.findall ('.//' + OOo_Tag ('text', 'sequence-decl', m)) :
        ...     name = n.get (OOo_Tag ('text', 'name', m))
        ...     print name
        Illustration
        Table
        Text
        Drawing
        >>> for n in c.findall ('.//' + OOo_Tag ('text', 'p', m)) :
        ...     name = n.get (OOo_Tag ('text', 'style-name', m))
        ...     if not name or name.startswith ('Concat') :
        ...         print ">%s<" % name
        >Concat_P1<
        >Concat_P2<
        >Concat_Frame contents<
        >>> for n in c.findall ('.//' + OOo_Tag ('draw', 'text-box', m)) :
        ...     attrs = 'name', 'style-name', 'z-index'
        ...     attrs = [n.get (OOo_Tag ('draw', i, m)) for i in attrs]
        ...     attrs.append (n.get (OOo_Tag ('text', 'anchor-page-number', m)))
        ...     print attrs
        ['Frame1', 'fr1', '0', '1']
        ['Frame2', 'fr1', '3', '2']
        ['Frame3', 'Concat_fr1', '6', '3']
        ['Frame4', 'Concat_fr2', '7', '3']
        ['Frame5', 'Concat_fr3', '8', '3']
        ['Frame6', 'Concat_fr1', '9', '3']
        ['Frame7', 'fr4', '10', '3']
        ['Frame8', 'fr4', '11', '3']
        ['Frame9', 'fr4', '12', '3']
        ['Frame10', 'fr4', '13', '3']
        ['Frame11', 'fr4', '14', '3']
        ['Frame12', 'fr4', '15', '3']
        ['Frame13', 'fr5', '16', '3']
        ['Frame14', 'fr4', '18', '3']
        ['Frame15', 'fr4', '19', '3']
        ['Frame16', 'fr4', '20', '3']
        ['Frame17', 'fr6', '17', '3']
        ['Frame18', 'fr4', '23', '3']
        ['Frame19', 'fr3', '2', None]
        ['Frame20', 'fr3', '5', None]
        >>> for n in c.findall ('.//' + OOo_Tag ('text', 'section', m)) :
        ...     attrs = 'name', 'style-name'
        ...     attrs = [n.get (OOo_Tag ('text', i, m)) for i in attrs]
        ...     print attrs
        ['Section1', 'Sect1']
        ['Section2', 'Sect1']
        ['Section3', 'Sect1']
        ['Section4', 'Sect1']
        ['Section5', 'Sect1']
        ['Section6', 'Sect1']
        ['Section7', 'Concat_Sect1']
        ['Section8', 'Concat_Sect1']
        ['Section9', 'Concat_Sect1']
        ['Section10', 'Concat_Sect1']
        ['Section11', 'Concat_Sect1']
        ['Section12', 'Concat_Sect1']
        ['Section13', 'Concat_Sect1']
        ['Section14', 'Concat_Sect1']
        ['Section15', 'Concat_Sect1']
        ['Section16', 'Concat_Sect1']
        ['Section17', 'Concat_Sect1']
        ['Section18', 'Concat_Sect1']
        ['Section19', 'Concat_Sect1']
        ['Section20', 'Concat_Sect1']
        ['Section21', 'Concat_Sect1']
        ['Section22', 'Concat_Sect1']
        ['Section23', 'Concat_Sect1']
        ['Section24', 'Concat_Sect1']
        ['Section25', 'Concat_Sect1']
        ['Section26', 'Concat_Sect1']
        ['Section27', 'Concat_Sect1']
        ['Section28', 'Sect1']
        ['Section29', 'Sect1']
        ['Section30', 'Sect1']
        ['Section31', 'Sect1']
        ['Section32', 'Sect1']
        ['Section33', 'Sect1']
        >>> for n in c.findall ('.//' + OOo_Tag ('draw', 'rect', m)) :
        ...     attrs = 'style-name', 'text-style-name', 'z-index'
        ...     attrs = [n.get (OOo_Tag ('draw', i, m)) for i in attrs]
        ...     attrs.append (n.get (OOo_Tag ('text', 'anchor-page-number', m)))
        ...     print attrs
        ['gr1', 'P1', '1', '1']
        ['gr1', 'P1', '4', '2']
        >>> for n in c.findall ('.//' + OOo_Tag ('draw', 'line', m)) :
        ...     attrs = 'style-name', 'text-style-name', 'z-index'
        ...     attrs = [n.get (OOo_Tag ('draw', i, m)) for i in attrs]
        ...     print attrs
        ['gr1', 'P1', '24']
        ['gr1', 'P1', '22']
        ['gr1', 'P1', '21']
        >>> for n in s.findall ('.//' + OOo_Tag ('style', 'style', m)) :
        ...     if n.get (OOo_Tag ('style', 'name', m)).startswith ('Co') :
        ...         attrs = 'name', 'class', 'family'
        ...         attrs = [n.get (OOo_Tag ('style', i, m)) for i in attrs]
        ...         print attrs
        ...         props = n.find ('./' + OOo_Tag ('style', 'properties', m))
        ...         if props is not None and len (props) :
        ...             props [0].tag
        ['Concat_Standard', 'text', 'paragraph']
        '{http://openoffice.org/2000/style}tab-stops'
        ['Concat_Text body', 'text', 'paragraph']
        ['Concat_List', 'list', 'paragraph']
        ['Concat_Caption', 'extra', 'paragraph']
        ['Concat_Frame contents', 'extra', 'paragraph']
        ['Concat_Index', 'index', 'paragraph']
        ['Concat_Frame', None, 'graphics']
        ['Concat_OLE', None, 'graphics']
        >>> for n in c.findall ('.//*') :
        ...     zidx = n.get (OOo_Tag ('draw', 'z-index', m))
        ...     if zidx :
        ...         print ':'.join(split_tag (n.tag)), zidx
        draw:text-box 0
        draw:rect 1
        draw:text-box 3
        draw:rect 4
        draw:text-box 6
        draw:text-box 7
        draw:text-box 8
        draw:text-box 9
        draw:text-box 10
        draw:text-box 11
        draw:text-box 12
        draw:text-box 13
        draw:text-box 14
        draw:text-box 15
        draw:text-box 16
        draw:text-box 18
        draw:text-box 19
        draw:text-box 20
        draw:text-box 17
        draw:text-box 23
        draw:line 24
        draw:text-box 2
        draw:text-box 5
        draw:line 22
        draw:line 21
        >>> sio = StringIO ()
        >>> o   = OOoPy (infile = 'carta.stw', outfile = sio)
        >>> t = Transformer (
        ...     o.mimetype
        ...   , get_meta (o.mimetype)
        ...   , Transforms.Addpagebreak_Style ()
        ...   , Transforms.Mailmerge
        ...     ( iterator = 
        ...         ( dict
        ...             ( Spett = "Spettabile"
        ...             , contraente = "First person"
        ...             , indirizzo = "street? 1"
        ...             , tipo = "racc. A.C."
        ...             , luogo = "Varese"
        ...             , oggetto = "Saluti"
        ...             )
        ...         , dict
        ...             ( Spett = "Egregio"
        ...             , contraente = "Second Person"
        ...             , indirizzo = "street? 2"
        ...             , tipo = "Raccomandata"
        ...             , luogo = "Gavirate"
        ...             , oggetto = "Ossequi"
        ...             )
        ...         )
        ...     )
        ...   , renumber_all (o.mimetype)
        ...   , set_meta (o.mimetype)
        ...   , Transforms.Fix_OOo_Tag ()
        ...   )
        >>> t.transform(o)
        >>> o.close()
        >>> ov  = sio.getvalue ()
        >>> f   = open ("carta-out.stw", "wb")
        >>> f.write (ov)
        >>> f.close ()
        >>> o = OOoPy (infile = sio)
        >>> m = o.mimetype
        >>> c = o.read ('content.xml')
        >>> body = c.find (OOo_Tag ('office', 'body', mimetype = m))
        >>> vset = './/' + OOo_Tag ('text', 'variable-set', mimetype = m)
        >>> for node in body.findall (vset) :
        ...     name = node.get (OOo_Tag ('text', 'name', m))
        ...     print name, ':', node.text
        Spett : Spettabile
        contraente : First person
        indirizzo : street? 1
        Spett : Egregio
        contraente : Second Person
        indirizzo : street? 2
        tipo : racc. A.C.
        luogo : Varese
        oggetto : Saluti
        tipo : Raccomandata
        luogo : Gavirate
        oggetto : Ossequi
        >>> sio = StringIO ()
        >>> o   = OOoPy (infile = 'test.odt', outfile = sio)
        >>> t   = Transformer (
        ...       o.mimetype
        ...     , get_meta (o.mimetype)
        ...     , Transforms.Addpagebreak_Style ()
        ...     , Transforms.Mailmerge
        ...       ( iterator = 
        ...         ( dict (firstname = 'Erika', lastname = 'Nobody')
        ...         , dict (firstname = 'Eric',  lastname = 'Wizard')
        ...         , cb
        ...         )
        ...       )
        ...     , renumber_all (o.mimetype)
        ...     , set_meta (o.mimetype)
        ...     , Transforms.Fix_OOo_Tag ()
        ...     )
        >>> t.transform (o)
        >>> for i in meta_counts :
        ...     print i, t [':'.join (('Set_Attribute', i))]
        character-count 951
        image-count 0
        object-count 0
        page-count 3
        paragraph-count 53
        table-count 3
        word-count 162
        >>> name = t ['Addpagebreak_Style:stylename']
        >>> name
        'P2'
        >>> o.close ()
        >>> ov  = sio.getvalue ()
        >>> f   = open ("testout.odt", "wb")
        >>> f.write (ov)
        >>> f.close ()
        >>> o = OOoPy (infile = sio)
        >>> m = o.mimetype
        >>> c = o.read ('content.xml')
        >>> body = c.find (OOo_Tag ('office', 'body', m))
        >>> for n in body.findall ('.//*') :
        ...     zidx = n.get (OOo_Tag ('draw', 'z-index', m))
        ...     if zidx :
        ...         print ':'.join(split_tag (n.tag)), zidx
        draw:frame 0
        draw:rect 1
        draw:frame 3
        draw:rect 4
        draw:frame 6
        draw:rect 7
        draw:frame 2
        draw:frame 5
        draw:frame 8
        >>> for n in body.findall ('.//' + OOo_Tag ('text', 'p', m)) :
        ...     if n.get (OOo_Tag ('text', 'style-name', m)) == name :
        ...         print n.tag
        {urn:oasis:names:tc:opendocument:xmlns:text:1.0}p
        {urn:oasis:names:tc:opendocument:xmlns:text:1.0}p
        >>> vset = './/' + OOo_Tag ('text', 'variable-set', m)
        >>> for n in body.findall (vset) :
        ...     if n.get (OOo_Tag ('text', 'name', m), None).endswith ('name') :
        ...         name = n.get (OOo_Tag ('text', 'name', m))
        ...         print name, ':', n.text
        firstname : Erika
        lastname : Nobody
        firstname : Eric
        lastname : Wizard
        firstname : Hugo
        lastname : Testman
        firstname : Erika
        lastname : Nobody
        firstname : Eric
        lastname : Wizard
        firstname : Hugo
        lastname : Testman
        >>> for n in body.findall ('.//' + OOo_Tag ('draw', 'frame', m)) :
        ...     print n.get (OOo_Tag ('draw', 'name', m)),
        ...     print n.get (OOo_Tag ('text', 'anchor-page-number', m))
        Frame1 1
        Frame2 2
        Frame3 3
        Frame4 None
        Frame5 None
        Frame6 None
        >>> for n in body.findall ('.//' + OOo_Tag ('text', 'section', m)) :
        ...     print n.get (OOo_Tag ('text', 'name', m))
        Section1
        Section2
        Section3
        Section4
        Section5
        Section6
        Section7
        Section8
        Section9
        Section10
        Section11
        Section12
        Section13
        Section14
        Section15
        Section16
        Section17
        Section18
        >>> for n in body.findall ('.//' + OOo_Tag ('table', 'table', m)) :
        ...     print n.get (OOo_Tag ('table', 'name', m))
        Table1
        Table2
        Table3
        >>> r = o.read ('meta.xml')
        >>> meta = r.find ('.//' + OOo_Tag ('meta', 'document-statistic', m))
        >>> for i in meta_counts :
        ...     print i, repr (meta.get (OOo_Tag ('meta', i, m)))
        character-count '951'
        image-count '0'
        object-count '0'
        page-count '3'
        paragraph-count '53'
        table-count '3'
        word-count '162'
        >>> o.close ()
        >>> sio = StringIO ()
        >>> o   = OOoPy (infile = 'carta.odt', outfile = sio)
        >>> t = Transformer (
        ...     o.mimetype
        ...   , get_meta (o.mimetype)
        ...   , Transforms.Addpagebreak_Style ()
        ...   , Transforms.Mailmerge
        ...     ( iterator = 
        ...         ( dict
        ...             ( Spett = "Spettabile"
        ...             , contraente = "First person"
        ...             , indirizzo = "street? 1"
        ...             , tipo = "racc. A.C."
        ...             , luogo = "Varese"
        ...             , oggetto = "Saluti"
        ...             )
        ...         , dict
        ...             ( Spett = "Egregio"
        ...             , contraente = "Second Person"
        ...             , indirizzo = "street? 2"
        ...             , tipo = "Raccomandata"
        ...             , luogo = "Gavirate"
        ...             , oggetto = "Ossequi"
        ...             )
        ...         )
        ...     )
        ...   , renumber_all (o.mimetype)
        ...   , set_meta (o.mimetype)
        ...   , Transforms.Fix_OOo_Tag ()
        ...   )
        >>> t.transform(o)
        >>> o.close()
        >>> ov  = sio.getvalue ()
        >>> f   = open ("carta-out.odt", "wb")
        >>> f.write (ov)
        >>> f.close ()
        >>> o = OOoPy (infile = sio)
        >>> m = o.mimetype
        >>> c = o.read ('content.xml')
        >>> body = c.find (OOo_Tag ('office', 'body', mimetype = m))
        >>> vset = './/' + OOo_Tag ('text', 'variable-set', mimetype = m)
        >>> for node in body.findall (vset) :
        ...     name = node.get (OOo_Tag ('text', 'name', m))
        ...     print name, ':', node.text
        Spett : Spettabile
        contraente : First person
        indirizzo : street? 1
        Spett : Egregio
        contraente : Second Person
        indirizzo : street? 2
        tipo : racc. A.C.
        luogo : Varese
        oggetto : Saluti
        tipo : Raccomandata
        luogo : Gavirate
        oggetto : Ossequi
        >>> sio = StringIO ()
        >>> o   = OOoPy (infile = 'test.odt', outfile = sio)
        >>> t   = Transformer (
        ...       o.mimetype
        ...     , get_meta (o.mimetype)
        ...     , Transforms.Concatenate ('test.odt', 'rechng.odt')
        ...     , renumber_all (o.mimetype)
        ...     , set_meta (o.mimetype)
        ...     , Transforms.Fix_OOo_Tag ()
        ...     )
        >>> t.transform (o)
        >>> for i in meta_counts :
        ...     print i, repr (t [':'.join (('Set_Attribute', i))])
        character-count '1131'
        image-count '0'
        object-count '0'
        page-count '3'
        paragraph-count '80'
        table-count '2'
        word-count '159'
        >>> o.close ()
        >>> ov  = sio.getvalue ()
        >>> f   = open ("testout3.odt", "wb")
        >>> f.write (ov)
        >>> f.close ()
        >>> o = OOoPy (infile = sio)
        >>> m = o.mimetype
        >>> c = o.read ('content.xml')
        >>> s = o.read ('styles.xml')
        >>> for n in c.findall ('./*/*') :
        ...     name = n.get (OOo_Tag ('style', 'name', m))
        ...     if name :
        ...         parent = n.get (OOo_Tag ('style', 'parent-style-name', m))
        ...         print '"%s", "%s"' % (name, parent)
        "Tahoma1", "None"
        "Bitstream Vera Sans", "None"
        "Tahoma", "None"
        "Nimbus Roman No9 L", "None"
        "Courier New", "None"
        "Arial Black", "None"
        "New Century Schoolbook", "None"
        "Times New Roman", "None"
        "Arial", "None"
        "Helvetica", "None"
        "Table1", "None"
        "Table1.A", "None"
        "Table1.A1", "None"
        "Table1.E1", "None"
        "Table1.A2", "None"
        "Table1.E2", "None"
        "P1", "None"
        "fr1", "Frame"
        "fr2", "Frame"
        "Sect1", "None"
        "gr1", "None"
        "P2", "Standard"
        "Standard_Concat", "None"
        "Concat_P1", "Concat_Frame_20_contents"
        "Concat_P2", "Concat_Frame_20_contents"
        "P3", "Concat_Frame_20_contents"
        "P4", "Concat_Standard"
        "P5", "Concat_Standard"
        "P6", "Concat_Frame_20_contents"
        "P7", "Concat_Frame_20_contents"
        "P8", "Concat_Frame_20_contents"
        "P9", "Concat_Frame_20_contents"
        "P10", "Concat_Frame_20_contents"
        "P11", "Concat_Frame_20_contents"
        "P12", "Concat_Frame_20_contents"
        "P14", "Concat_Standard"
        "P15", "Concat_Standard"
        "P16", "Concat_Standard"
        "P17", "Concat_Standard"
        "P18", "Concat_Standard"
        "P19", "Concat_Standard"
        "P20", "Concat_Standard"
        "P21", "Concat_Standard"
        "P22", "Concat_Standard"
        "P23", "Concat_Standard"
        "Concat_fr1", "Frame"
        "Concat_fr2", "Frame"
        "fr3", "Frame"
        "fr4", "Frame"
        "fr5", "Frame"
        "fr6", "Frame"
        "Concat_gr1", "None"
        "N0", "None"
        "N2", "None"
        "P14_Concat", "Concat_Standard"
        >>> for n in c.findall ('.//' + OOo_Tag ('text', 'variable-decl', m)) :
        ...     name = n.get (OOo_Tag ('text', 'name', m))
        ...     print name
        salutation
        firstname
        lastname
        street
        country
        postalcode
        city
        date
        invoice.invoice_no
        invoice.abo.aboprice.abotype.description
        address.salutation
        address.title
        address.firstname
        address.lastname
        address.function
        address.street
        address.country
        address.postalcode
        address.city
        invoice.subscriber.salutation
        invoice.subscriber.title
        invoice.subscriber.firstname
        invoice.subscriber.lastname
        invoice.subscriber.function
        invoice.subscriber.street
        invoice.subscriber.country
        invoice.subscriber.postalcode
        invoice.subscriber.city
        invoice.period_start
        invoice.period_end
        invoice.currency.name
        invoice.amount
        invoice.subscriber.initial
        >>> for n in c.findall ('.//' + OOo_Tag ('text', 'sequence-decl', m)) :
        ...     name = n.get (OOo_Tag ('text', 'name', m))
        ...     print name
        Illustration
        Table
        Text
        Drawing
        >>> for n in c.findall ('.//' + OOo_Tag ('text', 'p', m)) :
        ...     name = n.get (OOo_Tag ('text', 'style-name', m))
        ...     if not name or name.startswith ('Concat') :
        ...         print ':'.join(split_tag (n.tag)), ">%s<" % name
        text:p >None<
        text:p >None<
        text:p >Concat_P1<
        text:p >Concat_P1<
        text:p >Concat_P2<
        text:p >Concat_P2<
        text:p >Concat_P2<
        text:p >Concat_P2<
        text:p >Concat_P2<
        text:p >Concat_P2<
        text:p >Concat_P2<
        text:p >Concat_P2<
        text:p >Concat_P2<
        text:p >Concat_P2<
        text:p >Concat_Frame_20_contents<
        text:p >None<
        text:p >None<
        text:p >None<
        >>> for n in c.findall ('.//' + OOo_Tag ('draw', 'frame', m)) :
        ...     attrs = 'name', 'style-name', 'z-index'
        ...     attrs = [n.get (OOo_Tag ('draw', i, m)) for i in attrs]
        ...     attrs.append (n.get (OOo_Tag ('text', 'anchor-page-number', m)))
        ...     print attrs
        ['Frame1', 'fr1', '0', '1']
        ['Frame2', 'fr1', '3', '2']
        ['Frame3', 'Concat_fr1', '6', '3']
        ['Frame4', 'Concat_fr2', '7', '3']
        ['Frame5', 'fr3', '8', '3']
        ['Frame6', 'Concat_fr1', '9', '3']
        ['Frame7', 'fr4', '10', '3']
        ['Frame8', 'fr4', '11', '3']
        ['Frame9', 'fr4', '12', '3']
        ['Frame10', 'fr4', '13', '3']
        ['Frame11', 'fr4', '14', '3']
        ['Frame12', 'fr4', '15', '3']
        ['Frame13', 'fr5', '16', '3']
        ['Frame14', 'fr4', '18', '3']
        ['Frame15', 'fr4', '19', '3']
        ['Frame16', 'fr4', '20', '3']
        ['Frame17', 'fr6', '17', '3']
        ['Frame18', 'fr4', '23', '3']
        ['Frame19', 'fr2', '2', None]
        ['Frame20', 'fr2', '5', None]
        >>> for n in c.findall ('.//' + OOo_Tag ('text', 'section', m)) :
        ...     attrs = 'name', 'style-name'
        ...     attrs = [n.get (OOo_Tag ('text', i, m)) for i in attrs]
        ...     print attrs
        ['Section1', 'Sect1']
        ['Section2', 'Sect1']
        ['Section3', 'Sect1']
        ['Section4', 'Sect1']
        ['Section5', 'Sect1']
        ['Section6', 'Sect1']
        ['Section7', 'Sect1']
        ['Section8', 'Sect1']
        ['Section9', 'Sect1']
        ['Section10', 'Sect1']
        ['Section11', 'Sect1']
        ['Section12', 'Sect1']
        ['Section13', 'Sect1']
        ['Section14', 'Sect1']
        ['Section15', 'Sect1']
        ['Section16', 'Sect1']
        ['Section17', 'Sect1']
        ['Section18', 'Sect1']
        ['Section19', 'Sect1']
        ['Section20', 'Sect1']
        ['Section21', 'Sect1']
        ['Section22', 'Sect1']
        ['Section23', 'Sect1']
        ['Section24', 'Sect1']
        ['Section25', 'Sect1']
        ['Section26', 'Sect1']
        ['Section27', 'Sect1']
        ['Section28', 'Sect1']
        ['Section29', 'Sect1']
        ['Section30', 'Sect1']
        ['Section31', 'Sect1']
        ['Section32', 'Sect1']
        ['Section33', 'Sect1']
        >>> for n in c.findall ('.//' + OOo_Tag ('draw', 'rect', m)) :
        ...     attrs = 'style-name', 'text-style-name', 'z-index'
        ...     attrs = [n.get (OOo_Tag ('draw', i, m)) for i in attrs]
        ...     attrs.append (n.get (OOo_Tag ('text', 'anchor-page-number', m)))
        ...     print attrs
        ['gr1', 'P1', '1', '1']
        ['gr1', 'P1', '4', '2']
        >>> for n in c.findall ('.//' + OOo_Tag ('draw', 'line', m)) :
        ...     attrs = 'style-name', 'text-style-name', 'z-index'
        ...     attrs = [n.get (OOo_Tag ('draw', i, m)) for i in attrs]
        ...     print attrs
        ['Concat_gr1', 'P1', '24']
        ['Concat_gr1', 'P1', '22']
        ['Concat_gr1', 'P1', '21']
        >>> for n in s.findall ('.//' + OOo_Tag ('style', 'style', m)) :
        ...     if n.get (OOo_Tag ('style', 'name', m)).startswith ('Co') :
        ...         attrs = 'name', 'display-name', 'class', 'family'
        ...         attrs = [n.get (OOo_Tag ('style', i, m)) for i in attrs]
        ...         print attrs
        ...         props = n.find ('./' + OOo_Tag ('style', 'properties', m))
        ...         if props is not None and len (props) :
        ...             props [0].tag
        ['Concat_Standard', None, 'text', 'paragraph']
        ['Concat_Text_20_body', 'Concat Text body', 'text', 'paragraph']
        ['Concat_List', None, 'list', 'paragraph']
        ['Concat_Caption', None, 'extra', 'paragraph']
        ['Concat_Frame_20_contents', 'Concat Frame contents', 'extra', 'paragraph']
        ['Concat_Index', None, 'index', 'paragraph']
        >>> for n in c.findall ('.//*') :
        ...     zidx = n.get (OOo_Tag ('draw', 'z-index', m))
        ...     if zidx :
        ...         print ':'.join(split_tag (n.tag)), zidx
        draw:frame 0
        draw:rect 1
        draw:frame 3
        draw:rect 4
        draw:frame 6
        draw:frame 7
        draw:frame 8
        draw:frame 9
        draw:frame 10
        draw:frame 11
        draw:frame 12
        draw:frame 13
        draw:frame 14
        draw:frame 15
        draw:frame 16
        draw:frame 18
        draw:frame 19
        draw:frame 20
        draw:frame 17
        draw:frame 23
        draw:line 24
        draw:frame 2
        draw:frame 5
        draw:line 22
        draw:line 21
        >>> from os import system
        >>> system ('python ./ooo_fieldreplace -i test.odt -o testout.odt '
        ...         'salutation=Frau firstname=Erika lastname=Musterfrau '
        ...         'country=D postalcode=00815 city=Niemandsdorf '
        ...         'street="Beispielstrasse 42"')
        0
        >>> o = OOoPy (infile = 'testout.odt')
        >>> c = o.read ('content.xml')
        >>> m = o.mimetype
        >>> body = c.find (OOo_Tag ('office', 'body', mimetype = m))
        >>> vset = './/' + OOo_Tag ('text', 'variable-set', mimetype = m)
        >>> for node in body.findall (vset) :
        ...     name = node.get (OOo_Tag ('text', 'name', m))
        ...     print name, ':', node.text
        salutation : Frau
        firstname : Erika
        lastname : Musterfrau
        street : Beispielstrasse 42
        country : D
        postalcode : 00815
        city : Niemandsdorf
        salutation : Frau
        firstname : Erika
        lastname : Musterfrau
        street : Beispielstrasse 42
        country : D
        postalcode : 00815
        city : Niemandsdorf
        >>> o.close ()
        >>> system ("./ooo_mailmerge -o testout.odt -d, carta.odt x.csv")
        0
        >>> o = OOoPy (infile = 'testout.odt')
        >>> m = o.mimetype
        >>> c = o.read ('content.xml')
        >>> body = c.find (OOo_Tag ('office', 'body', mimetype = m))
        >>> vset = './/' + OOo_Tag ('text', 'variable-set', mimetype = m)
        >>> for node in body.findall (vset) :
        ...     name = node.get (OOo_Tag ('text', 'name', m))
        ...     print name, ':', node.text
        Spett : Spettabile
        contraente : First person
        indirizzo : street? 1
        Spett : Egregio
        contraente : Second Person
        indirizzo : street? 2
        tipo : racc. A.C.
        luogo : Varese
        oggetto : Saluti
        tipo : Raccomandata
        luogo : Gavirate
        oggetto : Ossequi
        >>> o.close ()
    """
    def __init__ (self, mimetype, *tf) :
        assert (mimetype in mimetypes)
        self.mimetype     = mimetype
        self.transforms   = {}
        for t in tf :
            self.insert (t)
        self.dictionary   = {}
        self.has_key      = self.dictionary.has_key
        self.__contains__ = self.has_key
    # end def __init__

    def insert (self, transform) :
        """Insert a new transform"""
        t = transform
        if t.prio not in self.transforms :
            self.transforms [t.prio] = []
        self.transforms [t.prio].append (t)
        t.register (self)
    # end def append

    def transform (self, ooopy) :
        """
            Apply all the transforms in priority order.
            Priority order is global over all transforms.
        """
        self.trees = {}
        for f in files :
            self.trees [f] = ooopy.read (f)
        #self.dictionary = {} # clear dict when transforming another ooopy
        prios = self.transforms.keys ()
        prios.sort ()
        for p in prios :
            for t in self.transforms [p] :
                t.apply_all (self.trees)
        for e in self.trees.itervalues () :
            e.write ()
    # end def transform

    def __getitem__ (self, key) :
        return self.dictionary [key]
    # end def __getitem__

    def __setitem__ (self, key, value) :
        self.dictionary [key] = value
    # end def __setitem__
# end class Transformer
