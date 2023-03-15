# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarEditorController/models/listModel.py
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
from qgis.PyQt.QtCore import QModelIndex, Qt, QSize, QAbstractListModel
from qgis.PyQt.QtWidgets import QDateEdit, QDoubleSpinBox, QLineEdit, QComboBox, QSpinBox, QCheckBox, QLabel, QDateTimeEdit
from qgis.PyQt.QtGui import QColor
from qgis.gui import QgsFilterLineEdit
from EditorMetadadosMarswInforbiomares import CONSTANTS as cons
from EditorMetadadosMarswInforbiomares.snimarEditorController.models.customComboBoxModel import CustomComboBox


class ListModel(QAbstractListModel):
    def __init__(self, parent, element_type, header, fraction_flag, list_view, validationfunction=lambda x: [True, None]):

        self.header = header
        self.listElements = []
        self.elementType = element_type
        self.fractionFlag = fraction_flag
        self.view = list_view
        self.validation = validationfunction
        self.valList = []
        self.father = parent
        if self.father is not None:
            self.tableName = self.father.findChild(QLabel, "label_" + self.view.objectName())
            if self.tableName is not None:
                self.tableName = self.tableName.text()
        QAbstractListModel.__init__(self, list_view)

    def rowCount(self, parent=QModelIndex(), **kwargs):
        return len(self.listElements)

    def data(self, index, role=Qt.DisplayRole):

        return_value_types = [QLineEdit, QComboBox, QgsFilterLineEdit, QDateTimeEdit]
        adjust_size_types = [QComboBox, QDoubleSpinBox, QSpinBox, QDateEdit, QgsFilterLineEdit,
                             QDateTimeEdit, CustomComboBox]
        if not index.isValid() or index.row() > self.rowCount() or index.column() != 0:
            return None
        elif role == Qt.DisplayRole and self.elementType in return_value_types:
            return self.listElements[index.row()]
        elif role == Qt.DisplayRole and self.elementType == CustomComboBox:
            try:
                return self.listElements[index.row()].term_pt
            except:
                return self.listElements[index.row()]
        elif role == Qt.DisplayRole and (self.elementType == QDoubleSpinBox or self.elementType == QSpinBox):
            if self.fractionFlag:
                return "1:" + str(self.listElements[index.row()])
            return self.listElements[index.row()]
        elif role == Qt.DisplayRole and self.elementType == QDateEdit:
            if self.listElements[index.row()] is None:
                return None
            else:
                return self.listElements[index.row()].toString(cons.DATE_FORMAT)
        elif role == Qt.EditRole:
            return self.listElements[index.row()]
        elif role == Qt.SizeHintRole and self.elementType in adjust_size_types:
            return QSize(16, 22)
        elif role == Qt.CheckStateRole and self.elementType == QCheckBox:
            if self.listElements[index.row()]:
                return Qt.Checked
            else:
                return Qt.Unchecked
        elif role == Qt.BackgroundRole:
            if self.valList[index.row()][0]:
                return None
            else:
                return QColor(cons.ERROR_COLOR)
        elif role == Qt.ToolTipRole:
            if self.valList[index.row()][0]:
                if self.elementType == CustomComboBox:
                    return formatTooltip(self.listElements[index.row()].description)
                else:
                    return None
            else:
                return formatTooltip(self.valList[index.row()][1])
        else:
            return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        return self.header

    def setData(self, index, value, role=Qt.EditRole):

        if not index.isValid() or role != Qt.EditRole or value in self.listElements:
            return False
        self.listElements[index.row()] = value
        res = self.validation(self.listElements[index.row()])
        self.valList[index.row()] = [res[0], res[1]]
        self.manage_incomplete_fields()
        self.dataChanged.emit(index, index)
        self.view.selectionModel().reset()
        return True

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable

    def addNewRow(self, value):
        if value in self.listElements:
            return False
        self.beginInsertRows(QModelIndex(), len(self.listElements), len(self.listElements))
        self.listElements.append(value)
        res = self.validation(value)
        self.valList.append([res[0], res[1]])
        self.manage_incomplete_fields()
        self.endInsertRows()
        index = self.index(0, 0)
        self.dataChanged.emit(index, index)
        return True

    def removeSpecificRow(self, row):
        self.beginRemoveRows(QModelIndex(), row, row)
        ret = self.listElements.pop(row)
        self.valList.pop(row)
        self.manage_incomplete_fields()
        self.endRemoveRows()
        self.dataChanged.emit(self.index(0, 0), self.index(0, 0))
        return ret

    def removeListRows(self, list_QIndexes):
        ret = []
        for i in sorted(list(x.row() for x in list_QIndexes))[::-1]:
            ret += [self.removeSpecificRow(i)]
        return ret

    def deleteAll(self):
        self.beginRemoveRows(QModelIndex(), 0, self.rowCount())
        self.listElements = []
        self.valList = []
        self.manage_incomplete_fields()
        self.endRemoveRows()
        self.dataChanged.emit(self.index(0, 0), self.index(0, 0))

    def manage_incomplete_fields(self):
        if self.father is None:
            return
        have_incomplete_rows = False
        for x in self.valList:
            if not x[0]:
                have_incomplete_rows = True
                break

        if have_incomplete_rows:
            self.father.superParent.register_incomplete_entries(self.father.objectName(), self.tableName)
        else:
            self.father.superParent.unregister_incomplete_entries(self.father.objectName(), self.tableName)

    def get_all_items(self):
        try:
            if self.elementType == CustomComboBox:
                ret = []
                for x in self.listElements:
                    ret.append(x)
                return ret
            else:
                return self.listElements
        except:
            return self.listElements

    def contains(self, element):
        return element in self.listElements


def formatTooltip(text):
    return "<font>" + text + "</font>"
