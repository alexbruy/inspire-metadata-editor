# -*- coding: ISO-8859-15 -*-
# =============================================================================
# Copyright (c) 2008 Tom Kralidis
#
# Authors : Tom Kralidis <tomkralidis@gmail.com>
#
# Contact email: tomkralidis@gmail.com
# =============================================================================

from __future__ import (absolute_import, division, print_function)

import sys
from dateutil import parser
from datetime import datetime
import pytz
from .etree import etree, ParseError
from .namespaces import Namespaces
try:                    # Python 3
    from urllib.parse import urlsplit, urlencode
except ImportError:     # Python 2
    from urlparse import urlsplit
    from urllib import urlencode

try:
    from StringIO import StringIO  # Python 2
    BytesIO = StringIO
except ImportError:
    from io import StringIO, BytesIO  # Python 3

import cgi
import re
from copy import deepcopy
import warnings
import time
import six
#import requests

# Infinite DateTimes for Python.  Used in SWE 2.0 and other OGC specs as "INF" and "-INF"
class InfiniteDateTime(object):
    def __lt__(self, other):
        return False
    def __gt__(self, other):
        return True
    def timetuple(self):
        return tuple()
class NegativeInfiniteDateTime(object):
    def __lt__(self, other):
        return True
    def __gt__(self, other):
        return False
    def timetuple(self):
        return tuple()


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')
def format_string(prop_string):
    """
        Formats a property string to remove spaces and go from CamelCase to pep8
        from: http://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-camel-case
    """
    if prop_string is None:
        return ''
    st_r = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', prop_string)
    st_r = st_r.replace(' ','')
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', st_r).lower()

def xml_to_dict(root, prefix=None, depth=1, diction=None):
    """
        Recursively iterates through an xml element to convert each element in the tree to a (key,val). Where key is the element
        tag and val is the inner-text of the element. Note that this recursively go through the tree until the depth specified.

        Parameters
        ===========
        :root - root xml element, starting point of iteration
        :prefix - a string to prepend to the resulting key (optional)
        :depth - the number of depths to process in the tree (optional)
        :diction - the dictionary to insert the (tag,text) pairs into (optional)

        Return
        =======
        Dictionary of (key,value); where key is the element tag stripped of namespace and cleaned up to be pep8 and
        value is the inner-text of the element. Note that duplicate elements will be replaced by the last element of the 
        same tag in the tree.
    """
    ret = diction if diction is not None else dict()
    for child in root:
        val = testXMLValue(child)
        # skip values that are empty or None
        if val is None or val == '':
            if depth > 1:
                ret = xml_to_dict(child,prefix=prefix,depth=(depth-1),diction=ret)
            continue

        key = format_string(child.tag.split('}')[-1])

        if prefix is not None:
            key = prefix + key

        ret[key] = val
        if depth > 1:
            ret = xml_to_dict(child,prefix=prefix,depth=(depth-1),diction=ret)

    return ret

#default namespace for nspath is OWS common
OWS_NAMESPACE = 'http://www.opengis.net/ows/1.1'
def nspath(path, ns=OWS_NAMESPACE):

    """

    Prefix the given path with the given namespace identifier.
    
    Parameters
    ----------

    - path: ElementTree API Compatible path expression
    - ns: the XML namespace URI.

    """

    if ns is None or path is None:
        return -1

    components = []
    for component in path.split('/'):
        if component != '*':
            component = '{%s}%s' % (ns, component)
        components.append(component)
    return '/'.join(components)

def nspath_eval(xpath, namespaces):
    ''' Return an etree friendly xpath '''
    out = []
    for chunks in xpath.split('/'):
        namespace, element = chunks.split(':')
        out.append('{%s}%s' % (namespaces[namespace], element))
    return '/'.join(out)

def cleanup_namespaces(element):
    """ Remove unused namespaces from an element """
    if etree.__name__ == 'lxml.etree':
        etree.cleanup_namespaces(element)
        return element
    else:
        return etree.fromstring(etree.tostring(element))


def add_namespaces(root, ns_keys):
    if isinstance(ns_keys, six.string_types):
        ns_keys = [ns_keys]

    namespaces = Namespaces()

    ns_keys = [(x, namespaces.get_namespace(x)) for x in ns_keys]

    if etree.__name__ != 'lxml.etree':
        # We can just add more namespaces when not using lxml.
        # We can't re-add an existing namespaces.  Get a list of current
        # namespaces in use
        existing_namespaces = set()
        for elem in root.getiterator():
            if elem.tag[0] == "{":
                uri, tag = elem.tag[1:].split("}")
                existing_namespaces.add(namespaces.get_namespace_from_url(uri))
        for key, link in ns_keys:
            if link is not None and key not in existing_namespaces:
                root.set("xmlns:%s" % key, link)
        return root
    else:
        # lxml does not support setting xmlns attributes
        # Update the elements nsmap with new namespaces
        new_map = root.nsmap
        for key, link in ns_keys:
            if link is not None:
                new_map[key] = link
        # Recreate the root element with updated nsmap
        new_root = etree.Element(root.tag, nsmap=new_map)
        # Carry over attributes
        for a, v in list(root.items()):
            new_root.set(a, v)
        # Carry over children
        for child in root:
            new_root.append(deepcopy(child))
        return new_root


