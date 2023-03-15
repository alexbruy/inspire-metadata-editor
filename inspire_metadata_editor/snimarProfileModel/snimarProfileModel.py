# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarProfileModel/snimarProfileModel.py
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
# import keyword
from builtins import zip
from builtins import range
from builtins import object
import os
import re
import datetime

# OWSLib imports
import EditorMetadadosMarswInforbiomares
from EditorMetadadosMarswInforbiomares.libs.owslib import iso
from EditorMetadadosMarswInforbiomares.libs.owslib import util
from EditorMetadadosMarswInforbiomares.libs.owslib import namespaces
from EditorMetadadosMarswInforbiomares.CONSTANTS import Scopes as SCOPES
from EditorMetadadosMarswInforbiomares.CONSTANTS import SNIMAR_BASE_DIR

from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = os.path.join(SNIMAR_BASE_DIR, 'snimarProfileModel/jinja2Templates/')

namespaces = iso.get_namespaces()
namespaces['gml-old'] = namespaces['gml']
namespaces['gml'] = namespaces['gml32']


class CI_ResponsibleParty(iso.CI_ResponsibleParty):
    def __init__(self, md=None):
        super(CI_ResponsibleParty, self).__init__(md)
        if md is None:
            self.email = []
            self.fax = []
            self.onlineresource = None
            self.phone = []
            self.role = None
            self.role_pt = None
        else:
            self.phone = []
            for val in md.findall(
                util.nspath_eval(
                    'gmd:contactInfo/gmd:CI_Contact/gmd:phone/gmd:CI_Telephone/gmd:voice/gco'
                    ':CharacterString',
                    namespaces)):
                self.phone.append(util.testXMLValue(val))

            self.fax = []
            for val in md.findall(
                util.nspath_eval(
                    'gmd:contactInfo/gmd:CI_Contact/gmd:phone/gmd:CI_Telephone/gmd:facsimile'
                    '/gco:CharacterString',
                    namespaces)):
                self.fax.append(util.testXMLValue(val))

            self.email = []
            for val in md.findall(util.nspath_eval(
                'gmd:contactInfo/gmd:CI_Contact/gmd:address/gmd:CI_Address/gmd'
                ':electronicMailAddress/gco:CharacterString',
                namespaces)):
                self.email.append(util.testXMLValue(val))


class MD_Metadata(iso.MD_Metadata):
    def __init__(self, md=None, scope=None):
        super(MD_Metadata, self).__init__(md)
        self.scope = SCOPES.get_string_representation(scope)
        if md is None:
            self.identification = None
            self.serviceidentification = None
            self.referencesystem = []
            self.contact = []
        else:
            if hasattr(md, 'getroot'):
                root = md.getroot()
                global namespaces
                if hasattr(root, 'nsmap'):
                    namespaces.update(root.nsmap)
            val = md.find(
                util.nspath_eval('gmd:identificationInfo/gmd:MD_DataIdentification', namespaces))
            if val is not None:
                self.identification = MD_DataIdentification(val, self.hierarchy)
                self.serviceidentification = None
            else:
                val = md.find(
                    util.nspath_eval('gmd:identificationInfo/srv:SV_ServiceIdentification',
                                     namespaces))
                if val is not None:
                    self.serviceidentification = SV_ServiceIdentification(val, self.hierarchy)
                    self.identification = None
                else:
                    self.identification = None
                    self.serviceidentification = None
            if self.language is None:
                val = md.find(util.nspath_eval('gmd:language/gmd:LanguageCode', namespaces))
                self.language = util.testXMLAttribute(val, 'codeListValue')

            val = md.find(util.nspath_eval('gmd:dataQualityInfo/gmd:DQ_DataQuality', namespaces))
            if val is not None:
                self.dataquality = DQ_DataQuality(val)
            else:
                self.dataquality = None
            self.referencesystem = []
            for val in md.findall(
                util.nspath_eval('gmd:referenceSystemInfo/gmd:MD_ReferenceSystem', namespaces)):
                referencesystem = iso.MD_ReferenceSystem(val)
                if referencesystem is not None:
                    self.referencesystem.append(referencesystem)

            val = md.find(util.nspath_eval('gmd:distributionInfo/gmd:MD_Distribution', namespaces))
            if val is not None:
                self.distribution = MD_Distribution(val)
            else:
                self.distribution = None
            self.contact = []
            for i in md.findall(
                util.nspath_eval('gmd:contact/gmd:CI_ResponsibleParty', namespaces)):
                o = CI_ResponsibleParty(i)
                self.contact.append(o)


