# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarEditorController/dialogs/freekeywords_dialog.py
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
import platform
from qgis.PyQt.QtCore import QDate, QRegExp
from qgis.PyQt.QtWidgets import QDialog, QToolTip
from qgis.PyQt.QtGui import QCursor, QFont
from EditorMetadadosMarswInforbiomares.snimarQtInterfaceView.pyuic4GeneratedSourceFiles.dialogs import chooseFreeKeywordDialog
from qgis.PyQt import QtGui as qgui
from qgis.PyQt import QtWidgets as qwidgets
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import table_list_aux as tla
from EditorMetadadosMarswInforbiomares import CONSTANTS as cons
from EditorMetadadosMarswInforbiomares.snimarEditorController.models.customComboBoxModel import CustomComboBoxModel
from EditorMetadadosMarswInforbiomares.snimarQtInterfaceView.pyuic4GeneratedSourceFiles import keywordsPanel
from EditorMetadadosMarswInforbiomares.snimarEditorController.models.null_QDateEdit import NullQDateEditWrapper


class FreeKeyWordsDialog(QDialog, chooseFreeKeywordDialog.Ui_dialogDate):
    def __init__(self, parent, combos, coord=None):

        if not coord:
            coord = ["", None, "", None, None]
        super(FreeKeyWordsDialog, self).__init__(parent)
        if platform.system() != "Linux":
            font = QFont()
            font.setFamily(u"Segoe UI Symbol")
            self.setFont(font)
        self.setupUi(self)
        self.date_date_2 = NullQDateEditWrapper(self.date_date_2)
        self.setModal(True)
        self.combo_dataType.setModel(CustomComboBoxModel(self, [None] + sorted(list(combos[1].values()), key=lambda x: x.term_pt)))
        self.combo_dataType.setCurrentIndex(0)
        self.date_date_2.clear()
        self.combo_type.setModel(CustomComboBoxModel(self, [None] + sorted(list(combos[0].values()), key=lambda x: x.term_pt)))
        self.btn_cancelar.clicked.connect(lambda: self.done(QDialog.Rejected))
        self.line_keyword.textChanged.connect(lambda: self.check_fields())
        self.line_thesaurus.textChanged.connect(lambda: self.check_fields())
        self.combo_type.currentIndexChanged.connect(lambda: self.check_fields())
        self.combo_dataType.currentIndexChanged.connect(lambda: self.check_fields())
        self.date_date_2.get_original().dateTimeChanged.connect(lambda: self.check_fields())
        self.btn_adicionar.clicked.connect(lambda: self.done(QDialog.Accepted))
        self.btn_adicionar.setDisabled(True)
        self.combo_type.setDisabled(True)
        self.line_thesaurus.setDisabled(True)
        self.date_date_2.setDisabled(True)
        self.btn_clear_date_date_2.setDisabled(True)
        self.combo_dataType.setDisabled(True)

        self.line_keyword.setText(coord[0])
        if coord[1] is not None:
            buf = combos[0].get(coord[1].term_pt, None)
            if buf is not None:
                self.combo_type.setCurrentIndex(self.combo_type.findText(buf.term_pt))
        self.line_thesaurus.setText(coord[2])
        if coord[3] is None:
            self.date_date_2.clear()
        else:
            self.date_date_2.setDate(coord[3])
        if coord[4] is not None:
            buf = combos[1].get(coord[4].term, None)
            if buf is not None:
                self.combo_dataType.setCurrentIndex(self.combo_dataType.findText(buf.term_pt))
        self.superParent = None
        temp = self.parent()
        while self.superParent is None:
            if issubclass(type(temp), keywordsPanel.Ui_keywords):
                self.superParent = temp
            else:
                temp = temp.parent()

        for info in self.findChildren(qwidgets.QPushButton, QRegExp('info_*')):
            info.setIcon(qgui.QIcon(':/resourcesFolder/icons/help_icon.svg'))
            info.setText('')
            info.pressed.connect(self.printHelp)

        self.btn_clear_date_date_2.setIcon(qgui.QIcon(':/resourcesFolder/icons/delete_field.svg'))
        self.btn_clear_date_date_2.pressed.connect(lambda: self.date_date_2.clear())

    def get_data_list(self):

        data = self.date_date_2.get_date()
        if self.line_thesaurus.text().strip() == "":
            data = None
            self.combo_dataType.setCurrentIndex(0)

        return [self.line_keyword.text().strip(),
                self.combo_type.itemData(self.combo_type.currentIndex()),
                self.line_thesaurus.text().strip(),
                data,
                self.combo_dataType.itemData(self.combo_dataType.currentIndex())]

    def check_fields(self):
        if len(self.line_keyword.text().strip()) == 0:
            self.setMandatory(self.label_line_keyword, u"Elemento Obrigatório.")
            self.unsetMandatory(self.label_date_date_2)
            self.unsetMandatory(self.label_combo_dataType)
            self.btn_adicionar.setDisabled(True)
            self.combo_type.setDisabled(True)
            self.line_thesaurus.setDisabled(True)
            self.date_date_2.setDisabled(True)
            self.btn_clear_date_date_2.setDisabled(True)
            self.combo_dataType.setDisabled(True)
        elif len(self.line_thesaurus.text().strip()) == 0:
            self.unsetMandatory(self.label_line_keyword)
            self.unsetMandatory(self.label_date_date_2)
            self.unsetMandatory(self.label_combo_dataType)
            self.combo_type.setDisabled(False)
            self.line_thesaurus.setDisabled(False)
            self.btn_adicionar.setDisabled(False)
            self.date_date_2.setDisabled(True)
            self.btn_clear_date_date_2.setDisabled(True)
            self.combo_dataType.setDisabled(True)
        elif not self.date_date_2.get_date() is None and len(self.combo_dataType.currentText()) != 0:
            self.combo_type.setDisabled(False)
            self.line_thesaurus.setDisabled(False)
            self.btn_adicionar.setDisabled(False)
            self.date_date_2.setDisabled(False)
            self.btn_clear_date_date_2.setDisabled(False)
            self.combo_dataType.setDisabled(False)
            self.unsetMandatory(self.label_line_keyword)
            self.unsetMandatory(self.label_date_date_2)
            self.unsetMandatory(self.label_combo_dataType)
        else:
            self.unsetMandatory(self.label_line_keyword)
            self.unsetMandatory(self.label_date_date_2)
            self.unsetMandatory(self.label_combo_dataType)
            self.combo_type.setDisabled(False)
            self.line_thesaurus.setDisabled(False)
            self.btn_adicionar.setDisabled(True)
            self.date_date_2.setDisabled(False)
            self.btn_clear_date_date_2.setDisabled(False)
            self.combo_dataType.setDisabled(False)
            if self.date_date_2.get_date() is None:
                self.setMandatory(self.label_date_date_2, u"Elemento Obrigatório.")
            if len(self.combo_dataType.currentText()) == 0:
                self.setMandatory(self.label_combo_dataType, u"Elemento Obrigatório.")

    def setMandatory(self, label, toolTipmsg):
        label_text = tla.setLabelRed(label.text() + u' ' + u'\u26a0')
        label.setText(label_text)
        label.setToolTip(tla.formatTooltip(toolTipmsg))

    def unsetMandatory(self, label):
        label_text = tla.unsetLabelRed(label.text().replace(u'\u26a0', '')).strip()
        label.setText(label_text)
        label.setToolTip(u"")

    def printHelp(self):
        QToolTip.showText(QCursor.pos(),
                          tla.formatTooltip(self.superParent.superParent.helps['chooseFreeKeywordDialog'][self.sender().objectName()]),
                          None)
