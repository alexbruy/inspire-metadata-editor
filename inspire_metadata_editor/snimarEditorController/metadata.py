# -*- coding: utf-8 -*-
##############################################################################
#
#  Title:   snimarEditorController/metadata.py
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
import uuid

# UI generated python modules
from qgis.PyQt.QtCore import Qt, QPoint
from qgis.PyQt.QtGui import QIcon, QCursor
from qgis.PyQt.QtWidgets import QToolTip, QDateTimeEdit, QDateEdit, QWidget
from EditorMetadadosMarswInforbiomares.snimarQtInterfaceView.pyuic4GeneratedSourceFiles import metadataPanel
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import table_list_aux as tla
from EditorMetadadosMarswInforbiomares import CONSTANTS as cons
from EditorMetadadosMarswInforbiomares.snimarEditorController import contactWidget
from EditorMetadadosMarswInforbiomares.snimarProfileModel import snimarProfileModel
from EditorMetadadosMarswInforbiomares.snimarEditorController.models.table_list_aux import unsetLabelRed
from EditorMetadadosMarswInforbiomares.snimarEditorController.models import customComboBoxModel as customCombo
from  EditorMetadadosMarswInforbiomares.snimarEditorController.models.null_QDateEdit import NullQDateEditWrapper


class MetadataWidget(QWidget, metadataPanel.Ui_metadata):
    def __init__(self, parent):
        super(MetadataWidget, self).__init__(parent)
        self.setupUi(self)
        self.datestamp = NullQDateEditWrapper(self.datestamp)
        self.superParent = self.parent()

        tla.setupMandatoryField(self, self.fileidentifier, self.label_fileidentifier, u"Elemento obrigatório em falta")
        tla.setupMandatoryField(self, self.datestamp, self.label_datestamp, u"Elemento obrigatório em falta")
        tla.setupMandatoryField(self, self.language, self.label_language, u"Elemento obrigatório em falta")
        tla.setupMandatoryField(self, self.stdname, self.label_stdname, u"Elemento obrigatório em falta")
        tla.setupMandatoryField(self, self.stdversion, self.label_stdversion, u"Elemento obrigatório em falta")

        self.pal = qgui.QPalette()
        self.pal.setColor(self.pal.Background, qgui.QColor(cons.ERROR_COLOR))
        self.contacts_list = []

        for btn in self.findChildren(qwidgets.QPushButton, qcore.QRegExp('btn_*')):
            if '_add_' in btn.objectName():
                btn.setIcon(qgui.QIcon(':/resourcesFolder/icons/plus_icon.svg'))
                btn.setText('')
            elif '_del_' in btn.objectName():
                btn.setIcon(qgui.QIcon(':/resourcesFolder/icons/delete_icon.svg'))
                btn.setText('')
            elif '_clear_' in btn.objectName():
                btn.setIcon(qgui.QIcon(':/resourcesFolder/icons/delete_field.svg'))

            split_name = btn.objectName().split('_')
            if len(split_name) == 4 and split_name[2] == 'uuid':
                btn.clicked.connect(self.generate_uuid)

        for info in self.findChildren(qwidgets.QPushButton, qcore.QRegExp('info_*')):
            info.setIcon(qgui.QIcon(':/resourcesFolder/icons/help_icon.svg'))
            info.setText('')
            info.pressed.connect(self.printHelp)

        self.btn_adi_contact.setIcon(qgui.QIcon(':/resourcesFolder/icons/plus_icon.svg'))
        self.combo_items_languagecode = customCombo.dic_to_CustomComboBox_dic(
            self.superParent.codelist["LanguageCode"])
        self.combo_items_md_charactersetCode = customCombo.dic_to_CustomComboBox_dic(self.superParent.codelist["MD_CharacterSetCode"])

        self.language.setModel(
            customCombo.CustomComboBoxModel(self, sorted(list(self.combo_items_languagecode.values()), key=lambda x: x.term_pt)))
        self.language.setCurrentIndex(self.language.findText(cons.PREDEF_LANG_METADATA))
        self.language.setDisabled(True)
        self.datestamp.clear()
        self.characterset.setModel(
            customCombo.CustomComboBoxModel(self, sorted(list(self.combo_items_md_charactersetCode.values()), key=lambda x: x.term_pt)))
        self.characterset.setCurrentIndex(self.characterset.findText(cons.PREDEF_CHARSET))

        self.stdname.setText(cons.SNIMAR_PROFILE_NAME)
        self.stdname.setDisabled(True)
        self.stdversion.setDisabled(True)
        self.stdversion.setText(cons.SNIMAR_PROFILE_VERSION)
        self.btn_adi_contact.clicked.connect(self.addContact)
        self.check_mandatory_contacts()

        self.eater = tla.EatWheel()
        for x in self.findChildren(qwidgets.QComboBox):
            x.installEventFilter(self.eater)
            x.setFocusPolicy(Qt.StrongFocus)
        for x in self.findChildren(QDateEdit):
            x.installEventFilter(self.eater)
            x.setFocusPolicy(Qt.StrongFocus)

        self.btn_clear_datestamp.pressed.connect(lambda: self.datestamp.clear())

        self.datestamp.get_original().editingFinished.connect(self.reftemocheck)
        self.datestamp.get_original().dateTimeChanged.connect(self.reftemocheck)
        self.reftemocheck()

    def reftemocheck(self):
        if self.datestamp.get_date() is None and self.label_datestamp.toolTip() == "":

            label_text = tla.setLabelRed(self.label_datestamp.text().replace(u'\u26a0', '') + u' ' + u'\u26a0')
            self.label_datestamp.setText(label_text)
            self.label_datestamp.setToolTip(u"Elemento Obrigatorio.")
            self.superParent.register_mandatory_missingfield(self.objectName(), unsetLabelRed(self.label_datestamp.text()))
        elif self.datestamp.get_date() is not None and self.label_datestamp.toolTip() != "":
            label_text = tla.unsetLabelRed(self.label_datestamp.text().replace(u'\u26a0', '')).strip()
            self.label_datestamp.setText(label_text)
            self.label_datestamp.setToolTip(u'')
            self.superParent.unregister_mandatory_missingfield(self.objectName(), unsetLabelRed(self.label_datestamp.text()))

    def printHelp(self):
        QToolTip.showText(QCursor.pos(), tla.formatTooltip(self.superParent.helps['metadataPanel'][self.sender().objectName()]), None)

    def addContact(self):
        contact = contactWidget.InlineContactWidget(self, self.superParent.orgs)
        self.Contacts.insertWidget(-1, contact)
        self.Contacts.setAlignment(Qt.AlignTop)
        self.contacts_list.append(contact)
        self.check_mandatory_contacts()
        self.check_contacts_completness()

    def deleteContact(self, contact):
        self.Contacts.removeWidget(contact)
        self.contacts_list.remove(contact)
        contact.close()
        self.check_mandatory_contacts()
        self.check_contacts_completness()

    @qcore.pyqtSlot()
    def generate_uuid(self):
        target_name = self.sender().objectName().split('_')[3]
        target = self.findChild(qwidgets.QLineEdit, target_name)
        uuid_str = str(uuid.uuid4())
        target.setText(uuid_str)

    def get_data(self, md):
        if self.datestamp.get_date() is not None:
            md.datestamp = self.datestamp.get_date().toString(cons.DATE_FORMAT)
        md.identifier = self.fileidentifier.text()
        md.charset = self.characterset.currentText()

        md.language = self.language.itemData(self.language.currentIndex())

        md.stdname = self.stdname.text()
        md.stdver = self.stdversion.text()

        for contact in self.contacts_list:
            temp = contact.get_data()
            if temp.role == "pointOfContact":
                md.contact.insert(0, temp)
            else:
                md.contact.append(temp)

        return md

    def set_data(self, md=None):
        if md is not None:
            self.fileidentifier.setText(md.identifier)

            self.datestamp.setDate(qcore.QDate.fromString(md.datestamp, cons.DATE_FORMAT))

            if self.combo_items_md_charactersetCode.get(md.charset) is None:
                self.characterset.setCurrentIndex(self.characterset.findText(cons.PREDEF_CHARSET))
            else:
                self.characterset.setCurrentIndex(self.characterset.findText(self.combo_items_md_charactersetCode.get(md.charset).term_pt))

            # Set contacts
            contact_index = 0
            for contact in md.contact:
                self.addContact()
                contact_object = self.contacts_list[contact_index]
                contact_object.set_data(contact)
                contact_index += 1
        self.reftemocheck()

    def check_mandatory_contacts(self):
        if self.Contacts.count() == 0:
            label_text = tla.setLabelRed(self.label_contacts.text().replace(u'\u26a0', '') + u' ' + u'\u26a0')
            self.label_contacts.setText(label_text)
            self.label_contacts.setToolTip(u"É necessario pelo menos um contacto.")
            self.superParent.register_mandatory_missingfield(self.objectName(), unsetLabelRed(self.label_contacts.text()))
        else:
            label_text = tla.unsetLabelRed(self.label_contacts.text().replace(u'\u26a0', '')).strip()
            self.label_contacts.setText(label_text)
            self.label_contacts.setToolTip(u"")
            self.superParent.unregister_mandatory_missingfield(self.objectName(), unsetLabelRed(self.label_contacts.text()))

    def check_contacts_completness(self):
        self.check_role()
        for x in self.contacts_list:
            if not x.isComplete():
                self.superParent.register_incomplete_entries(self.objectName(), "Contactos")
                return
        self.superParent.unregister_incomplete_entries(self.objectName(), "Contactos")

    def check_role(self):
        have_poc = False
        for cont in self.contacts_list:
            if cont.get_role() == 'pointOfContact':
                have_poc = True
                break
        if not have_poc:
            label_text = tla.setLabelRed(self.label_contacts.text().replace(u'\u26a0', '') + u' ' + u'\u26a0')
            self.label_contacts.setText(label_text)
            self.label_contacts.setToolTip(u"É necessario pelo menos um contacto com a função 'Contacto'.")
            self.superParent.register_mandatory_missingfield(self.objectName(), unsetLabelRed(self.label_contacts.text()))
        else:
            label_text = tla.unsetLabelRed(self.label_contacts.text().replace(u'\u26a0', '')).strip()
            self.label_contacts.setText(label_text)
            self.label_contacts.setToolTip(u"")
            self.superParent.unregister_mandatory_missingfield(self.objectName(), unsetLabelRed(self.label_contacts.text()))
