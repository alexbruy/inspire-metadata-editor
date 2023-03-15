# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarEditorController/models/delegates.py
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
from __future__ import absolute_import
from builtins import str
import sys

from qgis.PyQt import QtCore as qcore
from qgis.PyQt import QtGui as qgui
from qgis.PyQt.QtWidgets import QItemDelegate, QPushButton

from qgis._gui import QgsFilterLineEdit
from EditorMetadadosMarswInforbiomares import CONSTANTS as cons
from .customComboBoxModel import CustomComboBoxModel


class DoubleSpinBoxDelegate(QItemDelegate):
    def __init__(self, parent, double_precision):
        self.precision = double_precision
        super(DoubleSpinBoxDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        editor = QDoubleSpinBox(parent)
        editor.setButtonSymbols(QAbstractSpinBox.NoButtons)
        editor.setSingleStep(0)
        editor.setMaximum(self.precision[0])
        editor.setMinimum(self.precision[1])
        editor.setDecimals(self.precision[2])
        return editor

    def setEditorData(self, editor, index):
        value = index.data(Qt.EditRole)
        editor.setValue(float(str(value).replace(',', '.')))

    def setModelData(self, editor, model, index):
        model.setData(index, float(editor.text().strip().replace(',', '.')), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class SpinBoxDelegate(QItemDelegate):
    def __init__(self, parent):
        super(SpinBoxDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        editor = QSpinBox(parent)
        editor.setButtonSymbols(QAbstractSpinBox.NoButtons)
        editor.setSingleStep(0)
        editor.setMaximum(100000000)

        return editor

    def setEditorData(self, editor, index):
        value = index.data(Qt.EditRole)
        editor.setValue(value)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.value(), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class QgsFilterLineEditDelegate(QItemDelegate):
    def __init__(self, parent):
        super(QgsFilterLineEditDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        editor = QgsFilterLineEdit(parent)
        editor.setSizePolicy(qcore.QSizePolicy.MinimumExpanding, qcore.QSizePolicy.MinimumExpanding)
        editor.setDisabled(True)
        editor.setDisabled(False)
        return editor

    def setEditorData(self, editor, index):
        value = index.data(Qt.EditRole)
        editor.setText(value)
        editor.setSizePolicy(qcore.QSizePolicy.MinimumExpanding, qcore.QSizePolicy.MinimumExpanding)
        editor.setDisabled(True)
        editor.setDisabled(False)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.value().strip(), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        r = option.rect
        editor.setGeometry(r)


class ComboBoxDelegate(QItemDelegate):
    def __init__(self, parent, comboItems):
        super(ComboBoxDelegate, self).__init__(parent)
        self.comboItems = comboItems

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(self.comboItems)
        return editor

    def setEditorData(self, editor, index):
        value = index.data()
        if editor.findText(value) == -1:
            editor.setCurrentIndex(0)
        else:
            editor.setCurrentIndex(editor.findText(value))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentText(), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def sizehint(self, option, index):
        return qcore.QSize(100, 100)


class CustomComboBoxDelegate(QItemDelegate):
    def __init__(self, parent, comboItems):
        super(CustomComboBoxDelegate, self).__init__(parent)
        self.comboItems = comboItems

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.setModel(CustomComboBoxModel(self, self.comboItems))
        return editor

    def setEditorData(self, editor, index):
        value = index.data()
        if editor.findData(value) == -1:
            editor.setCurrentIndex(0)
        else:
            editor.setCurrentIndex(editor.findData(value))

    def setModelData(self, editor, model, index):
        row = editor.currentIndex()
        qindex = editor.model().index(row, 0)
        model.setData(index, qindex.data(role=Qt.UserRole), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def sizehint(self, option, index):
        return qcore.QSize(100, 100)


class DateEditDelegate(QItemDelegate):
    def __init__(self, parent):
        super(DateEditDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        self.editor = QDateEdit(parent)
        self.editor.setDisplayFormat(cons.DATE_FORMAT)
        self.editor.setCalendarPopup(True)
        return self.editor

    def setEditorData(self, editor, index):
        editor.setDate(index.data(role=Qt.EditRole))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.date(), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def sizehint(self, option, index):
        return qcore.QSize(100, 100)


class QDateTimeEditDelegate(QItemDelegate):
    def __init__(self, parent):
        super(QDateTimeEditDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        self.editor = QDateTimeEdit(parent)
        self.editor.setDisplayFormat(cons.DATE_TIME_FORMAT)
        self.editor.setCalendarPopup(False)
        self.editor.setButtonSymbols(QAbstractSpinBox.NoButtons)

        return self.editor

    def setEditorData(self, editor, index):
        date = QDateTime.fromString(index.data(), cons.DATE_TIME_FORMAT)
        editor.setDateTime(date)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.dateTime().toString(cons.DATE_TIME_FORMAT), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def sizehint(self, option, index):
        return qcore.QSize(100, 100)


class ButtonDelegate(QItemDelegate):
    def __init__(self, parent, functionOwner):
        QItemDelegate.__init__(self, parent)
        self.functionOwner = functionOwner

    def paint(self, painter, option, index):
        if not self.parent().indexWidget(index):
            btn_reload = QPushButton(index.data(), self.parent())
            btn_reload.clicked.connect(lambda: self.functionOwner.update_validity(index))
            btn_reload.setMinimumSize(qcore.QSize(26, 26))
            btn_reload.setMaximumSize(qcore.QSize(26, 26))
            btn_reload.setIcon(qgui.QIcon(':/resourcesFolder/icons/refresh_icon.svg'))
            self.parent().setIndexWidget(index, btn_reload)