class MD_DataIdentification(iso.MD_DataIdentification):
    def __init__(self, md=None, identtype=None):
        super(MD_DataIdentification, self).__init__(md, identtype)
        if md is None:
            self.titleEN = None
            self.abstractEN = None
            self.extent = []
            self.credits = []
            self.language = []
            self.status = []
            self.resourcemaintenance = []
            self.graphicoverview = None
            self.temporalextent_start = []
            self.temporalextent_end = []
            self.temporalextent_id = []
            self.spatialrepresentation = []
            self.legalconstraints = []
            self.securityconstraints = []
            self.charset = None
            self.contact = []
        else:
            val = md.find(
                util.nspath_eval(
                    'gmd:citation/gmd:CI_Citation/gmd:title/gmd:PT_FreeText/gmd:textGroup/gmd'
                    ':LocalisedCharacterString',
                    namespaces))
            self.titleEN = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'gmd:abstract/gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString',
                namespaces))
            self.abstractEN = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'gmd:graphicOverview/gmd:MD_BrowseGraphic/gmd:fileName/gco:CharacterString',
                namespaces))
            self.graphicoverview = util.testXMLValue(val)

            val = md.find(util.nspath_eval('gmd:characterSet/gmd:MD_CharacterSetCode', namespaces))
            self.charset = util.testXMLAttribute(val, 'codeListValue')

            self.credits = []
            for val in md.findall(util.nspath_eval('gmd:credit/gco:CharacterString', namespaces)):
                self.credits.append(util.testXMLValue(val))

            self.status = []
            for val in md.findall(util.nspath_eval('gmd:status/gmd:MD_ProgressCode', namespaces)):
                self.status.append(util.testXMLAttribute(val, 'codeListValue'))

            self.resourcemaintenance = []
            for val in md.findall(util.nspath_eval(
                'gmd:resourceMaintenance/gmd:MD_MaintenanceInformation/gmd'
                ':maintenanceAndUpdateFrequency/gmd:MD_MaintenanceFrequencyCode',
                namespaces)):
                self.resourcemaintenance.append(util.testXMLAttribute(val, 'codeListValue'))

            self.spatialrepresentation = []
            for val in md.findall(util.nspath_eval(
                'gmd:spatialRepresentationType/gmd:MD_SpatialRepresentationTypeCode',
                namespaces)):
                self.spatialrepresentation.append(util.testXMLAttribute(val, 'codeListValue'))

            self.language = []
            for val in md.findall(util.nspath_eval('gmd:language/gmd:LanguageCode', namespaces)):
                self.language.append(util.testXMLAttribute(val, 'codeListValue'))

            self.uselimitation = []
            for i in md.findall(
                util.nspath_eval(
                    'gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:useLimitation/gco'
                    ':CharacterString',
                    namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.uselimitation.append(val)

            self.accessconstraints = []
            for val in md.findall(
                util.nspath_eval(
                    'gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:accessConstraints'
                    '/gmd:MD_RestrictionCode',
                    namespaces)):
                if val is not None:
                    uu = util.testXMLAttribute(val, 'codeListValue')
                    self.accessconstraints.append(uu)

            self.otherconstraints = []
            for i in md.findall(util.nspath_eval(
                'gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco'
                ':CharacterString',
                namespaces)):
                val = util.testXMLValue(i)
                if val is not None:

                    self.otherconstraints.append(val)

            self.useconstraints = []
            for val in md.findall(
                util.nspath_eval(
                    'gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:useConstraints/gmd'
                    ':MD_RestrictionCode',
                    namespaces)):
                if val is not None:
                    uu = util.testXMLAttribute(val, 'codeListValue')
                    self.useconstraints.append(uu)

            self.securityconstraints = []
            for val in md.findall(
                util.nspath_eval(
                    'gmd:resourceConstraints/gmd:MD_SecurityConstraints/gmd:classification'
                    '/gmd:MD_ClassificationCode',
                    namespaces)):
                if val is not None:
                    uu = util.testXMLAttribute(val, 'codeListValue')
                    self.securityconstraints.append(uu)

            self.keywords = []
            for val in md.findall(
                util.nspath_eval('gmd:descriptiveKeywords/gmd:MD_Keywords', namespaces)):
                uu = util.testXMLAttribute(val, 'uuid')
                kid = util.testXMLAttribute(val, 'id')
                self.keywords.append(MD_Keywords(val, uuid=uu, kid=kid))

            self.contact = []
            for i in md.findall(
                util.nspath_eval('gmd:pointOfContact/gmd:CI_ResponsibleParty', namespaces)):
                o = CI_ResponsibleParty(i)
                self.contact.append(o)

            self.uricode = []
            self.uricodespace = []

            # Find the MD_Identifiers in the MD_DataIdentification
            for val in md.findall(
                util.nspath_eval(
                    'gmd:citation/gmd:CI_Citation/gmd:identifier/gmd:MD_Identifier/gmd:code'
                    '/gco:CharacterString',
                    namespaces)):
                val = util.testXMLValue(val)
                if val is not None:
                    self.uricode.append(val)
                    self.uricodespace.append(None)

            codes = md.findall(
                util.nspath_eval(
                    'gmd:citation/gmd:CI_Citation/gmd:identifier/gmd:RS_Identifier/gmd:code/gco'
                    ':CharacterString',
                    namespaces))
            codespaces = md.findall(
                util.nspath_eval(
                    'gmd:citation/gmd:CI_Citation/gmd:identifier/gmd:RS_Identifier/gmd:codeSpace'
                    '/gco:CharacterString',
                    namespaces))
            if len(codes) == len(codespaces):
                for i in range(0, len(codes), 1):
                    val = util.testXMLValue(codes[i])
                    if val is not None and val.strip() != "":
                        self.uricode.append(val)
                        val = util.testXMLValue(codespaces[i])
                        if val is not None and val.strip() != "":
                            self.uricodespace.append(val)
                        else:
                            self.uricodespace.append(None)

            # Process the extents
            self.temporalextent_id = []
            self.temporalextent_end = []
            self.temporalextent_start = []
            self.extent = []
            one_temp = False
            one_vert = False
            extents = md.findall(util.nspath_eval('gmd:extent', namespaces))
            for extent in extents:
                val = None
                for e in extent.findall(
                    util.nspath_eval('gmd:EX_Extent/gmd:geographicElement', namespaces)):
                    if e.find(util.nspath_eval('gmd:EX_GeographicBoundingBox',
                                               namespaces)) is not None or e.find(
                        util.nspath_eval('gmd:EX_GeographicDescription',
                                         namespaces)) is not None:
                        val = e
                        self.extent.append(EX_Extent(val))
                if not one_temp:  # the SNIMar profile only allows one instance, the rest will
                    # be discarded
                    for e in extent.findall(
                        util.nspath_eval('gmd:EX_Extent/gmd:temporalElement', namespaces)):
                        if e is None:
                            continue

                        valBP = e.find(util.nspath_eval(
                            'gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:beginPosition',
                            namespaces))
                        if valBP is None:
                            namespaces['gml'] = namespaces['gml-old']
                            valBP = e.find(
                                util.nspath_eval('gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:beginPosition',
                                                 namespaces))
                        valEP = e.find(util.nspath_eval(
                            'gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:endPosition',
                            namespaces))
                        valID = e.find(
                            util.nspath_eval('gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod',
                                             namespaces))
                        self.extent.append(
                            EX_TemporalExtent(id=None, beginposition=util.testXMLValue(valBP),
                                              endposition=util.testXMLValue(valEP)))
                        one_temp = True
                if not one_vert:  # the SNIMar profile only allows one instance, the rest will
                    # be discarded
                    for e in extent.findall(
                        util.nspath_eval('gmd:EX_Extent/gmd:verticalElement', namespaces)):
                        if e.find(
                            util.nspath_eval('gmd:EX_VerticalExtent', namespaces)) is not None:
                            self.extent.append(EX_VerticalExtent(e))
                            one_vert = True

    @property
    def md_identifiers(self):
        md_identifiers = []
        for i in range(len(self.uricode)):
            if self.uricodespace[i] is None:
                md_identifiers.append(self.uricode[i])
        return md_identifiers

    @md_identifiers.setter
    def md_identifiers(self, code):
        self.uricode.append(code)
        self.uricodespace.append(None)

    @property
    def rs_identifiers(self):
        rs_identifiers = []
        for i in range(len(self.uricode)):
            if self.uricodespace[i] is not None:
                rs_identifiers.append((self.uricode[i], self.uricodespace[i]))
        return rs_identifiers

    @rs_identifiers.setter
    def rs_identifiers(self, code, codespace):
        self.uricode.append(code)
        if codespace.strip() == "":
            codespace = None
        self.uricodespace.append(codespace)


class SV_ServiceIdentification(iso.SV_ServiceIdentification):
    def __init__(self, md=None, identtype=None):
        super(SV_ServiceIdentification, self).__init__(md)
        self.uricode = []
        self.uricodespace = []
        if md is None:
            self.titleEN = None
            self.abstractEN = None
            self.alternatetitle = None
            self.extent = []
            self.credits = []
            self.uselimitation = []
            self.accessconstraints = []
            self.classification = []
            self.otherconstraints = []
            self.securityconstraints = []
            self.useconstraints = []
            self.graphicoverview = None
            self.temporalextent_start = []
            self.temporalextent_end = []
            self.temporalextent_id = []
            self.legalconstraints = []
            self.securityconstraints = []
            self.contact = []
            self.keywords = []
            self.status = []
            self.purpose = None
            self.date = []
            self.datetype = []
        else:

            self.couplingtype = iso._testCodeListValue(
                md.find(util.nspath_eval('srv:couplingType/srv:SV_CouplingType', namespaces)))

            self.uselimitation = []
            for i in md.findall(
                util.nspath_eval(
                    'gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:useLimitation/gco'
                    ':CharacterString',
                    namespaces)):
                val = util.testXMLValue(i)
                if val is not None:
                    self.uselimitation.append(val)

            self.accessconstraints = []
            for val in md.findall(
                util.nspath_eval(
                    'gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:accessConstraints'
                    '/gmd:MD_RestrictionCode',
                    namespaces)):
                if val is not None:
                    uu = util.testXMLAttribute(val, 'codeListValue')
                    self.accessconstraints.append(uu)

            self.otherconstraints = []
            for i in md.findall(util.nspath_eval(
                'gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco'
                ':CharacterString',
                namespaces)):
                val = util.testXMLValue(i)
                if val is not None:

                    self.otherconstraints.append(val)

            self.useconstraints = []
            for val in md.findall(
                util.nspath_eval(
                    'gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:useConstraints/gmd'
                    ':MD_RestrictionCode',
                    namespaces)):
                if val is not None:
                    uu = util.testXMLAttribute(val, 'codeListValue')
                    self.useconstraints.append(uu)

            self.securityconstraints = []
            for val in md.findall(
                util.nspath_eval(
                    'gmd:resourceConstraints/gmd:MD_SecurityConstraints/gmd:classification'
                    '/gmd:MD_ClassificationCode',
                    namespaces)):
                if val is not None:
                    uu = util.testXMLAttribute(val, 'codeListValue')
                    self.securityconstraints.append(uu)
            self.date = []
            self.datetype = []

            for i in md.findall(
                util.nspath_eval('gmd:citation/gmd:CI_Citation/gmd:date/gmd:CI_Date',
                                 namespaces)):
                self.date.append(iso.CI_Date(i))

            val = md.find(util.nspath_eval('gmd:purpose/gco:CharacterString', namespaces))
            self.purpose = util.testXMLValue(val)

            self.status = []
            for val in md.findall(util.nspath_eval('gmd:status/gmd:MD_ProgressCode', namespaces)):
                self.status.append(util.testXMLAttribute(val, 'codeListValue'))

            val = md.find(
                util.nspath_eval(
                    'gmd:citation/gmd:CI_Citation/gmd:title/gmd:PT_FreeText/gmd:textGroup/gmd'
                    ':LocalisedCharacterString',
                    namespaces))
            self.titleEN = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'gmd:abstract/gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString',
                namespaces))
            self.abstractEN = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'gmd:citation/gmd:CI_Citation/gmd:alternateTitle/gco:CharacterString', namespaces))
            self.alternatetitle = util.testXMLValue(val)

            val = md.find(util.nspath_eval(
                'gmd:graphicOverview/gmd:MD_BrowseGraphic/gmd:fileName/gco:CharacterString',
                namespaces))
            self.graphicoverview = util.testXMLValue(val)

            self.credits = []
            for val in md.findall(util.nspath_eval('gmd:credit/gco:CharacterString', namespaces)):
                self.credits.append(util.testXMLValue(val))

            self.resourcemaintenance = []
            for val in md.findall(util.nspath_eval(
                'gmd:resourceMaintenance/gmd:MD_MaintenanceInformation/gmd'
                ':maintenanceAndUpdateFrequency/gmd:MD_MaintenanceFrequencyCode',
                namespaces)):
                self.resourcemaintenance.append(util.testXMLAttribute(val, 'codeListValue'))

            self.keywords = []
            for val in md.findall(
                util.nspath_eval('gmd:descriptiveKeywords/gmd:MD_Keywords', namespaces)):
                uu = util.testXMLAttribute(val, 'uuid')
                kid = util.testXMLAttribute(val, 'id')
                self.keywords.append(MD_Keywords(val, uuid=uu, kid=kid))

            self.contact = []
            for i in md.findall(
                util.nspath_eval('gmd:pointOfContact/gmd:CI_ResponsibleParty', namespaces)):
                o = CI_ResponsibleParty(i)
                self.contact.append(o)

            # Find the MD_Identifiers in the MD_DataIdentification
            for val in md.findall(
                util.nspath_eval(
                    'gmd:citation/gmd:CI_Citation/gmd:identifier/gmd:MD_Identifier/gmd:code'
                    '/gco:CharacterString',
                    namespaces)):
                val = util.testXMLValue(val)
                if val is not None:
                    self.uricode.append(val)
                    self.uricodespace.append(None)

            codes = md.findall(
                util.nspath_eval(
                    'gmd:citation/gmd:CI_Citation/gmd:identifier/gmd:RS_Identifier/gmd:code/gco'
                    ':CharacterString',
                    namespaces))
            codespaces = md.findall(
                util.nspath_eval(
                    'gmd:citation/gmd:CI_Citation/gmd:identifier/gmd:RS_Identifier/gmd:codeSpace'
                    '/gco:CharacterString',
                    namespaces))
            if len(codes) == len(codespaces):
                for i in range(0, len(codes), 1):
                    val = util.testXMLValue(codes[i])
                    if val is not None and val.strip() != "":
                        self.uricode.append(val)
                        val = util.testXMLValue(codespaces[i])
                        if val is not None and val.strip() != "":
                            self.uricodespace.append(val)
                        else:
                            self.uricodespace.append(None)

            # Process the extents
            self.temporalextent_id = []
            self.temporalextent_end = []
            self.temporalextent_start = []
            self.extent = []
            extents = md.findall(util.nspath_eval('srv:extent', namespaces))
            for extent in extents:
                val = None
                for e in extent.findall(
                    util.nspath_eval('gmd:EX_Extent/gmd:geographicElement', namespaces)):
                    if e.find(util.nspath_eval('gmd:EX_GeographicBoundingBox',
                                               namespaces)) is not None or e.find(
                        util.nspath_eval('gmd:EX_GeographicDescription', namespaces)) is not None:
                        val = e
                        self.extent.append(EX_Extent(val))

                for e in extent.findall(
                    util.nspath_eval('gmd:EX_Extent/gmd:temporalElement', namespaces)):
                    valBP = e.find(util.nspath_eval(
                        'gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:beginPosition',
                        namespaces))
                    if valBP is None:
                            namespaces['gml'] = namespaces['gml-old']
                            valBP = e.find(
                                util.nspath_eval('gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:beginPosition',
                                                 namespaces))
                    valEP = e.find(util.nspath_eval(
                        'gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml:endPosition',
                        namespaces))
                    valID = e.find(
                        util.nspath_eval('gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod',
                                         namespaces))
                    self.extent.append(
                        EX_TemporalExtent(id=None, beginposition=util.testXMLValue(valBP),
                                          endposition=util.testXMLValue(valEP)))

                for e in extent.findall(
                    util.nspath_eval('gmd:EX_Extent/gmd:verticalElement', namespaces)):
                    if e.find(util.nspath_eval('gmd:EX_VerticalExtent', namespaces)) is not None:
                        self.extent.append(EX_VerticalExtent(e))

    @property
    def md_identifiers(self):
        md_identifiers = []
        for i in range(len(self.uricode)):
            if self.uricodespace[i] is None:
                md_identifiers.append(self.uricode[i])
        return md_identifiers

    @md_identifiers.setter
    def md_identifiers(self, code):
        self.uricode.append(code)
        self.uricodespace.append(None)

    @property
    def rs_identifiers(self):
        rs_identifiers = []
        for i in range(len(self.uricode)):
            if self.uricodespace[i] is not None:
                rs_identifiers.append((self.uricode[i], self.uricodespace[i]))
        return rs_identifiers

    @rs_identifiers.setter
    def rs_identifiers(self, code, codespace):
        self.uricode.append(code)
        if codespace.strip() == "":
            codespace = None
        self.uricodespace.append(codespace)


