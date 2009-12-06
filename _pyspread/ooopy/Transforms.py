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
from Transformer             import files, split_tag, OOo_Tag, Transform
from Transformer             import mimetypes, namespace_by_name
from Version                 import VERSION
from copy                    import deepcopy

# counts in meta.xml
meta_counts = \
    ( 'character-count', 'image-count', 'object-count', 'page-count'
    , 'paragraph-count', 'table-count', 'word-count'
    )

class Access_Attribute (autosuper) :
    """ For performance reasons we do not specify a separate transform
        for each attribute-read or -change operation. Instead we define
        all the attribute accesses we want to perform as objects that
        follow the attribute access api and apply them all using an
        Attribute_Access in one go.
    """

    def __init__ (self, key = None, prefix = None, ** kw) :
        self.__super.__init__ (key = key, prefix = prefix, **kw)
        self.key = key
        if key :
            if not prefix :
                prefix   = self.__class__.__name__
            self.key = ':'.join ((prefix, key))
    # end def __init__

    def register (self, transformer) :
        self.transformer = transformer
    # end def register

    def use_value (self, oldval = None) :
        """ Can change the given value by returning the new value. If
            returning None or oldval the attribute stays unchanged.
        """
        raise NotImplementedError, "use_value must be defined in derived class"
    # end def use_value

# end class Access_Attribute

class Get_Attribute (Access_Attribute) :
    """ An example of not changing an attribute but only storing the
        value in the transformer
    """

    def __init__ (self, tag, attr, key, transform = None, ** kw) :
        self.__super.__init__ (key = key, **kw)
        self.tag        = tag
        self.attribute  = attr
        self.transform  = transform
    # end def __init__

    def use_value (self, oldval = None) :
        self.transformer [self.key] = oldval
        return None
    # end def use_value

# end def Get_Attribute

class Get_Max (Access_Attribute) :
    """ Get the maximum value of an attribute """

    def __init__ (self, tag, attr, key, transform = None, ** kw) :
        self.__super.__init__ (key = key, **kw)
        self.tag        = tag
        self.attribute  = attr
        self.transform  = transform
    # end def __init__

    def register (self, transformer) :
        self.__super.register (transformer)
        self.transformer [self.key] = -1
    # end def register

    def use_value (self, oldval = None) :
        if  self.transformer [self.key] < oldval :
            self.transformer [self.key] = oldval
        return None
    # end def use_value

# end def Get_Max

class Renumber (Access_Attribute) :
    """ Specifies a renumbering transform. OOo has a 'name' attribute
        for several different tags, e.g., tables, frames, sections etc.
        These names must be unique in the whole document. OOo itself
        solves this by appending a unique number to a basename for each
        element, e.g., sections are named 'Section1', 'Section2', ...
        Renumber transforms can be applied to correct the numbering
        after operations that destroy the unique numbering, e.g., after
        a mailmerge where the same document is repeatedly appended.

        The force parameter specifies if the new renumbered name should
        be inserted even if the attribute in question does not exist.
    """

    def __init__ \
        (self, tag, name = None, attr = None, start = 1, force = False) :
        self.__super.__init__ ()
        tag_ns, tag_name = split_tag (tag)
        self.tag_ns      = tag_ns
        self.tag         = tag
        self.name        = name or tag_name [0].upper () + tag_name [1:]
        self.num         = start
        self.force       = force
        self.attribute   = attr
    # end def __init__

    def register (self, transformer) :
        self.__super.register (transformer)
        if not self.attribute :
            self.attribute = OOo_Tag (self.tag_ns, 'name', transformer.mimetype)
    # end def register

    def use_value (self, oldval = None) :
        if oldval is None and not self.force :
            return
        name = "%s%d" % (self.name, self.num)
        self.num += 1
        return name
    # end def use_value

# end class Renumber

class Set_Attribute (Access_Attribute) :
    """
        Similar to the renumbering transform in that we are assigning
        new values to some attributes. But in this case we give keys
        into the Transformer dict to replace some tag attributes.
    """

    def __init__ \
        ( self
        , tag
        , attr
        , key       = None
        , transform = None
        , value     = None
        , oldvalue  = None
        , ** kw
        ) :
        self.__super.__init__ (key = key, ** kw)
        self.tag        = tag
        self.attribute  = attr
        self.transform  = transform
        self.value      = value
        self.oldvalue   = oldvalue
    # end def __init__

    def use_value (self, oldval) :
        if oldval is None :
            return None
        if self.oldvalue and oldval != self.oldvalue :
            return None
        if self.key and self.transformer.has_key (self.key) :
            return str (self.transformer [self.key])
        return self.value
    # end def use_value

# end class Set_Attribute

def set_attributes_from_dict (tag, attr, d) :
    """ Convenience function: iterate over a dict and return a list of
        Set_Attribute objects specifying replacement of attributes in
        the dictionary
    """
    return [Set_Attribute (tag, attr, oldvalue = k, value = v)
            for k,v in d.iteritems ()
           ]
