# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarEditorController/models/table_list_aux.py
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
import types
from qgis.gui import QgsFilterLineEdit

from qgis.PyQt.QtCore import QDateTime, QObject, QEvent
from qgis.PyQt.QtWidgets import QLineEdit, QComboBox, QDoubleSpinBox, QAbstractItemView, QPushButton, QSpinBox, QDialog, QHeaderView, QCheckBox, QListView, QPlainTextEdit, QTableView, QDateTimeEdit, QDateEdit

from EditorMetadadosMarswInforbiomares.snimarEditorController.models.listModel import ListModel
from EditorMetadadosMarswInforbiomares.snimarEditorController.models.tableModel import TableModel
from EditorMetadadosMarswInforbiomares.snimarEditorController.models.delegates import DoubleSpinBoxDelegate, SpinBoxDelegate, ComboBoxDelegate, \
    DateEditDelegate, CustomComboBoxDelegate, QDateTimeEditDelegate, QgsFilterLineEditDelegate
from EditorMetadadosMarswInforbiomares import CONSTANTS as cons
from EditorMetadadosMarswInforbiomares.snimarEditorController.models.customComboBoxModel import CustomComboBox, CustomComboBoxModel


def addToListView(list, box, format_Date=cons.DATE_TIME_FORMAT, raw=False, combo=False):
    if raw and combo:
        list.model().addNewRow(box.itemData(box.currentIndex()))
    elif type(box) == QDateEdit:
        list.model().addNewRow(box.date())
    else:
        ret = getText(box, format_date=format_Date)
        if ret is None or ret == "":
            return
        if hasattr(box, 'clear'):
            box.clear()
        list.model().addNewRow(ret)
    list.scrollToBottom()


def removeSelectedFromList(list, combo=None):
    if list.selectionModel().hasSelection() and list.model().rowCount() > 0:
        list.model().removeListRows(list.selectionModel().selectedRows())
        list.selectionModel().reset()  # to clear the selected row


def addToTableView(table, dataSources, mandatorysources, date_format=cons.DATE_TIME_FORMAT):
    to_add_line = []
    i = 0
    for box in dataSources:
        if type(box) in [QComboBox, CustomComboBox]:
            text = box.itemData(box.currentIndex())
        elif type(box) == QDateEdit:
            text = box.date()
        else:
            text = getText(box, date_format)

        if text is None and i in mandatorysources:
            return
        to_add_line.append(text)
        i += 1
    for box in dataSources:
        if hasattr(box, 'clear') and type(box) not in [QDateEdit, QDateTimeEdit]:
            box.clear()
    table.model().addNewRow(to_add_line)
    table.scrollToBottom()


def getText(box, format_date=cons.DATE_TIME_FORMAT):
    ret_qString = None
    if type(box) == QLineEdit or type(box) == QgsFilterLineEdit:
        ret_qString = box.text().strip()
    elif type(box) == QComboBox:
        ret_qString = box.currentText().strip()
    elif type(box) == QDateTimeEdit:
        if box.dateTime().toString() == "":
            ret_qString = ""
        else:
            ret_qString = box.dateTime().toString(format_date).strip()
    elif type(box) == QSpinBox or type(box) == QDoubleSpinBox:
        ret_qString = box.value()
    elif type(box) == QCheckBox:
        return box.isChecked()
    if len(str(ret_qString)) == 0:
        return None
    else:
        return ret_qString


