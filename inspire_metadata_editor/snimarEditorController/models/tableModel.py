# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarEditorController/models/tableModel.py
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
from builtins import range
import operator
import unicodedata

from qgis.PyQt.QtCore import QAbstractTableModel, QModelIndex, Qt, QSize, QDate
from qgis.PyQt.QtWidgets import QLineEdit, QCheckBox, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox, QHeaderView, QTableView, QLabel, QDateTimeEdit
from qgis.PyQt.QtGui import QBrush, QColor, QStandardItem
from qgis._gui import QgsFilterLineEdit
from EditorMetadadosMarswInforbiomares import CONSTANTS as cons
from EditorMetadadosMarswInforbiomares.snimarEditorController.models.customComboBoxModel import CustomComboBox


def rm_accents(input_str):
    if isinstance(input_str, str):
        nfkd_form = unicodedata.normalize('NFKD', input_str)
        only_ascii = nfkd_form.encode('ASCII', 'ignore')
        return only_ascii


class TableModel(QAbstractTableModel):
    def __init__(self, parent, header, type_mappings, table_view, isEditable=True, validationfunction=lambda x: [True, None],
                 initial_data=None):
        self.header = header
        self.matrix = initial_data if initial_data else []
        self.type_mappings = type_mappings

        self.view = table_view
        self.isEditable = isEditable
        self.validation = validationfunction
        self.valList = [[True, None]] * len(self.matrix) if initial_data else []
        self.father = parent
        self.tableName = self.father.findChild(QLabel, "label_" + self.view.objectName())

        if self.tableName is not None:
            self.tableName = self.tableName.text()

        QAbstractTableModel.__init__(self, self.view)
        self.fixTableSizes()

    def rowCount(self, parent=QModelIndex(), **kwargs):
        return len(self.matrix)

    def columnCount(self, parent=QModelIndex(), **kwargs):
        return len(self.header)

    def data(self, index, role=Qt.DisplayRole):

        return_value_types = [QLineEdit, QComboBox, QgsFilterLineEdit, QDateTimeEdit]
        adjust_size_types = [QComboBox, QDoubleSpinBox, QSpinBox, CustomComboBox]

        if not index.isValid() and index.row() >= self.rowCount() and index.column >= self.columnCount():
            return None
        elif role == Qt.DisplayRole and self.type_mappings[index.column()] in return_value_types:
            return self.matrix[index.row()][index.column()]
        elif role == Qt.DisplayRole and self.type_mappings[index.column()] == QDateEdit:
            if self.matrix[index.row()][index.column()] is None:
                return None
            else:
                return self.matrix[index.row()][index.column()].toString(cons.DATE_FORMAT)
        elif role == Qt.DisplayRole and self.type_mappings[index.column()] == CustomComboBox:
            try:
                return self.matrix[index.row()][index.column()].term_pt
            except:
                return self.matrix[index.row()][index.column()]
        elif role == Qt.DisplayRole and (
                        self.type_mappings[index.column()] == QDoubleSpinBox or self.type_mappings[index.column()] == QSpinBox):
            return str(self.matrix[index.row()][index.column()])
        elif role == Qt.EditRole:
            return self.matrix[index.row()][index.column()]
        elif role == Qt.SizeHintRole and self.type_mappings[index.column()] in adjust_size_types:
            return QSize(16, 22)
        elif role == Qt.CheckStateRole and self.type_mappings[index.column()] == QCheckBox:
            if self.matrix[index.row()][index.column()]:
                return Qt.Checked
            else:
                return Qt.Unchecked
        elif role == Qt.BackgroundRole:
            try:
                if self.valList[index.row()][0]:
                    return None
                else:
                    return QColor(cons.ERROR_COLOR)
            except IndexError:
                return None
        elif role == Qt.ToolTipRole:
            try:
                if self.valList[index.row()][0]:
                    if self.matrix[index.row()][index.column()] is None:
                        return None
                    else:
                        text = u'' + str(self.matrix[index.row()][index.column()])
                        return formatTooltip(text)
                else:
                    text = self.valList[index.row()][1]
                    return formatTooltip(text)
            except IndexError:
                return None
        else:
            return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        try:
            if role == Qt.DisplayRole and section < len(self.header):
                return self.header[section]
        except AttributeError:
            return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.CheckStateRole:
            if value == Qt.Checked:
                self.matrix[index.row()][index.column()] = True
            else:
                self.matrix[index.row()][index.column()] = False
            self.dataChanged.emit(index, index)
            return True

        if not index.isValid() or role != Qt.EditRole:
            return False
        self.matrix[index.row()][index.column()] = value
        res = self.validation(self.matrix[index.row()])
        if len(self.valList) > 0:
            self.valList[index.row()] = [res[0], res[1]]
        self.manage_incomplete_fields()
        self.dataChanged.emit(index, index)
        return True

    def setDataRow(self, index, value, role=Qt.EditRole,check_dup_on=None):
        if not index.isValid() or role != Qt.EditRole or self.contains(value):
            return False
        self.beginResetModel()
        self.matrix[index.row()] = value
        res = self.validation(self.matrix[index.row()])
        self.valList[index.row()] = [res[0], res[1]]
        self.manage_incomplete_fields()
        self.endResetModel()
        self.dataChanged.emit(index, index)
        return True

    def flags(self, index):

        if self.type_mappings[index.column()] == QCheckBox:
            return Qt.ItemIsUserCheckable | Qt.ItemIsEnabled
        if not self.isEditable:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def addNewRow(self, row_data, check_dup_on=None):
        if self.contains(row_data, check_dup_on=check_dup_on):
            return False
        self.beginInsertRows(QModelIndex(), len(self.matrix), len(self.matrix))
        res = self.validation(row_data)
        self.valList.append([res[0], res[1]])
        self.manage_incomplete_fields()
        self.matrix.append(row_data)
        index = self.index(0, len(self.matrix) - 1)
        self.endInsertRows()
        self.fixTableSizes()
        self.dataChanged.emit(index, index)
        return True

    def removeSpecificRow(self, row):
        """
        Why no comments?? Is row an Integer or a ModelIndex?????? AAAARRRGGHH
        It's an int!
        """
        self.beginRemoveRows(QModelIndex(), row, row)
        self.matrix.pop(row)
        self.valList.pop(row)
        self.manage_incomplete_fields()
        self.endRemoveRows()
        return row

    def removeListRows(self, list_QIndexes):

        for i in sorted(list(x.row() for x in list_QIndexes))[::-1]:
            self.removeSpecificRow(i)

    def fixTableSizes(self):
        self.view.setVisible(False)
        self.view.resizeRowsToContents()
        self.view.resizeColumnsToContents()
        self.view.setVisible(True)

    def manage_incomplete_fields(self):
        have_incomplete_rows = False
        for x in self.valList:
            if not x[0]:
                have_incomplete_rows = True
        try:
            if have_incomplete_rows:
                self.father.superParent.register_incomplete_entries(self.father.objectName(), self.tableName)
            else:
                self.father.superParent.unregister_incomplete_entries(self.father.objectName(), self.tableName)
        except Exception:
            pass

    def contains(self, row_elements_list, check_dup_on=None):
        if not check_dup_on:
            check_dup_on = []
        for row in self.matrix:
            for i in range(0, len(row)):
                if i in check_dup_on or check_dup_on == []:
                    if row[i] != row_elements_list[i]:
                        break
            else:
                return True
        return False

    def contains_at_column(self, value, column):
        if column >= self.columnCount():
            return False
        for row in self.matrix:
            if row[column] == value:
                return True
        return False

    def refresh(self, index):
        self.dataChanged.emit(index, index)

    def sort(self, Ncol, order):
        """Attempt to sort the tables"""
        if Ncol in [0, 1, 2, 3, 4]:
            self.layoutAboutToBeChanged.emit()
            try:
                self.matrix = sorted(self.matrix, key=lambda x: rm_accents(x[Ncol]))
            except TypeError:
                pass

            if order == Qt.DescendingOrder:
                self.matrix.reverse()
            self.layoutChanged.emit()

    def remove_all(self):
        self.beginRemoveRows(QModelIndex(), 0, 0)
        self.layoutAboutToBeChanged.emit()
        self.matrix = []
        self.endRemoveRows()
        self.layoutChanged.emit()



def formatTooltip(text):
    return "<font>" + text + "</font>"