# end def set_attributes_from_dict

class Reanchor (Access_Attribute) :
    """
        Similar to the renumbering transform in that we are assigning
        new values to some attributes. But in this case we want to
        relocate objects that are anchored to a page.
    """

    def __init__ (self, offset, tag, attr = None) :
        self.__super.__init__ ()
        self.offset     = int (offset)
        self.tag        = tag
        self.attribute  = attr
    # end def __init__

    def register (self, transformer) :
        self.__super.register (transformer)
        if not self.attribute :
            self.attribute = \
                OOo_Tag ('text', 'anchor-page-number', transformer.mimetype)
    # end def register

    def use_value (self, oldval) :
        if oldval is None :
            return oldval
        return "%d" % (int (oldval) + self.offset)
    # end def use_value

# end class Reanchor

#
# general transforms applicable to several .xml files
#

class Attribute_Access (Transform) :
    """
        Read or Change attributes in an OOo document.
        Can be used for renumbering, moving anchored objects, etc.
        Expects a list of attribute changer objects that follow the
        attribute changer API. This API is very simple:

        - Member function "use_value" returns the new value of an
          attribute, or if unchanged the old value
        - The attribute "tag" gives the tag for an element we are
          searching
        - The attribute "attribute" gives the name of the attribute we
          want to read or change.
        For examples of the attribute changer API, see Renumber and
        Reanchor above.
    """
    filename = 'content.xml'
    prio     = 110

    def __init__ (self, attrchangers, filename = None, ** kw) :
        self.filename     = filename or self.filename
        self.attrchangers = {}
        # allow several changers for a single tag
        self.attrchangers [None] = []
        self.changers = attrchangers
        self.__super.__init__ (** kw)
    # end def __init__

    def register (self, transformer) :
        """ Register transformer with all attrchangers. """
        self.__super.register (transformer)
        for r in self.changers :
            if r.tag not in self.attrchangers :
                self.attrchangers [r.tag] = []
            self.attrchangers [r.tag].append (r)
            r.register (transformer)
    # end def register

    def apply (self, root) :
        """ Search for all tags for which we renumber and replace name """
        for n in [root] + root.findall ('.//*') :
            changers = \
                self.attrchangers [None] + self.attrchangers.get (n.tag, [])
            for r in changers :
                nval = r.use_value (n.get (r.attribute))
                if nval is not None :
                    n.set (r.attribute, nval)
    # end def apply

# end class Attribute_Access

#
# meta.xml transforms
#

class Editinfo (Transform) :
    """
        This is an example of modifying OOo meta info (edit information,
        author, etc). We set some of the items (program that generated
        the OOo file, modification time, number of edit cyles and overall
        edit duration).  It's easy to subclass this transform and replace
        the "replace" variable (pun intended) in the derived class.
    """
    filename = 'meta.xml'
    prio     = 20
    repl     = \
        { ('meta', 'generator')        : 'OOoPy field replacement'
        , ('dc',   'date')             : time.strftime ('%Y-%m-%dT%H:%M:%S')
        , ('meta', 'editing-cycles')   : '0'
        , ('meta', 'editing-duration') : 'PT0M0S'
        }
    replace  = {}
    # iterate over all mimetypes, so this works for all known mimetypes
    # of OOo documents.
    for m in mimetypes :
        for params, value in repl.iteritems () :
            replace [OOo_Tag (mimetype = m, *params)] = value

    def apply (self, root) :
        for node in root.findall (self.oootag ('office', 'meta') + '/*') :
            if self.replace.has_key (node.tag) :
                node.text = self.replace [node.tag]
    # end def apply
# end class Editinfo

#
# settings.xml transforms
#

class Autoupdate (Transform) :
    """
        This is an example of modifying OOo settings. We set some of the
        AutoUpdate configuration items in OOo to true. We also specify
        that links should be updated when reading.

        This was originally intended to make OOo correctly display fields
        if they were changed with the Field_Replace below
        (similar to pressing F9 after loading the generated document in
        OOo). In particular I usually make spaces depend on field
        contents so that I don't have spurious spaces if a field is
        empty. Now it would be nice if OOo displayed the spaces correctly
        after loading a document (It does update the fields before
        printing, so this is only a cosmetic problem :-). This apparently
        does not work. If anybody knows how to achieve this, please let
        me know: mailto:rsc@runtux.com
    """
    filename = 'settings.xml'
    prio     = 20

    def apply (self, root) :
        config = None
        for config in root.findall \
            ( self.oootag ('office', 'settings')
            + '/'
            + self.oootag ('config', 'config-item-set')
            ) :
            name = config.get (self.oootag ('config', 'name'))
            if name == 'configuration-settings' :
                break
        for node in config.findall (self.oootag ('config', 'config-item')) :
            name = node.get (self.oootag ('config', 'name'))
            if name == 'LinkUpdateMode' :  # update when reading
                node.text = '2'
            # update fields when reading
            if name == 'FieldAutoUpdate' or name == 'ChartAutoUpdate' :
                node.text = 'true'
    # end def apply