def setupListView(listView, elementType, parent, comboList=[], fraction_flag=False,
                  double_precision=[999999999, -999999999, 7], validationfunction=lambda x: [True, None],
                  date_format=cons.DATE_TIME_FORMAT, NoParent=False):
    if not NoParent:
        listViewModel = ListModel(parent, elementType, listView.objectName(), fraction_flag, listView,
                                  validationfunction=validationfunction)
    else:
        listViewModel = ListModel(parent.parent, elementType, listView.objectName(), fraction_flag, listView,
                                  validationfunction=validationfunction)
    listView.setModel(listViewModel)
    comboBox = None
    raw = False
    # setup Delegates

    if elementType == QDoubleSpinBox:
        listView.setItemDelegate(DoubleSpinBoxDelegate(parent, double_precision))
        sourceBox = parent.findChild(QDoubleSpinBox, 'spin_' + listView.objectName())
    elif elementType == QSpinBox:
        listView.setItemDelegate(SpinBoxDelegate(parent))
        sourceBox = parent.findChild(QSpinBox, 'spin_' + listView.objectName())
    elif elementType == QDateTimeEdit:
        listView.setItemDelegate(QDateTimeEditDelegate(parent))
        sourceBox = parent.findChild(QDateTimeEdit, 'date_' + listView.objectName())
    elif elementType == QDateEdit:
        listView.setItemDelegate(DateEditDelegate(parent))
        sourceBox = parent.findChild(QDateEdit, 'date_' + listView.objectName())
    elif elementType == QComboBox:
        listView.setItemDelegate(ComboBoxDelegate(parent, comboList))
        sourceBox = parent.findChild(QComboBox, 'combo_' + listView.objectName())
        sourceBox.addItems(comboList.sort())
        sourceBox.model()
        comboBox = sourceBox
    elif elementType == CustomComboBox:
        listView.setItemDelegate(CustomComboBoxDelegate(parent, comboList))
        sourceBox = parent.findChild(QComboBox, 'combo_' + listView.objectName())
        sourceBox.setModel(CustomComboBoxModel(parent, sorted(comboList, key=lambda x: x.term_pt)))
        comboBox = sourceBox
        raw = True
    else:
        listView.setItemDelegate(QgsFilterLineEditDelegate(parent))
        sourceBox = parent.findChild(QgsFilterLineEdit, 'line_' + listView.objectName())

    listView.setSelectionMode(QAbstractItemView.ContiguousSelection)
    # buttons
    addButton = parent.findChild(QPushButton, 'btn_add_' + listView.objectName())
    removeButton = parent.findChild(QPushButton, 'btn_del_' + listView.objectName())

    addButton.clicked.connect(lambda: addToListView(listView, sourceBox, date_format, raw=raw, combo=comboBox))
    removeButton.clicked.connect(lambda: removeSelectedFromList(listView, combo=comboBox))


def setupTableView(parent, tableView, header, columnsTypes, addSources, comboList=None, double_precision=[999999999, -999999999, 7],
                   validationfunction=lambda x: [True, None], mandatorysources=[],
                   date_format=cons.DATE_TIME_FORMAT,
                   model_data=None):
    comboIter = 0

    if addSources is not None:
        if type(addSources) != list:
            model = TableModel(parent, header, columnsTypes, tableView, validationfunction=validationfunction, isEditable=False,
                               initial_data=model_data)
        else:
            model = TableModel(parent, header, columnsTypes, tableView, validationfunction=validationfunction, initial_data=model_data)
            for i in range(0, len(columnsTypes), 1):
                if columnsTypes[i] == QComboBox:
                    tableView.setItemDelegateForColumn(i, ComboBoxDelegate(parent, sorted(comboList[comboIter])))
                    comboIter += 1
                elif columnsTypes[i] == CustomComboBox:
                    tableView.setItemDelegateForColumn(i,
                                                       CustomComboBoxDelegate(parent, sorted(list(comboList[comboIter].values()),
                                                                                             key=lambda x: x.term_pt)))
                    comboIter += 1
                    raw = True
                elif columnsTypes[i] == QDateTimeEdit:
                    tableView.setItemDelegateForColumn(i, QDateTimeEditDelegate(parent))
                elif columnsTypes[i] == QDateEdit:
                    tableView.setItemDelegateForColumn(i, DateEditDelegate(parent))
                elif columnsTypes[i] == QSpinBox:
                    tableView.setItemDelegateForColumn(i, SpinBoxDelegate(parent))
                elif columnsTypes[i] == QDoubleSpinBox:
                    tableView.setItemDelegateForColumn(i, DoubleSpinBoxDelegate(parent, double_precision))
                elif columnsTypes[i] == QgsFilterLineEdit:
                    tableView.setItemDelegateForColumn(i, QgsFilterLineEditDelegate(parent))
    else:
        model = TableModel(parent, header, columnsTypes, tableView, validationfunction=validationfunction, initial_data=model_data)
    tableView.setModel(model)
    tableView.resizeColumnsToContents()

    tableView.verticalHeader().setVisible(False)
    tableView.resizeRowsToContents()
    tableView.verticalHeader().setMinimumSectionSize(40)
    tableView.verticalHeader().setDefaultSectionSize(40)
    tableView.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
    tableView.setSelectionMode(QAbstractItemView.ContiguousSelection)

    if addSources is not None:
        if type(addSources) != list:
            addButton = parent.findChild(QPushButton, 'btn_open_' + tableView.objectName())
            addButton.clicked.connect(lambda: callDialogAndAddNew(tableView, addSources, comboList))
        elif len(addSources) != 0:
            addButton = parent.findChild(QPushButton, 'btn_add_' + tableView.objectName())
            addButton.clicked.connect(lambda: addToTableView(tableView, addSources, mandatorysources, date_format))

        removeButton = parent.findChild(QPushButton, 'btn_del_' + tableView.objectName())
        removeButton.clicked.connect(lambda: removeSelectedFromList(tableView))


