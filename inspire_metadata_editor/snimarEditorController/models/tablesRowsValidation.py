# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarEditorController/models/tablesRowsValidation.py
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
import traceback

from qgis.PyQt.QtCore import QDateTime
from EditorMetadadosMarswInforbiomares.snimarProfileModel import snimarProfileModel
from EditorMetadadosMarswInforbiomares import CONSTANTS as cons
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import table_list_aux as tla
from EditorMetadadosMarswInforbiomares.snimarEditorController.models.customComboBoxModel import CodeListItem


class Distribution(object):
    def __init__(self, online_list):
        self.onlineList = online_list

    def distribuituionformat(self, row):
        if row[0] == "" or row[1] == "" or row[1] is None or row[0] is None:
            return [False, u"Os dois elementos são obrigatórios."]
        else:
            return [True, None]

    def resourcelocator(self, row):
        if row[1] not in self.onlineList:
            return [False, u"O função " + str(row[1]) + u" não se encontra na lista predefenida."]
        elif row[0] == "":
            return [False, u"O URL é obrigatório."]
        else:
            return [True, None]


class GeographicInfo(object):
    def __init__(self):
        pass

    def boundingbox(self, row):
        pass

    def geographicidentifier(self, row):
        pass

    def referencesystem(self, row):
        pass


class Identification(object):
    def __init__(self):
        pass

    def identifiers(self, row):
        if row[0] == u"" or row[0] == None:
            return [False, u"O elemento Identificador não pode ser vazio."]
        return [True, None]


class Keywords(object):
    def __init__(self, keywordtypes, datatypes):
        self.freewordsTypes = keywordtypes+[None]
        self.dataypes = datatypes
        self.thesaurus = None

    def snimarkeywords(self, row):
        row_word = row[1]
        row_type = row[0].term
        row_uuid = row[-1]
        if row_uuid not in self.thesaurus.keywords_list:
            return [False, u'Esta palavra não possui um identificador válido! Provavelmente foi alterado. Experimente readicionar a palavra',None,None]
        elif row_word != self.thesaurus.keywords_list[row_uuid]['word']:
            return [False, u'Esta palavra não pertence ao Thesaurus SNIMar! Provavelmente a palavra foi alterada no Thesaurus!',self.thesaurus.keywords_list[row_uuid]['word'],'word']
        elif row_type != self.thesaurus.keywords_list[row_uuid]['type']:
            return [False, u'Esta palavra não possui um tipo válido!',self.thesaurus.keywords_list[row_uuid]['type'],'type']
        else:
            return [True, None,None,None]

    def freekeywords(self, row):
        if row[0] == "":
            return [False, u"Falta a palavra-chave."]
        elif row[1] is not None and row[1] not in self.freewordsTypes:
            return [False, u"O tipo de palavra-chave não pertence aos tipos predefinidos."]
        elif row[4] is not None and row[4] not in self.dataypes:

            return [False, u"O tipo de data não pertence aos tipos predefinidos."]
        elif row[2] is not None and row[2] != "" and ((row[3] == "" or row[3] is None) or (row[4] == "" or row[4] is None)):
            return [False, u"A informação sobre o Thesaurus encontra-se incompleta"]
        else:
            return [True, None]

    def set_thesaurus(self, thesaurus):
        self.thesaurus = thesaurus


class Quality(object):
    def __init__(self):
        pass

    def processsteps(self, row):
        if row[0]is None or(row[0] is not None and row[0].strip() == ""):
            return [False, u"A descrição é obrigatória."]
        else:
            return [True, None]


class Restrictions(object):
    def __init__(self, restrictions_list):
        self.restrictions_list = restrictions_list

    def legalrestrictions(self, row):

        # Added the try/catch but didnt verified if it may harm the validation logic
        if row[1] is not None and row[1] not in self.restrictions_list:
            return [False, u"O valor do item Restrições de Acesso não pertence a lista predefenida."]
        if row[2] is not None and row[2] not in self.restrictions_list:
            return [False, u"O valor do item Restrições de Uso não pertence a lista predefenida."]
        if row[0] is None or row[0].strip() == "" or row[2] is None or row[1] is None:
            return [False, u"Elementos em Falta."]
        else:
            if (row[3] is None or row[3].strip() == "") and (
                            row[2].term == cons.OTHER_RESTRICTIONS_STR or row[1].term == cons.OTHER_RESTRICTIONS_STR):
                return [False,
                        u"O item Outras Restrições é obrigatório, se foi selecionado como opção nos elementos anteriores."]
            else:
                return [True, None]


class TemporalInfo(object):
    def __init__(self):
        pass

    def timeextension(self, row):
        bdate = QDateTime.fromString(row[0], cons.DATE_TIME_FORMAT)
        edate = QDateTime.fromString(row[1], cons.DATE_TIME_FORMAT)

        if bdate is None:
            return [False, u"Data de inicio em falta."]
        elif edate is None:
            return [False, u"Data de fim em falta."]
        elif bdate > edate:
            return [False, u"A data de inicio é posterior a data de fim."]
        else:
            return [True, None]