# end class Autoupdate

#
# content.xml transforms
#

class Field_Replace (Transform) :
    """
        Takes a dict of replacement key-value pairs. The key is the name
        of a variable in OOo. Additional replacement key-value pairs may
        be specified in ** kw. Alternatively a callback mechanism for
        variable name lookups is provided. The callback function is
        given the name of a variable in OOo and is expected to return
        the replacement value or None if the variable value should not
        be replaced.
    """
    filename = 'content.xml'
    prio     = 100

    def __init__ (self, prio = None, replace = None, ** kw) :
        """ replace is something behaving like a dict or something
            callable for name lookups
        """
        self.__super.__init__ (prio, ** kw)
        self.replace  = replace or {}
        self.dict     = kw
    # end def __init__

    def apply (self, root) :
        tbody = self.find_tbody (root)
        for tag in 'variable-set', 'variable-get', 'variable-input' :
            for node in tbody.findall ('.//' + self.oootag ('text', tag)) :
                attr = 'name'
                if tag == 'text-input' :
                    attr = 'description'
                name = node.get (self.oootag ('text', attr))
                if callable (self.replace) :
                    replace = self.replace (name)
                    if replace :
                        node.text = replace
                elif name in self.replace :
                    node.text = self.replace [name]
                elif name in self.dict :
                    node.text = self.dict    [name]
    # end def apply
# end class Field_Replace

class Addpagebreak_Style (Transform) :
    """
        This transformation adds a new ad-hoc paragraph style to the
        content part of the OOo document. This is needed to be able to
        add new page breaks to an OOo document. Adding a new page break
        is then a matter of adding an empty paragraph with the given page
        break style.

        We first look through all defined paragraph styles for
        determining a new paragraph style number. Convention is P<num>
        for paragraph styles. We search the highest number and use this
        incremented by one for the new style to insert. Then we insert
        the new style and store the resulting style name in the
        transformer under the key class_name:stylename where class_name
        is our own class name.
    """
    filename = 'content.xml'
    prio     = 30
    para     = re.compile (r'P([0-9]+)')

    def apply (self, root) :
        max_style = 0
        styles = root.find (self.oootag ('office', 'automatic-styles'))
        for s in styles.findall ('./' + self.oootag ('style', 'style')) :
            m = self.para.match (s.get (self.oootag ('style', 'name'), ''))
            if m :
                num = int (m.group (1))
                if num > max_style :
                    max_style = num
        stylename = 'P%d' % (max_style + 1)
        new = SubElement \
            ( styles
            , self.oootag ('style', 'style')
            , { self.oootag ('style', 'name')              : stylename
              , self.oootag ('style', 'family')            : 'paragraph'
              , self.oootag ('style', 'parent-style-name') : 'Standard'
              }
            )
        SubElement \
            ( new
            , self.properties_tag
            , { self.oootag ('fo', 'break-after') : 'page' }
            )
        self.set ('stylename', stylename)
    # end def apply
# end class Addpagebreak_Style

class Addpagebreak (Transform) :
    """
        This transformation adds a page break to the last page of the OOo
        text. This is needed, e.g., when doing mail-merge: We append a
        page break to the tbody and then append the next page. This
        transform needs the name of the paragraph style specifying the
        page break style. Default is to use
        'Addpagebreak_Style:stylename' as the key for
        retrieving the page style. Alternatively the page style or the
        page style key can be specified in the constructor.
    """
    filename = 'content.xml'
    prio     = 50

    def __init__ (self, stylename = None, stylekey = None, ** kw) :
        self.__super.__init__ (** kw)
        self.stylename = stylename
        self.stylekey  = stylekey or 'Addpagebreak_Style:stylename'
    # end def __init__

    def apply (self, root) :
        """append to tbody e.g., <text:p text:style-name="P4"/>"""
        tbody     = self.find_tbody (root)
        stylename = self.stylename or self.transformer [self.stylekey]
        SubElement \
            ( tbody
            , self.oootag ('text', 'p')
            , { self.oootag ('text', 'style-name') : stylename }
            )
    # end def apply
# end class Addpagebreak

class Fix_OOo_Tag (Transform) :
    """
        OOo writer conditions are attributes where the *value* is
        prefixed by an XML namespace. If the ooow namespace declaration
        is not in scope, all conditions will evaluate to false. I
        consider this a bug (a violation of the ideas of XML) of OOo.
        Nevertheless to make conditions work, we insert the ooow
        namespace declaration into the top-level element.
    """
    filename = 'content.xml'
    prio     = 10000

    def apply (self, root) :
        if self.mimetype == mimetypes [1] :
            root.set ('xmlns:ooow', namespace_by_name [self.mimetype]['ooow'])
    # end def apply
# end class Fix_OOo_Tag

