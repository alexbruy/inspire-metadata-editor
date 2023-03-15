# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarProfileModel/snimarThesaurusBuilder.py
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
import json
import os
import textwrap
from qgis.PyQt.QtCore import QDate, QSize
from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import customComboBoxModel as customCombo
from EditorMetadadosMarswInforbiomares import CONSTANTS


class SnimarThesurusModel(object):
    def __init__(self, stable=False):
        with open(CONSTANTS.SNIMAR_THESAURUS_META) as json_data:
            src_json = json.load(json_data)
            version = src_json['current_version']

        if stable:
            with open(os.path.join(CONSTANTS.SNIMAR_BASE_DIR,
                                   "resourcesFolder/CodeLists/SnimarkeyWords/snimarThesaurus" + version + ".json")) as json_data:
                src_json = json.load(json_data)
                self.model_root = SnimarThesaurus(u"Thesaurus SNIMar", src_json[u'stable_version'],
                                                  src_json[u'last_update'].split('T')[0])
        else:
            with open(os.path.join(CONSTANTS.SNIMAR_BASE_DIR, "resourcesFolder/CodeLists/SnimarkeyWords/snimarThesaurus" + ".json")) as json_data:
                src_json = json.load(json_data)
                self.model_root = SnimarThesaurus(u"Thesaurus SNIMar", src_json[u'version'], src_json[u'last_update'].split('T')[0])

        temp_disciplines = SnimarTypes("Disciplinas")
        for disc in src_json["disciplines"]:
            if disc == 'name_pt':
                continue
            temp_disc = SnimarDiscipline(cc_id=src_json['disciplines'][disc]["id"],
                                         cc_uuid=src_json['disciplines'][disc].get("uuid"),
                                         term=src_json['disciplines'][disc].get("term_word"),
                                         kw_type=u"Disciplina",
                                         thesaurus_info=self.model_root.thesaurus_info_dic(),
                                         source=src_json['disciplines'][disc].get("source"),
                                         meaning=src_json['disciplines'][disc].get("meaning"),
                                         term_en=src_json['disciplines'][disc]['translates'].get('EN'))
            uuid = src_json['disciplines'][disc].get('uuid')
            word = src_json['disciplines'][disc].get('term_word')
            self.model_root.keywords_list[uuid] = {'word': word, 'type': 'discipline'}

            params = src_json['disciplines'][disc]['parameters']
            for par in params:
                temp_disc.appendRow(SnimarKeyWord(cc_id=params[par].get("id"),
                                                  cc_uuid=params[par].get("uuid"),
                                                  term=params[par].get("parameter_term"),
                                                  kw_type=u"Parâmetro",
                                                  thesaurus_info=self.model_root.thesaurus_info_dic(),
                                                  source=params[par].get("source"),
                                                  meaning=params[par].get("meaning"),
                                                  term_en=params[par]['translates'].get("EN")))
                uuid = params[par].get('uuid')
                word = params[par].get('parameter_term')
                self.model_root.keywords_list[uuid] = {'word': word, 'type': 'parameter'}

            temp_disciplines.appendRow(temp_disc)
        self.model_root.appendRow(temp_disciplines)

        for x in list(src_json.keys()):
            if x in [u"disciplines", u"version", u"last_update", u"stable_version"]:
                continue
            temp_type = SnimarTypes(src_json[x]["name_pt"])

            for kw in list(src_json[x]["keywords"].values()):
                temp_type.appendRow(SnimarKeyWord(cc_id=kw.get("id"),
                                                  cc_uuid=kw.get("uuid"),
                                                  term=kw.get("term_word"),
                                                  kw_type=temp_type.name,
                                                  thesaurus_info=self.model_root.thesaurus_info_dic(),
                                                  source=kw.get("source"),
                                                  meaning=kw.get("meaning"),
                                                  term_en=kw['translates'].get("EN")))
                uuid = kw.get('uuid')
                word = kw.get('term_word')
                self.model_root.keywords_list[uuid] = {'word': word, 'type': x}
            self.model_root.appendRow(temp_type)

        self.model_root.sort(0)
        self.model_root.sort(1)
        self.model_root.sort(2)
        self.model_root.sort(3)

    def get_Model(self):
        return self.model_root


class SnimarKeyWord(QStandardItem):
    def __init__(self, cc_id, cc_uuid, term, kw_type, thesaurus_info, source=None, meaning=None, term_en=None, *args):
        QStandardItem.__init__(self, *args)
        self.kw_type = kw_type
        self.cc_id = cc_id
        self.cc_uuid = cc_uuid
        self.term = term
        self.meaning = meaning
        self.source = source
        self.thesaurus_info = thesaurus_info
        self.term_en = term_en
        self.setText(text_wrapper(self.term))
        self.setSizeHint(QSize(180, 55))
        self.setCheckable(True)
        self.setDropEnabled(False)
        self.setToolTip(self.compile_tooltip())

    def compile_tooltip(self):
        tooltip = u""
        if self.meaning is not None and self.meaning.strip() != "":
            tooltip = u"<b>Definição: </b>" + self.meaning
        if self.source is not None and self.source.strip() != "":
            tooltip = tooltip + u"<br><br><b>Fonte: </b>" + self.source
        if self.term_en is not None and self.term_en.strip() != "":
            tooltip = tooltip + u"<br><br><b>Inglês: </b>" + self.term_en
        if tooltip == "":
            return None
        else:
            return u"<FONT>" + tooltip + u"</FONT>"


class SnimarDiscipline(QStandardItem):
    def __init__(self, cc_id, cc_uuid, term, kw_type, thesaurus_info, source=None, meaning=None, term_en=None, *args):
        QStandardItem.__init__(self, *args)
        self.kw_type = kw_type
        self.cc_id = cc_id
        self.cc_uuid = cc_uuid
        self.term = term
        self.source = source
        self.thesaurus_info = thesaurus_info
        self.meaning = meaning
        self.term_en = term_en
        self.setSizeHint(QSize(180, 60))
        self.setText(text_wrapper(self.term))
        self.setCheckable(True)
        self.setToolTip(self.compile_tooltip())

    def compile_tooltip(self):
        tooltip = u""
        if self.meaning is not None and self.meaning.strip() != "":
            tooltip = u"<b>Definição: </b>" + self.meaning
        if self.source is not None and self.source.strip() != "":
            tooltip = tooltip + u"<br><br><b>Fonte: </b>" + self.source
        if self.term_en is not None and self.term_en.strip() != "":
            tooltip = tooltip + u"<br><br><b>Inglês: </b>" + self.term_en
        if tooltip == "":
            return None
        else:
            return u"<FONT>" + tooltip + u"</FONT>"


def text_wrapper(text):
    w = textwrap.TextWrapper(width=30, break_long_words=True, replace_whitespace=False)
    return '\n'.join(w.wrap(text))


class SnimarThesaurus(QStandardItemModel):
    def __init__(self, name=None, version=None, date=None, *args):
        QStandardItemModel.__init__(self, *args)
        self.name = name
        self.version = version
        self.date = date
        self.keywords_list = {}

    def thesaurus_info_dic(self):
        return {
            'title': u"" + self.name + u" " + self.version,
            'version': u"" + self.version,
            'date': u"" + self.date,
            'datetype': customCombo.CodeListItem(u"publication", u"Publicação")
        }


class SnimarTypes(QStandardItem):
    def __init__(self, name, *args):
        QStandardItem.__init__(self, *args)
        self.name = name
        self.setText(text_wrapper(self.name))
        self.setSizeHint(QSize(180, 60))