def get_domainconsistency_report(md):
    report = {
        'specification': None,
        'explanation': None,
        'date': None,
        'datetype': None,
        'pass': False,
    }
    if hasattr(md, 'dataquality') and md.dataquality is not None:
        report['specification'] = md.dataquality.specificationtitle
        report['explanation'] = md.dataquality.conformanceexplanation
        report['date'] = md.dataquality.conformancedate[0] if len(
            md.dataquality.conformancedate) > 0 else None
        report['datetype'] = md.dataquality.conformancedatetype[0] if len(
            md.dataquality.conformancedatetype) > 0 else None
        report['pass'] = md.dataquality.conformancedegree[0] if len(
            md.dataquality.conformancedegree) > 0 else None
    return report


class DQ_DataQuality(iso.DQ_DataQuality):
    def __init__(self, md=None):
        super(DQ_DataQuality, self).__init__(md)
        if md is None:
            self.conformanceexplanation = None
            self.lineageEN = None
            self.sources = []
            self.process_steps_description = []
            self.process_steps_date = []
            self.process_steps_rationale = []
        else:
            val = md.find(util.nspath_eval(
                'gmd:report/gmd:DQ_DomainConsistency/gmd:result/gmd:DQ_ConformanceResult/gmd'
                ':explanation/gco:CharacterString',
                namespaces))
            val = util.testXMLValue(val)
            self.conformanceexplanation = val

            val = md.find(
                util.nspath_eval(
                    'gmd:lineage/gmd:LI_Lineage/gmd:statement/gmd:PT_FreeText/gmd:textGroup/gmd'
                    ':LocalisedCharacterString',
                    namespaces))
            val = util.testXMLValue(val)
            self.lineageEN = val

            self.sources = []
            for val in md.findall(
                util.nspath_eval(
                    'gmd:lineage/gmd:LI_Lineage/gmd:source/gmd:LI_Source/gmd:description/gco'
                    ':CharacterString',
                    namespaces)):
                val = util.testXMLValue(val)
                self.sources.append(val)

            self.process_steps_description = []
            self.process_steps_date = []
            self.process_steps_rationale = []

            for val in md.findall(util.nspath_eval(
                'gmd:lineage/gmd:LI_Lineage/gmd:processStep/gmd:LI_ProcessStep', namespaces)):
                description = val.find(
                    util.nspath_eval('gmd:description/gco:CharacterString', namespaces))
                description = util.testXMLValue(description)
                self.process_steps_description.append(description)

                date = val.find(util.nspath_eval('gmd:dateTime/gco:DateTime', namespaces))
                date = util.testXMLValue(date)
                self.process_steps_date.append(date)

                rationale = val.find(
                    util.nspath_eval('gmd:rationale/gco:CharacterString', namespaces))
                rationale = util.testXMLValue(rationale)
                self.process_steps_rationale.append(rationale)

    @property
    def process_steps(self):
        return list(zip(self.process_steps_description, self.process_steps_date,
                   self.process_steps_rationale))

    @process_steps.setter
    def process_steps(self, data):
        for i in range(len(data)):
            self.process_steps_description.append(data[i][0])
            self.process_steps_date.append(data[i][1])
            self.process_steps_rationale.append(data[i][2])


