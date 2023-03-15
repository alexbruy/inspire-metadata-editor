# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarEditorController/models/customComboBoxModel.py
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
from qgis.PyQt.QtCore import QModelIndex, Qt, QEvent, QAbstractListModel
from qgis.PyQt.QtWidgets import QComboBox, QTreeView, QFrame

EnglishTermRole = 100


class CodeListItem(object):
    def __init__(self, term=None, term_pt=None, description=None, dic=None):
        """
            Can be used in two ways :

        :param term:
        :param term_pt:
        :param description:
        :param dic:
        """
        if dic is not None:
            self.term = dic["en"]
            self.term_pt = dic["pt"]
            self.description = dic["description"]
        else:
            self.term = term
            self.term_pt = term_pt
            self.description = description

    def __unicode__(self):
        return str(self.term_pt)

    def __str__(self):
        return self.term_pt


class Reference_System_Item(CodeListItem):
    def __init__(self, code=None, codeSpace=None, name=None):
        CodeListItem.__init__(self)
        self.code = str(code)
        self.codeSpace = str(codeSpace)
        self.name = name
        self.term_pt = self.name + u"-" + self.codeSpace + u':' + self.code
        self.description = self.term_pt
        self.term = self.term_pt


class CustomComboBoxModel(QAbstractListModel):
    def __init__(self, parent, initialData):
        self.listElements = initialData
        self.reverse_dic = {}
        for x in initialData:
            if x is None:
                continue
            self.reverse_dic[x.term] = x
        QAbstractListModel.__init__(self, parent)

    def rowCount(self, parent=QModelIndex(), **kwargs):
        return len(self.listElements)

    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid() or index.row() > self.rowCount() or index.column() != 0:
            return None
        elif self.listElements[index.row()] is None and role != Qt.UserRole:
            return u''
        elif role == Qt.DisplayRole:
            return self.listElements[index.row()].term_pt
        elif role == Qt.ToolTipRole:
            return formatTooltip(self.listElements[index.row()].description)
        elif role == Qt.UserRole:
            return self.listElements[index.row()]
        else:
            return None

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def reverse_lookup(self, term_en):
        return self.reverse_dic[term_en]


class CustomComboBox(QComboBox):
    def __init__(self):
        QComboBox.__init__(self)


def dic_to_CustomComboBox_dic(dic):
    """
    Builds a CodeListItem dict based of a dict

    :type dic: dict
    """
    ret = {}
    for x in list(dic.keys()):
        ret[x] = CodeListItem(dic=dic[x])
    return ret


def reverse_en_to_pt_keys(dic):
    ret = {}
    for x in list(dic.values()):
        ret[x.term_pt] = x
    return ret


def reverse_pt_to_en_keys(dic):
    ret = {}
    for x in list(dic.values()):
        ret[x.term] = x
    return ret


def formatTooltip(text):
    return "<font>" + text + "</font>"


