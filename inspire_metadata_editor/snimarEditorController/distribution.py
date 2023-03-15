# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarEditorController/distribution.py
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
from qgis.PyQt import QtWidgets as qwidgets

# UI generated python modules
from qgis.PyQt.QtCore import Qt, QDateTime
from qgis.PyQt.QtWidgets import QToolTip, QDateTimeEdit, QWidget
from qgis.PyQt.QtGui import QCursor
from qgis._gui import QgsFilterLineEdit

from EditorMetadadosMarswInforbiomares.snimarQtInterfaceView.pyuic4GeneratedSourceFiles import distributionPanel
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import table_list_aux as tla
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import tablesRowsValidation as tval
from EditorMetadadosMarswInforbiomares.snimarProfileModel import snimarProfileModel
from EditorMetadadosMarswInforbiomares.snimarEditorController import contactWidget
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import customComboBoxModel as customCombo
from EditorMetadadosMarswInforbiomares.CONSTANTS import Scopes as SCOPES


class DistributionWidget(QWidget, distributionPanel.Ui_distribution):
    def __init__(self, parent, scope):
        super(DistributionWidget, self).__init__(parent)
        self.setupUi(self)
        self.superParent = self.parent()
        self.combo_items_ci_onlinefunctioncode = customCombo.dic_to_CustomComboBox_dic(
            self.superParent.codelist["CI_OnLineFunctionCode"])
        self.tableValidation = tval.Distribution(list(self.combo_items_ci_onlinefunctioncode.values()))

        tla.setupTableView(self, self.distributionformat,
                           [u'Nome do Formato', u'Versão'],
                           [QgsFilterLineEdit, QgsFilterLineEdit],
                           [self.line_name, self.line_version], mandatorysources=[0, 1],
                           validationfunction=self.tableValidation.distribuituionformat)
        self.distributionformat.horizontalHeader().setSectionResizeMode(qwidgets.QHeaderView.Stretch)

        self.combo_function.setModel(
            customCombo.CustomComboBoxModel(self, sorted(list(self.combo_items_ci_onlinefunctioncode.values()), key=lambda x: x.term_pt)))
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

        self.btn_adi_contact.setIcon(qgui.QIcon(':/resourcesFolder/icons/plus_icon.svg'))

        tla.setupMandatoryField(self, self.distributionformat, self.label_distributionformat, u"Obrigatório conter pelo "
                                                                                              u"menos uma entrada.")
        self.contacts_list = []
        self.btn_adi_contact.clicked.connect(self.addContact)
        self.eater = tla.EatWheel()
        for x in self.findChildren(qwidgets.QComboBox):
            x.installEventFilter(self.eater)
            x.setFocusPolicy(Qt.StrongFocus)
        for x in self.findChildren(QDateTimeEdit):
            x.installEventFilter(self.eater)
            x.setFocusPolicy(Qt.StrongFocus)

        self.scope = scope
        if self.scope == SCOPES.SERVICES:
            tla.setupTableView(self, self.resourcelocator,
                               [u'URL'],
                               [QgsFilterLineEdit],
                               [self.line_linkage],
                               mandatorysources=[0])
            tla.setupMandatoryField(self, self.resourcelocator, self.label_resourcelocator, u"Obrigatório conter pelo menos uma entrada.")
            self.combo_function.setHidden(True)
            self.resourcelocator.verticalHeader().hide()
        else:
            tla.setupTableView(self, self.resourcelocator,
                               [u'URL', u'Função'],
                               [QgsFilterLineEdit, customCombo.CustomComboBox],
                               [self.line_linkage, self.combo_function],
                               comboList=[self.combo_items_ci_onlinefunctioncode], mandatorysources=[0, 1],
                               validationfunction=self.tableValidation.resourcelocator)
        self.resourcelocator.horizontalHeader().setSectionResizeMode(qwidgets.QHeaderView.Stretch)

    @qcore.pyqtSlot()
    def printHelp(self):
        QToolTip.showText(QCursor.pos(), tla.formatTooltip(self.superParent.helps['distributionPanel'][self.sender().objectName()]), None)

    def set_data(self, md=None):
        if md is not None and md.distribution is not None:
            if md.distribution.size is not None:
                self.filesize.setValue(float(md.distribution.size.replace(',', '.')))

            for row in md.distribution.online:
                if row.function is None:
                    data = [row.url, None]
                else:
                    data = [row.url, self.combo_items_ci_onlinefunctioncode[row.function]]
                self.resourcelocator.model().addNewRow(data)

            for row in md.distribution.distribution_format:
                self.distributionformat.model().addNewRow(row)

            # Set contacts
            contact_index = 0
            for contact in md.distribution.distributor:
                self.addContact()
                contact_object = self.contacts_list[contact_index]
                contact_object.set_data(contact)
                contact_index += 1

    def get_data(self, md=None):

        if md.distribution is None:
            md.distribution = snimarProfileModel.MD_Distribution()

        size = self.filesize.value()
        if size != 0.:
            md.distribution.size = size

        md.distribution.distribution_format = self.distributionformat.model().matrix

        for row in self.resourcelocator.model().matrix:
            online_resource = snimarProfileModel.iso.CI_OnlineResource()
            online_resource.url = str(row[0])
            if self.scope != SCOPES.SERVICES:
                online_resource.function = self.combo_items_ci_onlinefunctioncode[row[1].term]
            md.distribution.online.append(online_resource)

        for contact in self.contacts_list:
            new_contact = contact.get_data()
            new_contact.role = 'distributor'
            new_contact.role_pt = 'Distribuidor'
            new_distributor = snimarProfileModel.iso.MD_Distributor()
            new_distributor.contact = new_contact
            md.distribution.distributor.append(new_distributor)
        return md

    def addContact(self):
        contact = contactWidget.InlineContactWidget(self,self.superParent.orgs, in_distribution=True)
        self.Contacts.insertWidget(-1, contact)
        self.Contacts.setAlignment(Qt.AlignTop)
        self.contacts_list.append(contact)
        self.check_contacts_completness()

    def deleteContact(self, contact):
        self.Contacts.removeWidget(contact)
        self.contacts_list.remove(contact)
        contact.close()
        self.check_contacts_completness()

    def check_contacts_completness(self):
        for x in self.contacts_list:
            if not x.isComplete():
                self.superParent.register_incomplete_entries(self.objectName(), "Contactos")
                return
        self.superParent.unregister_incomplete_entries(self.objectName(), "Contactos")