def getXMLInteger(elem, tag):
    """
    Return the text within the named tag as an integer.

    Raises an exception if the tag cannot be found or if its textual
    value cannot be converted to an integer.

    Parameters
    ----------

    - elem: the element to search within
    - tag: the name of the tag to look for

    """
    e = elem.find(tag)
    if e is None:
        raise ValueError('Missing %s in %s' % (tag, elem))
    return int(e.text.strip())


def testXMLValue(val, attrib=False):
    """

    Test that the XML value exists, return val.text, else return None

    Parameters
    ----------

    - val: the value to be tested

    """

    if val is not None:
        if attrib:
            return val.strip()
        elif val.text:  
            return val.text.strip()
        else:
            return None	
    else:
        return None

def testXMLAttribute(element, attribute):
    """

    Test that the XML element and attribute exist, return attribute's value, else return None

    Parameters
    ----------

    - element: the element containing the attribute
    - attribute: the attribute name

    """
    if element is not None:
        return element.get(attribute)

    return None

def element_to_string(element, encoding=None, xml_declaration=False):
    """
    Returns a string from a XML object

    Parameters
    ----------
    - element: etree Element
    - encoding (optional): encoding in string form. 'utf-8', 'ISO-8859-1', etc.
    - xml_declaration (optional): whether to include xml declaration

    """

    output = None

    if encoding is None:
        encoding = "ISO-8859-1"

    if etree.__name__ == 'lxml.etree':
        if xml_declaration:
            if encoding in ['unicode', 'utf-8']:
                output = '<?xml version="1.0" encoding="utf-8" standalone="no"?>\n%s' % \
                       etree.tostring(element, encoding='unicode')
            else:
                output = etree.tostring(element, encoding=encoding, xml_declaration=True)
        else:
                output = etree.tostring(element)
    else:
        if xml_declaration:
            output = '<?xml version="1.0" encoding="%s" standalone="no"?>\n%s' % (encoding,
                   etree.tostring(element, encoding=encoding))
        else:
            output = etree.tostring(element)

    return output


def xml2string(xml):
    """

    Return a string of XML object

    Parameters
    ----------

    - xml: xml string

    """
    warnings.warn("DEPRECIATION WARNING!  You should now use the 'element_to_string' method \
                   The 'xml2string' method will be removed in a future version of OWSLib.")
    return '<?xml version="1.0" encoding="ISO-8859-1" standalone="no"?>\n' + xml

def xmlvalid(xml, xsd):
    """

    Test whether an XML document is valid

    Parameters
    ----------

    - xml: XML content
    - xsd: pointer to XML Schema (local file path or URL)

    """

    xsd1 = etree.parse(xsd)
    xsd2 = etree.XMLSchema(xsd1)

    doc = etree.parse(StringIO(xml))
    return xsd2.validate(doc)

def xmltag_split(tag):
    ''' Return XML element bare tag name (without prefix) '''
    try:
        return tag.split('}')[1]
    except:
        return tag

def getNamespace(element):
        return ""

def dump(obj, prefix=''):
    '''Utility function to print to standard output a generic object with all its attributes.'''

    print("%s %s.%s : %s" % (prefix, obj.__module__, obj.__class__.__name__, obj.__dict__))

def getTypedValue(type, value):
    ''' Utility function to cast a string value to the appropriate XSD type. '''
    
    if type=='boolean':
       return bool(value)
    elif type=='integer':
       return int(value)
    elif type=='float':
        return float(value)
    elif type=='string':
        return str(value)
    else:
        return value # no type casting


def extract_time(element):
    ''' return a datetime object based on a gml text string

ex:
<gml:beginPosition>2006-07-27T21:10:00Z</gml:beginPosition>
<gml:endPosition indeterminatePosition="now"/>

If there happens to be a strange element with both attributes and text,
use the text.
ex: <gml:beginPosition indeterminatePosition="now">2006-07-27T21:10:00Z</gml:beginPosition>
Would be 2006-07-27T21:10:00Z, not 'now'

'''
    if element is None:
        return None

    try:
        dt = parser.parse(element.text)
    except Exception:
        att = testXMLValue(element.attrib.get('indeterminatePosition'), True)
        if att and att == 'now':
            dt = datetime.utcnow()
            dt.replace(tzinfo=pytz.utc)
        else:
            dt = None
    return dt


def extract_xml_list(elements):
    """
Some people don't have seperate tags for their keywords and seperate them with
a newline. This will extract out all of the keywords correctly.
"""
    keywords = [re.split(r'[\n\r]+',f.text) for f in elements if f.text]
    flattened = [item.strip() for sublist in keywords for item in sublist]
    remove_blank = [_f for _f in flattened if _f]
    return remove_blank

import logging
# Null logging handler
try:
    # Python 2.7
    NullHandler = logging.NullHandler
except AttributeError:
    # Python < 2.7
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
log = logging.getLogger('owslib')
log.addHandler(NullHandler())

# OrderedDict
try:  # 2.7
    from collections import OrderedDict
except:  # 2.6
    from ordereddict import OrderedDict


