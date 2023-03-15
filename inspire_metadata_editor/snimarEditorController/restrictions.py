# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarEditorController/restrictions.py
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
from qgis.PyQt import QtCore as qcore
from qgis.PyQt import QtGui as qgui
from qgis.PyQt import QtWidgets as qwidgets

# UI generated python modules
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QToolTip, QDateTimeEdit, QWidget
from qgis.PyQt.QtGui import QCursor
from qgis._gui import QgsFilterLineEdit

from EditorMetadadosMarswInforbiomares.snimarQtInterfaceView.pyuic4GeneratedSourceFiles import restrictionsPanel
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import table_list_aux as tla
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import listRowsValidation as lval
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import customComboBoxModel as customCombo
from EditorMetadadosMarswInforbiomares.CONSTANTS import Scopes as SCOPES


class RestrictionsWidget(QWidget, restrictionsPanel.Ui_restrictions):
    def __init__(self, parent, scope):
        super(RestrictionsWidget, self).__init__(parent)
        self.setupUi(self)
        self.superParent = self.parent()
        self.scope = scope

        self.combo_items_md_restrictionscode = customCombo.dic_to_CustomComboBox_dic(
            self.superParent.codelist["MD_RestrictionCode"])
        self.combo_items_md_classificationcode = customCombo.dic_to_CustomComboBox_dic(
            self.superParent.codelist["MD_ClassificationCode"])
        self.listValidation = lval.Restrictions(list(self.combo_items_md_classificationcode.values()),
                                                list(self.combo_items_md_restrictionscode.values()))

        tla.setupListView(self.useLimitation, QgsFilterLineEdit, self)
        tla.setupListView(self.accessConstraints, customCombo.CustomComboBox, self, comboList=list(self.combo_items_md_restrictionscode.values()),
                          validationfunction=self.listValidation.accessConstraints)
        tla.setupListView(self.useConstraints, customCombo.CustomComboBox, self, comboList=list(self.combo_items_md_restrictionscode.values()),
                          validationfunction=self.listValidation.useConstraints)
        tla.setupListView(self.otherConstraints, QgsFilterLineEdit, self)

        tla.setupListView(self.securityrestrictions,
                          customCombo.CustomComboBox,
                          self,
                          comboList=list(self.combo_items_md_classificationcode.values()),
                          validationfunction=self.listValidation.securityrestrictions)

        for btn in self.findChildren(qwidgets.QPushButton, qcore.QRegExp('btn_*')):
            if '_add_' in btn.objectName():
                btn.setIcon(qgui.QIcon(':/resourcesFolder/icons/plus_icon.svg'))
                btn.setText('')
            elif '_del_' in btn.objectName():
                btn.setIcon(qgui.QIcon(':/resourcesFolder/icons/delete_icon.svg'))
                btn.setText('')
        for info in self.findChildren(qwidgets.QPushButton, qcore.QRegExp('info_*')):
            info.setIcon(qgui.QIcon(':/resourcesFolder/icons/help_icon.svg'))
            info.setText('')
            info.pressed.connect(self.printHelp)

        tla.setupMandatoryField(self, self.useLimitation, self.label_useLimitation, u"Obrigatório conter pelomenos uma entrada")
        tla.setupMandatoryField(self, self.accessConstraints, self.label_accessConstraints, u"Obrigatório conter pelomenos uma entrada")
        tla.setupMandatoryField(self, self.useConstraints, self.label_useConstraints, u"Obrigatório conter pelo menos uma entrada")

        self.accessConstraints.model().rowsInserted.connect(self.check_others)
        self.accessConstraints.model().rowsRemoved.connect(self.check_others)
        self.useConstraints.model().rowsInserted.connect(self.check_others)
        self.useConstraints.model().rowsRemoved.connect(self.check_others)

        self.eater = tla.EatWheel()
        for x in self.findChildren(qwidgets.QComboBox):
            x.installEventFilter(self.eater)
            x.setFocusPolicy(Qt.StrongFocus)
        for x in self.findChildren(QDateTimeEdit):
            x.installEventFilter(self.eater)
            x.setFocusPolicy(Qt.StrongFocus)

    @qcore.pyqtSlot()
    def printHelp(self):
        QToolTip.showText(QCursor.pos(), tla.formatTooltip(self.superParent.helps['restrictionsPanel'][self.sender().objectName()]), None)

    def get_data(self, md):
        """Updates the md object with the data in the restrictions snimarEditorController"""

        if self.scope != SCOPES.SERVICES:
            common = md.identification
        else:
            common = md.serviceidentification
        common.securityconstraints = self.securityrestrictions.model().get_all_items()
        common.uselimitation = self.useLimitation.model().get_all_items()
        common.accessconstraints = self.accessConstraints.model().get_all_items()
        common.useconstraints = self.useConstraints.model().get_all_items()
        common.otherconstraints = self.otherConstraints.model().get_all_items()

        return md

    def set_data(self, md):
        if md is None:
            return None
        if self.scope != SCOPES.SERVICES:
            common = md.identification
        else:
            common = md.serviceidentification
        if common is None:
            return
        for row in common.securityconstraints:
            if self.combo_items_md_classificationcode.get(row) is None:
                self.securityrestrictions.model().addNewRow(
                    customCombo.CodeListItem(row, row, row))
            else:
                self.securityrestrictions.model().addNewRow(self.combo_items_md_classificationcode[row])

        for row in common.useconstraints:
            if self.combo_items_md_restrictionscode.get(row) is None:
                self.useConstraints.model().addNewRow(
                    customCombo.CodeListItem(row, row, row))
            else:
                self.useConstraints.model().addNewRow(self.combo_items_md_restrictionscode[row])

        for row in common.accessconstraints:
            if self.combo_items_md_restrictionscode.get(row) is None:
                self.accessConstraints.model().addNewRow(
                    customCombo.CodeListItem(row, row, row))
            else:
                self.accessConstraints.model().addNewRow(self.combo_items_md_restrictionscode[row])

        for row in common.uselimitation:
            if row is not None and row.strip() != "":
                self.useLimitation.model().addNewRow(row)

        for row in common.otherconstraints:
            if row is not None and row.strip() != "":
                self.otherConstraints.model().addNewRow(row)

    def check_others(self):

        bucket = [x.term for x in self.accessConstraints.model().get_all_items()] + [x.term for x in
                                                                                     self.useConstraints.model().get_all_items()]
        if 'otherRestrictions' in bucket:
            tla.setupMandatoryField(self, self.otherConstraints, self.label_otherConstraints, u"Obrigatório conter pelo menos uma entrada")
        else:
            tla.unsetupMandatoryField(self, self.otherConstraints, self.label_otherConstraints)