def callDialogAndAddNew(tableView, dialogType, combos=None):
    if combos is None:
        dialog = dialogType(tableView)
    else:
        dialog = dialogType(tableView, combos)
    code = dialog.exec_()
    if code == QDialog.Rejected:
        return
    data = dialog.get_data_list()
    if data is None:
        return
    else:
        tableView.model().addNewRow(data)
        tableView.scrollToBottom()


def callDialogAndEdit(tableView, dialogType, index, combos=None):
    values = tableView.model().matrix[index.row()]
    if combos is None:
        dialog = dialogType(tableView, values)
    else:
        dialog = dialogType(tableView, combos, values)
    code = dialog.exec_()
    if code == QDialog.Rejected:
        return
    data = dialog.get_data_list()
    if data is None:
        return
    else:
        tableView.model().setDataRow(index, data)


def setupMandatoryField(parent, field, fieldLabel, tooltipmsg):
    if type(field) in [QgsFilterLineEdit, QLineEdit]:
        field.textChanged.connect(lambda: checkMandatory(parent, field, fieldLabel, tooltipmsg))
    elif type(field) == QPlainTextEdit:
        field.textChanged.connect(lambda: checkMandatory(parent, field, fieldLabel, tooltipmsg))
    elif type(field) == QComboBox:
        field.currentIndexChanged.connect(lambda: checkMandatory(parent, field, fieldLabel, tooltipmsg))
    elif type(field) in [QListView, QTableView]:
        field.model().rowsInserted.connect(lambda: checkMandatory(parent, field, fieldLabel, tooltipmsg))
        field.model().rowsRemoved.connect(lambda: checkMandatory(parent, field, fieldLabel, tooltipmsg))
    elif type(field) == QDateTimeEdit:
        field.dateTimeChanged.connect(lambda: checkMandatory(parent, field, fieldLabel, tooltipmsg))
    checkMandatory(parent, field, fieldLabel, tooltipmsg)


def checkMandatory(father, field, fieldLabel, tooltipmsg):
    """
    result : False the field is not valid
            True the field is valid
    """

    result = None
    if type(field) in [QgsFilterLineEdit, QLineEdit]:
        result = checkMandatoryLineEdit(field, fieldLabel, tooltipmsg)
    elif type(field) == QPlainTextEdit:
        result = checkMandatoryPlainTextEdit(field, fieldLabel, tooltipmsg)
    elif type(field) == QComboBox:
        result = checkMandatoryComboBox(field, fieldLabel, tooltipmsg)
    elif type(field) in [QListView, QTableView]:
        result = checkMandatoryTableListView(field, fieldLabel, tooltipmsg)
    elif type(field) == QDateTimeEdit:
        result = checkMandatoryDate(field, fieldLabel, tooltipmsg)

    if father is None or result is None:
        return
    if result:
        father.superParent.unregister_mandatory_missingfield(father.objectName(), unsetLabelRed(fieldLabel.text()))
    else:  # register mandatory
        father.superParent.register_mandatory_missingfield(father.objectName(), unsetLabelRed(fieldLabel.text()))


def checkMandatorySpin(field, fieldlabel, toolTipmsg):
    if field.value() == 0 and fieldlabel.toolTip() == u"":
        label_text = setLabelRed(fieldlabel.text() + u' ' + u'\u26a0')
        fieldlabel.setText(label_text)
        fieldlabel.setToolTip(formatTooltip(toolTipmsg))
        return False

    elif field.value() != 0 and fieldlabel.toolTip() != u"":
        label_text = unsetLabelRed(fieldlabel.text().replace(u'\u26a0', '')).strip()
        fieldlabel.setText(label_text)
        fieldlabel.setToolTip(u'')
        return True
    else:
        return None


def checkMandatoryLineEdit(field, fieldlabel, toolTipmsg):
    if field.text().strip() == u"" and fieldlabel.toolTip() == u"":
        label_text = setLabelRed(fieldlabel.text() + u' ' + u'\u26a0')
        fieldlabel.setText(label_text)
        fieldlabel.setToolTip(formatTooltip(toolTipmsg))
        return False
    elif field.text().strip() != u"" and fieldlabel.toolTip() != u"":
        label_text = unsetLabelRed(fieldlabel.text().replace(u'\u26a0', '')).strip()
        fieldlabel.setText(label_text)
        fieldlabel.setToolTip(u'')
        return True
    else:
        return None