class _Body_Concat (Transform) :
    """ Various methods for modifying the tbody split into various pieces
        that have to keep sequence in order to not confuse OOo.
    """
    ooo_sections  = {}
    for m in mimetypes :
        ooo_sections [m] = \
            [ { OOo_Tag ('text', 'variable-decls',   m) : 1
              , OOo_Tag ('text', 'sequence-decls',   m) : 1
              , OOo_Tag ('text', 'user-field-decls', m) : 1
              , OOo_Tag ('office', 'forms',          m) : 1
              }
            , { OOo_Tag ('draw', 'frame',            m) : 1
              , OOo_Tag ('draw', 'rect',             m) : 1
              , OOo_Tag ('draw', 'text-box',         m) : 1
              }
            ]

    def _textbody (self) :
        """
            We use the office:body (OOo 1.X)/office:text (OOo 1.X)
            element as a container for various transforms...
        """
        return Element (self.textbody_tag)
    # end def _textbody

    def _divide (self, textbody) :
        """ Divide self.copy into parts that must keep their sequence.
            We use another textbody tag for storing the parts...
            Side-effect of setting self.copyparts is intended.
        """
        self.copyparts = self._textbody ()
        self.copyparts.append (self._textbody ())
        l = len (self.ooo_sections [self.mimetype])
        idx = 0
        for e in textbody :
            while idx < l :
                if e.tag in self.ooo_sections [self.mimetype][idx] :
                    break
                else :
                    self.copyparts.append (self._textbody ())
                    idx += 1
            self.copyparts [-1].append (e)
        declarations = self.copyparts [0]
        del self.copyparts [0]
        return declarations
    # end def _divide

    def divide_body (self, root) :
        cont       = root
        if cont.tag != self.oootag ('office', 'document-content') :
            cont   = root.find  (self.oootag ('office', 'document-content'))
        tbody      = cont.find  (self.oootag ('office', 'body'))
        # OOo 2.X has an office:text inside office:body that contains
        # the real text contents:
        if self.mimetype == mimetypes [1] :
            cont   = tbody
            tbody  = cont.find (self.oootag ('office', 'text'))
        idx        = cont [:].index (tbody)
        self.tbody = cont [idx] = self._textbody ()
        self.declarations = self._divide (tbody)
        self.bodyparts    = self.copyparts
    # end def divide_body

    def append_declarations (self) :
        for e in self.declarations :
            self.tbody.append (e)
    # end def append_declarations

    def append_to_body (self, cp) :
        for i in range (len (self.bodyparts)) :
            for j in cp [i] :
                self.bodyparts [i].append (j)
    # end def append_to_body

    def assemble_body (self) :
        for p in self.bodyparts :
            for e in p :
                self.tbody.append (e)
    # end def assemble_body

    def _get_meta (self, var, classname = 'Get_Attribute', prefix = "") :
        """ get page- and paragraph-count etc. meta-info """
        return int (self.transformer [':'.join ((classname, prefix + var))])
    # end def _get_meta

    def _set_meta (self, var, value, classname = 'Set_Attribute', prefix = "") :
        """ set page- and paragraph-count etc. meta-info """
        self.transformer [':'.join ((classname, prefix + var))] = str (value)
    # end def _set_meta
# end class _Body_Concat

class Mailmerge (_Body_Concat) :
    """
        This transformation is used to create a mailmerge document using
        the current document as the template. In the constructor we get
        an iterator that provides a data set for each item in the
        iteration. Elements the iterator has to provide are either
        something that follows the Mapping Type interface (it looks like
        a dict) or something that is callable and can be used for
        name-value lookups.

        A precondition for this transform is the application of the
        Addpagebreak_Style to guarantee that we know the style
        for adding a page break to the current document. Alternatively
        the stylename (or the stylekey if a different name should be used
        for lookup in the current transformer) can be given in the
        constructor.
    """
    filename = 'content.xml'
    prio     = 60

    def __init__ \
        (self, iterator, stylename = None, stylekey = None, ** kw) :
        self.__super.__init__ (** kw)
        self.iterator  = iterator
        self.stylename = stylename
        self.stylekey  = stylekey
    # end def __init__

    def apply (self, root) :
        """
            Copy old tbody, create new empty one and repeatedly append the
            new tbody.
        """
        pb = Addpagebreak \
            ( stylename   = self.stylename
            , stylekey    = self.stylekey
            , transformer = self.transformer
            )
        zi = Attribute_Access \
            ( (Get_Max (None, self.oootag ('draw', 'z-index'), 'z-index'),)
            , transformer = self.transformer
            )
        zi.apply (root)

        pagecount  = self._get_meta ('page-count')
        z_index    = self._get_meta ('z-index', classname = 'Get_Max') + 1
        ra         = Attribute_Access \
            ( ( Reanchor (pagecount, self.oootag ('draw', 'text-box'))
              , Reanchor (pagecount, self.oootag ('draw', 'rect'))
              , Reanchor (pagecount, self.oootag ('draw', 'frame'))
              , Reanchor (z_index, None, self.oootag ('draw', 'z-index'))
              )
            , transformer = self.transformer # transformer added
            )
        self.divide_body (root)
        self.bodyparts = [self._textbody () for i in self.copyparts]

        count = 0
        for i in self.iterator :
            count += 1
            fr = Field_Replace (replace = i, transformer = self.transformer)
            # add page break only to non-empty tbody
            # reanchor only after the first mailmerge
            if self.tbody : # tbody non-empty (but existing!)
                pb.apply (self.bodyparts [-1])
                ra.apply (self.copyparts)
            else :
                self.append_declarations ()
            cp = deepcopy (self.copyparts)
            fr.apply (cp)
            self.append_to_body (cp)
        # new page-count:
        for i in meta_counts :
            self._set_meta (i, count * self._get_meta (i))
        # we have added count-1 paragraphs, because each page-break is a
        # paragraph.
        p = 'paragraph-count'
        self._set_meta \
            (p, self._get_meta (p, classname = 'Set_Attribute') + (count - 1))
        self.assemble_body ()
    # end def apply