class EX_Extent(iso.EX_Extent):
    def __init__(self, md=None):
        super(EX_Extent, self).__init__(md)
        if md is None:
            self.hasresource = True
        else:
            val = md.find(
                util.nspath_eval('gmd:EX_GeographicBoundingBox/gmd:extentTypeCode/gco:Boolean',
                                 namespaces))
            val1 = util.testXMLValue(val)
            if val1 is None:
                val = md.find(
                    util.nspath_eval('gmd:EX_GeographicDescription/gmd:extentTypeCode/gco:Boolean',
                                     namespaces))
                val1 = util.testXMLValue(val)
            if val1 is None:
                self.hasresource = 'true'
            else:
                self.hasresource = val1


class EX_VerticalExtent(object):
    def __init__(self, md=None):
        if md is None:
            self.min = None
            self.max = None
            self.crs = None
        else:
            val = md.find(
                util.nspath_eval('gmd:EX_VerticalExtent/gmd:minimumValue/gco:Real', namespaces))
            self.min = util.testXMLValue(val)

            val = md.find(
                util.nspath_eval('gmd:EX_VerticalExtent/gmd:maximumValue/gco:Real', namespaces))
            self.max = util.testXMLValue(val)

            val = md.find(util.nspath_eval('gmd:EX_VerticalExtent/gmd:verticalCRS', namespaces))
            self.crs = util.testXMLAttribute(val, util.nspath_eval('xlink:href', namespaces))


