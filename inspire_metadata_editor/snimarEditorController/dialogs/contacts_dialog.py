# -*- coding: utf-8 -*-

##############################################################################
#
#  Title:   snimarEditorController/dialogs/contacts_dialog.py
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

import os
import json
import platform

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QMetaObject, Qt, QRegExp
from qgis.PyQt.QtWidgets import QWidget, QToolTip, QDateTimeEdit, QDialog, QPushButton, QComboBox, QMessageBox, QListWidget, QLineEdit, QListWidgetItem
from qgis.PyQt.QtGui import QCursor, QFont, QIcon

from inspire_metadata_editor.snimarEditorController.models import table_list_aux as tla
from inspire_metadata_editor.snimarEditorController.models import customComboBoxModel as cus

from inspire_metadata_editor.snimarQtInterfaceView.pyuic4GeneratedSourceFiles.dialogs import contactListManagerWindow

from inspire_metadata_editor.gui.add_organization_dialog import AddOrganizationDialog
from inspire_metadata_editor.constants import PLUGIN_ROOT

WIDGET, BASE = uic.loadUiType(os.path.join(PLUGIN_ROOT, "ui", "contacts_dialog.ui"))

CONTACTFILE = os.path.join(os.path.join(os.path.abspath(os.path.expanduser('~')), '.snimar'), 'contact_list.json')
OUTRA = "Outra - Especificar Abaixo"