# end class Mailmerge

def tree_serialise (element, prefix = '', mimetype = mimetypes [1]) :
    """ Serialise a style-element of an OOo document (e.g., a
        style:font-decl, style:default-style, etc declaration).
        We remove the name of the style and return something that is a
        representation of the style element which can be used as a
        dictionary key.
        The serialisation format is a tuple containing the tag as the
        first item, the attributes (as key,value pairs returned by
        items()) as the second item and the following items are
        serialisations of children.
    """
    attr = dict (element.attrib)
    stylename = OOo_Tag ('style', 'name', mimetype)
    if stylename in attr : del attr [stylename]
    attr = attr.items ()
    attr.sort ()
    attr = tuple (attr)
    serial = [prefix + element.tag, attr]
    for e in element :
        serial.append (tree_serialise (e, prefix, mimetype))
    return tuple (serial)
# end def tree_serialise

class Concatenate (_Body_Concat) :
    """
        This transformation is used to create a new document from a
        concatenation of several documents.  In the constructor we get a
        list of documents to append to the master document.
    """
    prio     = 80
    style_containers = {}
    ref_attrs        = {}
    for m in mimetypes :
        style_containers.update \
            ({ OOo_Tag ('office', 'font-decls',       m) : 1
             , OOo_Tag ('office', 'font-face-decls',  m) : 1
             , OOo_Tag ('office', 'styles',           m) : 1
             , OOo_Tag ('office', 'automatic-styles', m) : 1
             , OOo_Tag ('office', 'master-styles',    m) : 1
            })
        # Cross-references in OOo document:
        # 'attribute' references another element with 'tag'.
        # If attribute names change, we must replace references, too.
        #     attribute                                :
        #     tag
        ref_attrs.update \
            ({ OOo_Tag ('style', 'parent-style-name', m) :
               OOo_Tag ('style', 'style',             m)
             , OOo_Tag ('style', 'master-page-name',  m) :
               OOo_Tag ('style', 'master-page',       m)
             , OOo_Tag ('style', 'page-layout-name',  m) : # OOo 2.X
               OOo_Tag ('style', 'page-layout',       m)
             , OOo_Tag ('style', 'page-master-name',  m) :
               OOo_Tag ('style', 'page-master',       m)
             , OOo_Tag ('text',  'style-name',        m) :
               OOo_Tag ('style', 'style',             m)
             , OOo_Tag ('draw',  'style-name',        m) :
               OOo_Tag ('style', 'style',             m)
             , OOo_Tag ('draw',  'text-style-name',   m) :
               OOo_Tag ('style', 'style',             m)
            })
    stylefiles = ['styles.xml', 'content.xml']
    oofiles    = stylefiles + ['meta.xml']

    body_decl_sections = ['variable-decl', 'sequence-decl']

    def __init__ \
        (self, * docs, ** kw) :
        self.__super.__init__ (** kw)
        self.docs = []
        for doc in docs :
            self.docs.append (OOoPy (infile = doc))
            assert (self.docs [-1].mimetype == self.docs [0].mimetype)
    # end def __init__

    def apply_all (self, trees) :
        assert (self.docs [0].mimetype == self.transformer.mimetype)
        self.serialised = {}
        self.stylenames = {}
        self.namemaps   = [{}]
        self.tab_depend = {}
        for s in self.ref_attrs.itervalues () :
            self.namemaps [0][s] = {}
        self.body_decls = {}
        for s in self.body_decl_sections :
            self.body_decls [s] = {}
        self.trees      = {}
        for f in self.oofiles :
            self.trees [f] = [trees [f].getroot ()]
        self.sections   = {}
        for f in self.stylefiles :
            self.sections [f] = {}
            for node in self.trees [f][0] :
                self.sections [f][node.tag] = node
        for d in self.docs :
            self.namemaps.append ({})
            for s in self.ref_attrs.itervalues () :
                self.namemaps [-1][s] = {}
            for f in self.oofiles :
                self.trees [f].append (d.read (f).getroot ())
        # append a pagebreak style, will be optimized away if duplicate
        pbs = Addpagebreak_Style (transformer = self.transformer)
        pbs.apply (self.trees ['content.xml'][0])
        get_attr = []
        for attr in meta_counts :
            a = self.oootag ('meta', attr)
            t = self.oootag ('meta', 'document-statistic')
            get_attr.append (Get_Attribute (t, a, 'concat-' + attr))
        zi = Attribute_Access \
            ( (Get_Max (None, self.oootag ('draw', 'z-index'), 'z-index'),)
            , transformer = self.transformer
            )
        zi.apply (self.trees ['content.xml'][0])
        self.zi = Attribute_Access \
            ( (Get_Max (None, self.oootag ('draw', 'z-index'), 'concat-z-index')
              ,
              )
            , transformer = self.transformer
            )
        self.getmeta = Attribute_Access \
            (get_attr, filename = 'meta.xml', transformer = self.transformer)
        self.pbname = self.transformer \
            [':'.join (('Addpagebreak_Style', 'stylename'))]
        for s in self.trees ['styles.xml'][0].findall \
            ('.//' + self.oootag ('style', 'default-style')) :
            if s.get (self.oootag ('style', 'family')) == 'paragraph' :
                default_style = s
                break
        self.default_properties = default_style.find \
            ('./' + self.properties_tag)
        self.set_pagestyle ()
        for f in 'styles.xml', 'content.xml' :
            self.style_merge (f)
        self.body_concat ()
    # end def apply_all

    def apply_tab_correction (self, node) :
        """ Check if node depends on a style which has corrected tabs
            if yes, insert all the default tabs *after* the maximum tab
            position in that style.
        """
        tab_stops = self.oootag ('style', 'tab-stops')
        tab_stop  = self.oootag ('style', 'tab-stop')
        tab_pos   = self.oootag ('style', 'position')
        parent    = node.get (self.oootag ('style', 'parent-style-name'))
        if parent in self.tab_depend :
            for prop in node :
                if prop.tag != self.properties_tag :
                    continue
                for sub in prop :
                    if sub.tag == tab_stops :
                        self.tab_depend [parent] = 1
                        max = 0
                        for ts in sub :
                            assert (ts.tag == tab_stop)
                            pos = float (ts.get (tab_pos) [:-2])
                            if max < pos :
                                max = pos
                        self.insert_tabs (sub, max)
    # end def apply_tab_correction

    def _attr_rename (self, idx) :
        r = sum \
            ( [ set_attributes_from_dict (None, k, self.namemaps [idx][v])
                for k,v in self.ref_attrs.iteritems ()
              ]
            , []
            )
        return Attribute_Access (r, transformer = self.transformer)
    # end def _attr_rename

    def body_concat (self) :
        count = {}
        for i in meta_counts :
            count [i] = self._get_meta (i)
        count ['z-index'] = self._get_meta \
            ('z-index', classname = 'Get_Max') + 1
        pb   = Addpagebreak \
            (stylename = self.pbname, transformer = self.transformer)
        self.divide_body (self.trees ['content.xml'][0])
        self.body_decl (self.declarations, append = 0)
        for idx in range (1, len (self.docs) + 1) :
            meta    = self.trees ['meta.xml'][idx]
            content = self.trees ['content.xml'][idx]
            tbody   = self.find_tbody (content)
            self.getmeta.apply (meta)
            self.zi.apply      (tbody)

            ra = Attribute_Access \
              ( ( Reanchor 
                    (count ['page-count'], self.oootag ('draw', 'text-box'))
                , Reanchor
                    (count ['page-count'], self.oootag ('draw', 'rect'))
                , Reanchor
                    (count ['page-count'], self.oootag ('draw', 'frame'))
                , Reanchor
                    (count ['z-index'], None, self.oootag ('draw', 'z-index'))
                )
              , transformer = self.transformer # transformer added
              )
            for i in meta_counts :
                count [i] += self._get_meta (i, prefix = 'concat-')
            count ['paragraph-count'] += 1
            count ['z-index'] += self._get_meta \
                ('z-index', classname = 'Get_Max', prefix = 'concat-') + 1
            namemap = self.namemaps [idx][self.oootag ('style', 'style')]
            tr      = self._attr_rename (idx)
            pb.apply (self.bodyparts [-1])
            tr.apply (content)
            ra.apply (content)
            declarations = self._divide (tbody)
            self.body_decl (declarations)
            self.append_to_body (self.copyparts)
        self.append_declarations ()
        self.assemble_body       ()
        for i in meta_counts :
            self._set_meta (i, count [i])
    # end def body_concat

    def body_decl (self, decl_section, append = 1) :
        for sect in self.body_decl_sections :
            s = self.declarations.find \
                ('.//' + self.oootag ('text', sect + 's'))
            d = self.body_decls [sect]
            t = self.oootag ('text', sect)
            for n in decl_section.findall ('.//' + t) :
                name = n.get (self.oootag ('text', 'name'))
                if name not in d :
                    if append and s : s.append (n)
                    d [name] = 1
    # end def body_decl

    def insert_tabs (self, element, max = 0) :
        """ Insert tab stops into the current element. Optionally after
            max = the current maximum tab-position
        """
        dist_tag = self.oootag ('style', 'tab-stop-distance')
        for k in range (1, len (self.tab_correct)) :
            if self.tab_correct [-k].isdigit() :
                break
        l    = float (self.tab_correct [:-k])
        unit = self.tab_correct [-k:]
        for ts in range (35) :
            pos = l * (ts + 1)
            if pos > max :
                SubElement \
                    ( element
                    , self.oootag ('style', 'tab-stop')
                    , { self.oootag ('style', 'position') : '%s%s' % (pos, unit)
                      }
                    )
    # end def insert_tabs

    def merge_defaultstyle (self, default_style, node) :
        assert default_style is not None
        assert node is not None
        proppath = './' + self.properties_tag
        defprops = default_style.find (proppath)
        props    = node.find          (proppath)
        sn       = self.oootag ('style', 'name')
        if props is None :
            props = Element (self.properties_tag)
        for k, v in defprops.attrib.iteritems () :
            if self.default_properties.get (k) != v and not props.get (k) :
                if k == self.oootag ('style', 'tab-stop-distance') :
                    self.tab_correct = v
                    self.tab_depend  = {node.get (sn) : 1}
                    stps = SubElement \
                        (props, self.oootag ('style', 'tab-stops'))
                    self.insert_tabs (stps)
                else :
                    props.set (k,v)
        if len (props) or props.attrib :
            node.append (props)
    # end def merge_defaultstyle

    def _newname (self, key, oldname) :
        stylenum = 0
        if (key, oldname) not in self.stylenames :
            self.stylenames [(key, oldname)] = 1
            return oldname
        newname = basename = 'Concat_%s' % oldname
        while (key, newname) in self.stylenames :
            stylenum += 1
            newname = '%s%d' % (basename, stylenum)
        self.stylenames [(key, newname)] = 1
        return newname
    # end def _newname

    def set_pagestyle (self) :
        """ For all documents: search for the first paragraph of the tbody
            and get its style. Modify this style to include a reference
            to the default page-style if it doesn't contain a reference
            to a page style. Insert the new style into the list of
            styles and modify the first paragraph to use the new page
            style.
            This procedure is necessary to make appended documents use
            their page style instead of the master page style of the
            first document.
            FIXME: We should search the style hierarchy backwards for
            the style of the first paragraph to check if there is a
            reference to a page-style somewhere and not override the
            page-style in this case. Otherwise appending complex
            documents that use a different page-style for the first page
            will not work if the page style is referenced in a style
            from which the first paragraph style derives.
        """
        for idx in range (1, len (self.docs) + 1) :
            croot  = self.trees  ['content.xml'][idx]
            sroot  = self.trees  ['styles.xml'] [idx]
            tbody  = self.find_tbody (croot)
            para   = tbody.find  ('./' + self.oootag ('text', 'p'))
            if para is None :
                para = tbody.find  ('./' + self.oootag ('text', 'list'))
            tsn    = self.oootag ('text', 'style-name')
            sname  = para.get    (tsn)
            styles = croot.find  (self.oootag ('office', 'automatic-styles'))
            ost    = sroot.find  (self.oootag ('office', 'styles'))
            mst    = sroot.find  (self.oootag ('office', 'master-styles'))
            assert mst
            assert mst [0].tag == self.oootag ('style', 'master-page')
            sntag  = self.oootag ('style', 'name')
            master = mst [0].get (sntag)
            mpn    = self.oootag ('style', 'master-page-name')
            stytag = self.oootag ('style', 'style')
            style  = None
            for s in styles :
                if s.tag == stytag :
                    # Explicit references to default style converted to
                    # explicit references to new page style.
                    if s.get (mpn) == '' :
                        s.set (mpn, master)
                    if s.get (sntag) == sname :
                        style = s
            if not style :
                for s in ost :
                    if s.tag == stytag and s.get (sntag) == sname :
                        style = s
                        break
            if style is not None and not style.get (mpn) :
                newstyle = deepcopy (style)
                # Don't register with newname: will be rewritten later
                # when appending. We assume that an original doc does
                # not already contain a style with _Concat suffix.
                newname = sname + '_Concat'
                para.set (tsn, newname)
                newstyle.set (self.oootag ('style', 'name'), newname)
                newstyle.set (mpn,                            master)
                styles.append (newstyle)
    # end def set_pagestyle

    def style_merge (self, oofile) :
        """ Loop over all the docs in our document list and look up the
            styles there. If a style matches an existing style in the
            original document, register the style name for later
            transformation if the style name in the original document
            does not match the style name in the appended document.  If
            no match is found, append style to master document and add
            to serialisation. If the style name already exists in the
            master document, a new style name is created. Names of
            parent styles are changed when appending -- this means that
            parent style names already have to be defined earlier in the
            document.

            If there is a reference to a parent style that is not yet
            defined, and the parent style is defined later, it is
            already too late, so an assertion is raised in this case.
            OOo seems to ensure declaration order of dependent styles,
            so this should not be a problem.
        """
        for idx in range (len (self.trees [oofile])) :
            namemap = self.namemaps [idx]
            root    = self.trees    [oofile][idx]
            delnode = []
            for nodeidx, node in enumerate (root) :
                if node.tag not in self.style_containers :
                    continue
                prefix = ''
                # font_decls may have same name in styles.xml and content.xml
                if node.tag == self.font_decls_tag :
                    prefix = oofile
                default_style = None
                for n in node :
                    if  (   n.tag == self.oootag ('style', 'default-style')
                        and (  n.get (self.oootag ('style', 'family'))
                            == 'paragraph'
                            )
                        ) :
                        default_style = n
                    name     = n.get (self.oootag ('style', 'name'), None)
                    if not name : continue
                    if  (   idx != 0
                        and name == 'Standard'
                        and n.get (self.oootag ('style', 'class'))  == 'text'
                        and (  n.get (self.oootag ('style', 'family'))
                            == 'paragraph'
                            )
                        ) :
                        self.merge_defaultstyle (default_style, n)
                    self.apply_tab_correction (n)
                    key = prefix + n.tag
                    if key not in namemap : namemap [key] = {}
                    tr = self._attr_rename (idx)
                    tr.apply (n)
                    sn  = tree_serialise (n, prefix, self.mimetype)
                    if sn in self.serialised :
                        newname = self.serialised [sn]
                        if name != newname :
                            assert \
                                (  name not in namemap [key]
                                or namemap [key][name] == newname
                                )
                            namemap [key][name] = newname
                            # optimize original doc: remove duplicate styles
                            if  not idx and node.tag != self.font_decls_tag :
                                pass
                                #delnode.append (nodeidx)
                    else :
                        newname = self._newname (key, name)
                        self.serialised [sn] = newname
                        if newname != name :
                            n.set (self.oootag ('style', 'name'), newname)
                            dn = self.oootag ('style', 'display-name')
                            disp_name = n.get (dn)
                            if disp_name :
                                n.set (dn, 'Concat ' + disp_name)
                            namemap [key][name] = newname
                        if idx != 0 :
                            self.sections [oofile][node.tag].append (n)
                assert not delnode or not idx
                delnode.reverse ()
                for i in delnode :
                    del node [i]
    # end style_merge
            
