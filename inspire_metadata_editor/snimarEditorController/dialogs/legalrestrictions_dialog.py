# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarEditorController/dialogs/legalrestrictions_dialog.py
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
from qgis.PyQt import QtCore as qcore
from qgis.PyQt import QtGui as qgui
import platform
from qgis.PyQt.QtWidgets import QToolTip, QDialog
from qgis.PyQt.QtGui import QCursor, QFont

from EditorMetadadosMarswInforbiomares.snimarQtInterfaceView.pyuic4GeneratedSourceFiles.dialogs import chooseLegalRestrictionDialog
from EditorMetadadosMarswInforbiomares import CONSTANTS as cons
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import table_list_aux as tla
from EditorMetadadosMarswInforbiomares.snimarEditorController.models.customComboBoxModel import CustomComboBoxModel
from EditorMetadadosMarswInforbiomares.snimarQtInterfaceView.pyuic4GeneratedSourceFiles import restrictionsPanel


class LegalRestrictionsDialog(QDialog, chooseLegalRestrictionDialog.Ui_Dialog):
    def __init__(self, parent, combos, coord=None):

        if not coord:
            coord = ["", None, None, ""]
        super(LegalRestrictionsDialog, self).__init__(parent)
        if platform.system() != "Linux":
            font = QFont()
            font.setFamily(u"Segoe UI Symbol")
            self.setFont(font)
        self.setupUi(self)
        self.setModal(True)
        self.restrict_dic = combos[0]
        self.combo_accessrestrictions.setModel(CustomComboBoxModel(self, [None] + sorted(list(combos[0].values()), key=lambda x: x.term_pt)))
        self.combo_userestrictions.setModel(CustomComboBoxModel(self, [None] + sorted(list(combos[0].values()), key=lambda x: x.term_pt)))
        self.btn_cancel.clicked.connect(lambda: self.done(QDialog.Rejected))
        self.btn_add.clicked.connect(lambda: self.done(QDialog.Accepted))
        self.line_uselimitations.textChanged.connect(self.checkInput)
        self.combo_accessrestrictions.currentIndexChanged.connect(self.checkInput)
        self.combo_userestrictions.currentIndexChanged.connect(self.checkInput)
        self.line_otherrestrictions.textEdited.connect(self.checkInput)

        self.line_uselimitations.setText(coord[0])
        if coord[1] is not None:
            buf = combos[0].get(coord[1].term, None)
            if buf is not None:
                self.combo_accessrestrictions.setCurrentIndex(self.combo_accessrestrictions.findText(buf.term_pt))

        if coord[2] is not None:
            buf = combos[0].get(coord[2].term, None)
            if buf is not None:
                self.combo_userestrictions.setCurrentIndex(self.combo_userestrictions.findText(buf.term_pt))

        self.line_otherrestrictions.setText(coord[3])
        self.checkInput()

        tla.setupMandatoryField(None, self.line_uselimitations, self.label_line_uselimitations, u"Elemento Obrigatório.")
        tla.setupMandatoryField(None, self.combo_accessrestrictions, self.label_combo_accessrestrictions,
                                u"Elemento Obrigatório.")
        tla.setupMandatoryField(None, self.combo_userestrictions, self.label_combo_userestrictions, u"Elemento Obrigatório.")
        self.superParent = None
        temp = self.parent()
        while self.superParent is None:
            if issubclass(type(temp), restrictionsPanel.Ui_restrictions):
                self.superParent = temp
            else:
                temp = temp.parent()
        for info in self.findChildren(qgui.QPushButton,qcore.QRegExp('info_*')):
            info.setIcon(qgui.QIcon(':/resourcesFolder/icons/help_icon.svg'))
            info.setText('')
            info.pressed.connect(self.printHelp)

    @qcore.pyqtSlot()
    def printHelp(self):
        QToolTip.showText(QCursor.pos(), tla.formatTooltip(self.superParent.superParent.helps['chooseLegalRestrictionDialog'][self.sender().objectName()]), None)

    def get_data_list(self):
        data = [str(self.line_uselimitations.text()).strip(),
                self.combo_accessrestrictions.itemData(self.combo_accessrestrictions.currentIndex()),
                self.combo_userestrictions.itemData(self.combo_userestrictions.currentIndex()),
                str(self.line_otherrestrictions.text()).strip()]

        return data

    def checkInput(self):
        if self.line_uselimitations.text().strip() == "" or \
                        self.combo_userestrictions.currentText().strip() == "" or \
                        self.combo_accessrestrictions.currentText().strip() == "":
            self.btn_add.setDisabled(True)
        else:
            self.btn_add.setDisabled(False)

        if self.line_otherrestrictions.text().strip() == "" and (
                        self.combo_accessrestrictions.itemData(self.combo_accessrestrictions.currentIndex()) == self.restrict_dic[
                        cons.OTHER_RESTRICTIONS_STR] or \
                            self.combo_userestrictions.itemData(self.combo_userestrictions.currentIndex()) == self.restrict_dic[
                            cons.OTHER_RESTRICTIONS_STR]):
            self.btn_add.setDisabled(True)
            tla.setupMandatoryField(None, self.line_otherrestrictions, self.label_line_otherrestrictions,
                                    u"Elemento Obrigatório, se foi selecionada a opção "
                                    u"" + cons.OTHER_RESTRICTIONS_STR + u" no elementos anteriores.")
        else:
            tla.unsetupMandatoryField(None, self.line_otherrestrictions, self.label_line_otherrestrictions)
