# coding=utf-8
##############################################################################
#
#  Title:   CONSTANTS.py
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
from builtins import object
import os
from qgis.utils import pluginDirectory

DATE_FORMAT = "yyyy-MM-dd"
DATE_TIME_FORMAT = "yyyy-MM-dd hh:mm:ss"
EXTERNAL_DATE_TIME_FORMAT = "yyyy-MM-ddThh:mm:ss"
ERROR_COLOR = u'crimson'

PREDEF_LANG_RESOURCES = u"Português"
PREDEF_LANG_METADATA = u"Português"

PREDEF_HIERQ_LEVEL = u"dataset"
PREDEF_CHARSET = u"utf8"

DEFAULT_MAINTENANCE_FREQUENCY_CODE = u"asNeeded"
OTHER_RESTRICTIONS_STR = u"otherRestrictions"

FILELIST_STORE = 'filelist.json'
SNIMAR_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SNIMAR_THESAURUS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resourcesFolder/CodeLists/SnimarkeyWords')
SNIMAR_THESAURUS_META = os.path.join(SNIMAR_THESAURUS_DIR, 'snimarThesaurus_meta.json')

# SNIMAR STUFF

SNIMAR_PROFILE_NAME = u'Perfil SNIMar'
SNIMAR_PROFILE_VERSION = u'v.0.9.3'


CODELIST_SERVER_URL='http://editor.snimar.pt/CODELISTS/'

RESOURCE_DIR = os.path.join(pluginDirectory('EditorMetadadosMarswInforbiomares'), 'resourcesFolder')
NAMESPACES = {
    'gml': 'http://www.opengis.net/gml/3.2',
    'gmx': 'http://www.isotc211.org/2005/gmx',
}
CODELIST_TAGS = [
    'MD_ScopeCode',
    'MD_CharacterSetCode',
    'MD_ProgressCode',
    'MD_MaintenanceFrequencyCode',
    'MD_SpatialRepresentationTypeCode',
    'MD_TopicCategoryCode',
]
TABLIST_SERVICES = [
    (u'Identificação', 'identification_icon.svg', u"identification"),
    (u'Operações (Serviços)', 'metadata_icon.svg', u'operations'),
    (u'Classificação & Palavras-Chave', 'keywords_icon.svg', u"keywords"),
    (u'Informação Geográfica', 'geographicinfo_icon.svg', u"geographicinfo"),
    (u'Informação Temporal', 'temporal_icon.svg', u"temporal"),
    (u'Qualidade', 'quality_icon.svg', u"quality"),
    (u'Restrições', 'restrictions_icon.svg', u"restrictions"),
    (u'Distribuição', 'distribution_icon.svg', u"distribution"),
    (u'Metadados', 'metadata_icon.svg', u"metadata"),
]
TABLIST_CDG_SERIES = [
    (u'Identificação', 'identification_icon.svg', u"identification"),
    (u'Classificação & Palavras-Chave', 'keywords_icon.svg', u"keywords"),
    (u'Informação Geográfica', 'geographicinfo_icon.svg', u"geographicinfo"),
    (u'Informação Temporal', 'temporal_icon.svg', u"temporal"),
    (u'Qualidade', 'quality_icon.svg', u"quality"),
    (u'Restrições', 'restrictions_icon.svg', u"restrictions"),
    (u'Distribuição', 'distribution_icon.svg', u"distribution"),
    (u'Metadados', 'metadata_icon.svg', u"metadata"),
]

SNIMAR_KEYWORDS_MANDATORY_TYPES = [u'Disciplina', u'Parâmetro']



INSPIRE_TEXT_DATASET = (
    u"REGULAMENTO (UE) N. o 1089/2010 DA COMISSÃO de 23 de Novembro de 2010 que estabelece as "
    u"disposições de execução da Directiva 2007/2/CE do Parlamento Europeu e do Conselho "
    u"relativamente à interoperabilidade dos conjuntos e serviços de dados geográficos")
INSPIRE_DATE_DATASET = '2010-12-08'

INSPIRE_TEXT_SERVICE = (
    u"REGULAMENTO (CE) N. o 976/2009 DA COMISSÃO de 19 de Outubro de 2009 que estabelece as "
    u"disposições de execução da Directiva 2007/2/CE do Parlamento Europeu e do Conselho no que "
    u"respeita aos serviços de rede")

INSPIRE_DATE_SERVICE = '2010-11-23'



class Scopes(object):
    def __init__(self):
        pass

    CDG = 0
    SERIES = 1
    SERVICES = 2

    @staticmethod
    def get_string_representation(scope_code):
        dic = {0: "dataset", 1: "series", 2: "service"}
        return dic.get(scope_code)

    @staticmethod
    def get_code_representation(scope_string):
        dic = {"dataset": 0, "series": 1, "service": 2}
        return dic.get(scope_string)

    @staticmethod
    def get_rich_text_translation(scope_string):
        dic = {"dataset": u"C.D.G.", "series": u"Serie", "service": u"Serviço"}
        return dic.get(scope_string)