# end class Concatenate

def renumber_frames (mimetype) :
    return \
        [ Renumber (OOo_Tag ('draw',  'text-box', mimetype), 'Frame') # OOo 1.X
        , Renumber (OOo_Tag ('draw',  'frame',    mimetype), 'Frame') # OOo 2.X
        ]
# end def renumber_frames

def renumber_sections (mimetype) :
    return [Renumber (OOo_Tag ('text',  'section', mimetype))]
# end def renumber_sections

def renumber_tables (mimetype) :
    return [Renumber (OOo_Tag ('table', 'table', mimetype))]
# end def renumber_tables

def renumber_images (mimetype) :
    return [Renumber (OOo_Tag ('draw', 'image', mimetype))]
# end def renumber_images

def renumber_all (mimetype) :
    """ Factory function for all renumberings parameterized with
        mimetype
    """
    return Attribute_Access \
        ( renumber_frames   (mimetype)
        + renumber_sections (mimetype)
        + renumber_tables   (mimetype)
        + renumber_images   (mimetype)
        ) 
# end def renumber_all

# used to have a separate Pagecount transform -- generalized to get
# some of the meta information using an Attribute_Access transform
# and set the same information later after possibly being updated by
# other transforms. We use another naming convention here for storing
# the info retrieved from the OOo document: We use the attribute name in
# the meta-information to store (and later retrieve) the information.

def get_meta (mimetype) :
    """ Factory function for Attribute_Access to get all interesting
        meta-data
    """
    get_attr = []
    for attr in meta_counts :
        a = OOo_Tag ('meta', attr, mimetype)
        t = OOo_Tag ('meta', 'document-statistic', mimetype)
        get_attr.append (Get_Attribute (t, a, attr))
    return Attribute_Access (get_attr, prio =  20, filename = 'meta.xml')
# end def get_meta

def set_meta (mimetype) :
    """ Factory function for Attribute_Access to set all interesting
        meta-data
    """
    set_attr = []
    for attr in meta_counts :
        a = OOo_Tag ('meta', attr, mimetype)
        t = OOo_Tag ('meta', 'document-statistic', mimetype)
        set_attr.append (Set_Attribute (t, a, attr))
    return Attribute_Access (set_attr, prio = 120, filename = 'meta.xml')
# end def set_meta
