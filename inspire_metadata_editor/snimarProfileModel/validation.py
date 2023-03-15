# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarProfileModel/validation.py
#  Authors: Pedro Dias, Eduardo Castanho, Joana Teixeira
#  Date:    2015-08-11T16:14:20
#
# ---------------------------------------------------------------------------
#
#  XML metadata editor plugin for QGIS developed for the SNIMar Project.
#  Copyright (C) 2015  Eduardo Castanho, Pedro Dias, Joana Teixeira
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from __future__ import print_function
from __future__ import absolute_import
import os
import platform
from . import snimarProfileModel
from EditorMetadadosMarswInforbiomares.libs.owslib.etree import etree


def validate(filename):
    """Validate a xml metadata file. Receives a string with the filename"""
    if not verify_md_metadata(filename):
        return None

    md = load_metadata(filename)
    if md.hierarchy not in ["dataset", "series", "service"]:
        md = None
    return md


def verify_md_metadata(filename):
    try:
        tree = etree.parse(filename)
    except etree.XMLSyntaxError:
        return False
    return 'MD_Metadata' in tree.getroot().tag if hasattr(tree, 'getroot') else False


def load_metadata(filename):
    try:
        md = snimarProfileModel.MD_Metadata(etree.parse(filename))
        return md
    except Exception as e:
        # fix_print_with_import
        print("ERROR:","Exception type:", e.__class__, "Message:", e.message)
        return None


def validate_service(md):
    error = []

    if md is None or md.hierarchy is None:
        error.append('Invalid')
        return error

    if md.hierarchy == 'service':
        if md.serviceidentification is None:
            error.append('serviceidentification')
        else:
            md.serviceidentification.couplingtype and error.append('couplingtype')
            len(md.serviceidentification.operations) < 1 and error.append('operations')
            len(md.serviceidentification.operateson) < 1 and error.append('operateson')
            md.serviceidentification.type is None and error.append('type')
        len(md.distribution.online) < 1 and error.append('online')

    return error


def validate_dataset(md):
    error = []

    if md is None or md.hierarchy is None:
        error.append('Invalid')
        return error

    if md.hierarchy == 'dataset' or md.hierarchy == 'serie':
        if md.identification is not None:
            len(md.identification.uricode) < 1 and error.append('identifier')
            len(md.identification.resourcemaintenance) < 1 and error.append('resourcemaintenance')
            len(md.identification.spatialrepresentation) < 1 and error.append('spatialrepresentation')
            len(md.identification.denominators) < 1 and len(md.identification.distance) < 1 and error.append('denominators or distance')

            # Keywords
            len(md.identification.topiccategory) < 1 and error.append('topiccategory')

            # Geographic and temporal extent
            len(md.identification.extent) < 1 and error.append('extent')
            len(md.identification.date) < 1 and error.append('date')

            # Quality
            md.dataquality is None and error.append('dataquality')

            # Constraints
            len(md.identification.useconstraints) < 1 and error.append('legalconstraints')
            len(md.identification.securityconstraints) < 1 and error.append('securityconstraints')

        # Distribution
        if md.distribution is not None:
            len(md.distribution.format) < 1 and error.append('format')

    return error


def validate_common(md):
    error = []

    if md is None or md.hierarchy is None:
        error.append('Invalid')
        return error

    # Assert top level elements
    md.stdname is None and error.append('stdname')
    md.stdver is None and error.append('stdver')
    md.identifier is None and error.append('identifier')

    # Assert identification elements
    if md.identification is None:
        error.append('identification')
    else:
        md.identification.title is None and error.append('title')
        md.identification.titleEN is None and error.append('titleEN')
        md.identification.abstract is None and error.append('abstract')
        md.identification.abstractEN is None and error.append('abstractEN')

    return error


def validate_keywords(md):
    md = snimarProfileModel.MD_Metadata()
    error = []

    if md is None or md.hierarchy is None:
        error.append('Invalid')
        return error

    if len(md.identification.keywords) < 1:
        error.append('Missing keywords')
        return error

    inspire_theme = 'INSPIRE' in [keyword['thesaurus']['title'] for keyword in md.identification.keywords]
    inspire_theme and error.append('inspire')

    # SNIMAR Validation

    # END SNIMAR Validation
    return error


def validate_common(md):
    """Validates fields common to different types of data"""
    error = []
    if md is None or md.hierarchy is None:
        error.append('Invalid')
        return error

    if md.identification is not None:
        md.identification.title is None and error.append('title')
        md.identification.titleEN is None and error.append('titleEN')
        md.identification.abstract is None and error.append('abstract')
        md.identification.abstractEN is None and error.append('abstractEN')
        len(md.identification.resourcemaintenance) < 1 and error.append('resourcemaintenance')
        (len(md.identification.date) < 1 or len(md.identification.datetype) < 1) and error.append('date')
        (len(md.identification.uselimitation) < 1 or len(md.identification.accessconstraints) < 1 or \
         len(md.identification.useconstraints) < 1) and error.append('resourceconstraints')

    return error