class EX_TemporalExtent(object):
    def __init__(self, md=None, id=None, beginposition=None, endposition=None):
        if md is None:
            self.beginposition = beginposition
            self.endposition = endposition
            self.id = id
        else:
            val = md.find(util.nspath_eval(
                'gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod', namespaces))
            self.id = util.testXMLAttribute(val, 'id')

            val = md.find(
                util.nspath_eval(
                    'gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml'
                    ':beginPosition',
                    namespaces))
            self.beginposition = util.testXMLValue(val)

            val = md.find(
                util.nspath_eval(
                    'gmd:temporalElement/gmd:EX_TemporalExtent/gmd:extent/gml:TimePeriod/gml'
                    ':endPosition',
                    namespaces))
            self.endposition = util.testXMLValue(val)


class MD_Keywords(object):
    def __init__(self, md=None, uuid=None, kid=None):
        if md is None:
            self.keywords = []
            self.type = None
            self.thesaurus = None
            self.cc_uuid = None
            self.cc_id = None
            self.kwdtype_codeList = 'http://standards.iso.org/ittf/PubliclyAvailableStandards' \
                                    '/ISO_19139_Schemas/resourcesFolder/codelist/gmxCodelists.xml' \
                                    '#MD_KeywordTypeCode'
        else:
            self.cc_uuid = uuid
            self.cc_id = kid
            self.keywords = []
            val = md.findall(util.nspath_eval('gmd:keyword/gco:CharacterString', namespaces))
            for word in val:
                self.keywords.append(util.testXMLValue(word))

            self.type = None
            val = md.find(util.nspath_eval('gmd:type/gmd:MD_KeywordTypeCode', namespaces))
            self.type = util.testXMLAttribute(val, 'codeListValue')

            self.thesaurus = None
            val = md.find(util.nspath_eval('gmd:thesaurusName/gmd:CI_Citation', namespaces))
            if val is not None:
                self.thesaurus = {}

                thesaurus = val.find(util.nspath_eval('gmd:title/gco:CharacterString', namespaces))
                self.thesaurus['title'] = util.testXMLValue(thesaurus)

                thesaurus = val.find(
                    util.nspath_eval('gmd:date/gmd:CI_Date/gmd:date/gco:Date', namespaces))
                self.thesaurus['date'] = util.testXMLValue(thesaurus)

                thesaurus = val.find(
                    util.nspath_eval('gmd:date/gmd:CI_Date/gmd:dateType/gmd:CI_DateTypeCode',
                                     namespaces))
                self.thesaurus['datetype'] = util.testXMLAttribute(thesaurus, 'codeListValue')

    def is_inspire(self):
        return self.thesaurus is not None and (
            'GEMET' in self.thesaurus['title'] and 'INSPIRE' in self.thesaurus['title'])

    def is_snimar(self):
        if self.thesaurus is None or self.cc_uuid is None or len(self.keywords) != 1:
            return False
        snimar_regex = '^ *thesaurus +snimar +v\.?\d+(\.(x|[0-9]+))? *$'
        if re.match(snimar_regex, self.thesaurus['title'], flags=re.IGNORECASE) is not None:
            self.kwdtype_codeList = 'http://collab-keywords.snimar.pt/codelists/gmxCodelists.xml'
            return True
        else:
            return False

    def is_worms(self):
        if self.thesaurus is None:
            return False
        return self.thesaurus['title'] == 'https://www.marinespecies.org/rest/'

    def is_crossref(self):
        if self.thesaurus is None:
            return False
        return 'https://api.crossref.org/works' in self.thesaurus['title']

    def is_serviceClassification(self):
        return self.thesaurus is not None and (
            'ISO - 19119 geographic services taxonomy' in self.thesaurus['title'])