def checkMandatoryPlainTextEdit(field, fieldlabel, toolTipmsg):
    if field.toPlainText().strip() == "" and fieldlabel.toolTip() == "":
        label_text = setLabelRed(fieldlabel.text() + u' ' + u'\u26a0')
        fieldlabel.setText(label_text)
        fieldlabel.setToolTip(formatTooltip(toolTipmsg))
        return False
    elif field.toPlainText().strip() != "" and fieldlabel.toolTip() != "":
        label_text = unsetLabelRed(fieldlabel.text().replace(u'\u26a0', '')).strip()
        fieldlabel.setText(label_text)
        fieldlabel.setToolTip(u'')
        return True
    else:
        return None


def checkMandatoryComboBox(field, fieldlabel, toolTipmsg):
    if field.currentText().strip() == u"" and fieldlabel.toolTip() == u"":
        label_text = setLabelRed(fieldlabel.text() + u' ' + u'\u26a0')
        fieldlabel.setText(label_text)
        fieldlabel.setToolTip(formatTooltip(toolTipmsg))
        return False
    elif field.currentText().strip() != u"" and fieldlabel.toolTip() != u"":
        label_text = unsetLabelRed(fieldlabel.text().replace(u'\u26a0', '')).strip()
        fieldlabel.setText(label_text)
        fieldlabel.setToolTip(u'')
        return True
    else:
        return None


def checkMandatoryTableListView(field, fieldlabel, toolTipmsg):
    if field.model().rowCount() == 0 and fieldlabel.toolTip() == u"":
        label_text = setLabelRed(fieldlabel.text() + u' ' + u'\u26a0')
        fieldlabel.setText(label_text)
        fieldlabel.setToolTip(formatTooltip(toolTipmsg))
        return False
    elif field.model().rowCount() > 0 and fieldlabel.toolTip() != u"":
        label_text = unsetLabelRed(fieldlabel.text().replace(u'\u26a0', '')).strip()
        fieldlabel.setText(label_text)
        fieldlabel.setToolTip(u'')
        return True
    else:
        return None


def checkMandatoryDate(field, fieldlabel, toolTipmsg):
    if field.dateTime().toString() == "" and fieldlabel.toolTip() == u"":
        label_text = setLabelRed(fieldlabel.text() + u' ' + u'\u26a0')
        fieldlabel.setText(label_text)
        fieldlabel.setToolTip(formatTooltip(toolTipmsg))
        return False
    elif field.dateTime().toString() != "" and fieldlabel.toolTip() != u"":
        label_text = unsetLabelRed(fieldlabel.text().replace(u'\u26a0', '')).strip()
        fieldlabel.setText(label_text)
        fieldlabel.setToolTip(u'')
        return True
    else:
        return None


def setLabelRed(text):
    return '<font color=\'' + cons.ERROR_COLOR + '\'>' + unsetLabelRed(text) + "</font>"


def unsetLabelRed(text):
    return text.replace('<font color=\'' + cons.ERROR_COLOR + '\'>', '').replace("</font>", '')


def unsetupMandatoryField(father, field, fieldlabel):
    label_text = unsetLabelRed(fieldlabel.text().replace(u'\u26a0', '')).strip()
    fieldlabel.setText(label_text)
    fieldlabel.setToolTip(u"")

    if father is not None:
        father.superParent.unregister_mandatory_missingfield(father.objectName(), unsetLabelRed(fieldlabel.text()))
    try:
        if type(field) in [QgsFilterLineEdit, QLineEdit]:
            field.textChanged.disconnect()
        elif type(field) == QPlainTextEdit:
            field.textChanged.disconnect()
        elif type(field) == QComboBox:
            field.currentIndexChanged.disconnect()
        elif type(field) in [QListView, QTableView]:
            field.model().rowsInserted.disconnect()
            field.model().rowsRemoved.disconnect()
        elif type(field) == QDateTimeEdit:
            field.dateTimeChanged.disconnect()
    except Exception:
        pass


class EatWheel(QObject):
    def eventFilter(self, watched, event):
        ignore_whell_list = [QComboBox, QDateTimeEdit, QDateEdit]
        if watched is None or event is None or QEvent is None:
            return False
        if event.type() == QEvent.Wheel and type(watched) in ignore_whell_list:
            event.ignore()
            return True
        else:
            return watched.eventFilter(watched, event)


def formatTooltip(text):
    return "<font>" + text + "</font>"
