# moose.py --- 
# 
# Filename: moose.py
# Description: 
# Author: Subhasis Ray
# Maintainer: 
# Copyright (C) 2010 Subhasis Ray, all rights reserved.
# Created: Sat Mar 12 14:02:40 2011 (+0530)
# Version: 
# Last-Updated: Thu Sep 27 19:28:42 2012 (+0530)
#           By: subha
#     Update #: 2152
# URL: 
# Keywords: 
# Compatibility: 
# 
# 

# Commentary: 
# 
# 
# 
# 

# Change log:
# 
# 
# 

# Code:

import cStringIO
import warnings
import platform
import pydoc
_py3k = False
if int(platform.python_version_tuple()[0]) >= 3:
    _py3k = True
from collections import defaultdict
from . import _moose
from ._moose import *
import __main__ as main

sequence_types = [ 'vector<double>',
                   'vector<int>',
                   'vector<long>',
                   'vector<unsigned int>',
                   'vector<float>',
                   'vector<unsigned long>',
                   'vector<short>',
                   'vector<Id>',
                   'vector<ObjId>' ]
known_types = ['void',
               'char',
               'short',
               'int',
               'unsigned int',
               'double',
               'float',
               'long',
               'unsigned long',
               'string',
               'ematrix',
               'melement'] + sequence_types

######################################################################
# Special function to generate objects of the right class from
# a given path.
#
# As of 2012-08-22, element() function has been renamed to_el because
# ObjId is now called element in pymoose. This function is not
# entirely deprecated as we do not yet have a way to call the
# destFields as functions from the base class.
######################################################################

def to_el(path):
    """Return a reference to an existing object as an instance of the
    appropriate class. If path does not exist, raises NameError.

    ematrix or element can be provided in stead of path"""
    if isinstance(path, ematrix) or isinstance(path, melement):
        classObj = eval(path.class_)
    elif isinstance(path, str):
        if not _moose.exists(path):
            raise NameError('Object %s not defined' % (path))
        oid = _moose.element(path)
        classObj = eval(oid.class_)
    else:
        raise TypeError('expected argument: ematrix/element/str')
    return classObj(path)

def arrayelement(path, className='Neutral'):
    """Return a reference to an existing object as an instance of the
    right class. If path does not exist, className is used for
    creating an instance of that class with the given path"""
    warnings.warn('use element.ematrix() to retrieve its container. \
ematrix instances can be used directly for getting \
tuple of the field values of its elements.', 
                  DeprecationWarning)
    if not exists(path):
        raise NameError('Object %s not defined' % (path))
    return ematrix(path)

################################################################
# Wrappers for global functions
################################################################ 
    
def pwe():
    """Print present working element. Convenience function for GENESIS
    users."""
    print _moose.getCwe().getPath()
    
def le(el=None):
    """List elements. 
    
    Parameters
    ----------
    el: str/melement/ematrix/None
    The element or the path under which to look. If `None`, children
    of current working element are displayed.
    """
    if el is None:
        el = getCwe()[0]
    elif isinstance(el, str):
        if not exists(el):
            raise ValueError('no such element')
        el = element(el)
    elif isinstance(el, ematrix):
        el = el[0]    
    print 'Elements under', el.path
    for ch in el.children:
        print ch.path

ce = setCwe # ce is a GENESIS shorthand for change element.

def syncDataHandler(target):
    """Synchronize data handlers for target.

    Parameter:
    target -- target element or path or ematrix.
    """
    raise NotImplementedError('The implementation is not working for IntFire - goes to invalid objects. \
First fix that issue with SynBase or something in that line.')
    if isinstance(target, str):
        if not _moose.exists(target):
            raise ValueError('%s: element does not exist.' % (target))
        target = ematrix(target)
        _moose.syncDataHandler(target)

def showfield(elem, field='*', showtype=False):
    """Show the fields of the element, their data types and values in
    human readable format. Convenience function for GENESIS users.

    Parameters:

    elem: str/melement instance
    Element or path of an existing element.

    field: str
    Field to be displayed. If '*', all fields are displayed.

    showtype: bool
    If True show the data type of each field.

    """
    if isinstance(elem, str):
        if not exists(elem):
            raise ValueError('no such element')
        elem = element(elem)
    if field == '*':        
        value_field_dict = getFieldDict(elem.class_, 'valueFinfo')
        max_type_len = max([len(dtype) for dtype in list(value_field_dict.values())])
        max_field_len = max([len(dtype) for dtype in list(value_field_dict.keys())])
        print '\n[', elem.path, ']'
        for key, dtype in list(value_field_dict.items()):
            if dtype == 'bad' or key == 'this' or key == 'dummy' or key == 'me' or dtype.startswith('vector') or 'ObjId' in dtype:
                continue
            value = elem.getField(key)
            if showtype:
                typestr = dtype.ljust(max_type_len + 4)
                # The following hack is for handling both Python 2 and
                # 3. Directly putting the print command in the if/else
                # clause causes syntax error in both systems.
                print typestr,
            print key.ljust(max_field_len + 4), '=', value
    else:
        try:
            print field, '=', elem.getField(field)
        except AttributeError:
            pass # Genesis silently ignores non existent fields

def showfields(element, showtype=False):
    """Convenience function. Should be deprecated if nobody uses it."""
    warnings.warn('Deprecated. Use showfield(element, field="*", showtype=True) instead.', DeprecationWarning)
    showfield(element, field='*', showtype=showtype)
    
finfotypes = [('valueFinfo', 'value field') , 
              ('srcFinfo', 'source field'),
              ('destFinfo', 'destination field'),
              ('lookupFinfo', 'lookup field')]

