# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarEditorController/contactWidget.py
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
from qgis.PyQt import QtCore as qcore
from qgis.PyQt import QtGui as qgui
from qgis.PyQt import QtWidgets as qwidgets
import json
import os
import platform
from qgis.utils import pluginDirectory
import re
from qgis.PyQt.QtCore import Qt, QUrl
from qgis.PyQt.QtGui import QPalette, QFont, QCursor
from qgis.PyQt.QtWidgets import QMessageBox, QToolTip, QDateTimeEdit, QDateEdit, QWidget
from qgis._gui import QgsFilterLineEdit
from EditorMetadadosMarswInforbiomares.snimarQtInterfaceView.pyuic4GeneratedSourceFiles.dialogs import contactInlinePanel
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import table_list_aux as tla
from EditorMetadadosMarswInforbiomares.snimarEditorController.dialogs import contacts_dialog
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import customComboBoxModel as customCombo
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import listRowsValidation as lval

from EditorMetadadosMarswInforbiomares.snimarProfileModel import snimarProfileModel

CONTACTFILE = os.path.join(os.path.join(os.path.abspath(os.path.expanduser('~')), '.snimar'), 'contact_list.json')
validator = lval.InlineContact()
OUTRA = "Outra - Especificar Abaixo"


class InlineContactWidget(QWidget, contactInlinePanel.Ui_contactWidget):
    def __init__(self, parent, orgslist, in_distribution=False):
        super(InlineContactWidget, self).__init__(parent)
        self.parent = parent
        self.superParent = parent.superParent
        self.setupUi(self)
        if platform.system() != "Linux":
            font = QFont()
            font.setFamily(u"Segoe UI Symbol")
            self.setFont(font)

        self.orgs = {}
        org = orgslist
        for x in org:
            name = org[x] + " (" + x + ")"
            self.orgs[x] = customCombo.CodeListItem(name, name, name)

        self.combo_org.setModel(
            customCombo.CustomComboBoxModel(self,
                                            [customCombo.CodeListItem(OUTRA, OUTRA, OUTRA)] + sorted(list(self.orgs.values()),
                                                                                                     key=lambda
                                                                                                         x: x.term_pt)))
        self.combo_org.currentIndexChanged.connect(self.check_org)

        # initialized where because if was on the spot the c++ garbage collector will destroy it and cause a error
        self.dialog = None
        tla.setupListView(self.phone, QgsFilterLineEdit, self, NoParent=True)
        tla.setupListView(self.email, QgsFilterLineEdit, self, NoParent=True)
        tla.setupListView(self.fax, QgsFilterLineEdit, self, NoParent=True)

        tla.setupMandatoryField(None, self.organization, self.label_organization,
                                tla.formatTooltip(u"Elemento Obrigatório."))
        tla.setupMandatoryField(None, self.email, self.label_email,
                                tla.formatTooltip(
                                    u"Deve ser indicado pelo menos um endereço eletrónico (\'<em>email</em>\')."))

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
        f = open(os.path.join(pluginDirectory('EditorMetadadosMarswInforbiomares'), 'resourcesFolder/stylesheet.qtcss'))
        self.sytlesheet = f.read()
        for btn in self.findChildren(qwidgets.QPushButton):
            btn.setStyleSheet(self.sytlesheet)
            btn.setFocusPolicy(Qt.NoFocus)
        self.name.editingFinished.connect(self.updateTitle)
        self.organization.textChanged.connect(self.updateTitle)
        self.city.editingFinished.connect(self.updateTitle)
        self.country.editingFinished.connect(self.updateTitle)
        self.email.model().dataChanged.connect(self.updateTitle)
        self.btn_del_contact.clicked.connect(self.deleteContact)
        self.btn_contact_list.clicked.connect(self.importFromListContacts)
        self.btn_addto_list_contacts.clicked.connect(self.addtoListOfContacts)
        self.mGroupBox.collapsedStateChanged.connect(self.hideButtons)
        self.btn_del_contact.setToolTip(tla.formatTooltip(u"Agagar contacto."))
        self.updateTitle()

        self.btn_addto_list_contacts.setIcon(qgui.QIcon(':/resourcesFolder/icons/save_icon.svg'))
        self.btn_addto_list_contacts.setToolTip(tla.formatTooltip(u"Guardar contacto na Lista de Contactos."))
        self.btn_contact_list.setIcon(qgui.QIcon(':/resourcesFolder/icons/contactsList_icon.svg'))
        self.btn_contact_list.setToolTip(u'Importar da Lista de Contactos')
        self.btn_contact_list.setText('')
        self.btn_addto_list_contacts.setText('')
        self.eater = tla.EatWheel()
        for x in self.findChildren(qwidgets.QComboBox):
            x.installEventFilter(self.eater)
            x.setFocusPolicy(Qt.StrongFocus)
        for x in self.findChildren(QDateTimeEdit):
            x.installEventFilter(self.eater)
            x.setFocusPolicy(Qt.StrongFocus)
        for x in self.findChildren(QDateEdit):
            x.installEventFilter(self.eater)
            x.setFocusPolicy(Qt.StrongFocus)

        if in_distribution:
            temp = {}
            temp["distributor"] = {}
            temp["distributor"]["en"] = "distributor"
            temp["distributor"]["pt"] = "Distribuidor"
            temp["distributor"]["description"] = "Distribuidor"

            self.roles = customCombo.dic_to_CustomComboBox_dic(temp)
            self.combo_role.setModel(
                customCombo.CustomComboBoxModel(self, sorted(list(self.roles.values()), key=lambda x: x.term_pt)))
            self.combo_role.setDisabled(True)
        else:
            self.roles = customCombo.dic_to_CustomComboBox_dic(self.superParent.codelist["CI_RoleCode"])
            self.combo_role.setModel(
                customCombo.CustomComboBoxModel(self, sorted(list(self.roles.values()), key=lambda x: x.term_pt)))
            tla.setupMandatoryField(None, self.combo_role, self.label_role,
                                    u"Tem que ser especificada uma função para o contacto.")
            self.combo_role.currentIndexChanged.connect(self.check_mandatory_completude)

    def printHelp(self):
        QToolTip.showText(QCursor.pos(),
                          tla.formatTooltip(self.superParent.helps['contactInlinePanel'][self.sender().objectName()]),
                          None)

    def updateTitle(self):

        texto = self.email.model().data(self.email.model().index(0, 0))
        if texto is None:
            texto = self.name.text().strip()

        texto += u" \u21D2 " + self.organization.text() + "-" + self.city.text() + "-" + self.country.text()
        texto = re.sub(r"^\-*", "", texto.strip())
        texto = re.sub(r"\-*$", "", texto.strip())
        texto = re.sub(r'\-\-+', '-', texto.strip())
        if texto.strip() == u'\u21D2':
            palette = QPalette()
            palette.setColor(QPalette.Text, Qt.red)
            self.mGroupBox.setPalette(palette)
            self.mGroupBox.setTitle(u"Contacto Incompleto \u26a0")
            self.setToolTip(u"Contacto Incompleto.")
        elif self.email.model().rowCount() == 0 or self.organization.text() == "":
            palette = QPalette()
            palette.setColor(QPalette.Text, Qt.red)
            self.mGroupBox.setPalette(palette)
            self.mGroupBox.setTitle(texto)
            self.setToolTip(u"Contacto Incompleto.")
        else:
            palette = QPalette()
            palette.setColor(QPalette.Text, Qt.black)
            self.mGroupBox.setPalette(palette)
            self.mGroupBox.setTitle(texto)
            self.setToolTip(u"")
        self.check_mandatory_completude()

    def deleteContact(self):
        message = qwidgets.QMessageBox()
        message.setModal(True)
        message.setWindowTitle(u'Remover contacto?')
        message.setIcon(qwidgets.QMessageBox.Warning)
        message.setText(u"Tem a certeza que pretende remover contacto?\n(Operação Irreversivel!)")
        message.addButton(u'Remover', qwidgets.QMessageBox.AcceptRole)
        message.addButton(u'Cancelar', qwidgets.QMessageBox.RejectRole)
        ret = message.exec_()
        if ret == qwidgets.QMessageBox.AcceptRole:
            self.parent.deleteContact(self)
        else:
            return

    def importFromListContacts(self):
        self.dialog = contacts_dialog.ContactsDialog(self.superParent.parent(), edition_mode=False)
        self.dialog.btn_add_contact_metadata.clicked.connect(
            lambda: self.loadContactObject(self.dialog.output_contact()))
        self.dialog.exec_()

    def addtoListOfContacts(self):

        if self.organization.text() == "" or self.email.model().rowCount() == 0:
            failmsg = QMessageBox()
            failmsg.setText(u"Contacto Incompleto.")
            failmsg.setIcon(QMessageBox.Critical)
            failmsg.setModal(True)
            failmsg.setWindowTitle(u"Editor SNIMar")
            failmsg.exec_()
            return

        current_contact = self.generate_contact_object()
        current_contact['name'] = str(self.name.text())
        current_contact['organization'] = str(self.organization.text())
        current_contact['delivery_point'] = str(self.address.text())
        current_contact['city'] = str(self.city.text())
        current_contact['postalcode'] = str(self.postalCode.text())
        current_contact['country'] = str(self.country.text())

        items = [str(self.phone.model().data(self.phone.model().index(row, 0))) for row in range(
            self.phone.model().rowCount())]
        current_contact['phone'] = items

        items = [str(self.email.model().data(self.email.model().index(row, 0))) for row in range(
            self.email.model().rowCount())]
        current_contact['email'] = items

        items = [str(self.fax.model().data(self.fax.model().index(0, row))) for row in range(
            self.fax.model().rowCount())]
        current_contact['fax'] = items

        current_contact['online'] = str(self.online.text())
        try:
            with open(CONTACTFILE, 'r') as fp:
                contact_array = json.load(fp)
        except Exception:
            contact_array = []

        current_contact['index'] = len(contact_array)
        contact_array.append(current_contact)

        with open(CONTACTFILE, 'w') as fp:
            json.dump(contact_array, fp)

        msg = QMessageBox()
        msg.setText(u"Contacto gravado na lista de contactos.")
        msg.setIcon(QMessageBox.Information)
        msg.setModal(True)
        msg.setWindowTitle(u"Editor SNIMar")
        msg.exec_()

    def loadContactObject(self, contactObject):
        self.name.clear()
        self.organization.clear()
        self.phone.model().deleteAll()
        self.fax.model().deleteAll()

        self.email.model().deleteAll()
        self.address.clear()
        self.city.clear()
        self.postalCode.clear()
        self.country.clear()
        self.online.clear()

        if contactObject is not None:
            self.name.setText(contactObject['name'])
            # self.organization.setText(contactObject['organization'])
            if contactObject['organization']:
                self.set_org(contactObject['organization'])
            # self.organization.setText(contact_source.organization)
            else:
                self.set_org("")
            self.address.setText(contactObject['delivery_point'])
            self.city.setText(contactObject['city'])
            self.postalCode.setText(contactObject['postalcode'])
            self.country.setText(contactObject['country'])
            self.online.setText(contactObject['online'])
            for x in contactObject['phone']:
                self.phone.model().addNewRow(x)
            for x in contactObject['fax']:
                self.fax.model().addNewRow(x)
            for x in contactObject['email']:
                self.email.model().addNewRow(x)

    def generate_contact_object(self):
        """Returns an empty contact dict"""
        d = {}
        d['index'] = -1
        d['name'] = None
        d['organization'] = None
        d['delivery_point'] = None
        d['city'] = None
        d['postalcode'] = None
        d['country'] = None
        d['phone'] = []
        d['fax'] = []
        d['email'] = []
        d['online'] = []
        return d

    def check_mandatory_completude(self):
        self.parent.check_contacts_completness()

    def isComplete(self):
        if self.email.model().rowCount() > 0 and self.organization.text() != "" and self.combo_role.currentText() != "":
            return True
        else:
            return False

    def hideButtons(self):
        if self.mGroupBox.isCollapsed():
            self.frame.hide()
        else:
            self.frame.show()

    def get_role(self):
        temp = self.combo_role.itemData(self.combo_role.currentIndex())
        if temp is None:
            return ""
        else:
            return temp.term

    def set_data(self, contact_source):
        if contact_source is None:
            return None
        if contact_source.name:
            self.name.setText(contact_source.name)
        if contact_source.organization:
            self.set_org(contact_source.organization)
            # self.organization.setText(contact_source.organization)
        else:
            self.set_org("")
        if contact_source.address:
            self.address.setText(contact_source.address)
        if contact_source.country:
            self.country.setText(contact_source.country)
        if contact_source.city:
            self.city.setText(contact_source.city)
        if contact_source.postcode:
            self.postalCode.setText(contact_source.postcode)
        if contact_source.phone:
            for phone in contact_source.phone:
                if phone is None:
                    continue
                self.phone.model().addNewRow(phone)
        if contact_source.email:
            for email in contact_source.email:
                if email is None:
                    continue
                self.email.model().addNewRow(email)
        if contact_source.fax:
            for fax in contact_source.fax:
                if fax is None:
                    continue
                self.fax.model().addNewRow(fax)
        if contact_source.onlineresource:
            self.online.setText(contact_source.onlineresource.url)
        if contact_source.role:
            role = self.roles.get(contact_source.role)
            if role is not None:
                self.combo_role.setCurrentIndex(self.combo_role.findText(role.term_pt))

    def get_data(self):
        new_contact = snimarProfileModel.CI_ResponsibleParty()
        role = self.combo_role.itemData(self.combo_role.currentIndex())
        new_contact.role = role.term
        new_contact.role_pt = role.term_pt
        new_contact.organization = str(self.organization.text())
        new_contact.email = self.email.model().listElements
        new_contact.fax = self.fax.model().listElements
        new_contact.phone = self.phone.model().listElements
        if self.online.text() is not None and self.online.text() != '':

            onlineresource = snimarProfileModel.iso.CI_OnlineResource()
            onlineresource.url = self.online.text()
            new_contact.onlineresource = onlineresource

        var = str(self.address.text())
        if var:
            new_contact.address = var
        var = str(self.country.text())
        if var:
            new_contact.country = var
        var = str(self.postalCode.text())
        if var:
            new_contact.postcode = var
        var = str(self.city.text())
        if var:
            new_contact.city = var
        var = str(self.name.text())
        if var:
            new_contact.name = var
        return new_contact

    def check_org(self):
        if self.combo_org.currentText() == OUTRA:
            # NOT IN THE LIST
            self.organization.setDisabled(False)
            self.organization.setText("")
        else:
            # IN THE LIST
            self.organization.setDisabled(True)
            self.organization.setText(self.combo_org.currentText())

    def set_org(self, org_name):

        if org_name in [x.term for x in list(self.orgs.values())]:
            self.combo_org.setCurrentIndex(self.combo_org.findText(org_name))
        else:
            self.combo_org.setCurrentIndex(0)
            self.check_org()
            self.organization.setText(org_name)