class MD_Distribution(iso.MD_Distribution):
    def __init__(self, md=None):
        super(MD_Distribution, self).__init__(md)
        if md is None:
            self.format = []
            self.version = []
            self.size = None
            self.distributor = []
        else:
            self.format = []
            self.version = []
            for val in md.findall(
                util.nspath_eval('gmd:distributionFormat/gmd:MD_Format', namespaces)):
                format1 = val.find(util.nspath_eval('gmd:name/gco:CharacterString', namespaces))
                version = val.find(util.nspath_eval('gmd:version/gco:CharacterString', namespaces))
                self.format.append(util.testXMLValue(format1))
                self.version.append(util.testXMLValue(version))

            val = md.find(util.nspath_eval(
                'gmd:transferOptions/gmd:MD_DigitalTransferOptions/gmd:transferSize/gco:Real',
                namespaces))
            self.size = util.testXMLValue(val)

            self.distributor = []
            for val in md.findall(
                util.nspath_eval(
                    'gmd:distributor/gmd:MD_Distributor/gmd:distributorContact/gmd'
                    ':CI_ResponsibleParty',
                    namespaces)):
                o = CI_ResponsibleParty(val)
                self.distributor.append(o)

    @property
    def distribution_format(self):
        return [list(a) for a in zip(self.format,
                                     self.version)]  # zip returns a list of tuples we need a
        # list of lists

    @distribution_format.setter
    def distribution_format(self, matrix):
        for data in matrix:
            self.format.append(data[0])
            self.version.append(data[1])


def export_xml(md):
    """Exports a MD_Metadata object into a xml file"""
    if md is None:
        return None

    loader = FileSystemLoader(TEMPLATES_DIR)
    env = Environment(loader=loader, autoescape=True, extensions=['jinja2.ext.autoescape'])
    env.finalize = silent_none
    template = env.get_template('md_metadata.xml')
    md_dict = md.__dict__
    md_dict['editor_version'] = EditorMetadadosMarswInforbiomares.__version__
    md_dict['editor_date'] = datetime.datetime.now()
    return template.render(md_dict)


def silent_none(value):
    if value is None:
        return ''
    return value