class ContactsDialog(WIDGET, BASE):
    def __init__(self, parent, edition_mode=True):
        super().__init__(parent)
        self.setupUi(self)

        if platform.system() != "Linux":
            font = QFont()
            font.setFamily(u"Segoe UI Symbol")
            self.setFont(font)

        # VIEW SETUP#############################################################
        self.superParent = self.parent()

        for btn in self.findChildren(QPushButton, QRegExp('btn_*')):
            if '_add_' in btn.objectName():
                btn.setIcon(QIcon(':/resourcesFolder/icons/plus_icon.svg'))
                btn.setText('')
            elif '_del_' in btn.objectName():
                btn.setIcon(QIcon(':/resourcesFolder/icons/delete_icon.svg'))
                btn.setText('')
            elif '_clear_' in btn.objectName():
                btn.setIcon(QIcon(':/resourcesFolder/icons/delete_field.svg'))

        lists = ['phone', 'fax', 'email']
        for item in lists:
            btn = self.findChild(QPushButton, 'btn_add_' + item)
            btn.clicked.connect(self.add_list_row)
            btn = self.findChild(QPushButton, 'btn_del_' + item)
            btn.clicked.connect(self.del_list_row)

        for info in self.findChildren(QPushButton, QRegExp('info_*')):
            info.setIcon(QIcon(':/resourcesFolder/icons/help_icon.svg'))
            info.setText('')
            info.pressed.connect(self.printHelp)

        # Contact list connections and variables
        self.contact_array = None
        self.open_contact_array()
        self.current_contact = None
        self.contact_list.clearSelection()
        self.contactPanel.setDisabled(True)

        # SETUP THE DIALOG MODE
        if edition_mode:  # EDITION MODE
            self.populate_organizations()

            self.combo_org.currentIndexChanged.connect(self.check_org)
            self.btn_contact_add.setVisible(True)
            self.btn_contact_del.setVisible(True)
            self.cancelChanges()
            self.btn_add_contact_metadata.setVisible(False)

            # CONNECTING FIELDS THAT CAN BE CHANGED
            self.name.textChanged.connect(self.changesMade)
            self.organization.textChanged.connect(self.changesMade)
            self.city.textChanged.connect(self.changesMade)
            self.postalcode.textChanged.connect(self.changesMade)
            self.country.textChanged.connect(self.changesMade)
            self.delivery_point.textChanged.connect(self.changesMade)
            self.phone.model().rowsInserted.connect(self.changesMade)
            self.fax.model().rowsInserted.connect(self.changesMade)
            self.email.model().rowsInserted.connect(self.changesMade)
            self.online.textChanged.connect(self.changesMade)
            self.phone.model().rowsRemoved.connect(self.changesMade)
            self.fax.model().rowsRemoved.connect(self.changesMade)
            self.email.model().rowsRemoved.connect(self.changesMade)
            self.online.textChanged.connect(self.changesMade)

            # SETUP MANDATORY FIELDS VISUAL VALIDATION
            self.organization.editingFinished.connect(self.setup_mandatory_label)
            self.name.editingFinished.connect(self.setup_mandatory_label)
            self.setup_mandatory_label()

            # ACTIONS SETUP
            self.btn_contact_save.clicked.connect(self.save_contact)  # save contact
            self.btn_cancelClose.clicked.connect(self.cancelChanges)  # cancel changes and revert contact
            self.btn_contact_add.clicked.connect(self.new_contact)  # add new contact if changes in current contact exists ask...
            self.btn_contact_del.clicked.connect(self.delete_contact)  # delete contact with confirmation
            self.contact_list.itemClicked.connect(self.selection_changed)  # change current selection if changes exists ask...

            self.btn_add_organization.clicked.connect(self.add_new_organization)
            self.btn_remove_organization.setIcon(QIcon(os.path.join(PLUGIN_ROOT, "resourcesFolder", "icons", "delete_icon.svg")))
            self.btn_remove_organization.clicked.connect(self.remove_organization)
        else:  # EXPORT MODE
            self.contactPanel.hide()
            self.btn_add_contact_metadata.setVisible(True)
            self.btn_contact_add.setVisible(False)
            self.btn_contact_del.setVisible(False)
            self.adjustSize()

        # ACTIONS SETUP
        self.contact_list.itemClicked.connect(self.selection_changed_export_Mode)  # change current selection
        # ACTIONS FUNCTIONS
        self.eater = tla.EatWheel()
        for x in self.findChildren(QComboBox):
            x.installEventFilter(self.eater)
            x.setFocusPolicy(Qt.StrongFocus)
        for x in self.findChildren(QDateTimeEdit):
            x.installEventFilter(self.eater)
            x.setFocusPolicy(Qt.StrongFocus)

    def printHelp(self):
        QToolTip.showText(QCursor.pos(), tla.formatTooltip(
            self.superParent.helps['contactListManagerWindow'][self.sender().objectName()]),
                          None)

    def save_contact(self):

        flags = self.mandatory_state()
        if all(flag == True for flag in list(flags.values())):
            # Get the data
            self.current_contact['name'] = str(self.name.text())
            self.current_contact['organization'] = str(self.organization.text())
            self.current_contact['delivery_point'] = str(self.delivery_point.text())
            self.current_contact['city'] = str(self.city.text())
            self.current_contact['postalcode'] = str(self.postalcode.text())
            self.current_contact['country'] = str(self.country.text())

            items = [str(self.phone.item(index).text()) for index in range(self.phone.count())]
            self.current_contact['phone'] = items

            items = [str(self.email.item(index).text()) for index in range(self.email.count())]
            self.current_contact['email'] = items

            items = [str(self.fax.item(index).text()) for index in range(self.fax.count())]
            self.current_contact['fax'] = items

            self.current_contact['online'] = str(self.online.text())
            if self.current_contact['index'] == -1:
                self.current_contact['index'] = len(self.contact_array)
                self.contact_array.append(self.current_contact)
                item_label = self.current_contact['name'] + ' - ' + self.current_contact['organization']
                self.contact_list.addItem(item_label)
                self.contact_list.setCurrentRow(self.current_contact['index'])
            else:
                self.contact_array[self.current_contact['index']] = self.current_contact
                item_label = self.current_contact['name'] + ' - ' + self.current_contact['organization']
                self.contact_list.item(self.current_contact['index']).setText(item_label)
            self.save_contact_array()
            self.present_contact()
            self.changes = False
            self.btn_cancelClose.setDisabled(True)
            self.btn_contact_save.setDisabled(True)

    def changesMade(self):
        self.changes = True
        self.btn_cancelClose.setDisabled(False)
        self.btn_contact_save.setDisabled(False)

    def cancelChanges(self):
        self.present_contact()
        self.changes = False
        self.btn_cancelClose.setDisabled(True)
        self.btn_contact_save.setDisabled(True)

    def new_contact(self):
        self.changes = True
        self.current_contact = None
        self.present_contact()
        self.current_contact = self.generate_contact_object()
        self.contact_list.clearSelection()
        self.contactPanel.setDisabled(False)

    def delete_contact(self):
        message = QMessageBox()
        message.setModal(True)
        message.setWindowTitle(self.tr('Remover contacto?'))
        message.setIcon(QMessageBox.Warning)
        message.setText(self.tr("Tem a certeza que pretende remover contacto?\n(Operação Irreversivel!)"))
        message.addButton(self.tr('Remover'), QMessageBox.AcceptRole)
        message.addButton(self.tr('Cancelar'), QMessageBox.RejectRole)
        ret = message.exec_()
        if ret == QMessageBox.AcceptRole:
            # get current selected index in list
            index = self.contact_list.currentRow()
            if index < 0:
                return
            self.contact_list.takeItem(index)
            self.contact_array.pop(index)
            self.save_contact_array()
            self.contact_list.clearSelection()
            self.contactPanel.setDisabled(True)
            self.current_contact = None
            self.present_contact()
            self.changes = False

    def selection_changed(self):
        index = self.contact_list.currentRow()
        if self.changes and self.current_contact is not None:
            message = QMessageBox()
            message.setModal(True)
            message.setWindowTitle(self.tr('Existem Alterações.'))
            message.setIcon(QMessageBox.Warning)
            message.setText(self.tr("Deseja guardar as alterações efectuadas?"))
            message.addButton(self.tr('Guardar'), QMessageBox.AcceptRole)
            message.addButton(self.tr('Cancelar'), QMessageBox.RejectRole)
            ret = message.exec_()
            if ret == QMessageBox.AcceptRole:
                self.save_contact()
        self.contactPanel.setDisabled(False)
        self.changes = False
        self.current_contact = self.contact_array[index]
        self.contact_list.setCurrentRow(index)
        self.present_contact()
        self.cancelChanges()

    def selection_changed_export_Mode(self):
        index = self.contact_list.currentRow()
        self.current_contact = self.contact_array[index]

    # CONTACT ARRAY OPERATIONS

    def save_contact_array(self):
        """Saves the current contact array to the contact_list.json"""
        with open(CONTACTFILE, 'w') as fp:
            json.dump(self.contact_array, fp)

    def open_contact_array(self):
        try:
            with open(CONTACTFILE, 'r') as fp:
                self.contact_array = json.load(fp)
        except Exception:
            self.contact_array = []
        self.fix_contact_list()
        if self.contact_array is None:
            self.contact_array = []

        if len(self.contact_array) > 0:
            list_item_texts = [(x['name'], x['organization']) for x in self.contact_array]
            items_labels = [item_text[0] + ' - ' + item_text[1] for item_text in list_item_texts]
            self.contact_list.addItems(items_labels)

    def add_list_row(self):
        """Add a new row to the specific list that shares the same name with the button that
        emits the signal that fires the slot."""
        sender_name = self.sender().objectName()
        target_list = self.findChild(QListWidget, sender_name.split('_')[2])
        target_input = self.findChild(QLineEdit, sender_name.split('_')[2] + '_input')

        if target_list is not None and target_input is not None:
            input_text = target_input.text()
            if len(input_text) > 0:
                item = QListWidgetItem(input_text)
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                target_list.addItem(item)
                target_input.setText('')

    def del_list_row(self):
        """Works like the add_list_row, but deletes the selected row from the list that shares
        its name with button that emits the signal."""
        sender_name = self.sender().objectName()
        target_list = self.findChild(QListWidget, sender_name.split('_')[2])

        index = target_list.currentRow()
        if index is not None:
            target_list.takeItem(index)
            target_list.setCurrentRow(-1)

    def present_contact(self):
        self.name.clear()
        self.organization.clear()
        self.delivery_point.clear()
        self.city.clear()
        self.postalcode.clear()
        self.country.clear()
        self.phone.clear()
        self.fax.clear()
        self.email.clear()
        self.online.clear()

        if self.current_contact is not None:
            self.name.setText(self.current_contact['name'])
            self.set_org(self.current_contact['organization'])
            # self.organization.setText(self.current_contact['organization'])
            self.delivery_point.setText(self.current_contact['delivery_point'])
            self.city.setText(self.current_contact['city'])
            self.postalcode.setText(self.current_contact['postalcode'])
            self.country.setText(self.current_contact['country'])
            self.phone.addItems(self.current_contact['phone'])
            self.fax.addItems(self.current_contact['fax'])
            self.email.addItems(self.current_contact['email'])
            self.online.setText(self.current_contact['online'])

        self.setup_mandatory_label()

    # AUX FUNCTIONS ###########################################################
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
        d['online'] = None
        return d

    def mandatory_state(self):
        """Validates that mandatory fields are written."""

        organization = len(str(self.organization.text())) > 0

        return {
            'organization': True
            }

    def setup_mandatory_label(self):
        state = self.mandatory_state()
        if not state['organization']:
            label_text = self.tr('Nome da Organização')
            label_text += u' ' + u'\u26a0'
            self.label_organization.setText(label_text)
            self.label_organization.setToolTip(self.tr('Elemento obrigatório em falta'))
        else:
            label_text = self.tr('Nome da Organização')
            self.label_organization.setText(label_text)
            self.label_organization.setToolTip(u'')

    def output_contact(self):
        return self.current_contact

    def fix_contact_list(self):
        ret = []
        for x in self.contact_array:
            x['fax'] = x.get('faxlist', [])
            x['online'] = x.get('online')[0] if x.get('online') is not None and type(x.get('online')) == list and len(
                x.get('online')) > 0 else  x.get('online')
            if not x['online']:
                x['online'] = None
            try:
                del x['faxlist']
                del x['address']
            except KeyError:
                continue
            ret.append(x)
        return ret

    def check_org(self):
        if self.combo_org.currentText() == OUTRA:
            #NOT IN THE LIST
            self.organization.setDisabled(False)
            self.organization.setText("")
        else:
            #IN THE LIST
            self.organization.setDisabled(True)
            self.organization.setText(self.combo_org.currentText())

    def set_org(self, org_name):
        if org_name in [x.term for x in list(self.orgs.values())]:
            self.combo_org.setCurrentIndex(self.combo_org.findText(org_name))
        else:
            self.combo_org.setCurrentIndex(0)
            self.check_org()
            self.organization.setText(org_name)

    def add_new_organization(self):
        dlg = AddOrganizationDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            short_name = dlg.short_name()
            full_name = dlg.full_name()

            if short_name in self.superParent.orgs:
                QMessageBox.warning(self, self.tr("Duplicate organization"), self.tr(f"Organization with '{short_name}' short name already exists!"))
                return

            self.superParent.orgs[short_name] = full_name
            with open(os.path.join(PLUGIN_ROOT, "resourcesFolder", "CodeLists", "SNIMar_ORGS.json"), "w", encoding="utf-8") as f:
                json.dump(self.superParent.orgs, f)

            self.populate_organizations()

    def remove_organization(self):
        org_name = self.combo_org.currentText()
        if org_name == "Outra - Especificar Abaixo":
            return

        key = None
        for k, v in self.superParent.orgs.items():
            if v == org_name:
                key = k
                break
        if key:
            del self.superParent.orgs[key]

        with open(os.path.join(PLUGIN_ROOT, "resourcesFolder", "CodeLists", "SNIMar_ORGS.json"), "w", encoding="utf-8") as f:
            json.dump(self.superParent.orgs, f)

        self.populate_organizations()


    def populate_organizations(self):
        self.orgs = {}
        org = self.superParent.orgs

        for x in org:
            name = org[x] + " (" + x + ")"
            self.orgs[x] = cus.CodeListItem(name, name, name)

        self.combo_org.setModel(
            cus.CustomComboBoxModel(self,
                                    [cus.CodeListItem(OUTRA, OUTRA, OUTRA)] + sorted(list(self.orgs.values()),
                                                                                     key=lambda x: x.term_pt)))