# 2012-01-11 19:20:39 (+0530) Subha: checked for compatibility with dh_branch
# 2012-09-27 19:26:30 (+0530) Subha: updated for compatibility with buildQ branch
def listmsg(pymoose_object):
    """Return a list containing the incoming and outgoing messages of
    the given object."""
    obj = pymoose_object
    ret = []
    if type(pymoose_object) is type(""):
        obj = moose__.Neutral(pymoose_object)
    for msg in obj.inMsg:
        ret.append(msg)
    for msg in obj.outMsg:
        ret.append(msg)
    return ret

# 2012-01-11 19:20:39 (+0530) Subha: checked for compatibility with dh_branch
# 2012-09-27 19:26:30 (+0530) Subha: updated for compatibility with buildQ branch
def showmsg(pymoose_object):
    """Prints the incoming and outgoing messages of the given object."""
    obj = pymoose_object
    if type(pymoose_object) is type(""):
        obj = moose__.Neutral(pymoose_object)
    print 'INCOMING:'
    for msg in obj.msgIn:
        print msg.e2.path, msg.destFieldsOnE2, '<---', msg.e1.path, msg.srcFieldsOnE1
    print 'OUTGOING:'
    for msg in obj.msgOut:
        print msg.e1.path, msg.srcFieldsOnE1, '--->', msg.e2.path, msg.destFieldsOnE2

def getfielddoc(tokens, indent=''):
    """Get the documentation for field specified by
    tokens[0].tokens[1].

    tokens should be a two element list/tuple where tokens[0] is a
    MOOSE class name and tokens[1] is the field name.
    """
    assert(len(tokens) > 1)
    for ftype, rtype in finfotypes:
        cel = _moose.element('/classes/'+tokens[0])
        numfinfo = getField(cel, 'num_'+ftype, 'unsigned')
        print 'numfinfo', numfinfo
        finfo = element('/classes/%s/%s' % (tokens[0], ftype))
        for ii in range(numfinfo):
            oid = melement(finfo.getId(), 0, ii, 0)
            print oid, oid.name
            if oid.name == tokens[1]:
                return '%s%s.%s: %s - %s\n' % \
                    (indent, tokens[0], tokens[1], 
                     oid.docs, rtype)    
    raise NameError('`%s` has no field called `%s`' 
                    % (tokens[0], tokens[1]))
                    
    
def getmoosedoc(tokens):
    """Retrieve MOOSE builtin documentation for tokens.
    
    tokens is a list or tuple containing: (classname, [fieldname])"""
    indent = '    '
    docstring = cStringIO.StringIO()
    if not tokens:
        return ""
    class_path = '/classes/%s' % (tokens[0])
    if exists(class_path):
        if len(tokens) == 1:
            docstring.write('%s\n' % (Cinfo(class_path).docs))
    else:
        raise NameError('name \'%s\' not defined.' % (tokens[0]))
    class_id = ematrix('/classes/%s' % (tokens[0]))
    if len(tokens) > 1:
        docstring.write(getfielddoc(tokens))
    else:
        finfoheaders = ['* Value Fields *', 
                        '* Source Fields *',
                        '* Destination Fields *',
                        '* Lookup Fields *']
        for ftype, rname in finfotypes:
            docstring.write('\n*%s*\n' % (rname))
            numfinfo = getField(class_id[0], 'num_'+ftype, 'unsigned')
            finfo = ematrix('/classes/%s/%s' % (tokens[0], ftype))
            for ii in range(numfinfo):
                oid = melement(finfo, 0, ii, 0)
                docstring.write('%s%s: %s\n' % 
                                (indent, oid.name, oid.type))
    ret = docstring.getvalue()
    docstring.close()
    return ret

# the global pager is set from pydoc even if the user asks for paged
# help once. this is to strike a balance between GENESIS user's
# expectation of control returning to command line after printing the
# help and python user's expectation of seeing the help via more/less.
pager=None

def doc(arg, paged=False):
    """Display the documentation for class or field in a class.
    
    Parameters
    ----------
    arg: str or moose class or instance of melement or instance of ematrix

    argument can be a string specifying a moose class name and a field
    name separated by a dot. e.g., 'Neutral.name'. Prepending `moose.`
    is allowed. Thus moose.doc('moose.Neutral.name') is equivalent to
    the above.
    
    argument can also be string specifying just a moose class name or
    a moose class or a moose object (instance of melement or ematrix
    or there subclasses). In that case, the builtin documentation for
    the corresponding moose class is displayed.

    paged: bool
    
    Whether to display the docs via builtin pager or print and
    exit. If not specified, it defaults to False and moose.doc(xyz)
    will print help on xyz and return control to command line.

    """
    # There is no way to dynamically access the MOOSE docs using
    # pydoc. (using properties requires copying all the docs strings
    # from MOOSE increasing the loading time by ~3x). Hence we provide a
    # separate function.
    global pager
    if paged and pager is None:
        pager = pydoc.pager
    tokens = []
    text = ''
    if isinstance(arg, str):
        tokens = arg.split('.')
        if tokens[0] == 'moose':
            tokens = tokens[1:]
    elif isinstance(arg, type):
        tokens = [arg.__name__]
    elif isinstance(arg, melement) or isinstance(arg, ematrix):
        text = '%s: %s\n\n' % (arg.path, arg.class_)
        tokens = [arg.class_]
    if tokens:
        text += getmoosedoc(tokens)
    else:
        text += pydoc.gethelp(arg)
    if pager:
        pager(text)
    else:
        print text
                

# 
# moose.py ends here
