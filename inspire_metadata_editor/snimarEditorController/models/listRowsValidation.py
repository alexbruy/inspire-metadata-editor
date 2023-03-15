# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarEditorController/models/listRowsValidation.py
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
from builtins import str
from builtins import object
import re
from EditorMetadadosMarswInforbiomares.snimarProfileModel import snimarProfileModel


class Identification(object):
    def __init__(self, resource_mantainence, language, spatial_representation, resource_status):
        self.resourcestatusM = resource_status
        self.resourceM = resource_mantainence
        self.languages = language
        self.geoRepreList = spatial_representation

    def resourcestatus(self, row):
        if row not in self.resourcestatusM:
            return [False, u"A entrada " + str(row) + u" não pertence a lista predefinida pelo Perfil SNIMar."]
        else:
            return [True, None]

    def resourcemaintenance(self, row):
        if row not in self.resourceM:
            return [False, u"A entrada " + str(row) + u" não pertence a lista predefinida pelo Perfil SNIMar."]
        else:
            return [True, None]

    def language(self, row):
        if row not in self.languages:
            return [False, u"A Língua " + str(row) + u" não pertence a lista predefinida."]
        else:
            return [True, None]

    def geographicrepresentation(self, row):
        if row not in self.geoRepreList:
            return [False, u"A Representação " + str(row) + u" não pertence a lista predefinida."]
        else:
            return [True, None]

    def credits(self, row):
        pass  # Not used

    def equivalentscale(self, row):
        if int(row) < 0:
            return [False, u"O denominador deve ser um número inteiro positivo."]
        else:
            return [True, None]

    def distance(self, row):
        if float(row) < 0:
            return [False, u"A distância deve ser um número inteiro positivo."]
        else:
            return [True, None]


class Keywords(object):
    def __init__(self, inpirelist, topiclist):
        self.inspireList = inpirelist

        self.topicList = topiclist

    def inspire(self, row):
        if row not in self.inspireList:
            return [False,
                    u"O tema " + str(
                        row) + u" não pertence a lista predefinida de temas INSPIRE.\nNão devem ser usados os termos em Inglês."]
        else:
            return [True, None]

    def topiccategory(self, row):
        if row not in self.topicList:
            return [False, u"A categoria " + str(row) + u" não pertence a lista predefinida de categorias temáticas."]
        else:
            return [True, None]


class Restrictions(object):
    def __init__(self, classificationlist, restriction_list):
        self.restriction_list = restriction_list
        self.classificationList = classificationlist

    def useConstraints(self, row):
        if row not in self.restriction_list:
            return [False, u"A Restrição " + str(row) + u" não pertence a lista predefinida de Restrições de Uso."]
        else:
            return [True, None]

    def accessConstraints(self, row):
        if row not in self.restriction_list:
            return [False, u"A Restrição " + str(row) + u" não pertence a lista predefinida de Restrições de Acesso."]
        else:
            return [True, None]

    def securityrestrictions(self, row):
        if row not in self.classificationList:
            return [False, u"A Restrição " + str(row) + u" não pertence a lista predefinida de Restrições de Segurança."]
        else:
            return [True, None]


class GeographicInfo(object):
    def __init__(self, refSys):
        self.refSys = refSys

    def referenceSystems(self, row):
        if row not in self.refSys:
            return [False, u"O Sistema de referência  " + str(row) + u" não pertence a lista predefinida de Sistemas de referência."]
        else:
            return [True, None]


class InlineContact(object):
    def __init__(self):
        self.email_pattern = re.compile('[^@]+@[^@]+\.[^@]+')

    def email(self, email):
        ret = self.email_pattern.match(email)
        if ret is None:
            return [False, u"O email não é valido"]
        else:
            return [True, None]
